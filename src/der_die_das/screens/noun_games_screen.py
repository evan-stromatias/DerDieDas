import random

from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from der_die_das.database.db_instance import db
from der_die_das.database.models import (
    BaseDbModel,
    GermanNounsGenderStats,
    GermanNounsPluralStats,
    GermanNounsTranslationStats,
)
from der_die_das.utils import generate_text_to_kivy_sound


class NounGamesBaseScreen(Screen):
    TOTAL_OPTIONS_ANSWERS = 3
    question_text = StringProperty("")
    translation = StringProperty("")
    correct_answers_counter = StringProperty("0")
    incorrect_answers_counter = StringProperty("0")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_correct_answers = 0
        self.total_incorrect_answers = 0

        self.button_1 = self.ids.Button1
        self.button_2 = self.ids.Button2
        self.button_3 = self.ids.Button3

        self.noun_db_entry = None
        self.sound = None
        self.sound_noun = None

        self.proceed_to_next_question = True
        self.translate_noun = True

    @property
    def db_model(self) -> BaseDbModel:
        raise NotImplementedError("User must provide a DB ORM model.")

    def check_answer_logic(self, answer: str) -> bool:
        raise NotImplementedError()

    def update_button_labels(self):
        raise NotImplementedError()

    def generate_question_text(self) -> str:
        raise NotImplementedError()

    def generate_positive_feedback_text(self) -> str:
        raise NotImplementedError()

    def generate_negative_feedback_text(self) -> str:
        raise NotImplementedError()

    def _fetch_random_noun(self):
        self.noun_db_entry = db.random_row()
        self.question_text = self.generate_question_text()
        if self.translate_noun:
            self.translation = self.noun_db_entry.translation

    def _play_audio_question(self):
        self._play_audio_noun_question()

    def _correct_answer_logic(self):
        self._play_audio_correct()
        self.total_correct_answers += 1
        self.correct_answers_counter = str(self.total_correct_answers)

    def _incorrect_answer_logic(self):
        self._play_audio_incorrect()
        self.total_incorrect_answers += 1
        self.incorrect_answers_counter = str(self.total_incorrect_answers)

    def _disable_buttons(self):
        self.button_1.disabled = True
        self.button_2.disabled = True
        self.button_3.disabled = True

    def _enable_buttons(self):
        self.button_1.disabled = False
        self.button_2.disabled = False
        self.button_3.disabled = False

    def _check_answer(self, answer: str):
        self._disable_buttons()
        is_correct = self.check_answer_logic(answer)
        if is_correct:
            self._correct_answer_logic()
        else:
            self._incorrect_answer_logic()

        db.add_db_object(
            db=self.db_model(nouns_id=self.noun_db_entry.id, german_noun=self.noun_db_entry, is_correct=is_correct)
        )

    def _play_audio_noun_question(self):
        self.sound_noun = generate_text_to_kivy_sound(self.generate_question_text())
        self.sound_noun.bind(on_stop=self.on_stop_playing_noun_sound)
        if self.sound_noun:
            self.sound_noun.play()

    def _play_audio(self, text):
        self.sound = generate_text_to_kivy_sound(text)
        self.sound.bind(on_stop=self.on_stop_playing_feedback_sound)
        if self.sound:
            self.sound.play()

    def _play_audio_correct(self):
        text = self.generate_positive_feedback_text()
        self.question_text = text
        self._play_audio(text)

    def _play_audio_incorrect(self):
        text = self.generate_negative_feedback_text()
        self.question_text = text
        self._play_audio(text)

    def _proceed_to_next_question_logic(self):
        self.proceed_to_next_question = True
        self._fetch_random_noun()
        self._play_audio_question()
        self.update_button_labels()

    def _stop_audio(self):
        if self.sound:
            self.sound.stop()
        if self.sound_noun:
            self.sound_noun.stop()

    # Kivy Callbacks
    def on_pre_enter(self, *args):
        sup = super().on_pre_enter(*args)
        if self.proceed_to_next_question:
            self._fetch_random_noun()

        self.proceed_to_next_question = False
        self.update_button_labels()
        return sup

    def on_enter(self, *args):
        sup = super().on_enter(*args)
        self._play_audio_question()
        return sup

    def on_leave(self, *args):
        sup = super().on_leave(*args)
        self._stop_audio()
        return sup

    def on_button_click(self, instance):
        self._check_answer(instance.text.lower())

    def on_stop_playing_noun_sound(self, *args, **kwargs):
        self.sound_noun.unload()

    def on_stop_playing_feedback_sound(self, *args, **kwargs):
        self.sound.unload()
        self._proceed_to_next_question_logic()
        self._enable_buttons()


class NounGenderScreen(NounGamesBaseScreen):
    db_model = GermanNounsGenderStats

    def check_answer_logic(self, answer: str) -> bool:
        return answer.lower() == self.noun_db_entry.gender.lower()

    def generate_question_text(self):
        return str(self.noun_db_entry.noun)

    def generate_positive_feedback_text(self) -> str:
        return f"JA! {self.noun_db_entry.gender} {self.noun_db_entry.noun}"

    def generate_negative_feedback_text(self) -> str:
        return f"NEIN! {self.noun_db_entry.gender} {self.noun_db_entry.noun}"

    def update_button_labels(self):
        self.button_1.text = "Der"
        self.button_2.text = "Die"
        self.button_3.text = "Das"


class NounPluralScreen(NounGamesBaseScreen):
    db_model = GermanNounsPluralStats

    def check_answer_logic(self, answer: str) -> bool:
        return answer.lower() == self.noun_db_entry.plural.lower()

    def generate_question_text(self):
        return f"{self.noun_db_entry.gender} {self.noun_db_entry.noun}. Die ..."

    def generate_positive_feedback_text(self) -> str:
        return f"JA! Die {self.noun_db_entry.noun}{self.noun_db_entry.plural.replace('-','')}."

    def generate_negative_feedback_text(self) -> str:
        return f"NEIN! Die {self.noun_db_entry.noun}{self.noun_db_entry.plural.replace('-', '')}."

    def update_button_labels(self):
        options = self.update_plural_options()
        self.button_1.text = options[0]
        self.button_2.text = options[1]
        self.button_3.text = options[2]

    def update_plural_options(self):
        options = [self.noun_db_entry.plural]

        while len(options) < self.TOTAL_OPTIONS_ANSWERS:
            rnd_noun = db.random_row()
            if rnd_noun.plural not in options:
                options.append(rnd_noun.plural)

        random.shuffle(options)
        return options


class NounTranslateScreen(NounGamesBaseScreen):
    db_model = GermanNounsTranslationStats

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translate_noun = False

    def check_answer_logic(self, answer: str) -> bool:
        return answer.lower() == self.noun_db_entry.translation.lower()

    def generate_question_text(self):
        return f"{self.noun_db_entry.gender} {self.noun_db_entry.noun}"

    def generate_positive_feedback_text(self) -> str:
        return f"Yes! {self.noun_db_entry.translation}"

    def generate_negative_feedback_text(self) -> str:
        return f"No! {self.noun_db_entry.translation}"

    def update_button_labels(self):
        options = self.update_plural_options()
        self.button_1.text = options[0]
        self.button_2.text = options[1]
        self.button_3.text = options[2]

    def update_plural_options(self):
        options = [self.noun_db_entry.translation]
        random_nouns = db.random_rows(self.TOTAL_OPTIONS_ANSWERS - len(options))
        for rn in random_nouns:
            print(rn)
            options.append(rn[0].translation)

        random.shuffle(options)
        return options
