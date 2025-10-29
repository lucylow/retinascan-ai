import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import ResNet50, EfficientNetB4


class RetinaScanAI:
    """
    Multi-disease retinal screening AI model
    Supports DR, Glaucoma, AMD detection with risk predictions
    """

    def __init__(self, model_type: str = "efficientnet", num_classes: int = 5):
        self.model_type = model_type
        self.num_classes = num_classes
        self.model = self._build_model()

    def _build_model(self) -> models.Model:
        """Build multi-task CNN for retinal disease detection."""

        if self.model_type == "efficientnet":
            base_model = EfficientNetB4(
                include_top=False,
                weights="imagenet",
                input_shape=(512, 512, 3),
            )
        else:
            base_model = ResNet50(
                include_top=False,
                weights="imagenet",
                input_shape=(512, 512, 3),
            )

        for layer in base_model.layers[:100]:
            layer.trainable = False

        inputs = keras.Input(shape=(512, 512, 3))
        x = base_model(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(512, activation="relu")(x)
        x = layers.Dropout(0.2)(x)

        dr_output = layers.Dense(self.num_classes, activation="softmax", name="dr_classification")(x)
        glaucoma_output = layers.Dense(2, activation="softmax", name="glaucoma")(x)
        amd_output = layers.Dense(2, activation="softmax", name="amd")(x)
        cvd_risk = layers.Dense(3, activation="softmax", name="cvd_risk")(x)
        kidney_risk = layers.Dense(3, activation="softmax", name="kidney_risk")(x)

        model = models.Model(
            inputs=inputs,
            outputs={
                "dr_classification": dr_output,
                "glaucoma": glaucoma_output,
                "amd": amd_output,
                "cvd_risk": cvd_risk,
                "kidney_risk": kidney_risk,
            },
        )

        return model

    def compile_model(self) -> None:
        """Compile with multi-task loss."""
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-4),
            loss={
                "dr_classification": "categorical_crossentropy",
                "glaucoma": "categorical_crossentropy",
                "amd": "categorical_crossentropy",
                "cvd_risk": "categorical_crossentropy",
                "kidney_risk": "categorical_crossentropy",
            },
            loss_weights={
                "dr_classification": 1.0,
                "glaucoma": 0.5,
                "amd": 0.5,
                "cvd_risk": 0.3,
                "kidney_risk": 0.3,
            },
            metrics=["accuracy"],
        )

    def predict_with_confidence(self, image: np.ndarray) -> dict:
        """Predict with confidence scores and referral flag from a single RGB image array."""
        predictions = self.model.predict(np.expand_dims(image, axis=0))

        result = {
            "dr_grade": self._get_dr_grade(predictions["dr_classification"][0]),
            "dr_confidence": float(np.max(predictions["dr_classification"][0])),
            "glaucoma_risk": "Positive" if predictions["glaucoma"][0][1] > 0.5 else "Negative",
            "glaucoma_confidence": float(np.max(predictions["glaucoma"][0])),
            "amd_risk": "Positive" if predictions["amd"][0][1] > 0.5 else "Negative",
            "cvd_risk": self._get_risk_level(predictions["cvd_risk"][0]),
            "kidney_risk": self._get_risk_level(predictions["kidney_risk"][0]),
            "requires_referral": self._check_referral_needed(predictions),
        }

        return result

    def _get_dr_grade(self, prediction: np.ndarray) -> str:
        grades = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
        return grades[int(np.argmax(prediction))]

    def _get_risk_level(self, prediction: np.ndarray) -> str:
        levels = ["Low", "Moderate", "High"]
        return levels[int(np.argmax(prediction))]

    def _check_referral_needed(self, predictions: dict) -> bool:
        dr_class = int(np.argmax(predictions["dr_classification"][0]))
        glaucoma_prob = float(predictions["glaucoma"][0][1])
        return dr_class >= 3 or glaucoma_prob > 0.7


# Eagerly create a compiled model for consumers that import this module
retina_ai = RetinaScanAI(model_type="efficientnet", num_classes=5)
retina_ai.compile_model()


