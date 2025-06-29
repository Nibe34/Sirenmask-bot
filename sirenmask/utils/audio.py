import os

def convert_ogg_to_wav(ogg_path, wav_path):
    os.system(f"ffmpeg -y -i \"{ogg_path}\" -ar 44100 -ac 1 \"{wav_path}\"")
