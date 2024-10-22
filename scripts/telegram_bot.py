from telegram import Update
from telegram.ext import filters, Application, CommandHandler, CallbackContext, MessageHandler

from config import TELEGRAM_BOT_TOKEN

from src.generative_ai.services import LangChainService
from src.speech2text.services import WhisperService
from src.fs_manager.services import TelegramBotApiArtifactsIO
from src.audio_formatter.services import PydubService
from src.text2speech.services import XTTSService
from src.telegram_api.services import user_verification
from src.shared.hash import md5_hash


speech_to_text = WhisperService()
text_to_speech = XTTSService()
file_system = TelegramBotApiArtifactsIO()
formatter = PydubService()
langchain = LangChainService()


async def verify_user(update: Update) -> None:
    user_id: str = str(update.effective_user.id)  # type: ignore
    user_verification(user_id)


async def start(update: Update, _: CallbackContext) -> None:
    await verify_user(update)
    await update.message.reply_text('Hello! I am your personal assistant. Let is start)')  # type: ignore


async def handle_audio(update: Update, context: CallbackContext) -> None:
    await verify_user(update)

    artifact_paths = []

    user_id: str = str(update.effective_user.id)  # type: ignore
    chat_id = update.message.chat_id  # type: ignore
    voice_message = update.message.voice  # type: ignore

    if not voice_message:
        await update.message.reply_text('Please, send me audio file.')  # type: ignore
        return

    input_file_path = await file_system.write_user_audio_file(user_id, voice_message)
    artifact_paths.append(input_file_path)
    output_file_path = formatter.processing(input_file_path, '.wav')  # type: ignore
    artifact_paths.append(output_file_path)
    text_message = speech_to_text.transcribe(output_file_path)

    for text_sentence in langchain.ask_model(text_message):
        sentence_hash = md5_hash(text_sentence)
        wav_ai_answer_filepath = file_system.make_user_artifact_file_path(
            user_id=user_id, filename=f'{sentence_hash}.wav'
        )
        artifact_paths.append(wav_ai_answer_filepath)
        text_to_speech.processing(wav_ai_answer_filepath, text_sentence)
        ogg_ai_answer_filepath = formatter.processing(wav_ai_answer_filepath, '.ogg')
        artifact_paths.append(ogg_ai_answer_filepath)
        await send_voice_message(context=context, chat_id=chat_id, file_path=ogg_ai_answer_filepath)

    file_system.delete_artifacts(user_id=user_id, filename_array=artifact_paths)


async def send_voice_message(context: CallbackContext, chat_id, file_path: str):
    with open(file_path, 'rb') as voice_file:
        await context.bot.send_voice(chat_id=chat_id, voice=voice_file)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, handle_audio))

    application.run_polling()


if __name__ == '__main__':
    main()
