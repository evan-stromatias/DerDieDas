# https://www.youtube.com/watch?v=l8Imtec4ReQ&ab_channel=freeCodeCamp.org
from pathlib import Path
from io import BytesIO
import random 

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import Session
from sqlalchemy import func
from gtts import gTTS
from gtts.tts import gTTSError
from kivy.core.audio import SoundLoader, Sound

from der_die_das.german.models import GermanNouns, GermanNounsGenderStats, GermanNounsPluralStats, GermanNounsTranslationStats
from kivy.uix.screenmanager import ScreenManager, Screen

from der_die_das import PRJ_BASE, DATA_ROOT_DIR_NAME, DB_FILE_NAME

def generate_text_to_kivy_sound(text: str, lang:str="de", slow:bool=False, fname:str="audio.mp3") -> Sound:
    try:
        question_audio = gTTS(text=text, lang=lang, slow=slow)
        audio_file = PRJ_BASE / DATA_ROOT_DIR_NAME / fname
        question_audio.save(audio_file)
    except gTTSError:
        audio_file = PRJ_BASE / DATA_ROOT_DIR_NAME / "1-second-of-silence.mp3"
    return SoundLoader.load(str(audio_file))


# Declare both screens
class MenuScreen(Screen):
    pass


class NounGenderScreen(Screen):        
    my_text = StringProperty("")
    translation = StringProperty("")
    correct_answers = StringProperty("0")
    incorrect_answers = StringProperty("0")
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self._correct_answers = 0
        self._incorrect_answers = 0
        self.engine = None
        self.session = None
        self.noun_db_entry = None

        self.sound = None
        self.sound_noun = None


    def _setup(self):
        self.engine = create_engine(f"sqlite:///{DB_FILE_NAME}", echo=True)
        self.session = Session(self.engine)
        if self.noun_db_entry is None:
            self._random_noun()
        self._play_audio_noun_question()

    def _random_noun(self):
        self.noun_db_entry = self.session.execute(select(GermanNouns).order_by(func.random())).first()[0]
        # self.noun_db_entry = self.session.execute(select(GermanNouns)).first()[0]
        self.my_text = self.noun_db_entry.noun
        self.translation = self.noun_db_entry.translation

    def _play_audio_noun_question(self):
        question_audio = gTTS(text=str(self.my_text), lang="de", slow=False)
        # question_audio.save("noun.mp3")
        # self.sound_noun = SoundLoader.load("noun.mp3")
        self.sound_noun = generate_text_to_kivy_sound(str(self.my_text))
        self.sound_noun.bind(on_stop=self.on_stop_playing_noun)
        if self.sound_noun:
            self.sound_noun.play()

    def _play_audio(self, text):
        self.sound = generate_text_to_kivy_sound(text)
        self.sound.bind(on_stop=self.on_stop_playing_gender_noun_feedback)
        if self.sound:
            self.sound.play()

    def _play_audio_correct(self):
        text = f"JA! {self.noun_db_entry.gender} {self.noun_db_entry.noun}"
        self.my_text = text
        self._play_audio(text)

    def _play_audio_incorrect(self):
        text = f"NEIN! {self.noun_db_entry.gender} {self.noun_db_entry.noun}"
        self.my_text = text
        self._play_audio(text)

    def _check_noun(self, noun: str):
        is_correct = noun == self.noun_db_entry.gender
        if is_correct:
            self._play_audio_correct()
            self._correct_answers += 1
            self.correct_answers = str(self._correct_answers)
        else:
            self._play_audio_incorrect()
            self._incorrect_answers +=1
            self.incorrect_answers = str(self._incorrect_answers)

        db = GermanNounsGenderStats(
                nouns_id=self.noun_db_entry.id,
                german_noun=self.noun_db_entry,
                is_correct=is_correct
                )
        self.session.add(db)
        self.session.commit()


    def on_enter(self, *args):
        sup = super().on_enter(*args)
        self._setup()
        return sup

    def on_button_click(self, instance):
        self._check_noun(instance.text.lower())

    def on_stop_playing_noun(self, *args, **kwargs):
        self.sound_noun.unload()

    def on_stop_playing_gender_noun_feedback(self, *args, **kwargs):
        self.sound.unload()
        self._random_noun()
        self._play_audio_noun_question()


class NounPluralScreen(Screen):        
    my_text = StringProperty("")
    my_text_plural = StringProperty("")
    translation = StringProperty("")
    correct_answers = StringProperty("0")
    incorrect_answers = StringProperty("0")
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self._btns = [
            self.ids["FirstPlural"],
            self.ids["SecondPlural"],
            self.ids["ThirdPlural"]
        ]
        
        self._correct_answers = 0
        self._incorrect_answers = 0

        self._noun_plurals = []

        self.engine = None
        self.session = None
        self.noun_db_entry = None

        self.sound = None
        self.sound_noun = None


    def _setup(self):
        self.engine = create_engine(f"sqlite:///{DB_FILE_NAME}", echo=True)
        self.session = Session(self.engine)
        if self.noun_db_entry is None:
            self._random_noun()
        self._play_audio_noun_question()

    def _random_noun(self):
        self._noun_plurals = []
        self.my_text_plural = ""
        self.noun_db_entry = self.session.execute(select(GermanNouns).order_by(func.random())).first()[0]

        self.my_text = f"{self.noun_db_entry.gender} {self.noun_db_entry.noun}. Die ..."
        
        self._noun_plurals.append(self.noun_db_entry.plural)
        random_nouns = self.session.execute(select(GermanNouns).order_by(func.random()).limit(3)).all()

        for noun_t in random_nouns:
            noun = noun_t[0]
            if noun.plural not in self._noun_plurals:
                self._noun_plurals.append(noun.plural)
            if len(self._noun_plurals) == 3:
                break
        
        random.shuffle(self._noun_plurals)
        for btn, rnd_plr in zip (self._btns, self._noun_plurals):
            btn.text = rnd_plr
        print(self._noun_plurals)
        self.translation = self.noun_db_entry.translation

    def _play_audio_noun_question(self):
        self.sound_noun = generate_text_to_kivy_sound(str(self.my_text))
        self.sound_noun.bind(on_stop=self.on_stop_playing_noun)
        if self.sound_noun:
            self.sound_noun.play()

    def _play_audio(self, text):
        self.sound = generate_text_to_kivy_sound(text)
        self.sound.bind(on_stop=self.on_stop_playing_gender_noun_feedback)
        if self.sound:
            self.sound.play()

    def _play_audio_correct(self):
        text1 = f"JA! {self.noun_db_entry.gender} {self.noun_db_entry.noun}. "
        text2 = f"Die {self.noun_db_entry.noun}{self.noun_db_entry.plural.replace('-','')}."

        self.my_text = text1
        self.my_text_plural = text2
        self._play_audio(text1 + text2)

    def _play_audio_incorrect(self):
        text1 = f"NEIN! {self.noun_db_entry.gender} {self.noun_db_entry.noun}. "
        text2 = f"Die {self.noun_db_entry.noun}{self.noun_db_entry.plural.replace('-', '')}."

        self.my_text = text1
        self.my_text_plural = text2
        self._play_audio(text1 + text2)

    def _check_noun(self, noun: str):
        is_correct = noun == self.noun_db_entry.plural
        if is_correct:
            self._play_audio_correct()
            self._correct_answers += 1
            self.correct_answers = str(self._correct_answers)
        else:
            self._play_audio_incorrect()
            self._incorrect_answers +=1
            self.incorrect_answers = str(self._incorrect_answers)

        db = GermanNounsPluralStats(
                nouns_id=self.noun_db_entry.id,
                german_noun=self.noun_db_entry,
                is_correct=is_correct
                )
        self.session.add(db)
        self.session.commit()


    def on_enter(self, *args):
        sup = super().on_enter(*args)
        self._setup()
        return sup

    def on_button_click(self, instance):
        self._check_noun(instance.text)

    def on_stop_playing_noun(self, *args, **kwargs):
        self.sound_noun.unload()

    def on_stop_playing_gender_noun_feedback(self, *args, **kwargs):
        self.sound.unload()
        self._random_noun()
        self._play_audio_noun_question()

class NounTranslateScreen(Screen):        
    my_text = StringProperty("")
    correct_answers = StringProperty("0")
    incorrect_answers = StringProperty("0")
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self._btns = [
            self.ids["First"],
            self.ids["Second"],
            self.ids["Third"]
        ]
        
        self._correct_answers = 0
        self._incorrect_answers = 0

        self._noun_translations = []

        self.engine = None
        self.session = None
        self.noun_db_entry = None

        self.sound = None
        self.sound_noun = None


    def _setup(self):
        self.engine = create_engine(f"sqlite:///{DB_FILE_NAME}", echo=True)
        self.session = Session(self.engine)
        if self.noun_db_entry is None:
            self._random_noun()
        self._play_audio_noun_question()

    def _random_noun(self):
        self._noun_translations = []
        self.my_text_plural = ""
        self.noun_db_entry = self.session.execute(select(GermanNouns).order_by(func.random())).first()[0]

        self.my_text = f"{self.noun_db_entry.gender} {self.noun_db_entry.noun}."
        
        self._noun_translations.append(self.noun_db_entry.translation)
        random_nouns = self.session.execute(select(GermanNouns).order_by(func.random()).limit(3)).all()

        for noun_t in random_nouns:
            noun = noun_t[0]
            if noun.plural not in self._noun_translations:
                self._noun_translations.append(noun.translation)
            if len(self._noun_translations) == 3:
                break
        
        random.shuffle(self._noun_translations)
        for btn, rnd_ in zip (self._btns, self._noun_translations):
            btn.text = rnd_
        print(self._noun_translations)

    def _play_audio_noun_question(self):
        self.sound_noun = generate_text_to_kivy_sound(str(self.my_text))
        self.sound_noun.bind(on_stop=self.on_stop_playing_noun)
        if self.sound_noun:
            self.sound_noun.play()

    def _play_audio(self, text, lang:str = "de"):
        self.sound = generate_text_to_kivy_sound(text, lang=lang)
        self.sound.bind(on_stop=self.on_stop_playing_gender_noun_feedback)
        if self.sound:
            self.sound.play()

    def _play_audio_correct(self):
        text = f"Yes! {self.noun_db_entry.translation}. "

        self.my_text = text
        self._play_audio(text, lang="en")

    def _play_audio_incorrect(self):
        text = f"No! {self.noun_db_entry.translation}. "

        self.my_text = text
        self._play_audio(text, lang="en")

    def _check_noun(self, translation: str):
        is_correct = translation == self.noun_db_entry.translation
        if is_correct:
            self._play_audio_correct()
            self._correct_answers += 1
            self.correct_answers = str(self._correct_answers)
        else:
            self._play_audio_incorrect()
            self._incorrect_answers +=1
            self.incorrect_answers = str(self._incorrect_answers)

        db = GermanNounsTranslationStats(
                nouns_id=self.noun_db_entry.id,
                german_noun=self.noun_db_entry,
                is_correct=is_correct
                )
        self.session.add(db)
        self.session.commit()


    def on_enter(self, *args):
        sup = super().on_enter(*args)
        self._setup()
        return sup
    
    def on_leave(self, *args):
        if self.sound:
            self.sound.stop()
            self.sound = None

    def on_button_click(self, instance):
        self._check_noun(instance.text)

    def on_stop_playing_noun(self, *args, **kwargs):
        self.sound_noun.unload()

    def on_stop_playing_gender_noun_feedback(self, *args, **kwargs):
        self.sound.unload()
        self._random_noun()
        self._play_audio_noun_question()
class SettingsScreen(Screen):
    pass

class StatsScreen(Screen):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = create_engine(f"sqlite:///{DB_FILE_NAME}", echo=True)
        self.session = Session(self.engine)



    def on_enter(self, *args):
        sup = super().on_enter(*args)

        noun_gender_results = self.session.execute(
        select(GermanNounsGenderStats, func.count(GermanNounsGenderStats.nouns_id).label("times")
               ).group_by(GermanNounsGenderStats.nouns_id
                          ).having(GermanNounsGenderStats.is_correct != True
                                   ).order_by(desc("times")).limit(3)).all()

        for i, ngr in enumerate(noun_gender_results):
            self.ids[f"GenderNounStatsIncorrect{i}"].text = f"{ngr[0].german_noun.gender} {ngr[0].german_noun.noun}"
            self.ids[f"GenderNounStatsIncorrect{i}Times"].text = str(ngr[1])


        noun_gender_results = self.session.execute(
        select(GermanNounsGenderStats, func.count(GermanNounsGenderStats.nouns_id).label("times")
               ).group_by(GermanNounsGenderStats.nouns_id
                          ).having(GermanNounsGenderStats.is_correct == True
                                   ).order_by(desc("times")).limit(3)).all()

        for i, ngr in enumerate(noun_gender_results):
            self.ids[f"GenderNounStatsCorrect{i}"].text = f"{ngr[0].german_noun.gender} {ngr[0].german_noun.noun}"
            self.ids[f"GenderNounStatsCorrect{i}Times"].text = str(ngr[1])




        noun_gender_results = self.session.execute(
        select(GermanNounsPluralStats, func.count(GermanNounsPluralStats.nouns_id).label("times")
               ).group_by(GermanNounsPluralStats.nouns_id
                          ).having(GermanNounsPluralStats.is_correct != True
                                   ).order_by(desc("times")).limit(3)).all()

        for i, ngr in enumerate(noun_gender_results):
            self.ids[f"GenderPluralStatsIncorrect{i}"].text = f"{ngr[0].german_noun.gender} {ngr[0].german_noun.noun}, {ngr[0].german_noun.plural}"
            self.ids[f"GenderPluralStatsIncorrect{i}Times"].text = str(ngr[1])

        noun_gender_results = self.session.execute(
        select(GermanNounsPluralStats, func.count(GermanNounsPluralStats.nouns_id).label("times")
               ).group_by(GermanNounsPluralStats.nouns_id
                          ).having(GermanNounsPluralStats.is_correct == True
                                   ).order_by(desc("times")).limit(3)).all()

        for i, ngr in enumerate(noun_gender_results):
            self.ids[f"GenderPluralStatsCorrect{i}"].text = f"{ngr[0].german_noun.gender} {ngr[0].german_noun.noun}, {ngr[0].german_noun.plural}"
            self.ids[f"GenderPluralStatsCorrect{i}Times"].text = str(ngr[1])






        noun_gender_results = self.session.execute(
        select(GermanNounsTranslationStats, func.count(GermanNounsTranslationStats.nouns_id).label("times")
               ).group_by(GermanNounsTranslationStats.nouns_id
                          ).having(GermanNounsTranslationStats.is_correct != True
                                   ).order_by(desc("times")).limit(3)).all()

        for i, ngr in enumerate(noun_gender_results):
            self.ids[f"GenderTransStatsIncorrect{i}"].text = f"{ngr[0].german_noun.gender} {ngr[0].german_noun.noun}"
            self.ids[f"GenderTransStatsIncorrect{i}Times"].text = str(ngr[1])

        noun_gender_results = self.session.execute(
        select(GermanNounsTranslationStats, func.count(GermanNounsTranslationStats.nouns_id).label("times")
               ).group_by(GermanNounsTranslationStats.nouns_id
                          ).having(GermanNounsTranslationStats.is_correct == True
                                   ).order_by(desc("times")).limit(3)).all()

        for i, ngr in enumerate(noun_gender_results):
            self.ids[f"GenderTransStatsCorrect{i}"].text = f"{ngr[0].german_noun.gender} {ngr[0].german_noun.noun}"
            self.ids[f"GenderTransStatsCorrect{i}Times"].text = str(ngr[1])


class DerDieDasApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(NounGenderScreen(name="noun_gender"))
        sm.add_widget(NounPluralScreen(name="noun_plural"))
        sm.add_widget(NounTranslateScreen(name="noun_translate"))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(StatsScreen(name='stats'))
        return sm

if __name__ == '__main__':
    DerDieDasApp().run()