from pathlib import Path

from kivy.logger import Logger
from sqlalchemy import create_engine, desc, func, select
from sqlalchemy.orm import Session

from der_die_das import CSV_FILE_NAME, DATA_ROOT_DIR_NAME, DERDIEDAS_TEMP_DIR
from der_die_das.db_fill_data import init_db
from der_die_das.models import (
    GermanNouns,
    GermanNounsGenderStats,
    GermanNounsPluralStats,
    GermanNounsTranslationStats,
)


class Database:
    def __init__(self, db_name: Path, echo: bool = False) -> None:
        Logger.info(f"[Database.__init__]\tLoading DB from {db_name}")
        self.engine = None
        self.session = None
        self._setup(db_name=db_name, echo=echo)

    def _setup(self, db_name: Path, echo: bool):
        if not db_name.exists():
            Logger.info("[Database._setup]\tDatabase does not exist. Initializing it now...")
            DERDIEDAS_TEMP_DIR.mkdir(parents=True, exist_ok=True)
            init_db(path_to_db_file=db_name, path_to_csv_file=DATA_ROOT_DIR_NAME / CSV_FILE_NAME)

        self.engine = create_engine(f"sqlite:///{db_name}", echo=echo)
        self.session = Session(self.engine)

    def random_row(self):
        return self.session.execute(select(GermanNouns).order_by(func.random())).first()[0]

    def random_rows(self, how_many: int = 3):
        return self.session.execute(select(GermanNouns).order_by(func.random()).limit(how_many)).all()

    def add_db_object(self, db):
        self.session.add(db)
        self.session.commit()

    def drop_user_stats_tables(self):
        self.session.query(GermanNounsGenderStats).delete()
        self.session.query(GermanNounsPluralStats).delete()
        self.session.query(GermanNounsTranslationStats).delete()
        self.session.commit()

    def get_stats_for(self, db, is_correct: bool, how_many: int):
        results = self.session.execute(
            select(db, func.count(db.nouns_id).label("times"))
            .group_by(db.nouns_id)
            .having(db.is_correct == is_correct)
            .order_by(desc("times"))
            .limit(how_many)
        ).all()
        return results
