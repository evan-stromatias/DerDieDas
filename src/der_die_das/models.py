from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseDbModel(DeclarativeBase):
    pass


class GermanNouns(BaseDbModel):
    __tablename__ = "german_nouns"
    id: Mapped[int] = mapped_column(primary_key=True)
    gender: Mapped[str]
    noun: Mapped[str]
    plural: Mapped[Optional[str]]
    translation: Mapped[str]

    german_nouns_gender_answers: Mapped[Optional[List["GermanNounsGenderStats"]]] = relationship(
        back_populates="german_noun"
    )
    german_nouns_plural_answers: Mapped[Optional[List["GermanNounsPluralStats"]]] = relationship(
        back_populates="german_noun"
    )
    german_nouns_translation_answers: Mapped[Optional[List["GermanNounsTranslationStats"]]] = relationship(
        back_populates="german_noun"
    )

    def __repr__(self) -> str:
        return f"GermanNouns(id={self.id!r}, gender={self.gender!r}, noun={self.noun!r}, plural={self.plural!r}, translation={self.translation!r})"


class GermanNounsGenderStats(BaseDbModel):
    __tablename__ = "german_nouns_gender_stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    nouns_id: Mapped[int] = mapped_column(ForeignKey("german_nouns.id"))
    german_noun: Mapped["GermanNouns"] = relationship(back_populates="german_nouns_gender_answers")
    is_correct: Mapped[bool]

    def __repr__(self) -> str:
        return f"GermanNounsGenderStats(id={self.id!r}, is_correct={self.is_correct!r}, nouns_id={self.nouns_id!r}, german_noun={self.german_noun!r})"


class GermanNounsPluralStats(BaseDbModel):
    __tablename__ = "german_nouns_plural_stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    nouns_id: Mapped[int] = mapped_column(ForeignKey("german_nouns.id"))
    german_noun: Mapped["GermanNouns"] = relationship(back_populates="german_nouns_plural_answers")
    is_correct: Mapped[bool]

    def __repr__(self) -> str:
        return f"GermanNounsPluralStats(id={self.id!r}, is_correct={self.is_correct!r}, nouns_id={self.nouns_id!r}, german_noun={self.german_noun!r})"


class GermanNounsTranslationStats(BaseDbModel):
    __tablename__ = "german_nouns_translation_stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    nouns_id: Mapped[int] = mapped_column(ForeignKey("german_nouns.id"))
    german_noun: Mapped["GermanNouns"] = relationship(back_populates="german_nouns_translation_answers")
    is_correct: Mapped[bool]

    def __repr__(self) -> str:
        return f"GermanNounsTranslationStats(id={self.id!r}, is_correct={self.is_correct!r}, nouns_id={self.nouns_id!r}, german_noun={self.german_noun!r})"
