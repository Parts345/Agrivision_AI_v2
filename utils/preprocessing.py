from __future__ import annotations

from typing import Tuple

import numpy as np
from PIL import Image, ImageOps


DEFAULT_IMAGE_SIZE: Tuple[int, int] = (224, 224)


def preprocess_image(
    image: Image.Image,
    target_size: Tuple[int, int] = DEFAULT_IMAGE_SIZE,
    normalize: bool = True,
) -> np.ndarray:
    """
    Convert an uploaded PIL image into a model-ready 4D tensor.

    Most Keras image classifiers trained with RGB rice leaf images expect:
    - RGB color channels
    - fixed spatial size such as 224x224
    - batch dimension
    - float values scaled to [0, 1]
    """
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    image = image.resize(target_size, Image.Resampling.LANCZOS)

    array = np.asarray(image, dtype=np.float32)
    if normalize:
        array = array / 255.0

    return np.expand_dims(array, axis=0)
