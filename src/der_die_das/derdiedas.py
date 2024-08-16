from kivy.app import App
from kivy.core.text import DEFAULT_FONT, LabelBase
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager

from der_die_das import ASSETS_ROOT_DIR_NAME
from der_die_das.screens.main_menu_screen import MenuScreen
from der_die_das.screens.noun_games.gender_screen import NounGenderScreen
from der_die_das.screens.noun_games.plural_screen import NounPluralScreen
from der_die_das.screens.noun_games.translate_screen import NounTranslateScreen
from der_die_das.screens.settings_screen import SettingsScreen
from der_die_das.screens.stats.gender_screen import StatsGenderScreen
from der_die_das.screens.stats.plural_screen import StatsPluralScreen
from der_die_das.screens.stats.stats_screen import StatsScreen
from der_die_das.screens.stats.translation_screen import StatsTranslationScreen

LabelBase.register(DEFAULT_FONT, str(ASSETS_ROOT_DIR_NAME / "fonts" / "amatic" / "AmaticSC-Regular.ttf"))


class DerDieDasImage(Image):
    def __init__(self, *args, **kwargs):
        super().__init__(source=str(ASSETS_ROOT_DIR_NAME / "images" / "logo.png"), *args, **kwargs)


class DerDieDasApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))

        sm.add_widget(NounGenderScreen(name="game_noun_gender"))
        sm.add_widget(NounPluralScreen(name="game_noun_plural"))
        sm.add_widget(NounTranslateScreen(name="game_noun_translate"))

        sm.add_widget(SettingsScreen(name='settings'))

        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(StatsGenderScreen(name="stats_gender"))
        sm.add_widget(StatsPluralScreen(name="stats_plural"))
        sm.add_widget(StatsTranslationScreen(name="stats_translation"))
        return sm


def main():
    DerDieDasApp().run()


if __name__ == '__main__':
    main()
