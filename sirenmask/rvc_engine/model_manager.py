import os
from sirenmask.config import VOICE_MODELS_PATH

def get_available_models():
    return [
        name for name in os.listdir(VOICE_MODELS_PATH)
        if os.path.isdir(os.path.join(VOICE_MODELS_PATH, name))
    ]
