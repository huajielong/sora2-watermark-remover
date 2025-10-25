from pathlib import Path

import cv2
import numpy as np
import torch
from loguru import logger

from sora2wm.configs import DEFAULT_WATERMARK_REMOVE_MODEL
from sora2wm.iopaint.const import DEFAULT_MODEL_DIR
from sora2wm.iopaint.download import cli_download_model, scan_models
from sora2wm.iopaint.model_manager import ModelManager
from sora2wm.iopaint.schema import InpaintRequest
from sora2wm.utils.devices_utils import get_device

# 代码基于 https://github.com/Sanster/IOPaint#，感谢他们的出色工作！


class WaterMarkRemover:
    """水印清除器类"""
    
    def __init__(self):
        """
        初始化水印清除器
        - 加载默认的水印移除模型
        - 自动下载缺失的模型权重
        - 设置适当的设备（CPU或GPU）
        """
        # 设置要使用的模型
        self.model = DEFAULT_WATERMARK_REMOVE_MODEL
        # 获取可用设备（CPU或GPU）
        self.device = get_device()

        # 扫描已安装的模型
        scanned_models = scan_models()
        # 检查模型是否已安装
        if self.model not in [it.name for it in scanned_models]:
            logger.info(
                f"{self.model} 模型未在 {DEFAULT_MODEL_DIR} 中找到，正在尝试下载"
            )
            # 下载模型
            cli_download_model(self.model)
        
        # 初始化模型管理器
        self.model_manager = ModelManager(name=self.model, device=self.device)
        # 创建修复请求配置
        self.inpaint_request = InpaintRequest()

    def clean(self, input_image: np.array, watermark_mask: np.array) -> np.array:
        """
        清除图像中的水印
        
        参数:
        - input_image: 输入图像（numpy数组格式）
        - watermark_mask: 水印掩码（与输入图像大小相同的numpy数组）
        
        返回:
        - 去除水印后的图像（numpy数组格式）
        """
        # 使用模型管理器进行修复
        inpaint_result = self.model_manager(
            input_image, watermark_mask, self.inpaint_request
        )
        # 转换颜色空间（从BGR到RGB）
        inpaint_result = cv2.cvtColor(inpaint_result, cv2.COLOR_BGR2RGB)
        return inpaint_result


if __name__ == "__main__":
    """水印清除器使用示例"""
    from pathlib import Path

    import cv2
    import numpy as np
    from tqdm import tqdm
    
    # 导入视频加载器
    from sora2wm.utils.video_utils import VideoLoader

    # ========= 配置参数 =========
    video_path = Path("resources/puppies.mp4")
    save_video = True
    out_path = Path("outputs/dog_vs_sam_detected.mp4")
    window = "Sora2 水印检测 (阈值+形态学+形状 + 追踪)"

    # 追踪/回退策略参数
    PREV_ROI_EXPAND = 2.2  # 上一框宽高的膨胀倍数（>1）
    AREA1 = (1000, 2000)  # 主检测面积范围
    AREA2 = (600, 4000)  # 回退阶段面积范围
    # ===========================

    # 初始化水印清除器
    Remover = WaterMarkRemover()
    # 初始化视频加载器
    video_loader = VideoLoader(video_path)

    # 预取一帧确定视频尺寸和帧率
    first_frame = None
    for first_frame in video_loader:
        break
    assert first_frame is not None, "无法读取视频帧"
    
    # 获取视频高度、宽度和帧率
    H, W = first_frame.shape[:2]
    fps = getattr(video_loader, "fps", 30)

    # 输出视频设置（原 | 二值化 | 所有轮廓 | 检测结果 四联画）
    writer = None
    if save_video:
        # 确保输出目录存在
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # 尝试使用H.264编码器
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W * 4, H))
        # 如果H.264编码器不可用，尝试MJPG编码器
        if not writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W * 4, H))
        assert writer.isOpened(), "无法创建输出视频文件"

    # 创建显示窗口
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    # ---- 工具函数 ----
    def _clip_rect(x0, y0, x1, y1, w_img, h_img):
        """裁剪矩形区域，确保在图像范围内"""
        x0 = max(0, min(x0, w_img - 1))
        x1 = max(0, min(x1, w_img))
        y0 = max(0, min(y0, h_img - 1))
        y1 = max(0, min(y1, h_img))
        # 确保矩形有效
        if x1 <= x0:
            x1 = x0 + 1
        if y1 <= y0:
            y1 = y0 + 1
        return x0, y0, x1, y1

    def _cnt_bbox(cnt):
        """计算轮廓的外接矩形框"""
        x, y, w, h = cv2.boundingRect(cnt)
        return (x, y, x + w, y + h)

    def _bbox_center(b):
        """计算矩形框的中心点坐标"""
        x0, y0, x1, y1 = b
        return ((x0 + x1) // 2, (y0 + y1) // 2)

    def detect_flower_like(image, prev_bbox=None):
        """
        检测类似花朵形状的水印
        
        识别流程：
        灰度范围 → 自适应阈值 → 仅在 3 个区域 + (可选)上一帧膨胀ROI 内找轮廓
        三个区域：1) 左上20%  2) 左下20%  3) 中间水平带 y∈[0.4H, 0.6H], x∈[0,W]
        
        参数：
        - image: 输入图像
        - prev_bbox: 上一帧的边界框（可选）
        
        返回：
        - bw_region: 区域内的二值图像
        - best_cnt: 最佳匹配的轮廓
        - contours_region: 区域内所有轮廓
        - region_boxes: 检测区域框
        - prev_roi_box: 上一帧的ROI框
        """
        # 转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 设置亮度范围（208 ± 20%）
        low, high = int(round(208 * 0.9)), int(round(208 * 1.1))
        mask = ((gray >= low) & (gray <= high)).astype(np.uint8) * 255

        # 应用自适应阈值并限制到亮度范围
        bw = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, -5
        )
        bw = cv2.bitwise_and(bw, mask)

        # -------- 定义三个检测区域：左上/左下/中间带 --------
        h_img, w_img = gray.shape[:2]
        r_top_left = (0, 0, int(0.2 * w_img), int(0.2 * h_img))  # 左上20%
        r_bot_left = (0, int(0.8 * h_img), int(0.2 * w_img), h_img)  # 左下20%
        y0, y1 = int(0.40 * h_img), int(0.60 * h_img)  # 中间带
        r_mid_band = (0, y0, w_img, y1)  # 水平中间带

        # 创建区域掩码
        region_mask = np.zeros_like(bw, dtype=np.uint8)
        for x0, ys, x1, ye in (r_top_left, r_bot_left):
            region_mask[ys:ye, x0:x1] = 255
        region_mask[y0:y1, :] = 255

        # -------- 追加：上一帧膨胀ROI --------
        prev_roi_box = None
        if prev_bbox is not None:
            px0, py0, px1, py1 = prev_bbox
            pw, ph = (px1 - px0), (py1 - py0)
            cx, cy = _bbox_center(prev_bbox)
            # 扩大搜索区域
            rw = int(pw * PREV_ROI_EXPAND)
            rh = int(ph * PREV_ROI_EXPAND)
            rx0, ry0 = cx - rw // 2, cy - rh // 2
            rx1, ry1 = cx + rw // 2, cy + rh // 2
            # 裁剪到图像范围内
            rx0, ry0, rx1, ry1 = _clip_rect(rx0, ry0, rx1, ry1, w_img, h_img)
            region_mask[ry0:ry1, rx0:rx1] = 255
            prev_roi_box = (rx0, ry0, rx1, ry1)

        # 提取区域内的二值图像
        bw_region = cv2.bitwise_and(bw, region_mask)

        # -------- 轮廓检测和形状筛选 --------
        def select_candidates(bw_bin, area_rng):
            """选择符合条件的轮廓候选"""
            # 查找所有外部轮廓
            contours, _ = cv2.findContours(
                bw_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cand = []
            for cnt in contours:
                # 筛选面积在指定范围内的轮廓
                area = cv2.contourArea(cnt)
                if area < area_rng[0] or area > area_rng[1]:
                    continue
                # 计算轮廓周长
                peri = cv2.arcLength(cnt, True)
                if peri == 0:
                    continue
                # 计算圆度（筛选花朵形状）
                circularity = 4.0 * np.pi * area / (peri * peri)
                if 0.55 <= circularity <= 0.95:
                    cand.append(cnt)
            return contours, cand

        # 使用主检测区域和面积范围
        contours_region, cand1 = select_candidates(bw_region, AREA1)

        best_cnt = None
        if cand1:
            # 若有上一帧，选择离上一帧中心最近的轮廓；否则选择面积最大的轮廓
            if prev_bbox is None:
                best_cnt = max(cand1, key=lambda c: cv2.contourArea(c))
            else:
                pcx, pcy = _bbox_center(prev_bbox)
                # 选择离上一帧中心最近的轮廓
                best_cnt = max(
                    cand1,
                    key=lambda c: -(
                        (((_cnt_bbox(c)[0] + _cnt_bbox(c)[2]) // 2 - pcx) ** 2)
                        + (((_cnt_bbox(c)[1] + _cnt_bbox(c)[3]) // 2 - pcy) ** 2)
                    ),
                )
        else:
            # 回退策略1：仅在上一帧 ROI 内放宽面积范围
            if prev_roi_box is not None:
                rx0, ry0, rx1, ry1 = prev_roi_box
                roi = np.zeros_like(bw_region)
                roi[ry0:ry1, rx0:rx1] = bw_region[ry0:ry1, rx0:rx1]
                _, cand2 = select_candidates(roi, AREA2)
                if cand2:
                    if prev_bbox is None:
                        best_cnt = max(cand2, key=lambda c: cv2.contourArea(c))
                    else:
                        pcx, pcy = _bbox_center(prev_bbox)
                        best_cnt = max(
                            cand2,
                            key=lambda c: -(
                                (((_cnt_bbox(c)[0] + _cnt_bbox(c)[2]) // 2 - pcx) ** 2)
                                + (
                                    ((_cnt_bbox(c)[1] + _cnt_bbox(c)[3]) // 2 - pcy)
                                    ** 2
                                )
                            ),
                        )
                else:
                    # 回退策略2：全区域搜索，使用放宽的面积范围，选择最近中心
                    if prev_bbox is not None:
                        _, cand3 = select_candidates(bw_region, AREA2)
                        if cand3:
                            pcx, pcy = _bbox_center(prev_bbox)
                            best_cnt = max(
                                cand3,
                                key=lambda c: -(
                                    (
                                        ((_cnt_bbox(c)[0] + _cnt_bbox(c)[2]) // 2 - pcx)
                                        ** 2
                                    )
                                    + (
                                        ((_cnt_bbox(c)[1] + _cnt_bbox(c)[3]) // 2 - pcy)
                                        ** 2
                                    )
                                ),
                            )

        region_boxes = (r_top_left, r_bot_left, r_mid_band, (y0, y1))
        return bw_region, best_cnt, contours_region, region_boxes, prev_roi_box

    # ---- 时序追踪状态（用字典避免 nonlocal/global） ----
    state = {"bbox": None}  # 保存上一帧外接框 (x0,y0,x1,y1)

    def process_and_show(frame, idx):
        """处理单帧并显示结果"""
        img = frame.copy()
        # 进行水印检测
        bw, best, contours, region_boxes, prev_roi_box = detect_flower_like(
            img, state["bbox"]
        )
        r_top_left, r_bot_left, r_mid_band, (y0, y1) = region_boxes

        # 显示所有轮廓（黄色）
        allc = img.copy()
        if contours:
            cv2.drawContours(allc, contours, -1, (0, 255, 255), 1)

        # 画三个检测区域：红框 + 中间带上下红线
        def draw_rect(im, rect, color=(0, 0, 255), th=2):
            """在图像上绘制矩形框"""
            x0, y0r, x1, y1r = rect
            cv2.rectangle(im, (x0, y0r), (x1, y1r), color, th)

        draw_rect(allc, r_top_left)
        draw_rect(allc, r_bot_left)
        draw_rect(allc, (r_mid_band[0], r_mid_band[1], r_mid_band[2], r_mid_band[3]))
        cv2.line(allc, (0, y0), (img.shape[1], y0), (0, 0, 255), 2)
        cv2.line(allc, (0, y1), (img.shape[1], y1), (0, 0, 255), 2)

        # 画上一帧的膨胀 ROI（青色）
        if prev_roi_box is not None:
            x0, y0r, x1, y1r = prev_roi_box
            cv2.rectangle(allc, (x0, y0r), (x1, y1r), (255, 255, 0), 2)

        # 显示最终检测结果
        vis = img.copy()
        title = "未检测到"
        if best is not None:
            # 绘制检测到的轮廓（绿色）
            cv2.drawContours(vis, [best], -1, (0, 255, 0), 2)
            # 更新边界框状态
            x0, y0r, x1, y1r = _cnt_bbox(best)
            state["bbox"] = (x0, y0r, x1, y1r)  # 更新追踪状态
            # 计算并绘制中心点
            M = cv2.moments(best)
            if M["m00"] > 0:
                cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                cv2.circle(vis, (cx, cy), 4, (0, 0, 255), -1)
            title = "已检测到"
        else:
            # 若未检测到，维持上一帧状态
            cv2.putText(
                vis,
                "未检测到水印（保持上一状态）",
                (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )
            if state["bbox"] is not None:
                x0, y0r, x1, y1r = state["bbox"]
                cv2.rectangle(vis, (x0, y0r), (x1, y1r), (255, 255, 0), 2)

        # 生成四联画：原图 | 区域内二值图 | 所有轮廓 | 最终检测
        panel = np.hstack([img, cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR), allc, vis])
        cv2.putText(
            panel,
            f"帧 {idx} | {title}",
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
        )

        # 显示结果
        cv2.imshow(window, panel)
        # 保存到输出视频
        if writer is not None:
            if panel.shape[:2] != (H, W * 4):
                panel = cv2.resize(panel, (W * 4, H), interpolation=cv2.INTER_AREA)
            writer.write(panel)

    # 处理第一帧
    process_and_show(first_frame, 0)

    # 处理剩余帧
    for idx, frame in enumerate(
        tqdm(video_loader, desc="处理帧", initial=1, unit="f")
    ):
        process_and_show(frame, idx)
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

    # 释放资源
    if writer is not None:
        writer.release()
        print(f"[完成] 可视化视频已保存: {out_path}")

    # 关闭所有OpenCV窗口
    cv2.destroyAllWindows()
