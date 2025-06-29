import os
import uuid
from sirenmask.config import TEMP_PATH
from sirenmask.rvc_engine.rvc_wrapper import convert_voice
from sirenmask.utils.audio import convert_ogg_to_wav

async def process_voice(voice_file, model_name):
    uid = uuid.uuid4().hex
    ogg_path = os.path.join(TEMP_PATH, f"{uid}.ogg")
    wav_path = ogg_path.replace(".ogg", ".wav")
    output_path = ogg_path.replace(".ogg", "_converted.wav")

    await voice_file.download_to_drive(ogg_path)
    convert_ogg_to_wav(ogg_path, wav_path)
    convert_voice(wav_path, model_name, output_path)
    return output_path
