from kivy import Logger
from kivy.uix.screenmanager import Screen

from der_die_das.database.db_instance import db


class SettingsScreen(Screen):
    def on_button_click_drop_stats(self, *args, **kwargs):
        Logger.info("Removing all user stats from DB.")
        db.drop_user_stats_tables()
