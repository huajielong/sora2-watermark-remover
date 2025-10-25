"""
水印检测工具函数模块

提供基于模板匹配的水印检测功能，用于识别图像中的水印位置
并生成水印掩码
"""

import cv2
import numpy as np

from sora2wm.configs import WATER_MARK_TEMPLATE_IMAGE_PATH

# 加载水印模板图像
tmpl = cv2.imread(WATER_MARK_TEMPLATE_IMAGE_PATH)
# 将模板转为灰度图以提高匹配效率
tmpl_gray = cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY)
# 获取模板图像的高度和宽度
h_tmpl, w_tmpl = tmpl_gray.shape


def detect_watermark(
    img: np.array,
    region_fraction: float = 0.25,
    threshold: float = 0.5,
    debug=False,  # 添加调试参数
):
    """
    使用模板匹配方法检测图像中的水印
    
    参数:
    - img: 输入图像的numpy数组
    - region_fraction: 搜索区域比例（当前未使用，保留兼容性）
    - threshold: 匹配阈值，高于此值的位置被认为是水印
    - debug: 是否显示调试信息
    
    返回:
    - mask_full: 水印掩码，255表示水印区域，0表示非水印区域
    - detections: 检测到的水印位置列表，每个元素为(x, y, width, height)
    """
    # 将输入图像转为灰度图
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h_img, w_img = img_gray.shape

    # 临时：先搜索全图，确认能检测到水印
    search_region = img_gray
    # 使用归一化相关系数进行模板匹配
    res = cv2.matchTemplate(search_region, tmpl_gray, cv2.TM_CCOEFF_NORMED)

    # 显示调试信息（如果debug=True）
    if debug:
        print(f"匹配结果范围: {res.min():.3f} ~ {res.max():.3f}")
        max_val = res.max()
        max_loc = np.unravel_index(res.argmax(), res.shape)
        print(f"最佳匹配位置: {max_loc}, 置信度: {max_val:.3f}")

    # 找出所有匹配值大于阈值的位置
    locs = np.where(res >= threshold)

    # 创建水印掩码（初始全为0）
    mask_full = np.zeros((h_img, w_img), dtype=np.uint8)
    # 存储检测结果的列表
    detections = []

    # 遍历所有检测到的水印位置
    for x, y in zip(*locs[::-1]):
        # 添加检测到的水印位置和尺寸
        detections.append((x, y, w_tmpl, h_tmpl))
        # 在掩码上标记水印区域为255
        mask_full[y : y + h_tmpl, x : x + w_tmpl] = 255

    # 创建膨胀核，用于扩大水印区域，确保完全覆盖
    kernel = np.ones((3, 3), np.uint8)
    # 对掩码进行膨胀操作，扩大水印区域
    mask_full = cv2.dilate(mask_full, kernel, iterations=1)

    return mask_full, detections


def get_bounding_box(detections, w_tmpl, h_tmpl):
    """
    计算所有检测到的水印位置的总边界框
    
    参数:
    - detections: 检测到的水印位置列表，可以是(x, y)或(x, y, w, h)格式
    - w_tmpl: 模板宽度（当detections为(x, y)格式时使用）
    - h_tmpl: 模板高度（当detections为(x, y)格式时使用）
    
    返回:
    - tuple: 总边界框 (min_x, min_y, max_x, max_y)
    """
    # 如果没有检测到任何水印，返回空边界框
    if not detections:
        return (0, 0, 0, 0)

    # 处理(x, y, w, h)格式的检测结果
    if len(detections[0]) == 4:
        min_x = min(x for x, y, w, h in detections)
        min_y = min(y for x, y, w, h in detections)
        max_x = max(x + w for x, y, w, h in detections)
        max_y = max(y + h for x, y, w, h in detections)
    # 兼容旧格式: (x, y)格式的检测结果
    else:
        min_x = min(x for x, y in detections)
        min_y = min(y for x, y in detections)
        # 添加模板宽度和高度来计算最大坐标
        max_x = max(x for x, y in detections) + w_tmpl
        max_y = max(y for x, y in detections) + h_tmpl

    # 返回总边界框的坐标
    return (min_x, min_y, max_x, max_y)
