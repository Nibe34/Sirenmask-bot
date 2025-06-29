import sys
import os
from types import SimpleNamespace
import torch
import soundfile as sf

from sirenmask.config import VOICE_MODELS_PATH
sys.path.append(os.path.abspath("rvc_lib"))
from rvc_lib.infer.modules.vc.modules import VC
from sirenmask.rvc_engine.postprocess import postprocess_audio


vc_model = None
current_model_name = None

def convert_voice(input_path, model_name, output_path):
    global vc_model, current_model_name

    model_dir = os.path.join(VOICE_MODELS_PATH, model_name)
    model_pth = next((f for f in os.listdir(model_dir) if f.endswith(".pth")), None)
    index_file = next((f for f in os.listdir(model_dir) if f.endswith(".index.pkl")), "")

    if not model_pth:
        raise FileNotFoundError("Модель .pth не знайдено в: " + model_dir)

    # Тепер просто ім’я файлу
    model_pth_filename = model_pth
    index_path = os.path.join(model_dir, index_file) if index_file else ""

    # Ініціалізація, якщо нова модель
    if vc_model is None or current_model_name != model_pth_filename:
        config = SimpleNamespace(
            is_half=False,
            device="cuda" if torch.cuda.is_available() else "cpu",
            x_pad=1,
            x_query=10,
            x_center=60,
            x_max=65
        )
        vc_model = VC(config)
        current_model_name = model_pth_filename

        os.environ["weight_root"] = VOICE_MODELS_PATH  # це важливо
        print(f"[✅] Завантаження моделі: {model_pth_filename}")
        relative_model_path = os.path.join(model_name, model_pth_filename)
        os.environ["weight_root"] = VOICE_MODELS_PATH
        os.environ["index_root"] = VOICE_MODELS_PATH
        os.environ["rmvpe_root"] = os.path.join("rvc_lib", "assets", "rmvpe")
        vc_model.get_vc(relative_model_path)

    info, output = vc_model.vc_single(
        sid=0,
        input_audio_path=input_path,
        f0_up_key=2,        # зміщення основної частоти (у півтонах), при >0 стає більш жіночним, при <0 більш чоловічним
        f0_file=None,
        f0_method="rmvpe",  # найвища якість
        file_index=index_path,
        file_index2="",
        index_rate=0.8,     # індекс подібності ознак голосу до навченої моделі, значення від 0 до 1
        filter_radius=7,    # зглажування частоти від 0 до 10, зменшуєшум але иоже прибирати деталі
        resample_sr=48000,  # частота дискретизації, покращує якість. 48000 це досить багато
        rms_mix_rate=0.25,  # баланс гучності між оригінальним і синтезованим сигналами, 0-1, оптимально 0.2-0.4
        protect=0.5         # захист нестабільних частот від заміни, 0-1, оптимально 0.25-0.5
    )

    if "Success" in info:
        sr, audio = output
        temp_path = output_path.replace(".wav", "_raw.wav")
        sf.write(temp_path, audio, sr)
        postprocess_audio(temp_path, output_path)
        os.remove(temp_path)
    else:
        raise RuntimeError(f"🔴 Конверсія не вдалася: {info}")
