"""The base class used by all Game Statistic Screens."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from der_die_das.database.db_fill_data import BaseDbModel
from der_die_das.database.db_instance import db


class StatsNounBaseScreen(Screen):
    CORRECT_COLOR = (0, 1, 0, 1)
    INCORRECT_COLOR = (1, 0, 0, 1)
    STATS_SCORE_SIZE_HINT = (0.25, 1.0)
    STATS_LABEL_SIZE = "30dp"
    NUM_STATS = 10
    DB_MODEL = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def db_model(self):
        return None

    def on_enter(self, *args):
        sup = super().on_enter(*args)
        correct = db.get_stats_for(self.db_model, is_correct=True, how_many=self.NUM_STATS)
        incorrect = db.get_stats_for(self.db_model, is_correct=False, how_many=self.NUM_STATS)

        correct_layout = self.ids.correct
        incorrect_layout = self.ids.incorrect

        correct_layout.clear_widgets()
        incorrect_layout.clear_widgets()

        self._fill_stats(layout=correct_layout, data=correct, color=self.CORRECT_COLOR, max_elems=self.NUM_STATS)

        self._fill_stats(layout=incorrect_layout, data=incorrect, color=self.INCORRECT_COLOR, max_elems=self.NUM_STATS)
        return sup

    def _create_widget(
        self, stat: BaseDbModel = None, times: str = None, color: tuple[float, float, float, float] = None
    ) -> Widget:
        g_noun_gender = stat.german_noun.gender if stat is not None else ""
        g_noun = stat.german_noun.noun if stat is not None else ""
        g_noun_plural = stat.german_noun.plural if stat is not None else ""
        times = times if times is not None else ""
        color = color if color is not None else (0, 0, 0, 1)

        hor_box = BoxLayout(orientation="horizontal")
        hor_box.add_widget(
            Label(
                text=f"{g_noun_gender} {g_noun} ({g_noun_plural})",
                color=color,
                font_size=self.STATS_LABEL_SIZE,
            )
        )
        hor_box.add_widget(
            Label(text=f"{times}", color=color, font_size=self.STATS_LABEL_SIZE, size_hint=self.STATS_SCORE_SIZE_HINT)
        )
        return hor_box

    def _fill_stats(self, layout, data, color, max_elems):
        count = 0
        for stat, times in data:
            hor_box = self._create_widget(stat, times, color)
            layout.add_widget(hor_box)
            count += 1
        self._fill_empty(layout, max_elems - count)

    def _fill_empty(self, layout, num):
        for _ in range(num):
            hor_box = self._create_widget()
            layout.add_widget(hor_box)
