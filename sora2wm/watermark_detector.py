from pathlib import Path

import numpy as np
from loguru import logger
from ultralytics import YOLO

from sora2wm.configs import WATER_MARK_DETECT_YOLO_WEIGHTS
from sora2wm.utils.download_utils import download_detector_weights
from sora2wm.utils.devices_utils import get_device
from sora2wm.utils.video_utils import VideoLoader

# 基于Sora2水印模板进行检测，然后获取图标部分区域


class Sora2WaterMarkDetector:
    """Sora2视频水印检测器"""
    
    def __init__(self):
        """初始化水印检测器"""
        # 下载检测器权重文件（如果不存在）
        download_detector_weights()
        logger.debug(f"开始加载YOLO水印检测模型。")
        # 加载YOLO模型
        self.model = YOLO(WATER_MARK_DETECT_YOLO_WEIGHTS)
        # 将模型移至适当的设备（CPU或GPU）
        self.model.to(str(get_device()))
        logger.debug(f"YOLO水印检测模型加载完成。")

        # 设置模型为评估模式
        self.model.eval()

    def detect(self, input_image: np.array):
        """
        检测图像中的水印
        
        参数:
        - input_image: 输入图像（numpy数组格式）
        
        返回:
        - 字典，包含检测结果信息：检测状态、边界框、置信度和中心点
        """
        # 运行YOLO模型推理
        results = self.model(input_image, verbose=False)
        # 提取第一个（也是唯一的）结果中的预测
        result = results[0]

        # 检查是否有任何检测结果
        if len(result.boxes) == 0:
            return {"detected": False, "bbox": None, "confidence": None, "center": None}

        # 获取第一个检测结果（置信度最高的）
        box = result.boxes[0]

        # 提取边界框坐标（xyxy格式）
        # 将张量转换为numpy数组，再转换为Python浮点数，最后转换为整数
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
        # 提取置信度分数
        confidence = float(box.conf[0].cpu().numpy())
        # 计算中心点
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        return {
            "detected": True,
            "bbox": (int(x1), int(y1), int(x2), int(y2)),  # 边界框坐标
            "confidence": confidence,  # 检测置信度
            "center": (int(center_x), int(center_y)),  # 中心点坐标
        }


if __name__ == "__main__":
    """水印检测器的演示示例"""
    from pathlib import Path

    import cv2
    from tqdm import tqdm

    # ========= 配置参数 =========
    # video_path = Path("resources/puppies.mp4") # 可选视频路径
    video_path = Path("resources/19700121_1645_68e0a027836c8191a50bea3717ea7485.mp4")
    save_video = True  # 是否保存可视化结果视频
    out_path = Path("outputs/Sora2_watermark_yolo_detected.mp4")  # 输出视频路径
    window = "Sora2 Watermark YOLO Detection"  # 显示窗口名称
    # ===========================

    # 初始化检测器
    detector = Sora2WaterMarkDetector()

    # 初始化视频加载器
    video_loader = VideoLoader(video_path)

    # 预取一帧确定视频尺寸和帧率
    first_frame = None
    for first_frame in video_loader:
        break
    assert first_frame is not None, "无法读取视频帧"

    # 获取视频尺寸和帧率
    H, W = first_frame.shape[:2]
    fps = getattr(video_loader, "fps", 30)  # 如果获取不到帧率，默认为30

    # 输出视频设置
    writer = None
    if save_video:
        # 确保输出目录存在
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # 尝试使用H.264编码器
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W, H))
        # 如果H.264编码器不可用，尝试MJPG编码器
        if not writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W, H))
        # 确保视频写入器正常打开
        assert writer.isOpened(), "无法创建输出视频文件"

    # 创建显示窗口
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    def visualize_detection(frame, detection_result, frame_idx):
        """在帧上可视化检测结果"""
        vis = frame.copy()

        if detection_result["detected"]:
            # 绘制水印边界框
            x1, y1, x2, y2 = detection_result["bbox"]
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 绘制中心点
            cx, cy = detection_result["center"]
            cv2.circle(vis, (cx, cy), 5, (0, 0, 255), -1)

            # 显示置信度
            conf = detection_result["confidence"]
            label = f"水印: {conf:.2f}"

            # 绘制文本背景
            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                vis, (x1, y1 - text_h - 10), (x1 + text_w + 5, y1), (0, 255, 0), -1
            )

            # 绘制标签文本
            cv2.putText(
                vis,
                label,
                (x1 + 2, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2,
            )

            # 设置状态信息（检测到水印）
            status = f"帧 {frame_idx} | 已检测到 | 置信度: {conf:.3f}"
            status_color = (0, 255, 0)
        else:
            # 设置状态信息（未检测到水印）
            status = f"帧 {frame_idx} | 未检测到水印"
            status_color = (0, 0, 255)

        # 在左上角显示帧信息
        cv2.putText(
            vis, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2
        )

        return vis

    # 处理第一帧
    print("开始处理视频...")
    detection = detector.detect(first_frame)
    vis_frame = visualize_detection(first_frame, detection, 0)
    cv2.imshow(window, vis_frame)
    if writer is not None:
        writer.write(vis_frame)

    # 处理剩余帧
    total_frames = 0  # 总帧数计数器
    detected_frames = 0  # 检测到水印的帧数计数器

    for idx, frame in enumerate(
        tqdm(video_loader, desc="处理帧", initial=1, unit="f"), start=1
    ):
        # 使用YOLO进行水印检测
        detection = detector.detect(frame)

        # 可视化检测结果
        vis_frame = visualize_detection(frame, detection, idx)

        # 更新统计信息
        total_frames += 1
        if detection["detected"]:
            detected_frames += 1

        # 显示处理后的帧
        cv2.imshow(window, vis_frame)

        # 保存到输出视频
        if writer is not None:
            writer.write(vis_frame)

        # 按键控制
        key = cv2.waitKey(max(1, int(1000 / max(1, int(fps))))) & 0xFF
        if key == ord("q"):  # 按q退出
            break
        elif key == ord(" "):  # 按空格键暂停
            while True:
                k = cv2.waitKey(50) & 0xFF
                if k in (ord(" "), ord("q")):  # 空格继续，q退出
                    if k == ord("q"):
                        idx = 10**9  # 设置一个大数，用于退出外层循环
                    break
            if idx >= 10**9:
                break

    # 清理资源
    if writer is not None:
        writer.release()
        print(f"\n[完成] 可视化视频已保存: {out_path}")

    # 打印检测统计信息
    total_frames += 1  # 包括第一帧
    if detection["detected"]:
        detected_frames += 1

    print(f"\n=== 检测统计 ===")
    print(f"总帧数: {total_frames}")
    print(f"检测到水印: {detected_frames} 帧")
    print(f"检测率: {detected_frames/total_frames*100:.2f}%")

    # 关闭所有OpenCV窗口
    cv2.destroyAllWindows()
