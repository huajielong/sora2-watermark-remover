from pathlib import Path

# 初始化ffmpeg路径配置（优先使用本地ffmpeg）
from sora2wm.utils.ffmpeg_utils import init_ffmpeg
init_ffmpeg()

import ffmpeg
import numpy as np


class VideoLoader:
    """
    视频加载器类，用于高效读取视频帧
    
    基于ffmpeg实现，支持逐帧读取视频，自动处理视频信息获取和资源清理
    """
    
    def __init__(self, video_path: Path):
        """
        初始化视频加载器
        
        参数:
        - video_path: 视频文件路径
        """
        self.video_path = video_path
        # 获取视频信息（分辨率、帧率、总帧数等）
        self.get_video_info()

    def get_video_info(self):
        """
        获取视频基本信息
        
        从视频文件中提取宽度、高度、帧率、总帧数和原始比特率等信息
        """
        # 使用ffmpeg探测视频文件信息
        probe = ffmpeg.probe(self.video_path)
        # 获取第一个视频流的信息
        video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
        
        # 提取视频宽度和高度
        width = int(video_info["width"])
        height = int(video_info["height"])
        
        # 计算帧率（注意：r_frame_rate通常是分数形式，需要eval计算）
        fps = eval(video_info["r_frame_rate"])
        
        # 存储视频基本信息
        self.width = width
        self.height = height
        self.fps = fps
        
        # 尝试获取总帧数
        if "nb_frames" in video_info:
            self.total_frames = int(video_info["nb_frames"])
        else:
            # 如果没有直接提供帧数，则通过时长计算
            duration = float(video_info.get("duration", probe["format"]["duration"]))
            self.total_frames = int(duration * self.fps)

        # 获取原始比特率（如果有）
        original_bitrate = video_info.get("bit_rate", None)
        self.original_bitrate = original_bitrate

    def __len__(self):
        """返回视频总帧数"""
        return self.total_frames

    def __iter__(self):
        """
        迭代器方法，用于逐帧读取视频
        
        生成器模式，每次yield一个视频帧
        确保即使提前退出迭代，资源也会被正确清理
        """
        # 创建ffmpeg子进程，将视频输出为原始视频流
        process_in = (
            ffmpeg.input(self.video_path)
            .output("pipe:", format="rawvideo", pix_fmt="bgr24")  # 输出为BGR格式的原始视频
            .global_args("-loglevel", "error")  # 只输出错误信息
            .run_async(pipe_stdout=True)  # 异步运行，启用标准输出管道
        )

        try:
            # 循环读取每一帧
            while True:
                # 读取一帧的数据（宽度×高度×3通道）
                in_bytes = process_in.stdout.read(self.width * self.height * 3)
                # 如果没有更多数据，退出循环
                if not in_bytes:
                    break

                # 将字节数据转换为numpy数组（BGR格式）
                frame = np.frombuffer(in_bytes, np.uint8).reshape(
                    [self.height, self.width, 3]
                )
                # 生成当前帧
                yield frame
        finally:
            # 确保进程被正确清理，即使提前退出迭代
            process_in.stdout.close()
            if process_in.stderr:
                process_in.stderr.close()
            process_in.wait()


if __name__ == "__main__":
    from tqdm import tqdm

    video_path = Path("resources/dog_vs_sam.mp4")

    # 创建 VideoLoader 实例
    loader = VideoLoader(video_path)

    # 显示视频信息
    print(f"视频路径: {video_path}")
    print(f"分辨率: {loader.width}x{loader.height}")
    print(f"帧率: {loader.fps:.2f} fps")
    print(f"总帧数: {loader.total_frames}")
    print(f"时长: {loader.total_frames / loader.fps:.2f} 秒")
    print("-" * 50)

    # 遍历所有帧并显示进度
    frame_count = 0
    for frame in tqdm(loader, total=len(loader), desc="处理视频"):
        frame_count += 1

        # 每隔 30 帧显示一次信息（可选）
        if frame_count % 30 == 0:
            print(
                f"\n第 {frame_count} 帧 - shape: {frame.shape}, dtype: {frame.dtype}, "
                f"min: {frame.min()}, max: {frame.max()}"
            )

    print(f"\n处理完成！共处理 {frame_count} 帧")

    # 测试提前退出（验证资源清理）
    print("\n测试提前退出...")
    loader2 = VideoLoader(video_path)
    for i, frame in enumerate(loader2):
        if i >= 5:  # 只读取前 5 帧
            print(f"提前退出，已读取 {i+1} 帧")
            break
    print("资源已正确清理")
