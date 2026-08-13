from __future__ import annotations

import shutil
import sys
from pathlib import Path

import imageio_ffmpeg
import PyInstaller.__main__


ROOT = Path(__file__).resolve().parent
ENTRY_POINT = ROOT / "WAVnormalize.py"
ICON = ROOT / "icon.ico"
APP_NAME = "WAVNormalizer"
LEGACY_APP_NAMES = ("AutoAudioEnhancer",)


def _remove_if_inside_workspace(path: Path) -> None:
    resolved = path.resolve()
    resolved.relative_to(ROOT)
    if resolved.is_dir():
        shutil.rmtree(resolved)
    elif resolved.exists():
        resolved.unlink()


def main() -> int:
    if not ENTRY_POINT.is_file():
        raise FileNotFoundError(f"Entry point not found: {ENTRY_POINT}")
    if not ICON.is_file():
        raise FileNotFoundError(f"Icon file not found: {ICON}")

    ffmpeg_binary = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    if not ffmpeg_binary.is_file():
        raise FileNotFoundError(f"imageio-ffmpeg binary not found: {ffmpeg_binary}")

    for legacy_name in LEGACY_APP_NAMES:
        _remove_if_inside_workspace(ROOT / "dist" / f"{legacy_name}.exe")
        _remove_if_inside_workspace(ROOT / f"{legacy_name}.spec")

    _remove_if_inside_workspace(ROOT / "build")
    _remove_if_inside_workspace(ROOT / f"{APP_NAME}.spec")

    separator = ";" if sys.platform == "win32" else ":"
    PyInstaller.__main__.run(
        [
            str(ENTRY_POINT),
            "--name",
            APP_NAME,
            "--onefile",
            "--console",
            "--noconfirm",
            "--icon",
            str(ICON),
            "--add-binary",
            f"{ffmpeg_binary}{separator}.",
            "--collect-all",
            "pedalboard",
            "--distpath",
            str(ROOT / "dist"),
            "--workpath",
            str(ROOT / "build"),
            "--specpath",
            str(ROOT),
        ]
    )

    executable = ROOT / "dist" / f"{APP_NAME}.exe"
    if not executable.is_file():
        raise RuntimeError(f"PyInstaller did not create: {executable}")
    print(f"Built: {executable} ({executable.stat().st_size / 1024 / 1024:.1f} MiB)")
    _remove_if_inside_workspace(ROOT / "build")
    _remove_if_inside_workspace(ROOT / f"{APP_NAME}.spec")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
