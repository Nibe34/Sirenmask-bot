import os
import uuid
from sirenmask.config import TEMP_PATH
from sirenmask.rvc_engine.rvc_wrapper import convert_voice
from sirenmask.utils.audio import convert_ogg_to_wav

async def process_voice(file, model_name, user_settings=None):
    uid = uuid.uuid4().hex
    ogg_path = os.path.join(TEMP_PATH, f"{uid}.ogg")
    wav_path = ogg_path.replace(".ogg", ".wav")
    output_path = ogg_path.replace(".ogg", "_converted.wav")

    try:
        await file.download_to_drive(ogg_path)
        convert_ogg_to_wav(ogg_path, wav_path)
        convert_voice(wav_path, model_name, output_path, user_settings)
        return output_path
    finally:
        # Видалити тимчасові файли
        for path in [ogg_path, wav_path]:
            if os.path.exists(path):
                os.remove(path)
