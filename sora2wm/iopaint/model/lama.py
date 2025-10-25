import os

import cv2
import numpy as np
import torch
from loguru import logger

from sora2wm.iopaint.helper import (
    download_model,
    get_cache_path_by_url,
    load_jit_model,
    norm_img,
)
from sora2wm.iopaint.schema import InpaintRequest

from .base import InpaintModel
from ...configs import LAMA_CLEAN_WEIGHTS

LAMA_MODEL_URL = os.environ.get(
    "LAMA_MODEL_URL",
    "https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt",
)
LAMA_MODEL_MD5 = os.environ.get("LAMA_MODEL_MD5", "e3aa4aaa15225a33ec84f9f4bc47e500")

ANIME_LAMA_MODEL_URL = os.environ.get(
    "ANIME_LAMA_MODEL_URL",
    "https://github.com/Sanster/models/releases/download/AnimeMangaInpainting/anime-manga-big-lama.pt",
)
ANIME_LAMA_MODEL_MD5 = os.environ.get(
    "ANIME_LAMA_MODEL_MD5", "29f284f36a0a510bcacf39ecf4c4d54f"
)


class LaMa(InpaintModel):
    name = "lama"
    pad_mod = 8
    is_erase_model = True

    @staticmethod
    def download():
        download_model(LAMA_MODEL_URL, LAMA_MODEL_MD5)

    def init_model(self, device, **kwargs):
        # 优先检查本地LAMA_CLEAN_WEIGHTS路径
        if os.path.exists(LAMA_CLEAN_WEIGHTS):
            logger.info(f"使用本地模型: {LAMA_CLEAN_WEIGHTS}")
            self.model = load_jit_model(LAMA_CLEAN_WEIGHTS, device, LAMA_MODEL_MD5).eval()
        else:
            # 如果本地文件不存在，从URL下载并加载
            self.model = load_jit_model(LAMA_MODEL_URL, device, LAMA_MODEL_MD5).eval()

    @staticmethod
    def is_downloaded() -> bool:
        return os.path.exists(get_cache_path_by_url(LAMA_MODEL_URL))

    def forward(self, image, mask, config: InpaintRequest):
        """Input image and output image have same size
        image: [H, W, C] RGB
        mask: [H, W]
        return: BGR IMAGE
        """
        image = norm_img(image)
        mask = norm_img(mask)

        mask = (mask > 0) * 1
        image = torch.from_numpy(image).unsqueeze(0).to(self.device)
        mask = torch.from_numpy(mask).unsqueeze(0).to(self.device)

        inpainted_image = self.model(image, mask)

        cur_res = inpainted_image[0].permute(1, 2, 0).detach().cpu().numpy()
        cur_res = np.clip(cur_res * 255, 0, 255).astype("uint8")
        cur_res = cv2.cvtColor(cur_res, cv2.COLOR_RGB2BGR)
        return cur_res


class AnimeLaMa(LaMa):
    name = "anime-lama"

    @staticmethod
    def download():
        download_model(ANIME_LAMA_MODEL_URL, ANIME_LAMA_MODEL_MD5)

    def init_model(self, device, **kwargs):
        # 优先使用本地模型，保持与LaMa类一致的加载方式
        if os.path.exists(LAMA_CLEAN_WEIGHTS):
            logger.info(f"使用本地模型: {LAMA_CLEAN_WEIGHTS}")
            self.model = load_jit_model(LAMA_CLEAN_WEIGHTS, device, ANIME_LAMA_MODEL_MD5).eval()
        else:
            self.model = load_jit_model(ANIME_LAMA_MODEL_URL, device, ANIME_LAMA_MODEL_MD5).eval()

    @staticmethod
    def is_downloaded() -> bool:
        return os.path.exists(get_cache_path_by_url(ANIME_LAMA_MODEL_URL))
