from pathlib import Path

import requests
from loguru import logger
from tqdm import tqdm

from sora2wm.configs import WATER_MARK_DETECT_YOLO_WEIGHTS

# 检测器权重下载链接
DETECTOR_URL = "https://github.com/linkedlist771/Sora2WatermarkRemover/releases/download/V0.0.1/best.pt"


def download_detector_weights():
    """
    下载水印检测器的YOLO权重文件
    
    如果权重文件不存在，则从GitHub Releases下载
    下载过程中显示进度条，并在完成后记录成功信息
    如果下载失败，会删除部分下载的文件并抛出异常
    """
    # 添加详细日志，显示当前检查的权重文件路径
    logger.debug(f"检查检测器权重文件: {WATER_MARK_DETECT_YOLO_WEIGHTS.absolute()}")
    
    # 检查权重文件是否已经存在
    if WATER_MARK_DETECT_YOLO_WEIGHTS.exists():
        # 记录日志：权重文件已找到，直接使用
        logger.success(f"✓ 本地权重文件已存在，直接使用: {WATER_MARK_DETECT_YOLO_WEIGHTS.absolute()}")
        return
    
    # 额外检查：尝试在当前工作目录和resources目录查找best.pt
    alt_paths = [
        Path('resources') / 'best.pt',  # 相对路径
        Path.cwd() / 'resources' / 'best.pt',  # 当前工作目录下的resources
        Path.cwd() / 'best.pt'  # 当前工作目录下
    ]
    
    # 检查备选路径
    for alt_path in alt_paths:
        if alt_path.exists():
            logger.success(f"✓ 在备选路径找到权重文件: {alt_path.absolute()}")
            # 确保目标目录存在
            WATER_MARK_DETECT_YOLO_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件到目标位置
            try:
                import shutil
                shutil.copy2(alt_path, WATER_MARK_DETECT_YOLO_WEIGHTS)
                logger.success(f"✓ 已将权重文件复制到: {WATER_MARK_DETECT_YOLO_WEIGHTS.absolute()}")
                return
            except Exception as e:
                logger.warning(f"复制权重文件时出错: {e}，将从网络下载")
    
    # 如果所有路径都不存在，记录日志：权重文件未找到，开始下载
    logger.debug(f"检测器权重未找到，从{DETECTOR_URL}下载")
    
    # 确保权重文件的父目录存在
    WATER_MARK_DETECT_YOLO_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 发起HTTP请求下载权重文件
        response = requests.get(DETECTOR_URL, stream=True, timeout=300)
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        
        # 获取文件总大小
        total_size = int(response.headers.get("content-length", 0))
        
        # 写入文件并显示进度条
        with open(WATER_MARK_DETECT_YOLO_WEIGHTS, "wb") as f:
            with tqdm(
                total=total_size, unit="B", unit_scale=True, desc="下载中"
            ) as pbar:
                # 分块下载文件
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤掉保持连接活跃的空块
                        f.write(chunk)
                        pbar.update(len(chunk))  # 更新进度条

        # 记录下载成功日志
        logger.success(f"✓ 权重下载完成: {WATER_MARK_DETECT_YOLO_WEIGHTS}")

    except requests.exceptions.RequestException as e:
        # 如果下载失败且文件已部分写入，删除该文件
        if WATER_MARK_DETECT_YOLO_WEIGHTS.exists():
            WATER_MARK_DETECT_YOLO_WEIGHTS.unlink()
        # 抛出运行时错误，显示下载失败原因
        raise RuntimeError(f"下载失败: {e}")
