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
