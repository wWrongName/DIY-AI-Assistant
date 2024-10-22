import os
from dotenv import load_dotenv

load_dotenv()


class EnvironmentError(Exception):
    def __init__(self, env_var_name: str):
        super().__init__(f'Environment variable {env_var_name} is not set')


def getenv(env_var_name: str) -> str:
    env = os.getenv(env_var_name)
    if env is None:
        raise EnvironmentError(env_var_name)
    return env


# Telegram API Setting
TELEGRAM_BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_ALLOWED_USERS = getenv('TELEGRAM_BOT_ALLOWED_USERS').split(',')

# LLM Settings
LLM_MODEL = getenv('LLM_MODEL')

# STT Settings
STT_WHISPER_MODEL = getenv('STT_WHISPER_MODEL')

# TTS Settings
TTS_XTTS_MODEL = getenv('TTS_XTTS_MODEL')
TTS_XTTS_SPEAKER = getenv('TTS_XTTS_SPEAKER')
TTS_XTTS_LANGUAGE = getenv('TTS_XTTS_LANGUAGE')

# File System Settings
config_script_path = os.path.abspath(__file__)
project_root_dir = os.path.dirname(config_script_path)
os.path.join(project_root_dir, getenv('FS_ROOT_PATH'))
FS_ROOT_PATH = os.path.join(project_root_dir, getenv('FS_ROOT_PATH'))

# Audio Capture Settings
AUDIO_CAPTURE_SAMPLE_RATE = float(getenv('AUDIO_CAPTURE_SAMPLE_RATE'))
AUDIO_CAPTURE_CHUNK_SIZE = getenv('AUDIO_CAPTURE_CHUNK_SIZE')
AUDIO_CAPTURE_CHANNELS = getenv('AUDIO_CAPTURE_CHANNELS')
AUDIO_CAPTURE_SILENCE_THRESHOLD = float(getenv('AUDIO_CAPTURE_SILENCE_THRESHOLD'))
AUDIO_CAPTURE_SILENCE_DURATION = float(getenv('AUDIO_CAPTURE_SILENCE_DURATION'))
AUDIO_CAPTURE_FILENAME = getenv('AUDIO_CAPTURE_FILENAME')
AUDIO_CAPTURE_KEY_WORD = getenv('AUDIO_CAPTURE_KEY_WORD')

# WebSockets Settings
WS_HOST = getenv('WS_HOST')
WS_PORT = int(getenv('WS_PORT'))
