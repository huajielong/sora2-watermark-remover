import torch
from functools import lru_cache
from loguru import logger


@lru_cache()
def get_device():
    """
    获取可用的最佳计算设备
    
    优先级顺序：
    1. CUDA (NVIDIA GPU)
    2. MPS (Apple Silicon)
    3. CPU (默认)
    
    使用lru_cache装饰器缓存结果，避免重复检测设备
    
    返回：
    - torch.device对象，表示选定的计算设备
    """
    # 默认使用CPU
    device = "cpu"
    
    # 检查是否有可用的CUDA设备（NVIDIA GPU）
    if torch.cuda.is_available():
        device = "cuda"
    
    # 检查是否有可用的MPS设备（Apple Silicon）
    # 注意：这里会覆盖前面的CUDA选择，因为MPS检查在CUDA之后
    if torch.backends.mps.is_available():
        device = "mps"
    
    # 记录使用的设备信息
    logger.debug(f"使用设备: {device}")
    
    # 返回对应的torch.device对象
    return torch.device(device)
