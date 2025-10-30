"""
Generative AI utilities for RetinaScan AI.

This module provides:
- RetinaGAN: GAN-based synthetic retinal image generation with severity controls
- AdvancedDataAugmenter: Generative augmentation focused on rare cases
- GenerativeExplainer: Visual progressions and educational content helpers
- GenerativeAnomalyDetector: Autoencoder-based anomaly detection/localization

Note: Heavy models are built lazily; TensorFlow 2.x and OpenCV are required.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import layers


class RetinaGAN:
    """Generative Adversarial Network for synthetic retinal image generation."""

    def __init__(self, img_shape: Tuple[int, int, int] = (224, 224, 3), latent_dim: int = 100):
        self.img_shape = img_shape
        self.latent_dim = latent_dim
        self.generator = self._build_generator()
        self.discriminator = self._build_discriminator()
        self.gan = self._build_gan()

    def _build_generator(self) -> tf.keras.Model:
        """Build generator network for retinal image synthesis."""

        model = tf.keras.Sequential(
            [
                layers.Dense(8 * 8 * 256, use_bias=False, input_shape=(self.latent_dim,)),
                layers.BatchNormalization(),
                layers.LeakyReLU(),
                layers.Reshape((8, 8, 256)),
                layers.Conv2DTranspose(128, (5, 5), strides=(2, 2), padding="same", use_bias=False),
                layers.BatchNormalization(),
                layers.LeakyReLU(),
                layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding="same", use_bias=False),
                layers.BatchNormalization(),
                layers.LeakyReLU(),
                layers.Conv2DTranspose(32, (5, 5), strides=(2, 2), padding="same", use_bias=False),
                layers.BatchNormalization(),
                layers.LeakyReLU(),
                layers.Conv2DTranspose(3, (5, 5), strides=(2, 2), padding="same", use_bias=False, activation="tanh"),
                layers.Cropping2D(((2, 2), (2, 2))),
            ]
        )
        return model

    def _build_discriminator(self) -> tf.keras.Model:
        """Build discriminator network."""

        model = tf.keras.Sequential(
            [
                layers.Conv2D(32, (5, 5), strides=(2, 2), padding="same", input_shape=self.img_shape),
                layers.LeakyReLU(),
                layers.Dropout(0.3),
                layers.Conv2D(64, (5, 5), strides=(2, 2), padding="same"),
                layers.LeakyReLU(),
                layers.Dropout(0.3),
                layers.Conv2D(128, (5, 5), strides=(2, 2), padding="same"),
                layers.LeakyReLU(),
                layers.Dropout(0.3),
                layers.Conv2D(256, (5, 5), strides=(2, 2), padding="same"),
                layers.LeakyReLU(),
                layers.Dropout(0.3),
                layers.Flatten(),
                layers.Dense(1, activation="sigmoid"),
            ]
        )
        return model

    def _build_gan(self) -> tf.keras.Model:
        """Build combined GAN model (generator + discriminator)."""

        self.discriminator.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        self.discriminator.trainable = False

        gan_input = layers.Input(shape=(self.latent_dim,))
        generated_img = self.generator(gan_input)
        gan_output = self.discriminator(generated_img)

        gan = tf.keras.Model(gan_input, gan_output)
        gan.compile(optimizer="adam", loss="binary_crossentropy")
        return gan

    def generate_synthetic_retina_images(self, num_images: int, severity_level: int) -> np.ndarray:
        """Generate synthetic retinal images with specific severity levels."""

        latent_vectors = self._control_latent_space(num_images, severity_level)
        generated_images = self.generator.predict(latent_vectors, verbose=0)
        processed_images = self._post_process_images(generated_images, severity_level)
        return processed_images

    def _control_latent_space(self, num_images: int, severity: int) -> np.ndarray:
        """Control latent space to generate specific severity patterns (heuristic)."""

        noise = np.random.normal(0, 1, (num_images, self.latent_dim))

        if severity == 1:
            noise[:, 10:20] += 0.5 * np.random.normal(0, 1, (num_images, 10))
        elif severity == 2:
            noise[:, 20:30] += 0.7 * np.random.normal(0, 1, (num_images, 10))
            noise[:, 30:40] += 0.3 * np.random.normal(0, 1, (num_images, 10))
        elif severity >= 3:
            noise[:, 40:60] += 1.0 * np.random.normal(0, 1, (num_images, 20))
            noise[:, 60:70] += 0.5 * np.random.normal(0, 1, (num_images, 10))

        return noise

    def _post_process_images(self, images: np.ndarray, severity: int) -> np.ndarray:
        """Post-process generated images to enhance realism."""

        processed: List[np.ndarray] = []
        for img in images:
            img = (img * 127.5 + 127.5).astype(np.uint8)
            img = self._add_retinal_artifacts(img, severity)
            img = self._adjust_retinal_colors(img)
            processed.append(img)
        return np.array(processed)

    def _add_retinal_artifacts(self, image: np.ndarray, severity: int) -> np.ndarray:
        """Add simplified retinal artifacts based on severity."""

        image = self._add_blood_vessels(image)
        if severity >= 1:
            image = self._add_microaneurysms(image, count=5 + severity * 3)
        if severity >= 2:
            image = self._add_hemorrhages(image, count=2 + severity)
        if severity >= 3:
            image = self._add_cotton_wool_spots(image, count=1 + severity)
            image = self._add_hard_exudates(image, count=3 + severity * 2)
        if severity == 4:
            image = self._add_neovascularization(image)
        return image

    def _add_blood_vessels(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        for _ in range(15):
            color = np.random.randint(30, 60)
            thickness = np.random.randint(1, 3)
            x1, y1 = np.random.randint(0, w), np.random.randint(0, h)
            x2, y2 = x1 + np.random.randint(-50, 50), y1 + np.random.randint(-50, 50)
            cv2.line(image, (x1, y1), (x2, y2), (color, color // 2, color // 3), thickness)
        return image

    def _add_microaneurysms(self, image: np.ndarray, count: int) -> np.ndarray:
        h, w = image.shape[:2]
        for _ in range(count):
            x, y = np.random.randint(50, w - 50), np.random.randint(50, h - 50)
            color = (
                np.random.randint(150, 200),
                np.random.randint(30, 60),
                np.random.randint(30, 60),
            )
            radius = np.random.randint(1, 3)
            cv2.circle(image, (x, y), radius, color, -1)
        return image

    def _add_hemorrhages(self, image: np.ndarray, count: int) -> np.ndarray:
        h, w = image.shape[:2]
        for _ in range(count):
            x, y = np.random.randint(50, w - 50), np.random.randint(50, h - 50)
            size = np.random.randint(3, 8)
            color = (
                np.random.randint(80, 120),
                np.random.randint(20, 40),
                np.random.randint(20, 40),
            )
            points: List[Tuple[int, int]] = []
            for i in range(8):
                angle = 2 * np.pi * i / 8
                r = size + np.random.randint(-1, 2)
                px = int(x + r * np.cos(angle))
                py = int(y + r * np.sin(angle))
                points.append((px, py))
            cv2.fillPoly(image, [np.array(points)], color)
        return image

    def _add_cotton_wool_spots(self, image: np.ndarray, count: int) -> np.ndarray:
        h, w = image.shape[:2]
        for _ in range(count):
            x, y = np.random.randint(50, w - 50), np.random.randint(50, h - 50)
            radius = np.random.randint(5, 12)
            cv2.circle(image, (x, y), radius, (240, 240, 240), -1)
            image = cv2.GaussianBlur(image, (3, 3), 0)
        return image

    def _add_hard_exudates(self, image: np.ndarray, count: int) -> np.ndarray:
        h, w = image.shape[:2]
        for _ in range(count):
            x, y = np.random.randint(50, w - 50), np.random.randint(50, h - 50)
            radius = np.random.randint(2, 5)
            cv2.circle(image, (x, y), radius, (255, 240, 180), -1)
        return image

    def _add_neovascularization(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        for _ in range(30):
            x1, y1 = np.random.randint(0, w), np.random.randint(0, h)
            x2, y2 = x1 + np.random.randint(-30, 30), y1 + np.random.randint(-30, 30)
            cv2.line(image, (x1, y1), (x2, y2), (120, 40, 40), 1)
        return image

    def _adjust_retinal_colors(self, image: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hsv[:, :, 0] = (hsv[:, :, 0] + np.random.randint(-5, 5)) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 0.8, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * np.random.uniform(0.9, 1.1), 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


class SyntheticDataGenerator:
    """Comprehensive synthetic data generation system."""

    def __init__(self) -> None:
        self.gan = RetinaGAN()
        self.diffusion_model = None

    def generate_training_dataset(self, target_size_per_class: int, original_distribution: Dict[int, int]) -> Dict[int, np.ndarray]:
        """Generate balanced synthetic dataset for each severity (0-4)."""

        synthetic_data: Dict[int, np.ndarray] = {}
        for severity in range(5):
            current_count = original_distribution.get(severity, 0)
            needed = max(0, target_size_per_class - current_count)
            if needed > 0:
                synthetic_images = self.gan.generate_synthetic_retina_images(needed, severity)
                synthetic_data[severity] = synthetic_images
        return synthetic_data

    def validate_synthetic_data(self, synthetic_images: np.ndarray, real_images: np.ndarray) -> Dict[str, float]:
        """Validate quality and similarity of synthetic data vs real."""

        metrics: Dict[str, float] = {}
        metrics["synthetic_diversity"] = self._calculate_diversity(synthetic_images)
        metrics["real_diversity"] = self._calculate_diversity(real_images)

        realism_scores: List[float] = []
        for img in synthetic_images:
            img_processed = (img.astype(np.float32) - 127.5) / 127.5
            img_processed = np.expand_dims(img_processed, 0)
            score = float(self.gan.discriminator.predict(img_processed, verbose=0)[0][0])
            realism_scores.append(score)
        metrics["average_realism_score"] = float(np.mean(realism_scores)) if realism_scores else 0.0
        metrics["realism_std"] = float(np.std(realism_scores)) if realism_scores else 0.0

        metrics["feature_similarity"] = self._compare_feature_distributions(synthetic_images, real_images)
        return metrics

    def _calculate_diversity(self, images: np.ndarray) -> float:
        if len(images) < 2:
            return 0.0
        flattened = images.reshape(len(images), -1)
        pairwise_distances: List[float] = []
        for i in range(len(flattened)):
            for j in range(i + 1, len(flattened)):
                dist = float(np.linalg.norm(flattened[i] - flattened[j]))
                pairwise_distances.append(dist)
        return float(np.mean(pairwise_distances)) if pairwise_distances else 0.0

    def _compare_feature_distributions(self, synthetic: np.ndarray, real: np.ndarray) -> float:
        feature_extractor = tf.keras.applications.EfficientNetB0(include_top=False, weights="imagenet", pooling="avg")
        synth_features = feature_extractor.predict(synthetic, verbose=0)
        real_features = feature_extractor.predict(real, verbose=0)
        synth_mean = np.mean(synth_features, axis=0)
        real_mean = np.mean(real_features, axis=0)
        similarity = np.dot(synth_mean, real_mean) / (np.linalg.norm(synth_mean) * np.linalg.norm(real_mean) + 1e-12)
        return float(similarity)


class AdvancedDataAugmenter:
    """Advanced data augmentation using generative AI."""

    def __init__(self) -> None:
        self.gan = RetinaGAN()

    def augment_rare_cases(self, rare_images: np.ndarray, labels: np.ndarray, target_count: int) -> Tuple[np.ndarray, np.ndarray]:
        augmented_images: List[np.ndarray] = []
        augmented_labels: List[int] = []
        per_image = max(1, target_count // max(1, len(rare_images)))
        for img, label in zip(rare_images, labels):
            variations = self._generate_variations(img, int(label), per_image)
            augmented_images.extend(variations)
            augmented_labels.extend([int(label)] * len(variations))
        return np.array(augmented_images), np.array(augmented_labels)

    def _generate_variations(self, base_image: np.ndarray, label: int, num_variations: int) -> List[np.ndarray]:
        variations: List[np.ndarray] = []
        for _ in range(num_variations):
            variation = self._gan_interpolation(base_image, label)
            style_variation = self._apply_style_variation(base_image)
            traditional_aug = self._traditional_then_generative(base_image)
            variations.extend([variation, style_variation, traditional_aug])
        return variations[:num_variations]

    def _gan_interpolation(self, base_image: np.ndarray, label: int) -> np.ndarray:
        base_latent = np.random.normal(0, 1, (1, self.gan.latent_dim))
        interpolation = base_latent + 0.3 * np.random.normal(0, 1, base_latent.shape)
        new_image = self.gan.generator.predict(interpolation, verbose=0)[0]
        new_image = (new_image * 127.5 + 127.5).astype(np.uint8)
        return new_image

    def _apply_style_variation(self, image: np.ndarray) -> np.ndarray:
        variation = image.copy().astype(np.float32)
        variation[:, :, 0] *= np.random.uniform(0.9, 1.1)
        variation[:, :, 1] *= np.random.uniform(0.9, 1.1)
        variation[:, :, 2] *= np.random.uniform(0.9, 1.1)
        variation = np.clip(variation, 0, 255).astype(np.uint8)
        return variation

    def _traditional_then_generative(self, image: np.ndarray) -> np.ndarray:
        augmented = self._traditional_augmentation(image)
        augmented = self._add_generative_artifacts(augmented)
        return augmented

    def _traditional_augmentation(self, image: np.ndarray) -> np.ndarray:
        angle = np.random.uniform(-15, 15)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h))
        alpha = np.random.uniform(0.8, 1.2)
        beta = np.random.uniform(-10, 10)
        adjusted = cv2.convertScaleAbs(rotated, alpha=alpha, beta=beta)
        if np.random.random() > 0.5:
            adjusted = cv2.flip(adjusted, 1)
        return adjusted

    def _add_generative_artifacts(self, image: np.ndarray) -> np.ndarray:
        artifact_type = np.random.choice(["noise", "blur", "vignette"])  # type: ignore[arg-type]
        if artifact_type == "noise":
            noise = np.random.normal(0, 3, image.shape).astype(np.float32)
            noisy_image = image.astype(np.float32) + noise
            image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        elif artifact_type == "blur":
            kernel_size = int(np.random.choice([3, 5]))  # type: ignore[arg-type]
            image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif artifact_type == "vignette":
            rows, cols = image.shape[:2]
            kernel_x = cv2.getGaussianKernel(cols, cols / 3)
            kernel_y = cv2.getGaussianKernel(rows, rows / 3)
            kernel = kernel_y * kernel_x.T
            mask = 255 * kernel / (np.linalg.norm(kernel) + 1e-12)
            mask = mask.astype(np.uint8)
            mask = cv2.merge([mask, mask, mask])
            image = cv2.addWeighted(image, 0.8, mask, 0.2, 0)
        return image


class GenerativeExplainer:
    """Use generative AI for enhanced explanations and education."""

    def __init__(self) -> None:
        self.gan = RetinaGAN()

    def generate_disease_progression(self, base_image: np.ndarray, current_severity: int, target_severity: int) -> List[np.ndarray]:
        progression_images: List[np.ndarray] = []
        steps = abs(target_severity - current_severity)
        if steps == 0:
            return [base_image]
        for step in range(1, steps + 1):
            severity = current_severity + step if target_severity > current_severity else current_severity - step
            progressed_image = self._morph_to_severity(base_image, severity)
            progression_images.append(progressed_image)
        return progression_images

    def _morph_to_severity(self, base_image: np.ndarray, target_severity: int) -> np.ndarray:
        morphed = base_image.copy()
        if target_severity == 0:
            morphed = self._remove_pathologies(morphed)
        elif target_severity == 1:
            morphed = self._add_mild_features(morphed)
        elif target_severity == 2:
            morphed = self._add_moderate_features(morphed)
        elif target_severity >= 3:
            morphed = self._add_severe_features(morphed, target_severity)
        return morphed

    def _remove_pathologies(self, image: np.ndarray) -> np.ndarray:
        return cv2.medianBlur(image, 3)

    def _add_mild_features(self, image: np.ndarray) -> np.ndarray:
        return AdvancedDataAugmenter()._add_generative_artifacts(image)

    def _add_moderate_features(self, image: np.ndarray) -> np.ndarray:
        aug = AdvancedDataAugmenter()
        image = aug._traditional_augmentation(image)
        return aug._add_generative_artifacts(image)

    def _add_severe_features(self, image: np.ndarray, severity: int) -> np.ndarray:
        gan = RetinaGAN()
        overlay = gan.generate_synthetic_retina_images(1, severity)[0]
        return cv2.addWeighted(image, 0.6, overlay, 0.4, 0)

    def generate_what_if_scenarios(self, image: np.ndarray, treatment_effect: str) -> np.ndarray:
        if treatment_effect == "laser_success":
            return self._simulate_laser_treatment(image)
        if treatment_effect == "anti_vegf_success":
            return cv2.bilateralFilter(image, d=5, sigmaColor=50, sigmaSpace=50)
        if treatment_effect == "disease_progression":
            return self._add_severe_features(image, 3)
        if treatment_effect == "early_detection":
            return self._remove_pathologies(image)
        return image

    def _simulate_laser_treatment(self, image: np.ndarray) -> np.ndarray:
        treated = image.copy()
        h, w = image.shape[:2]
        for _ in range(20):
            x = np.random.randint(50, w - 50)
            y = np.random.randint(50, h - 50)
            if np.sqrt((x - w / 2) ** 2 + (y - h / 2) ** 2) > min(w, h) / 3:
                cv2.circle(treated, (x, y), 2, (200, 200, 200), -1)
        return treated

    def create_educational_content(self, diagnosis: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        educational_content: Dict[str, Any] = {
            "personalized_explanation": self._generate_personalized_explanation(diagnosis, patient_data),
        }
        return educational_content

    def _generate_personalized_explanation(self, diagnosis: str, patient_data: Dict[str, Any]) -> str:  # type: ignore[name-defined]
        base_explanations: Dict[str, str] = {
            "No Diabetic Retinopathy": "Great news! Your retinal screening shows no signs of diabetic eye disease.",
            "Mild Diabetic Retinopathy": "Early signs of diabetic eye changes were detected (microaneurysms).",
            "Proliferative Diabetic Retinopathy": "Advanced changes detected; fragile new vessels may bleed and threaten vision.",
        }
        explanation = base_explanations.get(diagnosis, "Diabetic retinopathy changes were detected in your retina.")
        years = patient_data.get("diabetes_years")
        if isinstance(years, (int, float)):
            explanation += f" This is not uncommon for someone who has had diabetes for {int(years)} years."
        a1c = patient_data.get("hba1c")
        if isinstance(a1c, (int, float)) and a1c > 8:
            explanation += " Better blood sugar control can help slow progression."
        return explanation


class GenerativeAnomalyDetector:
    """Autoencoder-based anomaly detection/localization for retinal images."""

    def __init__(self) -> None:
        self.autoencoder = self._build_anomaly_detector()
        self.normal_patterns: np.ndarray | None = None

    def _build_anomaly_detector(self) -> tf.keras.Model:
        encoder = tf.keras.Sequential(
            [
                layers.Conv2D(32, (3, 3), activation="relu", padding="same", input_shape=(224, 224, 3)),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
                layers.MaxPooling2D((2, 2)),
            ]
        )
        decoder = tf.keras.Sequential(
            [
                layers.Conv2DTranspose(128, (3, 3), strides=2, activation="relu", padding="same"),
                layers.Conv2DTranspose(64, (3, 3), strides=2, activation="relu", padding="same"),
                layers.Conv2DTranspose(32, (3, 3), strides=2, activation="relu", padding="same"),
                layers.Conv2D(3, (3, 3), activation="sigmoid", padding="same"),
            ]
        )
        autoencoder = tf.keras.Sequential([encoder, decoder])
        autoencoder.compile(optimizer="adam", loss="mse")
        return autoencoder

    def learn_normal_patterns(self, normal_images: np.ndarray) -> None:
        self.autoencoder.fit(normal_images, normal_images, epochs=5, batch_size=16, verbose=0)
        self.normal_patterns = normal_images

    def detect_anomalies(self, test_images: np.ndarray, threshold: float = 0.02) -> Tuple[np.ndarray, np.ndarray]:
        reconstructions = self.autoencoder.predict(test_images, verbose=0)
        errors = np.mean(np.square(test_images - reconstructions), axis=(1, 2, 3))
        anomalies = errors > threshold
        return anomalies, errors

    def localize_anomalies(self, image: np.ndarray) -> np.ndarray:
        reconstruction = self.autoencoder.predict(np.expand_dims(image, 0), verbose=0)[0]
        error_map = np.mean(np.square(image - reconstruction), axis=2)
        error_map = (error_map - np.min(error_map)) / (np.max(error_map) - np.min(error_map) + 1e-12)
        return error_map

    def explain_anomaly(self, image: np.ndarray, error_map: np.ndarray) -> Dict[str, Any]:
        high_error_regions = error_map > 0.5
        anomaly_mask = (high_error_regions.astype(np.uint8) * 255)
        contours, _ = cv2.findContours(anomaly_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        analysis: Dict[str, Any] = {
            "anomaly_count": len(contours),
            "total_anomaly_area": int(np.sum(high_error_regions)),
            "anomaly_locations": [],
            "possible_causes": [],
        }
        h, w = image.shape[:2]
        for contour in contours:
            if cv2.contourArea(contour) > 10:
                x, y, bw, bh = cv2.boundingRect(contour)
                analysis["anomaly_locations"].append(
                    {
                        "bounding_box": (int(x), int(y), int(bw), int(bh)),
                        "area": float(cv2.contourArea(contour)),
                        "center": (int(x + bw // 2), int(y + bh // 2)),
                    }
                )
        analysis["possible_causes"] = self._suggest_anomaly_causes(analysis, (h, w))
        return analysis

    def _suggest_anomaly_causes(self, analysis: Dict[str, Any], hw: Tuple[int, int]) -> List[str]:
        causes: List[str] = []
        h, w = hw
        for location in analysis["anomaly_locations"]:
            x, y, area_w, area_h = location["bounding_box"]
            center_x, center_y = location["center"]
            if center_x < w / 3:
                region = "nasal retina"
            elif center_x > 2 * w / 3:
                region = "temporal retina"
            else:
                region = "central retina"
            if center_y < h / 3:
                region += " (superior)"
            elif center_y > 2 * h / 3:
                region += " (inferior)"
            else:
                region += " (mid)"
            if location["area"] < 50:
                causes.append(f"Small anomaly in {region} - possible microaneurysm or early hemorrhage")
            else:
                causes.append(f"Larger anomaly in {region} - possible hemorrhage, exudate, or artifact")
        return causes


__all__ = [
    "RetinaGAN",
    "SyntheticDataGenerator",
    "AdvancedDataAugmenter",
    "GenerativeExplainer",
    "GenerativeAnomalyDetector",
]


