from __future__ import annotations

import base64
import json
import marshal
from functools import lru_cache
from io import BytesIO
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf

from app.config import MODEL_CACHE_DIR, settings
from app.disease_info import CLASS_NAMES, get_disease_details


DEFAULT_IMAGE_SIZE = (224, 224)
KERAS3_COMPATIBLE_MODEL_PATH = MODEL_CACHE_DIR / "model_keras3_compatible.h5"
KERAS3_COMPATIBILITY_PATCH_VERSION = "2"


def _channel_reduce_mean(inputs):
    import tensorflow as tensorflow

    return tensorflow.reduce_mean(inputs, axis=-1, keepdims=True)


def _channel_reduce_max(inputs):
    import tensorflow as tensorflow

    return tensorflow.reduce_max(inputs, axis=-1, keepdims=True)


def _encoded_function_code(function) -> str:
    return base64.b64encode(marshal.dumps(function.__code__)).decode("utf-8")


def _patch_legacy_h5_for_keras3(source_path: Path) -> Path:
    import h5py

    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if (
        KERAS3_COMPATIBLE_MODEL_PATH.exists()
        and KERAS3_COMPATIBLE_MODEL_PATH.stat().st_mtime >= source_path.stat().st_mtime
    ):
        with h5py.File(KERAS3_COMPATIBLE_MODEL_PATH, "r") as cached_file:
            if cached_file.attrs.get("compatibility_patch_version") == KERAS3_COMPATIBILITY_PATCH_VERSION:
                return KERAS3_COMPATIBLE_MODEL_PATH

    if Path(source_path).resolve() != KERAS3_COMPATIBLE_MODEL_PATH.resolve():
        shutil.copyfile(source_path, KERAS3_COMPATIBLE_MODEL_PATH)
    mean_code = _encoded_function_code(_channel_reduce_mean)
    max_code = _encoded_function_code(_channel_reduce_max)
    merge_layers = {"Add", "Multiply", "Average", "Maximum", "Minimum", "Concatenate"}

    with h5py.File(KERAS3_COMPATIBLE_MODEL_PATH, "r+") as h5_file:
        model_config = h5_file.attrs.get("model_config")
        if model_config is None:
            return KERAS3_COMPATIBLE_MODEL_PATH

        if isinstance(model_config, bytes):
            model_config = model_config.decode("utf-8")

        config = json.loads(model_config)
        for layer in config.get("config", {}).get("layers", []):
            if layer.get("class_name") == "Lambda":
                function_config = layer["config"]["function"]["config"]
                code = marshal.loads(base64.b64decode(function_config["code"]))
                code_names = set(code.co_names)
                if "reduce_mean" in code_names or "reduce_max" in code_names:
                    input_shape = layer["inbound_nodes"][0]["args"][0]["config"]["shape"]
                    layer["config"]["output_shape"] = input_shape[1:-1] + [1]
                    function_config["code"] = mean_code if "reduce_mean" in code_names else max_code

            if layer.get("class_name") in merge_layers:
                for node in layer.get("inbound_nodes", []):
                    args = node.get("args", [])
                    if len(args) > 1 and not isinstance(args[0], list):
                        node["args"] = [args]

        h5_file.attrs.modify("model_config", json.dumps(config).encode("utf-8"))
        h5_file.attrs["compatibility_patch_version"] = KERAS3_COMPATIBILITY_PATCH_VERSION

    return KERAS3_COMPATIBLE_MODEL_PATH


@lru_cache(maxsize=1)
def load_model() -> tf.keras.Model:
    path = settings.model_path
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at {path}")

    try:
        return tf.keras.models.load_model(path, compile=False, safe_mode=False)
    except TypeError:
        try:
            if hasattr(tf.keras, "config") and hasattr(tf.keras.config, "enable_unsafe_deserialization"):
                tf.keras.config.enable_unsafe_deserialization()
            return tf.keras.models.load_model(path, compile=False)
        except Exception:
            compatible_path = _patch_legacy_h5_for_keras3(path)
            return tf.keras.models.load_model(compatible_path, compile=False, safe_mode=False)
    except Exception:
        compatible_path = _patch_legacy_h5_for_keras3(path)
        return tf.keras.models.load_model(compatible_path, compile=False, safe_mode=False)


def model_is_loaded() -> bool:
    """Report whether the model is already in memory without triggering a load."""
    return load_model.cache_info().currsize > 0


def _get_model_input_size(model: tf.keras.Model) -> tuple[int, int]:
    input_shape = model.input_shape[0] if isinstance(model.input_shape, list) else model.input_shape
    if len(input_shape) == 4 and input_shape[1] and input_shape[2]:
        return int(input_shape[1]), int(input_shape[2])
    return DEFAULT_IMAGE_SIZE


def preprocess_image(image_bytes: bytes, target_size: tuple[int, int]) -> np.ndarray:
    image = Image.open(BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    image = image.resize(target_size, Image.Resampling.LANCZOS)
    array = np.asarray(image, dtype=np.float32) / 255.0
    return np.expand_dims(array, axis=0)


def _to_probabilities(raw_prediction: np.ndarray) -> np.ndarray:
    prediction = np.asarray(raw_prediction).reshape(-1)
    if prediction.size == 1:
        positive = float(prediction[0])
        return np.array([1.0 - positive, positive], dtype=np.float32)

    total = float(np.sum(prediction))
    if np.all(prediction >= 0) and np.isclose(total, 1.0, atol=1e-3):
        return prediction.astype(np.float32)

    exp_values = np.exp(prediction - np.max(prediction))
    return (exp_values / np.sum(exp_values)).astype(np.float32)


def predict(image_bytes: bytes) -> dict[str, object]:
    model = load_model()
    processed = preprocess_image(image_bytes, _get_model_input_size(model))
    raw_prediction = model.predict(processed, verbose=0)
    probabilities = _to_probabilities(raw_prediction)

    if probabilities.size != len(CLASS_NAMES):
        raise ValueError(
            f"Model returned {probabilities.size} outputs, but {len(CLASS_NAMES)} class labels are configured. "
            "Update CLASS_NAMES in backend/app/disease_info.py."
        )

    best_index = int(np.argmax(probabilities))
    class_name = CLASS_NAMES[best_index]
    details = get_disease_details(class_name)
    # Keys are the internal class names so the frontend can translate them.
    probability_map = {
        name: float(probabilities[index])
        for index, name in enumerate(CLASS_NAMES)
    }

    return {
        "predicted_class": class_name,
        "predicted_label": details["label"],
        "confidence": float(probabilities[best_index]),
        "probabilities": probability_map,
        "description": details["description"],
        "symptoms": details["symptoms"],
        "causes": details["causes"],
        "prevention": details["prevention"],
        "treatment": details["treatment"],
        "risk_level": details["risk_level"],
    }
