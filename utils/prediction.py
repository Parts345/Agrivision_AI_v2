from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import marshal
from pathlib import Path
import shutil
from typing import Dict

import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image

from utils.preprocessing import DEFAULT_IMAGE_SIZE, preprocess_image


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT_DIR / "model"
MODEL_CACHE_DIR = MODEL_DIR / ".cache"
BUNDLED_MODEL_PATH = MODEL_CACHE_DIR / "model_keras3_compatible.h5"
MODEL_PATH = MODEL_DIR / "model.h5"
if not MODEL_PATH.exists() and BUNDLED_MODEL_PATH.exists():
    MODEL_PATH = BUNDLED_MODEL_PATH
KERAS3_COMPATIBLE_MODEL_PATH = MODEL_CACHE_DIR / "model_keras3_compatible.h5"
KERAS3_COMPATIBILITY_PATCH_VERSION = "2"

# Single source of truth: keep class order identical to the backend.
from backend.app.disease_info import CLASS_NAMES  # noqa: E402


@dataclass(frozen=True)
class PredictionResult:
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]


def _channel_reduce_mean(inputs):
    import tensorflow as tensorflow

    return tensorflow.reduce_mean(inputs, axis=-1, keepdims=True)


def _channel_reduce_max(inputs):
    import tensorflow as tensorflow

    return tensorflow.reduce_max(inputs, axis=-1, keepdims=True)


def _encoded_function_code(function) -> str:
    return base64.b64encode(marshal.dumps(function.__code__)).decode("utf-8")


def _patch_legacy_h5_for_keras3(source_path: Path) -> Path:
    """
    Create a Keras 3 compatible copy of a trusted legacy H5 model.

    The provided model stores CBAM spatial attention as Lambda layers and has
    older merge-layer inbound metadata. Modern Keras is stricter when loading
    these artifacts, so we patch only the JSON model config and leave weights
    untouched.
    """
    import h5py

    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if KERAS3_COMPATIBLE_MODEL_PATH.exists() and KERAS3_COMPATIBLE_MODEL_PATH.stat().st_mtime >= source_path.stat().st_mtime:
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


@st.cache_resource(show_spinner=False)
def load_model(model_path: str = str(MODEL_PATH)) -> tf.keras.Model:
    """Load the trusted Keras model once per Streamlit session."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at {path}")

    try:
        return tf.keras.models.load_model(path, compile=False, safe_mode=False)
    except TypeError:
        # Older TensorFlow/Keras versions do not expose safe_mode for H5 files.
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


def _get_model_input_size(model: tf.keras.Model) -> tuple[int, int]:
    """Infer the expected image size from model input shape when available."""
    input_shape = model.input_shape
    if isinstance(input_shape, list):
        input_shape = input_shape[0]

    if len(input_shape) == 4 and input_shape[1] and input_shape[2]:
        return int(input_shape[1]), int(input_shape[2])

    return DEFAULT_IMAGE_SIZE


def _to_probabilities(raw_prediction: np.ndarray) -> np.ndarray:
    """Return a stable probability vector for sigmoid, softmax, or logits outputs."""
    prediction = np.asarray(raw_prediction).reshape(-1)

    if prediction.size == 1:
        positive = float(prediction[0])
        return np.array([1.0 - positive, positive], dtype=np.float32)

    total = float(np.sum(prediction))
    if np.all(prediction >= 0) and np.isclose(total, 1.0, atol=1e-3):
        return prediction.astype(np.float32)

    exp_values = np.exp(prediction - np.max(prediction))
    return (exp_values / np.sum(exp_values)).astype(np.float32)


def predict_disease(image: Image.Image) -> PredictionResult:
    """Run preprocessing and model inference for a rice leaf image."""
    model = load_model()
    target_size = _get_model_input_size(model)
    processed_image = preprocess_image(image, target_size=target_size)

    raw_prediction = model.predict(processed_image, verbose=0)
    probabilities = _to_probabilities(raw_prediction)

    if probabilities.size != len(CLASS_NAMES):
        raise ValueError(
            f"Model returned {probabilities.size} outputs, but {len(CLASS_NAMES)} class names are configured. "
            "Update CLASS_NAMES in utils/prediction.py to match the trained model."
        )

    best_index = int(np.argmax(probabilities))
    probability_map = {
        class_name: float(probabilities[index])
        for index, class_name in enumerate(CLASS_NAMES)
    }

    return PredictionResult(
        predicted_class=CLASS_NAMES[best_index],
        confidence=float(probabilities[best_index]),
        probabilities=probability_map,
    )
