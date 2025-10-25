def test_load_model():
    from sora2wm.iopaint.model_manager import ModelManager
    from sora2wm.iopaint.plugins import InteractiveSeg

    interactive_seg_model = InteractiveSeg("vit_l", "cpu")

    models = ["lama", "ldm", "zits", "mat", "fcf", "manga", "migan"]
    for m in models:
        ModelManager(
            name=m,
            device="cpu",
            no_half=False,
            disable_nsfw=False,
            sd_cpu_textencoder=True,
            cpu_offload=True,
        )
