import cv2
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers, models


class RetinalImageQualityAssessment:
    """
    Automated image quality checker
    Ensures images are gradable before AI analysis
    """

    def __init__(self) -> None:
        self.model = self._build_quality_model()

    def _build_quality_model(self) -> models.Sequential:
        model = models.Sequential(
            [
                layers.Conv2D(32, (3, 3), activation="relu", input_shape=(256, 256, 3)),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(64, (3, 3), activation="relu"),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(128, (3, 3), activation="relu"),
                layers.GlobalAveragePooling2D(),
                layers.Dense(128, activation="relu"),
                layers.Dropout(0.3),
                layers.Dense(3, activation="softmax"),  # Good, Usable, Reject
            ]
        )

        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        return model

    def assess_quality(self, image: np.ndarray) -> dict:
        """
        Assess image quality with multiple checks.
        Returns a dict with quality, feedback and metrics.
        """
        img_resized = cv2.resize(image, (256, 256))
        img_normalized = img_resized / 255.0

        prediction = self.model.predict(np.expand_dims(img_normalized, axis=0))
        quality_class = int(np.argmax(prediction[0]))
        confidence = float(np.max(prediction[0]))

        quality_grades = ["Good", "Usable", "Reject"]
        quality_grade = quality_grades[quality_class]

        blur_score = self._check_blur(image)
        brightness_score = self._check_brightness(image)
        contrast_score = self._check_contrast(image)
        coverage_score = self._check_retinal_coverage(image)

        feedback = []
        should_retake = False

        if blur_score < 50:
            feedback.append("Image is blurry. Hold camera steady and refocus.")
            should_retake = True

        if brightness_score < 30 or brightness_score > 200:
            feedback.append("Lighting is poor. Adjust room lighting.")
            should_retake = True

        if contrast_score < 20:
            feedback.append("Low contrast detected. Ensure proper illumination.")
            should_retake = True

        if coverage_score < 0.6:
            feedback.append("Insufficient retinal area captured. Reposition camera.")
            should_retake = True

        if quality_class == 2:
            should_retake = True
            feedback.append("Image quality insufficient for analysis.")

        return {
            "quality_grade": quality_grade,
            "confidence": confidence,
            "should_retake": should_retake,
            "feedback": feedback,
            "metrics": {
                "blur": float(blur_score),
                "brightness": float(brightness_score),
                "contrast": float(contrast_score),
                "coverage": float(coverage_score),
            },
        }

    def _check_blur(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    def _check_brightness(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return float(np.mean(gray))

    def _check_contrast(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return float(np.std(gray))

    def _check_retinal_coverage(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
        white_pixels = float(np.sum(binary == 255))
        total_pixels = float(binary.size)
        return white_pixels / total_pixels


quality_checker = RetinalImageQualityAssessment()


