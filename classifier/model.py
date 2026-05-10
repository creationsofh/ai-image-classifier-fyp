import os
import numpy as np

# =========================
# PRODUCTION SAFETY (IMPORTANT FOR RENDER)
# =========================

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from tensorflow.keras.applications import (  # type: ignore
    EfficientNetB0,
    MobileNetV2,
    ResNet50,
    efficientnet,
    mobilenet_v2,
    resnet
)

from tensorflow.keras.preprocessing import image  # type: ignore


# =========================
# MODEL CACHE (LAZY LOADING)
# =========================

MODEL_CACHE = {}


# =========================
# MODEL CONFIG
# =========================

MODEL_CONFIG = {

    "efficientnet": {
        "loader": EfficientNetB0,
        "preprocess": efficientnet.preprocess_input,
        "decode": efficientnet.decode_predictions
    },

    "mobilenet": {
        "loader": MobileNetV2,
        "preprocess": mobilenet_v2.preprocess_input,
        "decode": mobilenet_v2.decode_predictions
    },

    "resnet": {
        "loader": ResNet50,
        "preprocess": resnet.preprocess_input,
        "decode": resnet.decode_predictions
    }

}


# =========================
# GET MODEL (LAZY LOAD)
# =========================

def get_model(model_name):

    if model_name not in MODEL_CACHE:

        MODEL_CACHE[model_name] = MODEL_CONFIG[model_name]["loader"](
            weights="imagenet"
        )

    return MODEL_CACHE[model_name]


# =========================
# PREDICTION FUNCTION
# =========================

def predict_image(img_path, model_name="efficientnet"):

    model_data = MODEL_CONFIG[model_name]

    model = get_model(model_name)

    preprocess = model_data["preprocess"]

    decode = model_data["decode"]

    # =========================
    # LOAD IMAGE
    # =========================

    img = image.load_img(
        img_path,
        target_size=(224, 224)
    )

    img_array = image.img_to_array(img)

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    img_array = preprocess(img_array)

    # =========================
    # PREDICTION
    # =========================

    preds = model.predict(img_array)

    decoded = decode(preds, top=3)[0]

    predictions = []

    for pred in decoded:

        predictions.append({

            "label": pred[1],

            "confidence": round(float(pred[2]) * 100, 2)

        })

    return {

        "label": predictions[0]["label"],

        "confidence": predictions[0]["confidence"],

        "top_predictions": predictions,

        "model_used": model_name

    }