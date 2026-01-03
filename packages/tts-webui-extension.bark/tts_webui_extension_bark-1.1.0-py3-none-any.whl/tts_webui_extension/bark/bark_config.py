from tts_webui.config.config_utils import get_config_value, set_config_value

EXTENSION_NAMESPACE = "extension_bark"

DEFAULT_BARK_CONFIG = {
    "text_use_gpu": True,
    "text_use_small": True,
    "coarse_use_gpu": True,
    "coarse_use_small": True,
    "fine_use_gpu": True,
    "fine_use_small": True,
    "codec_use_gpu": True,
}


def get_bark_config_value(key: str, default=None):
    """Get a bark config value, falling back to defaults."""
    if default is None:
        default = DEFAULT_BARK_CONFIG.get(key)
    return get_config_value(EXTENSION_NAMESPACE, key, default)


def set_bark_config_value(key: str, value):
    """Set a bark config value."""
    set_config_value(EXTENSION_NAMESPACE, key, value)


def get_bark_config():
    """Get the full bark config dict."""
    return {key: get_bark_config_value(key) for key in DEFAULT_BARK_CONFIG}


def save_bark_config(
    text_use_gpu: bool,
    text_use_small: bool,
    coarse_use_gpu: bool,
    coarse_use_small: bool,
    fine_use_gpu: bool,
    fine_use_small: bool,
    codec_use_gpu: bool,
):
    """Save all bark config values."""
    set_bark_config_value("text_use_gpu", text_use_gpu)
    set_bark_config_value("text_use_small", text_use_small)
    set_bark_config_value("coarse_use_gpu", coarse_use_gpu)
    set_bark_config_value("coarse_use_small", coarse_use_small)
    set_bark_config_value("fine_use_gpu", fine_use_gpu)
    set_bark_config_value("fine_use_small", fine_use_small)
    set_bark_config_value("codec_use_gpu", codec_use_gpu)

    return f"Saved: {str(get_bark_config())}"


def migrate_bark_config():
    """Migrate bark config from old 'model' namespace to 'extension_bark'."""
    for key in DEFAULT_BARK_CONFIG:
        old_value = get_config_value("model", key, None)
        if old_value is not None:
            set_bark_config_value(key, old_value)
            set_config_value("model", key, None)
