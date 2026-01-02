import os
import shutil
from dataclasses import dataclass
from pathlib import Path

CONFIG_FOLDER_NAME = ".tliner"


def _detect_work_folder() -> Path:
    env_value = os.environ.get("TIMELINER_WORK_FOLDER", "").strip()
    if env_value:
        return Path(os.path.expandvars(env_value)).resolve()

    cwd = Path.cwd().resolve()

    if (cwd / CONFIG_FOLDER_NAME).exists():
        return cwd

    default = cwd / "docs" / "timeline"
    (default / CONFIG_FOLDER_NAME).mkdir(parents=True, exist_ok=True)
    return default


def _setup_obsidian_vault(work_folder: Path) -> None:
    obsidian_dir = work_folder / ".obsidian"
    if obsidian_dir.exists():
        return

    template_dir = (Path(__file__).parent / "obsidian-template").resolve()
    if not template_dir.exists():
        return

    shutil.copytree(template_dir, obsidian_dir, dirs_exist_ok=True)


__wf = _detect_work_folder()
_setup_obsidian_vault(__wf)


@dataclass
class TimelinerConfig:
    work_folder: Path
    config_folder: Path
    logs_folder: Path


CONFIG = TimelinerConfig(work_folder=__wf, config_folder=__wf / CONFIG_FOLDER_NAME, logs_folder=__wf / CONFIG_FOLDER_NAME / "logs")
