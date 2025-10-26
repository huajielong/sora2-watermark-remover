# Sora2WatermarkRemover

English | [中文](README-zh.md)

This project provides an elegant way to remove the Sora2 watermark in the Sora2 generated videos.


- Watermark removed

https://github.com/user-attachments/assets/8cdc075e-7d15-4d04-8fa2-53dd287e5f4c

- Original

https://github.com/user-attachments/assets/3c850ff1-b8e3-41af-a46f-2c734406e77d

⭐️: **Yolo weights has been updated, try the new version watermark detect model, it should work better. Also, we have uploaded the labelled datasets into huggingface, check this [dataset](https://huggingface.co/datasets/LLinked/Sora2-watermark-dataset) out. Free free to train your custom detector model or improve our model!**


## 1. Method

The Sora2WatermarkRemover(we call it `Sora2Wm` later) is composed of two parsts:

- Sora2WaterMarkDetector: We trained a yolov11s version to detect the Sora2 watermark. (Thank you yolo!)

- WaterMarkRemover: We refer iopaint's implementation for watermark removal using the lama model.

  (This codebase is from https://github.com/Sanster/IOPaint#, thanks for their amazing work!)

Our Sora2Wm is purely deeplearning driven and yields good results in many generated videos.



## 2. Installation

### 2.1 Standard Installation

[FFmpeg](https://ffmpeg.org/) is needed for video processing, please install it first.  We highly recommend using the `uv` to install the environments:

1. installation:

```bash
uv sync
```

> now the envs will be installed at the `.ven`, you can activate the env using:
>
> ```bash
> source .venv/bin/activate
> ```

2. Downloaded the pretrained models:

The trained yolo weights will be stored in the `resources` dir as the `best.pt`.  And it will be automatically download from https://github.com/linkedlist771/Sora2WatermarkRemover/releases/download/V0.0.1/best.pt . The `Lama` model is downloaded from https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt, and will be stored in the torch cache dir. Both downloads are automatic, if you fail, please check your internet status.

### 2.2 Windows Portable Version Configuration

If you're using a Python Standalone packaged portable version, you need to configure local FFmpeg:

1. **Download FFmpeg**:
   - Visit: https://github.com/BtbN/FFmpeg-Builds/releases
   - Download the latest `ffmpeg-master-latest-win64-gpl.zip`
   - Extract the archive

2. **Place FFmpeg Files**:
   - Copy `bin/ffmpeg.exe` from the extracted folder to the project's `ffmpeg/` directory
   - Copy `bin/ffprobe.exe` from the extracted folder to the project's `ffmpeg/` directory
   
   Final directory structure:
   ```
   Sora2WatermarkRemover/
   ├── ffmpeg/
   │   ├── ffmpeg.exe
   │   └── ffprobe.exe
   ├── python/
   └── ...
   ```

3. **Verify Configuration**:
   - The program will automatically detect and use FFmpeg from the `ffmpeg/` directory on startup
   - If local FFmpeg is detected, you'll see "✓ FFmpeg已就绪" in the logs

> **Note**: The program prioritizes FFmpeg in the local `ffmpeg/` directory. If not found, it will fall back to the system's PATH environment variable.

## 3.  Demo

### 3.1 Command Line Usage
To have a basic usage, just try the `example.py`:

```python

from pathlib import Path
from sora2wm.core import Sora2WM


if __name__ == "__main__":
    input_video_path = Path(
        "resources/dog_vs_sam.mp4"
    )
    output_video_path = Path("outputs/Sora2_watermark_removed.mp4")
    Sora2_wm = Sora2WM()
    Sora2_wm.run(input_video_path, output_video_path)

```

### 3.2 Web Interface
We also provide you with a `streamlit` based interactive web page, try it with:

```bash
streamlit run app.py
```

### 3.3 Desktop GUI
We now support a desktop GUI application powered by PyQt5, providing the same functionality as the web interface but with a native desktop experience:

```bash
python desktop.py
```

Or use the provided batch script for Windows:

```bash
run_gui.bat
```

<img src="resources/app.png" style="zoom: 25%;" />

## **4. WebServer**

Here, we provide a **FastAPI-based web server** that can quickly turn this watermark remover into a service.

Simply run:

```
python start_server.py
```

The web server will start on port **5344**.

You can view the FastAPI [documentation](http://localhost:5344/docs) for more details.

There are three routes available:

1. **submit_remove_task**

   > After uploading a video, a task ID will be returned, and the video will begin processing immediately.

<img src="resources/53abf3fd-11a9-4dd7-a348-34920775f8ad.png" alt="image" style="zoom: 25%;" />

2. **get_results**

You can use the task ID obtained above to check the task status.

It will display the percentage of video processing completed.

Once finished, the returned data will include a **download URL**.

3. **download**

You can use the **download URL** from step 2 to retrieve the cleaned video.

## 5. Datasets

We have uploaded the labelled datasets into huggingface, check this out https://huggingface.co/datasets/LLinked/Sora2-watermark-dataset. Free free to train your custom detector model or improve our model!

## 6. API

Packaged as a Cog and [published to Replicate](https://replicate.com/uglyrobot/Sora2-watermark-remover) for simple API based usage.

## 7. License

 Apache License


## 8. Citation

If you use this project, please cite:

```bibtex
@misc{Sora2watermarkRemover2025,
  author = {linkedlist771},
  title = {Sora2WatermarkRemover},
  year = {2025},
  url = {https://github.com/linkedlist771/Sora2WatermarkRemover}
}
```

## 9. Acknowledgments

- [IOPaint](https://github.com/Sanster/IOPaint) for the LAMA implementation
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) for object detection
