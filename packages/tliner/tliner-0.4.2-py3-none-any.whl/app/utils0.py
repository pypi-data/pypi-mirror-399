import sys
from datetime import UTC, datetime

from loguru import logger as L  # noqa: N812

from .config import CONFIG

LOGS_FOLDER = CONFIG.logs_folder
LOGS_FOLDER.mkdir(parents=True, exist_ok=True)

MCP_LOG_FILE = LOGS_FOLDER / f"mcp-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.log"

L.remove()
L.add(sys.stderr, level="TRACE")
L.add(str(MCP_LOG_FILE), backtrace=True, diagnose=True, level="INFO", rotation="10 MB")

L.info(f"Work folder: {CONFIG.work_folder.resolve()}")
