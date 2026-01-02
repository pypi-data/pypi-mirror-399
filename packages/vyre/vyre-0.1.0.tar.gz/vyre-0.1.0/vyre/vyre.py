#!/usr/bin/env python3
import os
import sys
import json
import zipfile
import time
import argparse
import shutil
import subprocess
import tempfile
import uuid
import hashlib
import stat
import threading
import signal
from pathlib import Path
from datetime import datetime, timezone

VERSION = "0.1.0"
HOME = Path.home()
VYRE_DIR = HOME.joinpath(".local", "share", "vyre")
LOCKFILE = VYRE_DIR.joinpath(".lock")
BUILD_SLEEP_SECONDS = 4
INSTALL_SLEEP_SECONDS = 3
DEFAULT_MAX_LOG_LINES = 2000
LOG_FILE = VYRE_DIR.joinpath("vyre.log")

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

class SimpleLogger:
    def __init__(self, verbose=False, max_lines=DEFAULT_MAX_LOG_LINES, logfile=LOG_FILE):
        self.verbose = verbose
        self.max_lines = max_lines
        self.lines = []
        self._lock = threading.Lock()
        self.logfile = Path(logfile)
        try:
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def _push(self, level, msg):
        line = f"{now_iso()} [{level}] {msg}"
        with self._lock:
            self.lines.append(line)
            if len(self.lines) > self.max_lines:
                self.lines = self.lines[-self.max_lines:]
            try:
                with open(self.logfile, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception:
                pass
        if self.verbose:
            print(line)

    def info(self, msg):
        self._push("INFO", msg)

    def warn(self, msg):
        self._push("WARN", msg)

    def error(self, msg):
        self._push("ERROR", msg)

    def debug(self, msg):
        self._push("DEBUG", msg)

    def get_lines(self):
        with self._lock:
            return list(self.lines)

logger = SimpleLogger(verbose=False)

class LockGuard:
    def __init__(self, lockfile=LOCKFILE, timeout=10):
        self.lockfile = Path(lockfile)
        self.timeout = timeout
        self.have_lock = False

    def acquire(self):
        start = time.time()
        while True:
            try:
                self.lockfile.parent.mkdir(parents=True, exist_ok=True)
                fd = os.open(str(self.lockfile), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, str(os.getpid()).encode("utf-8"))
                finally:
                    os.close(fd)
                self.have_lock = True
                return True
            except FileExistsError:
                if time.time() - start > self.timeout:
                    return False
                time.sleep(0.1)
            except Exception:
                time.sleep(0.1)

    def release(self):
        if self.have_lock and self.lockfile.exists():
            try:
                self.lockfile.unlink()
            except Exception:
                pass
            self.have_lock = False

    def __enter__(self):
        ok = self.acquire()
        if not ok:
            raise SystemExit("failed to acquire vyre lock")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()

def ensure_dirs():
    try:
        VYRE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def read_json_file(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json_file(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def sanitize_name(s):
    if not isinstance(s, str):
        s = str(s)
    return "".join(c if (c.isalnum() or c in "._-") else "_" for c in s.strip()).strip("._-") or "unknown"

def generate_package_name(meta):
    author = sanitize_name(meta.get("author", "unknown"))
    appname = sanitize_name(meta.get("app_name", meta.get("app", "app")))
    return f"vyre.{author}.{appname}"

def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_extract(zipf, path):
    base = Path(path).resolve()
    for member in zipf.namelist():
        member_path = (Path(path) / member)
        try:
            member_resolved = member_path.resolve()
        except Exception:
            raise SystemExit("invalid archive with unsafe paths")
        try:
            member_resolved.relative_to(base)
        except Exception:
            raise SystemExit("invalid archive with unsafe paths")
    zipf.extractall(path)

class ValidationError(Exception):
    pass

class Manifest:
    required_fields = ("author", "entry_file", "version", "app_name")

    @staticmethod
    def load_from(path):
        data = read_json_file(path)
        Manifest.validate(data)
        return data

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            raise ValidationError("build.json must be an object")
        for f in Manifest.required_fields:
            if f not in data or not data[f]:
                raise ValidationError(f"missing required manifest field: {f}")
        if "package_name" in data and not isinstance(data["package_name"], str):
            raise ValidationError("package_name must be a string")
        if "version" in data and not isinstance(data["version"], (int, float, str)):
            raise ValidationError("version must be number or string")

class ProgressSimulator:
    def __init__(self, total_sec, verbose=False, prefix=""):
        self.total_sec = int(total_sec)
        self.verbose = verbose
        self.prefix = prefix

    def run(self):
        total = max(1, self.total_sec)
        for elapsed in range(1, total + 1):
            pct = int((elapsed / total) * 100)
            if self.verbose:
                print(f"{self.prefix}... {pct}%")
            time.sleep(1)

class PackageBuilder:
    def __init__(self, app_dir, out=None, verbose=False):
        self.app_dir = Path(app_dir)
        self.out = out
        self.verbose = verbose
        self.meta = None

    def verify_structure(self):
        if not self.app_dir.exists():
            raise SystemExit("app directory does not exist")
        content_dir = self.app_dir.joinpath("content")
        if not content_dir.exists() or not content_dir.is_dir():
            raise SystemExit("content/ directory missing inside app directory")
        build_json = self.app_dir.joinpath("build.json")
        if not build_json.exists():
            raise SystemExit("build.json not found in app directory")
        try:
            raw = read_json_file(build_json)
        except Exception:
            raise SystemExit("failed to read build.json")
        try:
            Manifest.validate(raw)
        except ValidationError as e:
            raise SystemExit(f"build.json validation failed: {e}")
        self.meta = raw
        self.meta.setdefault("version", raw.get("version", "0.0.0"))
        self.meta.setdefault("entry_file", raw.get("entry_file", "main.py"))
        self.meta.setdefault("app_name", raw.get("app_name", self.app_dir.name))
        self.meta["package_name"] = generate_package_name(self.meta)
        if "readme" in raw and raw["readme"] and not isinstance(raw["readme"], str):
            self.meta["readme"] = str(raw["readme"])
        if "license" in raw and raw["license"] and not isinstance(raw["license"], str):
            self.meta["license"] = str(raw["license"])
        return True

    def collect_files(self):
        content_dir = self.app_dir.joinpath("content")
        file_list = []
        for root, _, files in os.walk(content_dir):
            for f in files:
                full = Path(root).joinpath(f)
                rel = Path("content") / full.relative_to(content_dir)
                file_list.append((full, str(rel)))
        build_json = self.app_dir.joinpath("build.json")
        optional = []
        for name in ("README.md", "LICENSE"):
            p = self.app_dir.joinpath(name)
            if p.exists():
                optional.append((p, name))
        return file_list, build_json, optional

    def write_metadata_into_zip(self, zf):
        meta_copy = dict(self.meta)
        meta_copy["_built_at"] = now_iso()
        try:
            meta_copy["_sha256"] = compute_sha256(self.app_dir.joinpath("build.json"))
        except Exception:
            pass
        zf.writestr("metadata.json", json.dumps(meta_copy, ensure_ascii=False, indent=2))

    def build(self):
        self.verify_structure()
        files, build_json, optional = self.collect_files()
        package_name = self.meta["package_name"]
        version = str(self.meta["version"])
        out_fname = Path(self.out) if self.out else Path(f"{package_name}-{version}.vy")
        if self.verbose:
            logger.info(f"Preparing {package_name} version {version}")
        tmp = tempfile.mkdtemp(prefix="vyre_build_")
        try:
            with zipfile.ZipFile(out_fname, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for full, arc in files:
                    zf.write(full, arc)
                    if self.verbose:
                        logger.debug(f"added {arc}")
                zf.write(build_json, "build.json")
                for p, name in optional:
                    zf.write(p, name)
                    if self.verbose:
                        logger.debug(f"added optional {name}")
                self.write_metadata_into_zip(zf)
                if self.verbose:
                    logger.debug("finalizing archive")
            if self.verbose:
                p = ProgressSimulator(BUILD_SLEEP_SECONDS, verbose=True, prefix="[vyre build]")
                p.run()
                logger.info(f"Build complete: {out_fname.resolve()}")
            else:
                print(f"Build complete: {out_fname.resolve()}")
            try:
                st = out_fname.stat()
                os.chmod(out_fname, st.st_mode | stat.S_IREAD | stat.S_IWRITE)
            except Exception:
                pass
            return out_fname.resolve()
        finally:
            try:
                shutil.rmtree(tmp)
            except Exception:
                pass

class PackageInstaller:
    def __init__(self, vyre_file, verbose=False):
        self.vyre_file = Path(vyre_file)
        self.verbose = verbose
        self.meta = None

    def validate_package_file(self):
        if not self.vyre_file.exists():
            raise SystemExit("vyre file not found")
        try:
            with zipfile.ZipFile(self.vyre_file, "r") as zf:
                if "metadata.json" not in zf.namelist():
                    raise SystemExit("invalid .vy package (missing metadata.json)")
                raw = json.loads(zf.read("metadata.json").decode("utf-8"))
        except zipfile.BadZipFile:
            raise SystemExit("invalid .vy package (bad zip)")
        self.meta = raw
        if "package_name" not in raw:
            raise SystemExit("invalid package metadata (missing package_name)")
        return True

    def install_deps(self, target_dir):
        deps = self.meta.get("deps", [])
        if not deps:
            return

        deps_dir = target_dir / "_deps"
        deps_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(deps_dir),
            *deps,
        ]

        try:
            subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL if not self.verbose else None,
                stderr=subprocess.DEVNULL if not self.verbose else None,
            )
        except subprocess.CalledProcessError as e:
            raise SystemExit(f"failed to install dependencies: {e}")

    def install(self):
        self.validate_package_file()
        pkg = self.meta["package_name"]
        ensure_dirs()
        target = VYRE_DIR.joinpath(pkg)

        if target.exists():
            backup = VYRE_DIR.joinpath(f"{pkg}.bak.{int(time.time())}")
            try:
                shutil.move(str(target), str(backup))
            except Exception:
                raise SystemExit("failed to backup existing installation")

        try:
            with zipfile.ZipFile(self.vyre_file, "r") as zf:
                target.mkdir(parents=True, exist_ok=True)
                safe_extract(zf, target)
        except Exception as e:
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            raise SystemExit(f"failed to extract package: {e}")

        self.install_deps(target)

        try:
            meta_f = target / "metadata.json"
            meta = json.loads(meta_f.read_text(encoding="utf-8"))
            meta["_installed_at"] = now_iso()
            try:
                meta["_pkg_sha256"] = compute_sha256(self.vyre_file)
            except Exception:
                pass
            write_json_file(meta_f, meta)
        except Exception:
            pass

        if self.verbose:
            p = ProgressSimulator(INSTALL_SLEEP_SECONDS, verbose=True, prefix="[vyre install]")
            p.run()
            logger.info(f"Installed {pkg}")
        else:
            print(f"Installed {pkg}")

        return target
        
class PackageRegistry:
    def __init__(self):
        ensure_dirs()

    def iter_installed(self):
        try:
            entries = sorted(VYRE_DIR.iterdir())
        except Exception:
            entries = []
        for p in entries:
            if not p.is_dir():
                continue
            meta_f = p.joinpath("metadata.json")
            if not meta_f.exists():
                continue
            try:
                meta = json.loads(meta_f.read_text(encoding="utf-8"))
            except Exception:
                continue
            yield p.name, meta

    def list(self):
        for pkg, meta in self.iter_installed():
            pkgname = pkg
            app = meta.get("app_name", "-")
            ver = meta.get("version", "-")
            auth = meta.get("author", "-")
            print(f"{pkgname} - {app} - {ver} - {auth}")

    def find_by_package_or_app(self, name):
        for pkg, meta in self.iter_installed():
            if pkg == name or meta.get("app_name") == name:
                return VYRE_DIR.joinpath(pkg), meta
        return None, None

    def exists(self, package_name):
        return VYRE_DIR.joinpath(package_name).exists()

    def uninstall(self, package_name):
        target = VYRE_DIR.joinpath(package_name)
        if not target.exists():
            raise SystemExit("package not installed")
        backup = VYRE_DIR.joinpath(f"{package_name}.removed.{int(time.time())}")
        try:
            shutil.move(str(target), str(backup))
            try:
                shutil.rmtree(backup)
            except Exception:
                pass
            print(f"Uninstalled {package_name}")
        except Exception:
            raise SystemExit("failed to uninstall package")

class Runner:
    def __init__(self):
        ensure_dirs()
        self.registry = PackageRegistry()

    def resolve_target(self, name):
        pkgdir, meta = self.registry.find_by_package_or_app(name)
        if not pkgdir:
            raise SystemExit("only installed vyre applications can be run")
        return Path(pkgdir)

    def find_entry(self, pkgdir):
        meta_path = pkgdir / "metadata.json"
        if not meta_path.exists():
            raise SystemExit("metadata.json not found in installed package")

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            raise SystemExit("failed to load package metadata")

        entry_file = meta.get("entry_file", "main.py")
        content_dir = pkgdir / "content"

        if not content_dir.exists():
            raise SystemExit("content directory missing")

        entry_path = content_dir / entry_file
        if not entry_path.exists():
            raise SystemExit("entry file not found")

        return entry_path, content_dir

    def run(self, name, args):
        pkgdir = self.resolve_target(name)
        entry_path, content_dir = self.find_entry(pkgdir)

        deps_dir = pkgdir / "_deps"
        env = os.environ.copy()

        paths = []
        if deps_dir.exists():
            paths.append(str(deps_dir))
        paths.append(str(content_dir))
        if env.get("PYTHONPATH"):
            paths.append(env["PYTHONPATH"])

        env["PYTHONPATH"] = os.pathsep.join(paths)

        cmd = [sys.executable, "-u", str(entry_path)] + list(args)
        result = subprocess.run(cmd, cwd=str(content_dir), env=env)
        return result.returncode
        
def parse_args():
    p = argparse.ArgumentParser(
        prog="vyre",
        description="vyre application runner and package manager"
    )

    sp = p.add_subparsers(dest="cmd", required=True)

    # build
    b = sp.add_parser("build", help="build an application into a .vy package")
    b.add_argument("app_dir", help="application directory")
    b.add_argument("-o", "--out", help="output .vy file")
    b.add_argument("-v", "--verbose", action="store_true")

    # install
    i = sp.add_parser("install", help="install a .vy package")
    i.add_argument("vyre_file", help=".vy package file")
    i.add_argument("-v", "--verbose", action="store_true")

    # uninstall
    u = sp.add_parser("uninstall", help="uninstall an installed application")
    u.add_argument("package_name", help="installed package name")

    # list
    sp.add_parser("list", help="list installed applications")

    # info
    info = sp.add_parser("info", help="show application information")
    info.add_argument("package_name", help="installed package or app name")

    # run (ONLY installed apps)
    r = sp.add_parser("run", help="run an installed application")
    r.add_argument("package_name", help="installed package or app name")
    r.add_argument("args", nargs=argparse.REMAINDER, help="arguments passed to the application")

    # version
    sp.add_parser("version", help="show vyre version")

    # verify
    verify = sp.add_parser("verify", help="verify a .vy package")
    verify.add_argument("vyre_file", help=".vy package file")

    # export
    export = sp.add_parser("export", help="export an installed application to a .vy file")
    export.add_argument("package_name", help="installed package name")
    export.add_argument("-o", "--out", help="output .vy file")

    return p.parse_args()
    
def cmd_build(args):
    logger.debug("cmd_build called")
    b = PackageBuilder(args.app_dir, out=args.out, verbose=args.verbose)
    with LockGuard():
        out = b.build()
    return out

def cmd_install(args):
    logger.debug("cmd_install called")
    installer = PackageInstaller(args.vyre_file, verbose=args.verbose)
    with LockGuard():
        target = installer.install()
    return target

def cmd_uninstall(args):
    logger.debug("cmd_uninstall called")
    reg = PackageRegistry()
    with LockGuard():
        pkg = args.package_name
        pkgdir, meta = reg.find_by_package_or_app(pkg)
        if not pkgdir:
            raise SystemExit("package not installed")
        reg.uninstall(pkgdir.name)

def cmd_list(args):
    logger.debug("cmd_list called")
    reg = PackageRegistry()
    reg.list()

def cmd_info(args):
    logger.debug("cmd_info called")
    reg = PackageRegistry()
    pkgdir, meta = reg.find_by_package_or_app(args.package_name)

    if not pkgdir or not meta:
        raise SystemExit("package not installed")

    print(f"package: {meta.get('package_name', '-')}")
    print(f"app: {meta.get('app_name', '-')}")
    print(f"version: {meta.get('version', '-')}")
    print(f"author: {meta.get('author', '-')}")
    print(f"entry: {meta.get('entry_file', 'main.py')}")
    print(f"readme: {meta.get('readme', '-')}")
    print(f"license: {meta.get('license', '-')}")
    print(f"installed_at: {meta.get('_installed_at', '-')}")
    print(f"built_at: {meta.get('_built_at', '-')}")
    
def cmd_run(args):
    logger.debug("cmd_run called")
    runner = Runner()
    extra = args.args if args.args else []
    rc = runner.run(args.package_name, extra)
    sys.exit(rc or 0)

def cmd_version(args):
    print(VERSION)

def cmd_verify(args):
    vyre_file = Path(args.vyre_file)
    if not vyre_file.exists():
        raise SystemExit("vyre file not found")

    try:
        with zipfile.ZipFile(vyre_file, "r") as zf:
            names = zf.namelist()

            if "metadata.json" not in names:
                raise SystemExit("invalid package: metadata.json missing")

            if "build.json" not in names:
                raise SystemExit("invalid package: build.json missing")

            meta = json.loads(zf.read("metadata.json").decode("utf-8"))
            if "package_name" not in meta or "version" not in meta:
                raise SystemExit("invalid metadata.json")

            build = json.loads(zf.read("build.json").decode("utf-8"))
            Manifest.validate(build)

            print("package is valid")

    except zipfile.BadZipFile:
        raise SystemExit("invalid .vy file (bad zip)")
    except json.JSONDecodeError:
        raise SystemExit("invalid json inside package")
        
def cmd_export(args):
    pkg = args.package_name
    reg = PackageRegistry()
    target, meta = reg.find_by_package_or_app(pkg)
    if not target:
        raise SystemExit("package not found")
    out = Path(args.out) if args.out else Path(f"{pkg}.vy")
    tmp = tempfile.mkdtemp(prefix="vyre_export_")
    try:
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(target):
                for f in files:
                    full = Path(root).joinpath(f)
                    arc = full.relative_to(target)
                    zf.write(full, str(arc))
        print(f"Exported {pkg} to {out.resolve()}")
    finally:
        try:
            shutil.rmtree(tmp)
        except Exception:
            pass

def handle_signal(signum, frame):
    try:
        if LOCKFILE.exists():
            pid = LOCKFILE.read_text().strip()
            if pid == str(os.getpid()):
                LOCKFILE.unlink()
    finally:
        sys.exit(1)

signal.signal(signal.SIGINT, handle_signal)
try:
    signal.signal(signal.SIGTERM, handle_signal)
except Exception:
    pass

def main():
    args = parse_args()
    if args.cmd == "build":
        cmd_build(args)
    elif args.cmd == "install":
        cmd_install(args)
    elif args.cmd == "uninstall":
        cmd_uninstall(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "info":
        cmd_info(args)
    elif args.cmd == "run":
        cmd_run(args)
    elif args.cmd == "version":
        cmd_version(args)
    elif args.cmd == "verify":
        cmd_verify(args)
    elif args.cmd == "export":
        cmd_export(args)
    else:
        print("usage: vyre <build|install|uninstall|list|info|run|version|verify|export>")

if __name__ == "__main__":
    main()