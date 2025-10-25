"""
Sora2水印清除器 - 命令行使用示例

此脚本展示如何在命令行环境中使用Sora2WM类处理视频并移除水印
"""

from pathlib import Path

from sora2wm.core import Sora2WM  # 导入水印清除核心类

if __name__ == "__main__":
    # 输入视频路径 - 替换为您要处理的视频文件路径
    input_video_path = Path("resources/dog_vs_sam.mp4")
    
    # 输出视频路径 - 处理后的无水印视频将保存在此路径
    output_video_path = Path("outputs/sora2_watermark_removed.mp4")
    
    # 确保输出目录存在
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建水印清除器实例
    sora2_wm = Sora2WM()
    
    # 运行水印移除处理
    # 此过程会自动执行：
    # 1. 检测视频中的水印位置
    # 2. 逐帧移除水印
    # 3. 合并原始音频
    sora2_wm.run(input_video_path, output_video_path)
