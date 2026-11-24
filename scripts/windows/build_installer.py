"""Gera um instalador Windows x64 a partir do checkout atual."""

import argparse
import hashlib
import os
import platform
import shutil
import struct
import subprocess
import sys
import tomllib
from importlib.metadata import distribution, version
from pathlib import Path
from tempfile import mkdtemp

import pefile
from PySide6.QtCore import qVersion
import reportlab

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent
RUNTIME_PACKAGES = ("Pillow", "reportlab", "charset-normalizer", "PySide6-Essentials", "shiboken6")


def dll_version(path: Path) -> tuple[int, int]:
    with pefile.PE(str(path), fast_load=True) as dll:
        dll.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]]
        )
        version_info = dll.VS_FIXEDFILEINFO[0]
        return version_info.FileVersionMS, version_info.FileVersionLS


def align_msvc_runtime(bundle: Path) -> None:
    """Usa no carregador as DLLs mais recentes já coletadas no build."""
    libraries = bundle / "_internal"
    for directory in (libraries / "PySide6", libraries / "shiboken6"):
        for dll in directory.glob("*.dll"):
            if not dll.name.lower().startswith(("vcruntime140", "msvcp140")):
                continue
            target = libraries / dll.name.lower()
            if not target.exists() or dll_version(dll) > dll_version(target):
                shutil.copyfile(dll, target)


def collect_licenses(bundle: Path, compiler: Path, fonts: Path) -> None:
    notices = bundle / "Licencas"
    notices.mkdir(exist_ok=True)
    for package in RUNTIME_PACKAGES:
        metadata = distribution(package)
        for item in metadata.files or ():
            if not any(part.lower().startswith(("license", "copying", "notice"))
                       for part in item.parts):
                continue
            target = notices / package / Path(*item.parts[1:])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(metadata.locate_file(item), target)
    shutil.copyfile(fonts / "bitstream-vera-license.txt", notices / "Bitstream-Vera.txt")
    for license_name in ("GPL-3.0.txt", "LGPL-3.0.txt"):
        shutil.copyfile(SCRIPTS / "licenses" / license_name, notices / license_name)
    shutil.copyfile(Path(sys.base_prefix) / "LICENSE.txt", notices / "Python.txt")
    shutil.copyfile(ROOT / "docs" / "THIRD_PARTY_LICENSES.md", notices / "Terceiros.md")
    compiler_license = subprocess.check_output([compiler, "/LICENSE"])
    (notices / "NSIS.txt").write_bytes(compiler_license)
    qt = qVersion()
    pyside = version("PySide6-Essentials")
    (notices / "Versoes-e-fontes.txt").write_text(
        f"Python {platform.python_version()}\n"
        + "".join(f"{name} {version(name)}\n" for name in RUNTIME_PACKAGES)
        + f"Qt {qt}\n\n"
        + f"Qt: https://download.qt.io/official_releases/qt/{'.'.join(qt.split('.')[:2])}/{qt}/single/\n"
        + f"PySide6 e Shiboken: https://code.qt.io/cgit/pyside/pyside-setup.git/tag/?h=v{pyside}\n",
        encoding="utf-8",
    )


def write_uninstall_list(bundle: Path, list_file: Path) -> None:
    contents = sorted((path.relative_to(bundle) for path in bundle.rglob("*")),
                      key=lambda path: (-len(path.parts), str(path).casefold()))
    commands = []
    for relative in contents:
        command = "RMDir" if (bundle / relative).is_dir() else "Delete"
        nsis_path = str(relative).replace("$", "$$")
        commands.append(f'  {command} "$INSTDIR\\{nsis_path}"')
    list_file.write_text("\n".join(commands) + "\n", encoding="utf-8")


def assemble_installer(bundle: Path, compiler: Path, fonts: Path, app_version: str) -> Path:
    work = bundle.parent
    output = ROOT / "dist" / "windows"
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"OKAMI-Memorias-{app_version}-Windows-x64.exe"
    temp_target = work / target.name
    align_msvc_runtime(bundle)
    collect_licenses(bundle, compiler, fonts)
    file_list = work / "uninstall-files.nsh"
    write_uninstall_list(bundle, file_list)
    subprocess.run([
        compiler, "/INPUTCHARSET", "UTF8", f"/DVERSION={app_version}", f"/DBUNDLE={bundle}",
        f"/DSETUP={temp_target}", f"/DFILE_LIST={file_list}", SCRIPTS / "installer.nsi",
    ], cwd=ROOT, check=True)
    temp_target.replace(target)
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    target.with_suffix(".sha256").write_text(f"{digest}  {target.name}\n", encoding="ascii")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--makensis", default="makensis", help="Caminho do compilador NSIS")
    args = parser.parse_args()
    if sys.platform != "win32" or struct.calcsize("P") != 8 or platform.machine() != "AMD64":
        parser.error("Use Python x64 em Windows x64.")
    compiler_path = shutil.which(args.makensis)
    if compiler_path is None:
        parser.error("Compilador NSIS não encontrado. Informe --makensis.")
    compiler = Path(compiler_path).resolve()
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    app_version = project["project"]["version"]
    fonts = Path(reportlab.__file__).with_name("fonts")
    work_root = ROOT / "build" / "windows"
    work_root.mkdir(parents=True, exist_ok=True)
    work = Path(mkdtemp(prefix="p4-", dir=work_root))
    bundle = work / "OKAMI-Memorias"
    # Evita coletar DLLs homônimas de outros programas instalados na estação.
    windows = Path(os.environ["WINDIR"])
    build_env = os.environ.copy()
    build_env["PATH"] = os.pathsep.join(map(str, (
        windows / "System32", windows, Path(sys.base_prefix), Path(sys.base_prefix) / "DLLs",
    )))
    for variable in ("PYTHONHOME", "PYTHONPATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
        build_env.pop(variable, None)
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--onedir", "--windowed", "--noupx",
        "--name", bundle.name, "--distpath", str(work), "--workpath", str(work / "work"),
        "--specpath", str(work), "--paths", str(ROOT / "src"),
        "--add-data", f"{fonts / 'VeraBd.ttf'}:reportlab/fonts", str(SCRIPTS / "entry.py"),
    ], cwd=ROOT, env=build_env, check=True)
    print(assemble_installer(bundle, compiler, fonts, app_version))


if __name__ == "__main__":
    main()
