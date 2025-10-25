from pathlib import Path

import numpy as np
from ultralytics import YOLO

from sora2wm.configs import WATER_MARK_DETECT_YOLO_WEIGHTS
from sora2wm.utils.video_utils import VideoLoader

# based on the Sora2 tempalte to detect the whole, and then got the icon part area.

model = YOLO(WATER_MARK_DETECT_YOLO_WEIGHTS)
model.eval()

results = model("resources/first_frame.png")  # Predict on an image

print(results)
