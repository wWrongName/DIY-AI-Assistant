from abc import ABC, abstractmethod

from os import path, makedirs, remove

from telegram import Voice
from config import FS_ROOT_PATH


class BaseArtifactsIO(ABC):
    def __init__(self, root_path: str = FS_ROOT_PATH) -> None:
        self.fs_root = root_path

    async def read_user_audio_file(self, user_id):
        user_artifacts_path = self._make_user_artifacts_path(user_id)
        await self._read_audio_file(user_artifacts_path)

    async def write_user_audio_file(self, user_id: str, voice_message):
        user_artifacts_path = self._make_user_artifacts_path(user_id)
        if not path.exists(user_artifacts_path):
            makedirs(user_artifacts_path)
        return await self._write_audio_file(user_artifacts_path, voice_message)

    def make_user_artifact_file_path(self, user_id: str, filename: str) -> str:
        user_artifacts_path = self._make_user_artifacts_path(user_id)
        return path.join(user_artifacts_path, filename)

    def delete_artifacts(self, user_id: str, filename_array):
        for filename in filename_array:
            file_path = self.make_user_artifact_file_path(user_id, filename)
            if not path.exists(file_path):
                continue
            try:
                remove(file_path)
            except Exception as e:
                print(f'Cannot delete {filename}: {e}')

    def _make_user_artifacts_path(self, user_id) -> str:
        return path.join(self.fs_root, user_id)

    @abstractmethod
    async def _write_audio_file(self, artifacts_dir: str, voice_message):
        pass

    @abstractmethod
    async def _read_audio_file(self, artifacts_dir: str):
        pass


class TelegramBotApiArtifactsIO(BaseArtifactsIO):
    def __init__(self) -> None:
        super().__init__()

    async def _write_audio_file(self, artifacts_dir: str, voice_message: Voice) -> str:
        file = await voice_message.get_file()
        file_name = f'{voice_message.file_unique_id}.ogg'
        file_path = path.join(artifacts_dir, file_name)
        await file.download_to_drive(file_path)
        return file_path

    async def _read_audio_file(self, artifacts_dir: str):
        pass


class WebSocketsBotArtifactsIO(BaseArtifactsIO):
    _WS_BOT_NAMESPACE = 'ws_bot'

    def __init__(self) -> None:
        self.ws_bot_spec_file_name = 'ws_bot_spec_file.wav'
        super().__init__()

    async def write_ws_audio_file(self, filename: str, input_webm_buffer: list, user_id: str = _WS_BOT_NAMESPACE):
        return await self.write_user_audio_file(user_id, {'filename': filename, 'input_webm_buffer': input_webm_buffer})

    async def _write_audio_file(self, artifacts_dir: str, voice_message) -> str:
        file_path = path.join(artifacts_dir, voice_message['filename'])
        with open(file_path, 'ab') as f:
            for data in voice_message['input_webm_buffer']:
                f.write(data)
        return file_path

    def get_spec_file(self, user_id: str = _WS_BOT_NAMESPACE):
        user_artifacts_path = self._make_user_artifacts_path(user_id)
        file_path = path.join(user_artifacts_path, self.ws_bot_spec_file_name)
        return file_path

    def make_ws_artifact_file_path(self, filename: str, user_id: str = _WS_BOT_NAMESPACE) -> str:
        user_artifacts_path = self._make_user_artifacts_path(user_id)
        return path.join(user_artifacts_path, filename)

    async def _read_audio_file(self, artifacts_dir: str):
        pass
