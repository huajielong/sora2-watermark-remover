<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="v1.0"/>
  <img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="Apache 2.0"/>
  <img src="https://img.shields.io/badge/python-3.8+-orange" alt="Python 3.8+"/>
  <img src="https://img.shields.io/github/stars/huajielong/sora2-watermark-remover?style=social" alt="Stars"/>
  <img src="https://img.shields.io/badge/GPU-CUDA%20%7C%20CPU-brightgreen" alt="GPU/CPU"/>
  <img src="https://img.shields.io/badge/Model-YOLOv11%20%7C%20LAMA-purple" alt="Models"/>
</p>

<h1 align="center">🎬 Sora2 Watermark Remover</h1>
<p align="center"><b>基于深度学习的 Sora2 视频水印一键移除工具</b></p>
<p align="center">
  🖥️ 命令行 · 🌐 Web 界面 · 🖱️ 桌面 GUI · 🌍 Web 服务
</p>

<p align="center">
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#-core-methodology">🧠 Core Methodology</a> •
  <a href="#-usage-guide">🎮 Usage Guide</a> •
  <a href="#-faq">❓ FAQ</a>
</p>

> [中文说明](README.zh.md)

---

## 🤔 Tired of Manually Removing Watermarks Frame by Frame?

Sora2-generated videos come with built-in watermarks. Manual removal is time-consuming and labor-intensive, while traditional tools produce poor results:

| Problems You May Face | How Sora2 Watermark Remover Helps |
|:----------------------|:----------------------------------|
| ❓ Spending all day removing watermarks frame by frame | ✅ **Fully automated batch processing** — YOLOv11 precise detection + LAMA intelligent inpainting, done with one click |
| ❓ Traditional tools leave obvious修补痕迹 (inpainting artifacts) | ✅ **Deep learning inpainting** — LAMA model fills naturally, leaving almost no visible traces |
| ❓ CLI is too complex for colleagues | ✅ **Three modes available** — CLI / Web UI / Desktop GUI, accessible to everyone |
| ❓ Processing single videos is too slow | ✅ **Web service mode** — Task queue support, batch submit for async processing |
| ❓ Want to train your own detection model but have no data | ✅ **Open-source dataset** — 1000+ labeled samples on Hugging Face, ready to use |

### 🔥 Use Cases

> **Sora2 video batch watermark removal** → **Video content remixing** → **Social media asset processing** → **Video archiving & cleaning**

---

## 🚀 Quick Start

### Requirements

| Dependency | Version |
|:-----------|:-------:|
| Python | 3.8+ |
| FFmpeg | Latest |
| CUDA (optional) | 11.8+ |

### One-Click Installation

```bash
# 1. Clone the repo
git clone https://github.com/huajielong/sora2-watermark-remover.git
cd sora2-watermark-remover

# 2. Create virtual environment (uv recommended)
uv sync
# or using pip
# pip install -r requirements.txt

# 3. Activate environment
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows
```

> ⚡ Pretrained models (YOLOv11 + LAMA) will be downloaded automatically on first run — no manual action needed.

---

## 🧠 Core Methodology

Sora2 Watermark Remover consists of two deep learning components:

```
┌─────────────────────────────────────────────────────────────┐
│                 Sora2 Watermark Remover                       │
├───────────────────────┬─────────────────────────────────────┤
│                       │                                     │
│   🔍 Detection Module │   🧹 Removal Module                  │
│   YOLOv11s Detector   │   LAMA Inpainting Model             │
│                       │                                     │
│   • Precise watermark │   • Intelligent pixel filling        │
│     localization      │   • Background texture preservation  │
│   • Adapts to varying │   • Natural, artifact-free repair    │
│     video resolutions │                                     │
│   • High confidence   │                                     │
│     detection         │                                     │
│                       │                                     │
└───────────────────────┴─────────────────────────────────────┘
```

| Component | Model | Role |
|:----------|:------|:-----|
| 🔍 **Detection** | YOLOv11s | Precisely locates Sora2 watermark position and region |
| 🧹 **Removal** | LAMA (LaMa) | Image inpainting — intelligently fills watermark-covered areas |
| ⚡ **Video Processing** | FFmpeg | Frame extraction and reassembly, lossless quality |

**Result Preview:**

| Before (Original) | After (Watermark Removed) |
|:-----------------:|:-------------------------:|
| Original video with Sora2 watermark | Watermark precisely detected and naturally removed |

---

## 🎮 Usage Guide

Sora2 Watermark Remover offers **4 usage modes** for different scenarios:

### 🖥️ CLI (Fastest to Get Started)

```python
from pathlib import Path
from sora2wm.core import Sora2WM

input_video = Path("input.mp4")
output_video = Path("output_cleaned.mp4")
Sora2_wm = Sora2WM()
Sora2_wm.run(input_video, output_video)
```

### 🌐 Web UI (Interactive)

```bash
streamlit run app.py
```

Open your browser and visit `http://localhost:8501`, then upload a video.

### 🖱️ Desktop GUI (Native Experience)

```bash
python desktop.py
```

Built with PyQt5 for a native desktop experience, drag-and-drop operation, intuitive and easy to use.

**Package as Windows executable:**
```bash
python build_desktop.py
```

### 🌍 Web Service (Batch Processing)

```bash
python start_server.py
```

Starts a FastAPI server (port `5344`) supporting:
- `POST /submit_remove_task` — Submit a video processing task
- `GET /get_results` — Query task progress and results
- `GET /download` — Download the processed video

---

## ⚡ Core Features

| Feature | Description |
|:--------|:------------|
| 🎯 **YOLOv11 Precise Detection** | Trained dedicated detection model to accurately identify Sora2 watermark |
| 🧹 **LAMA Intelligent Inpainting** | Deep learning-based image inpainting, natural artifact-free filling |
| ⚡ **One-Click Batch Processing** | Supports single/batch video processing, fully automated workflow |
| 🖥️ **Three-Mode Interface** | CLI + Web UI + Desktop GUI |
| 🌍 **Web Service Mode** | FastAPI backend, supports remote calls and task queue |
| 🎮 **GPU/CPU Auto-Adaptation** | Uses CUDA acceleration on GPU, falls back to CPU otherwise |
| 📦 **Portable Version Support** | Windows portable package, no Python environment required |
| 🔬 **Open-Source Dataset** | 1000+ labeled Sora2 watermark samples |

---

## 🏗️ Tech Stack

| Technology | Purpose |
|:-----------|:--------|
| **Python** | Core development language |
| **YOLOv11s (Ultralytics)** | Sora2 watermark object detection |
| **LAMA (LaMa)** | Image inpainting and filling |
| **PyTorch** | Deep learning framework |
| **FFmpeg** | Video frame extraction and composition |
| **Streamlit** | Web interactive interface |
| **PyQt5** | Desktop GUI application |
| **FastAPI** | Web service backend |
| **Cog** | Replicate platform deployment |

---

## 📁 Project Structure

```
Sora2WatermarkRemover/
├── sora2wm/                 # Core module
│   ├── core.py              # Main engine
│   ├── detector/            # YOLO watermark detection
│   └── remover/             # LAMA watermark removal
├── app.py                   # Streamlit Web UI
├── desktop.py               # PyQt5 Desktop GUI
├── start_server.py          # FastAPI Web service
├── build_desktop.py         # Desktop package script
├── example.py               # Usage example
├── train/                   # Training scripts
├── datasets/                # Dataset
├── resources/               # Model weights and resources
├── ffmpeg/                  # Windows portable FFmpeg
├── 产品设计PRD.md           # Product requirement document
├── 技术实现方案.md          # Technical implementation plan
├── 工程项目说明书.md        # Project construction guide
├── requirements.txt         # Python dependencies
└── README.md                # 💡 You are here
```

---

## ❓ FAQ

<details>
<summary><b>What hardware is required?</b></summary>
An NVIDIA GPU (CUDA 11.8+) is recommended for best performance. The tool also works without a GPU — it will automatically fall back to CPU mode, though processing will be slower.
</details>

<details>
<summary><b>How are models downloaded?</b></summary>
YOLO weights (best.pt) and the LAMA model (big-lama.pt) are downloaded automatically on first run. If the download fails, please check your network connection or use a proxy.
</details>

<details>
<summary><b>Does it support batch processing multiple videos?</b></summary>
Yes. Use Web service mode (start_server.py) to submit multiple tasks — the system will queue and process them automatically. You can also call Sora2WM in a loop in your code.
</details>

<details>
<summary><b>Will video quality degrade after processing?</b></summary>
No. We use FFmpeg for lossless frame extraction and recomposition. The watermark area is intelligently repaired by LAMA and blends naturally with the rest of the frame — almost invisible to the naked eye.
</details>

<details>
<summary><b>Can I train my own detection model?</b></summary>
Yes! We have uploaded the labeled dataset to Hugging Face (<a href="https://huggingface.co/datasets/LLinked/Sora2-watermark-dataset">Sora2-watermark-dataset</a>). Use the scripts in the train/ directory to train your own model or improve the existing one.
</details>

<details>
<summary><b>How to use it on Windows?</b></summary>
We recommend using the Desktop GUI mode (python desktop.py), or the portable version: download FFmpeg into the ffmpeg/ directory and run. You can also use <code>python build_desktop.py</code> to package a standalone exe.
</details>

---

## 🧪 Dataset

We have uploaded the labeled Sora2 watermark dataset to Hugging Face:

👉 **[Sora2-watermark-dataset](https://huggingface.co/datasets/LLinked/Sora2-watermark-dataset)**

Contains 1000+ labeled images, welcome to use for training your own detection model or improving the existing one!

---

## 📚 Documentation Resources

| Document | Description |
|:---------|:------------|
| [📋 产品设计PRD](产品设计PRD.md) | Detailed product requirement description |
| [🔧 技术实现方案](技术实现方案.md) | System architecture and technical details |
| [📗 工程项目说明书](工程项目说明书.md) | Project structure and development guide |

---

## 🤝 Contributing

Contributions of any kind are welcome — submit Issues, Pull Requests, improve documentation, or train better models.

<a href="https://github.com/huajielong/sora2-watermark-remover/graphs/contributors">
  <img src="https://img.shields.io/badge/contributions-welcome-brightgreen" alt="Contributions Welcome"/>
</a>

### Acknowledgments

- [IOPaint](https://github.com/Sanster/IOPaint) — LAMA model implementation
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) — Object detection framework

## 📄 License

Apache 2.0 © [huajielong](https://github.com/huajielong)
