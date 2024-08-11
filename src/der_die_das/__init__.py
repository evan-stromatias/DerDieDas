from pathlib import Path

PRJ_BASE = Path(__file__).parent  # .parent.parent
DATA_ROOT_DIR_NAME = PRJ_BASE / "data"
ASSETS_ROOT_DIR_NAME = PRJ_BASE / "assets"
AUDIO_ROOT_DIR_NAME = ASSETS_ROOT_DIR_NAME / "audio"

DB_FILE_NAME = "derdiedas.db"
CSV_FILE_NAME = "all_chapters.csv"
NO_AUDIO_FILE_NAME = "1s-silence.mp3"

DERDIEDAS_DIR = Path.home() / ".derdiedas"
DERDIEDAS_DB_PATH = DERDIEDAS_DIR / DB_FILE_NAME
DERDIEDAS_TEMP_DIR = DERDIEDAS_DIR / "tmp"
