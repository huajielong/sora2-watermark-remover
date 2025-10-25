from pathlib import Path
from typing import Callable

import ffmpeg
import numpy as np
from loguru import logger
from tqdm import tqdm

# 初始化ffmpeg路径配置（优先使用本地ffmpeg）
from sora2wm.utils.ffmpeg_utils import init_ffmpeg
init_ffmpeg()

from sora2wm.utils.video_utils import VideoLoader
from sora2wm.watermark_remover import WaterMarkRemover
from sora2wm.watermark_detector import Sora2WaterMarkDetector


class Sora2WM:
    """Sora2视频水印清除器核心类"""
    
    def __init__(self):
        """初始化水印检测器和清除器"""
        # 初始化水印检测器
        self.detector = Sora2WaterMarkDetector()
        # 初始化水印清除器
        self.Remover = WaterMarkRemover()

    def run(
        self,
        input_video_path: Path,
        output_video_path: Path,
        progress_callback: Callable[[int], None] | None = None,
    ):
        """
        运行水印检测和清除流程
        
        参数:
        - input_video_path: 输入视频路径
        - output_video_path: 输出视频路径
        - progress_callback: 进度回调函数，可选
        """
        # 初始化视频加载器
        input_video_loader = VideoLoader(input_video_path)
        # 确保输出目录存在
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        # 获取视频属性
        width = input_video_loader.width
        height = input_video_loader.height
        fps = input_video_loader.fps
        total_frames = input_video_loader.total_frames

        # 定义临时输出文件路径
        temp_output_path = output_video_path.parent / f"temp_{output_video_path.name}"
        # 视频输出参数配置
        output_options = {
            "pix_fmt": "yuv420p",  # 像素格式
            "vcodec": "libx264",  # 视频编码器
            "preset": "slow",     # 编码预设
        }

        # 根据输入视频比特率设置输出视频质量
        if input_video_loader.original_bitrate:
            # 如果有原始比特率，使用略高的比特率以保证质量
            output_options["video_bitrate"] = str(
                int(int(input_video_loader.original_bitrate) * 1.2)
            )
        else:
            # 否则使用CRF参数控制质量
            output_options["crf"] = "18"

        # 创建FFmpeg输出进程
        process_out = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",  # 原始视频格式
                pix_fmt="bgr24",    # 像素格式
                s=f"{width}x{height}",  # 视频尺寸
                r=fps,               # 帧率
            )
            .output(str(temp_output_path), **output_options)  # 输出配置
            .overwrite_output()       # 覆盖现有文件
            .global_args("-loglevel", "error")  # 最小化日志输出
            .run_async(pipe_stdin=True)  # 异步运行并启用管道输入
        )

        # 存储帧和检测到的水印位置
        frame_and_mask = {}
        # 存储未检测到水印的帧索引
        detect_missed = []

        logger.debug(
            f"总帧数: {total_frames}, 帧率: {fps}, 宽度: {width}, 高度: {height}"
        )
        
        # 第一阶段：检测水印
        for idx, frame in enumerate(
            tqdm(input_video_loader, total=total_frames, desc="检测水印")
        ):
            # 检测当前帧中的水印
            detection_result = self.detector.detect(frame)
            if detection_result["detected"]:
                # 记录检测到水印的帧和边界框
                frame_and_mask[idx] = {"frame": frame, "bbox": detection_result["bbox"]}
            else:
                # 记录未检测到水印的帧
                frame_and_mask[idx] = {"frame": frame, "bbox": None}
                detect_missed.append(idx)

            # 更新进度（10% - 50%）
            if progress_callback and idx % 10 == 0:
                progress = 10 + int((idx / total_frames) * 40)
                progress_callback(progress)

        logger.debug(f"未检测到水印的帧: {detect_missed}")

        # 处理未检测到水印的帧，使用前后帧的水印位置进行插值
        for missed_idx in detect_missed:
            before = max(missed_idx - 1, 0)  # 前一帧索引
            after = min(missed_idx + 1, total_frames - 1)  # 后一帧索引
            before_box = frame_and_mask[before]["bbox"]
            after_box = frame_and_mask[after]["bbox"]
            # 优先使用前一帧的水印位置
            if before_box:
                frame_and_mask[missed_idx]["bbox"] = before_box
            # 如果前一帧没有，使用后一帧
            elif after_box:
                frame_and_mask[missed_idx]["bbox"] = after_box

        # 第二阶段：移除水印
        for idx in tqdm(range(total_frames), desc="移除水印"):
            frame_info = frame_and_mask[idx]
            frame = frame_info["frame"]
            bbox = frame_info["bbox"]
            
            if bbox is not None:
                # 提取水印边界框坐标
                x1, y1, x2, y2 = bbox
                # 创建水印掩码
                mask = np.zeros((height, width), dtype=np.uint8)
                mask[y1:y2, x1:x2] = 255  # 水印区域设为白色
                # 清除水印
                cleaned_frame = self.Remover.clean(frame, mask)
            else:
                # 如果没有检测到水印，使用原始帧
                cleaned_frame = frame
            
            # 将处理后的帧写入FFmpeg输入
            process_out.stdin.write(cleaned_frame.tobytes())

            # 更新进度（50% - 95%）
            if progress_callback and idx % 10 == 0:
                progress = 50 + int((idx / total_frames) * 45)
                progress_callback(progress)

        # 关闭FFmpeg输入流并等待处理完成
        process_out.stdin.close()
        process_out.wait()

        # 更新进度（95%）
        if progress_callback:
            progress_callback(95)

        # 合并音频轨道
        self.merge_audio_track(input_video_path, temp_output_path, output_video_path)

        # 更新进度（99%）
        if progress_callback:
            progress_callback(99)

    def merge_audio_track(
        self,
        input_video_path: Path,
        temp_output_path: Path,
        output_video_path: Path
    ):
        """
        合并原始音频轨道到处理后的视频
        
        参数:
        - input_video_path: 原始视频路径
        - temp_output_path: 无音频的处理后视频路径
        - output_video_path: 最终输出视频路径
        """
        logger.info("合并音频轨道中...")
        # 加载处理后的视频流
        video_stream = ffmpeg.input(str(temp_output_path))
        # 加载原始视频的音频流
        audio_stream = ffmpeg.input(str(input_video_path)).audio

        # 合并视频和音频
        (
            ffmpeg.output(
                video_stream,
                audio_stream,
                str(output_video_path),
                vcodec="copy",  # 直接复制视频流，不重新编码
                acodec="aac",  # 音频编码为AAC
            )
            .overwrite_output()  # 覆盖现有文件
            .run(quiet=True)     # 静默运行
        )
        
        # 清理临时文件
        temp_output_path.unlink()
        logger.info(f"已保存带音频的无水印视频到: {output_video_path}")


if __name__ == "__main__":
    """示例使用方法"""
    from pathlib import Path

    # 示例输入输出路径
    input_video_path = Path(
        "resources/19700121_1645_68e0a027836c8191a50bea3717ea7485.mp4"
    )
    output_video_path = Path("outputs/Sora2_watermark_removed.mp4")
    
    # 创建实例并运行
    Sora2_wm = Sora2WM()
    Sora2_wm.run(input_video_path, output_video_path)
