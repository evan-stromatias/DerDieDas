"""Given a CSV file with German Nouns initialize the Database."""

import argparse
import csv
from pathlib import Path

import tqdm
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from der_die_das import DATA_ROOT_DIR_NAME, DB_FILE_NAME, DERDIEDAS_DB_PATH, DERDIEDAS_DIR, DERDIEDAS_TEMP_DIR, PRJ_BASE
from der_die_das.database.models import *  # noqa

DATA_ROOT = PRJ_BASE / DATA_ROOT_DIR_NAME
DATA_CSV_FILE = "all_chapters.csv"


def parse_args() -> argparse.Namespace:
    """Parsing the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--csv",
        type=Path,
        help="Path to the CSV file with the German nouns to load to the db.",
        required=True,
    )
    return parser.parse_args()


def cli():
    DERDIEDAS_TEMP_DIR.mkdir(parents=True, exist_ok=True)

    args = parse_args()
    path_to_csv = args.csv
    print(f"Loading csv file: '{path_to_csv}' to the DerDieDas database.")

    init_db(path_to_db_file=DERDIEDAS_DIR / DB_FILE_NAME, path_to_csv_file=path_to_csv)


def main():
    DERDIEDAS_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    init_db(path_to_db_file=DERDIEDAS_DB_PATH, path_to_csv_file=DATA_ROOT_DIR_NAME / "all_chapters.csv")


def initialize_db(path_to_db_file: Path, echo: bool = False) -> Engine:
    engine = create_engine(f"sqlite:///{path_to_db_file}", echo=echo)
    BaseDbModel.metadata.create_all(engine)
    return engine


def init_db(path_to_db_file: Path, path_to_csv_file: Path, echo: bool = False):
    engine = initialize_db(path_to_db_file=path_to_db_file, echo=echo)

    with open(path_to_csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        csv_fieldnames = reader.fieldnames
        expected_fieldnames = GermanNouns.__table__.columns.keys()
        missing = set(csv_fieldnames) - set(expected_fieldnames)
        if missing:
            raise RuntimeError(f"Error the following fieldnames are missing from the CSV file: '{missing}'")

        with Session(engine) as session:
            entries = []
            for row in tqdm.tqdm(reader, desc="Filling up the DerDieDas database"):
                entries.append(GermanNouns(**row))

            session.add_all(entries)
            session.commit()

    print("Done!")


if __name__ == "__main__":
    main()
