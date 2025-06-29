import os
import subprocess
import librosa
import numpy as np
import soundfile as sf

def postprocess_audio(audio_path: str, output_path: str):
    # Постобробка аудіо: нормалізація + шумозаглушення (через ffmpeg)
    y, sr = librosa.load(audio_path, sr=None)
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak * 0.95

    temp_norm = output_path.replace(".wav", "_norm.wav")
    sf.write(temp_norm, y, sr)

    command = [
        "ffmpeg", "-y",
        "-i", temp_norm,
        "-af", "afftdn=nf=-25",
        output_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(temp_norm)
