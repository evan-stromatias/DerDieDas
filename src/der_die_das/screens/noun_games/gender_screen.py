from der_die_das.database.models import GermanNounsGenderStats
from der_die_das.screens.noun_games.base_screen import NounGamesBaseScreen


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
