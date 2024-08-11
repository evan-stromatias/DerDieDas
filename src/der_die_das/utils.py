from gtts import gTTS
from gtts.tts import gTTSError
from kivy import Logger
from kivy.core.audio import Sound, SoundLoader

from der_die_das import AUDIO_ROOT_DIR_NAME, DERDIEDAS_TEMP_DIR, NO_AUDIO_FILE_NAME


def generate_text_to_kivy_sound(text: str, lang: str = "de", slow: bool = False, fname: str = "audio.mp3") -> Sound:
    try:
        question_audio = gTTS(text=text, lang=lang, slow=slow)
        audio_file = DERDIEDAS_TEMP_DIR / fname
        question_audio.save(audio_file)
    except gTTSError:
        audio_file = AUDIO_ROOT_DIR_NAME / NO_AUDIO_FILE_NAME
        Logger.info(
            "[generate_text_to_kivy_sound]\t'gTTSError' exception raised possibly due to internet connectivity issues. Text-to-Speech cannot be used."
        )
    return SoundLoader.load(str(audio_file))
