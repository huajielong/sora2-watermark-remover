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

---

<p align="center">
  ⭐ If this project helps you, please give it a Star!
</p>

---

<h1 align="center">🎬 Sora2 Watermark Remover — Sora2视频水印一键移除</h1>
<p align="center"><b>基于YOLOv11+LAMA的Sora2视频水印一键移除工具 — 支持命令行/Web/桌面GUI/Web服务四种模式</b></p>

---

## 🤔 还在手动逐帧去除视频水印？

Sora2 生成的视频自带水印，手动去除费时费力，传统工具效果差：

| 你可能遇到的问题 | Sora2 Watermark Remover 帮你解决 |
|:-----------------|:-------------------------------|
| ❓ 手动逐帧去水印，一整天只处理了几个视频 | ✅ **全自动批处理** — YOLOv11 精准检测 + LAMA 智能修复，一键完成 |
| ❓ 传统去水印工具留下明显修补痕迹 | ✅ **深度学习修复** — LAMA 模型填充自然，几乎看不出处理痕迹 |
| ❓ 命令行操作门槛高，同事用不了 | ✅ **三模式可选** — CLI / Web 界面 / 桌面 GUI，谁都能上手 |
| ❓ 单个视频处理太慢，效率低 | ✅ **Web 服务模式** — 支持任务队列，批量提交异步处理 |
| ❓ 想训练自己的检测模型但没数据 | ✅ **开源数据集** — Hugging Face 已标注 1000+ 样本，直接可用 |

### 🔥 适用场景

> **Sora2 视频批量去水印** → **视频内容二次创作** → **自媒体素材处理** → **视频归档与清洗**

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|:-----|:----:|
| Python | 3.8+ |
| FFmpeg | 最新版 |
| CUDA (可选) | 11.8+ |

### 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/huajielong/sora2-watermark-remover.git
cd sora2-watermark-remover

# 2. 创建虚拟环境（推荐使用 uv）
uv sync
# 或使用 pip
# pip install -r requirements.txt

# 3. 激活环境
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows
```

> ⚡ 预训练模型（YOLOv11 + LAMA）将在首次运行时自动下载，无需手动操作。

---

## 🧠 核心方法

Sora2 Watermark Remover 由两大深度学习组件组成：

```
┌─────────────────────────────────────────────────────────────┐
│                     Sora2 Watermark Remover                    │
├───────────────────────┬─────────────────────────────────────┤
│                       │                                     │
│   🔍 水印检测模块       │   🧹 水印移除模块                    │
│   YOLOv11s Detector   │   LAMA Inpainting Model             │
│                       │                                     │
│   • 精准定位水印区域    │   • 智能填充缺失像素                  │
│   • 适应不同视频分辨率   │   • 保持背景纹理一致性                │
│   • 高置信度检测        │   • 自然无痕修复                     │
│                       │                                     │
└───────────────────────┴─────────────────────────────────────┘
```

| 组件 | 模型 | 作用 |
|:-----|:-----|:------|
| 🔍 **水印检测** | YOLOv11s | 精准定位 Sora2 水印位置和区域 |
| 🧹 **水印移除** | LAMA (LaMa) | 基于图像修复技术，智能填充水印覆盖区域 |
| ⚡ **视频处理** | FFmpeg | 视频帧提取与重组，保证画质无损 |

**效果演示：**

| 处理前（原视频） | 处理后（水印移除） |
|:----------------:|:------------------:|
| 原始视频含 Sora2 水印 | 水印被精准检测并自然移除 |

---

## 🎮 使用方式

Sora2 Watermark Remover 提供 **4 种使用方式**，满足不同场景需求：

### 🖥️ 命令行（最快上手）

```python
from pathlib import Path
from sora2wm.core import Sora2WM

input_video = Path("input.mp4")
output_video = Path("output_cleaned.mp4")
Sora2_wm = Sora2WM()
Sora2_wm.run(input_video, output_video)
```

### 🌐 Web 界面（交互式）

```bash
streamlit run app.py
```

打开浏览器访问 `http://localhost:8501`，上传视频即可。

### 🖱️ 桌面 GUI（原生体验）

```bash
python desktop.py
```

支持 PyQt5 原生桌面体验，拖拽操作，直观易用。

**打包为 Windows 可执行文件：**
```bash
python build_desktop.py
```

### 🌍 Web 服务（批量处理）

```bash
python start_server.py
```

启动 FastAPI 服务（端口 `5344`），支持：
- `POST /submit_remove_task` — 提交视频处理任务
- `GET /get_results` — 查询任务进度和结果
- `GET /download` — 下载处理后的视频

---

## ⚡ 核心功能

| 功能 | 说明 |
|:-----|:------|
| 🎯 **YOLOv11 精准检测** | 训练专用检测模型，精确识别 Sora2 水印 |
| 🧹 **LAMA 智能填充** | 基于深度学习的图像修复，填充自然无痕 |
| ⚡ **一键批处理** | 支持单个/批量视频处理，全自动流程 |
| 🖥️ **三模式界面** | 命令行 + Web 界面 + 桌面 GUI |
| 🌍 **Web 服务模式** | FastAPI 后端，支持远程调用和任务队列 |
| 🎮 **GPU/CPU 自动适配** | 有 GPU 自动使用 CUDA 加速，无 GPU 回退 CPU |
| 📦 **便携版支持** | Windows 便携版，无需安装 Python 环境 |
| 🔬 **开源数据集** | 已标注 1000+ 样本的 Sora2 水印数据集 |

---

## 🏗️ 技术栈

| 技术 | 用途 |
|:-----|:------|
| **Python** | 核心开发语言 |
| **YOLOv11s (Ultralytics)** | Sora2 水印目标检测 |
| **LAMA (LaMa)** | 图像修复与填充 |
| **PyTorch** | 深度学习框架 |
| **FFmpeg** | 视频帧提取与合成 |
| **Streamlit** | Web 交互界面 |
| **PyQt5** | 桌面 GUI 应用 |
| **FastAPI** | Web 服务后端 |
| **Cog** | Replicate 平台部署 |

---

## 📁 项目结构

```
Sora2WatermarkRemover/
├── sora2wm/                 # 核心模块
│   ├── core.py              # 主引擎
│   ├── detector/            # YOLO 水印检测
│   └── remover/             # LAMA 水印移除
├── app.py                   # Streamlit Web 界面
├── desktop.py               # PyQt5 桌面 GUI
├── start_server.py          # FastAPI Web 服务
├── build_desktop.py         # 桌面版打包脚本
├── example.py               # 使用示例
├── train/                   # 训练脚本
├── datasets/                # 数据集
├── resources/               # 模型权重与资源文件
├── ffmpeg/                  # Windows 便携版 FFmpeg
├── 产品设计PRD.md           # 产品需求文档
├── 技术实现方案.md          # 技术方案文档
├── 工程项目说明书.md        # 项目构建指南
├── requirements.txt         # Python 依赖
└── README.md                # 💡 你在这里
```

---

## ❓ 常见问题

<details>
<summary><b>需要什么硬件配置？</b></summary>
推荐使用 NVIDIA GPU（CUDA 11.8+）获得最佳性能。没有 GPU 也可以运行，程序会自动使用 CPU 模式，但处理速度会慢一些。
</details>

<details>
<summary><b>模型是怎么下载的？</b></summary>
YOLO 权重（best.pt）和 LAMA 模型（big-lama.pt）会在首次运行时自动下载。如果下载失败，请检查网络连接或使用代理。
</details>

<details>
<summary><b>支持批量处理多个视频吗？</b></summary>
支持。可以使用 Web 服务模式（start_server.py）提交多个任务，系统会自动排队处理。也可以在代码中循环调用 Sora2WM 处理多个视频。
</details>

<details>
<summary><b>处理后的视频画质会下降吗？</b></summary>
不会。我们使用 FFmpeg 进行无损帧提取和重新合成，水印区域经过 LAMA 智能修复后与其他区域自然融合，肉眼几乎看不出处理痕迹。
</details>

<details>
<summary><b>能训练自己的检测模型吗？</b></summary>
可以！我们已将标注数据集上传到 Hugging Face（<a href="https://huggingface.co/datasets/LLinked/Sora2-watermark-dataset">Sora2-watermark-dataset</a>），可以使用 train/ 目录下的脚本训练你自己的模型或改进现有模型。
</details>

<details>
<summary><b>Windows 上怎么用？</b></summary>
推荐使用桌面 GUI 模式（python desktop.py），或者使用便携版：下载 FFmpeg 放到 ffmpeg/ 目录，然后运行。也可以使用 <code>python build_desktop.py</code> 打包成独立的 exe 文件。
</details>

---

## 🧪 数据集

我们已将标注好的 Sora2 水印数据集上传到 Hugging Face：

👉 **[Sora2-watermark-dataset](https://huggingface.co/datasets/LLinked/Sora2-watermark-dataset)**

包含 1000+ 张标注图像，欢迎用于训练你自己的检测模型或改进现有模型！

---

## 📚 文档资源

| 文档 | 说明 |
|:-----|:------|
| [📋 产品设计PRD](产品设计PRD.md) | 详细的产品需求说明 |
| [🔧 技术实现方案](技术实现方案.md) | 系统架构和技术细节 |
| [📗 工程项目说明书](工程项目说明书.md) | 项目结构和开发指南 |

---

## 🤝 贡献

欢迎任何形式的贡献——提交 Issue、Pull Request、改进文档或训练更好的模型。

<a href="https://github.com/huajielong/sora2-watermark-remover/graphs/contributors">
  <img src="https://img.shields.io/badge/contributions-welcome-brightgreen" alt="Contributions Welcome"/>
</a>

### 致谢

- [IOPaint](https://github.com/Sanster/IOPaint) — LAMA 模型实现
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) — 目标检测框架

## 📄 许可证

Apache 2.0 © [huajielong](https://github.com/huajielong)

---

<p align="center">
  ⭐ 如果这个项目对你有帮助，请点个 Star 支持一下！
</p>
