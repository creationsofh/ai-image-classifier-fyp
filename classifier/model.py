import numpy as np

from tensorflow.keras.applications import ( #type: ignore
    EfficientNetB0,
    MobileNetV2,
    ResNet50,
    efficientnet,
    mobilenet_v2,
    resnet
)

from tensorflow.keras.preprocessing import image #type: ignore


# =========================
# LOAD MODELS
# =========================

efficientnet_model = EfficientNetB0(weights="imagenet")

mobilenet_model = MobileNetV2(weights="imagenet")

resnet_model = ResNet50(weights="imagenet")


# =========================
# MODEL REGISTRY
# =========================

MODEL_REGISTRY = {

    "efficientnet": {
        "model": efficientnet_model,
        "preprocess": efficientnet.preprocess_input,
        "decode": efficientnet.decode_predictions
    },

    "mobilenet": {
        "model": mobilenet_model,
        "preprocess": mobilenet_v2.preprocess_input,
        "decode": mobilenet_v2.decode_predictions
    },

    "resnet": {
        "model": resnet_model,
        "preprocess": resnet.preprocess_input,
        "decode": resnet.decode_predictions
    }

}


# =========================
# PREDICTION FUNCTION
# =========================

def predict_image(img_path, model_name="efficientnet"):

    model_data = MODEL_REGISTRY[model_name]

    model = model_data["model"]

    preprocess = model_data["preprocess"]

    decode = model_data["decode"]

    # load image
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

    # predict
    preds = model.predict(img_array)

    decoded = decode(preds, top=3)[0]

    predictions = []

    for pred in decoded:

        predictions.append({

            "label": pred[1],

            "confidence": round(
                float(pred[2]) * 100,
                2
            )

        })

    return {

        "label": predictions[0]["label"],

        "confidence": predictions[0]["confidence"],

        "top_predictions": predictions,

        "model_used": model_name

    }