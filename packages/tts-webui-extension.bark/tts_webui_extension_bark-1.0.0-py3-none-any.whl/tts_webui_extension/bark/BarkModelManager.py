import os

def bark_load_models_direct_api(
    text_use_gpu,
    text_use_small,
    coarse_use_gpu,
    coarse_use_small,
    fine_use_gpu,
    fine_use_small,
    codec_use_gpu,
    c,
    force_reload=False,
    model_name=None,
):
    from bark.generation import load_model, load_codec_model
    from .model_loader.loader import load_models_into_bark

    print("Loading Bark models...")
    if model_name:
        print(f"Loading custom model: {model_name}")
        model_path = os.path.join("data", "models", "bark", model_name)
        if not model_path.endswith(os.path.sep):
            model_path += os.path.sep
        load_models_into_bark(model_path)
        load_codec_model(use_gpu=codec_use_gpu, force_reload=force_reload)
    else:
        load_model("text_use_gpu", c["text_use_gpu"])
        load_model("coarse_use_gpu", c["coarse_use_gpu"])
        load_model("fine_use_gpu", c["fine_use_gpu"])
        load_model("codec_use_gpu", c["codec_use_gpu"])
        
        _ = load_model(
            model_type="text",
            use_gpu=text_use_gpu,
            use_small=text_use_small,
            force_reload=force_reload,
        )
        _ = load_model(
            model_type="coarse",
            use_gpu=coarse_use_gpu,
            use_small=coarse_use_small,
            force_reload=force_reload,
        )
        _ = load_model(
            model_type="fine",
            use_gpu=fine_use_gpu,
            use_small=fine_use_small,
            force_reload=force_reload,
        )
        _ = load_codec_model(use_gpu=codec_use_gpu, force_reload=force_reload)
    print("Loaded Bark models")


class BarkModelManager:
    def __init__(self):
        self.models_loaded = False
        self.current_model_name = None

    def get_models(self):
        models_dir = os.path.join("data", "models", "bark")
        if not os.path.exists(models_dir):
            return []
        return [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]

    def reload_models(self, config, model_name=None):
        from bark.generation import preload_models, load_codec_model
        from .model_loader.loader import load_models_into_bark

        self.models_loaded = True
        self.current_model_name = model_name
        c = config["extension_bark"]

        def _print_prop(name: str, gpu: bool, small: bool):
            def _yes_or_no(x: bool):
                return "Yes" if x else "No"

            print(
                f"\t- {name}:\t\t\t GPU: {_yes_or_no(gpu)}, Small Model: {_yes_or_no(small)}"
            )

        print(f"{'Reloading' if self.models_loaded else 'Loading'} Bark models")
        
        if model_name:
            print(f"Loading custom model: {model_name}")
            model_path = os.path.join("data", "models", "bark", model_name)
            if not model_path.endswith(os.path.sep):
                model_path += os.path.sep
            load_models_into_bark(model_path)
            load_codec_model(use_gpu=c["codec_use_gpu"], force_reload=True)
            return

        _print_prop("Text-to-Semantic", c["text_use_gpu"], c["text_use_small"])
        _print_prop("Semantic-to-Coarse", c["coarse_use_gpu"], c["coarse_use_small"])
        _print_prop("Coarse-to-Fine", c["fine_use_gpu"], c["fine_use_small"])
        _print_prop("Encodec", c["codec_use_gpu"], False)

        # preload_models(**c, force_reload=True)
        preload_models(
            coarse_use_gpu=c["coarse_use_gpu"],
            coarse_use_small=c["coarse_use_small"],
            fine_use_gpu=c["fine_use_gpu"],
            fine_use_small=c["fine_use_small"],
            text_use_gpu=c["text_use_gpu"],
            text_use_small=c["text_use_small"],
            codec_use_gpu=c["codec_use_gpu"],
            force_reload=True,
        )

    def unload_models(self):
        from bark.generation import clean_models

        print("Unloading Bark models...")
        self.models_loaded = False
        clean_models()
        print("Unloaded Bark models")

    def unload_model(self, model_key):
        from bark.generation import clean_models

        print(f"Unloading Bark model {model_key}")
        clean_models(model_key=model_key)
        print(f"Unloaded Bark model {model_key}")


bark_model_manager = BarkModelManager()
