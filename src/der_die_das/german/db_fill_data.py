from pathlib import Path
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from der_die_das import PRJ_BASE, DATA_ROOT_DIR_NAME, DB_FILE_NAME
from der_die_das.german.models import *

DATA_ROOT = Path(__file__).parent.parent / "data"
DATA_CSV_FILE = "all_chapters.csv"

APP_DB = Path.home() / ".der_die_das"
APP_DB.mkdir(parents=True, exist_ok=True)
APP_DB_NAME = "derdiedas.db"

db_url = f"sqlite://{APP_DB / APP_DB_NAME}"
print(db_url)
engine = create_engine(f"sqlite:///{DB_FILE_NAME}", echo=True)
Base.metadata.create_all(engine)

with open(PRJ_BASE / DATA_ROOT_DIR_NAME / DATA_CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    with Session(engine) as session:
        entries = []
        for row in reader:
            entries.append(GermanNouns(**row))

        session.add_all(entries)
        session.commit()