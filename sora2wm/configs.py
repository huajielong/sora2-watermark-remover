from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent.parent


# 资源目录配置
RESOURCES_DIR = ROOT / "resources"  # 资源文件目录
WATER_MARK_TEMPLATE_IMAGE_PATH = RESOURCES_DIR / "watermark_template.png"  # 水印模板图片路径

# 模型权重文件路径
WATER_MARK_DETECT_YOLO_WEIGHTS = RESOURCES_DIR / "best.pt"  # YOLO水印检测模型权重
LAMA_CLEAN_WEIGHTS = RESOURCES_DIR / "big-lama.pt"  # LAMA图像修复模型权重

# 输出目录
OUTPUT_DIR = ROOT / "output"  # 输出文件目录

# 创建输出目录，如已存在则不创建，同时创建父级目录（如果不存在）
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


# 模型配置
DEFAULT_WATERMARK_REMOVE_MODEL = "lama"  # 默认的水印移除模型

# 工作目录
WORKING_DIR = ROOT / "working_dir"  # 临时工作目录
WORKING_DIR.mkdir(exist_ok=True, parents=True)  # 创建工作目录

# 日志目录
LOGS_PATH = ROOT / "logs"  # 日志文件保存路径
LOGS_PATH.mkdir(exist_ok=True, parents=True)  # 创建日志目录

# 数据目录
DATA_PATH = ROOT / "data"  # 数据存储目录
DATA_PATH.mkdir(exist_ok=True, parents=True)  # 创建数据目录

# SQLite数据库文件路径
SQLITE_PATH = DATA_PATH / "db.sqlite3"  # 数据库文件位置


# FFmpeg工具目录
FFMPEG_DIR_PATH = ROOT / "ffmpeg"  # FFmpeg可执行文件目录
FFMPEG_DIR_PATH.mkdir(exist_ok=True, parents=True)  # 创建FFmpeg目录