import io
import base64
from typing import Dict, List, Tuple, Optional

import numpy as np
import cv2
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import tensorflow as tf
from tensorflow.keras.models import Model


class AIVisualizationService:
    """
    Advanced AI-powered visualization service for diabetic retinopathy detection.
    Implements GradCAM, attention heatmaps, and dashboard-friendly chart images.
    """

    def __init__(self, model: tf.keras.Model):
        self.model = model
        self.last_conv_layer_name = self._find_last_conv_layer()

    def _find_last_conv_layer(self) -> str:
        """Automatically find the last convolutional layer for GradCAM."""
        for layer in reversed(self.model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                return layer.name
        raise ValueError("No convolutional layer found in model")

    def generate_gradcam_heatmap(
        self,
        img_array: np.ndarray,
        pred_index: Optional[int] = None,
        colormap: int = cv2.COLORMAP_JET,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate Gradient-weighted Class Activation Mapping (GradCAM) heatmap.

        Args:
            img_array: Input image array with shape (1, H, W, 3) normalized [0,1]
            pred_index: Class index to visualize (None = use model-predicted class)
            colormap: OpenCV colormap

        Returns:
            heatmap (BGR uint8), superimposed image (BGR uint8)
        """
        grad_model = Model(
            inputs=self.model.input,
            outputs=[
                self.model.get_layer(self.last_conv_layer_name).output,
                self.model.output,
            ],
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            if pred_index is None:
                pred_index = int(tf.argmax(predictions[0]))
            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()

        h, w = img_array.shape[1], img_array.shape[2]
        heatmap = cv2.resize(heatmap, (w, h))
        heatmap_uint8 = np.uint8(255 * heatmap)
        heatmap_bgr = cv2.applyColorMap(heatmap_uint8, colormap)

        img_original = (img_array[0] * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_original, cv2.COLOR_RGB2BGR)
        superimposed_bgr = cv2.addWeighted(img_bgr, 0.6, heatmap_bgr, 0.4, 0)

        return heatmap_bgr, superimposed_bgr

    def detect_lesion_regions(self, heatmap: np.ndarray, threshold: float = 0.5) -> List[Dict]:
        """
        Detect and localize lesion-like regions from GradCAM activation map.
        Returns a list of dicts with bbox and confidence.
        """
        heatmap_gray = cv2.cvtColor(heatmap, cv2.COLOR_BGR2GRAY)
        heatmap_norm = heatmap_gray.astype(np.float32) / 255.0

        _, binary_mask = cv2.threshold(
            heatmap_norm, float(threshold), 1.0, cv2.THRESH_BINARY
        )
        binary_mask = np.uint8(binary_mask * 255)

        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions: List[Dict] = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area < 100:
                continue
            roi = heatmap_norm[y : y + h, x : x + w]
            confidence = float(np.mean(roi))
            regions.append(
                {
                    "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "confidence": confidence,
                    "area": int(area),
                    "lesion_type": self._classify_lesion_type(w, h, confidence),
                }
            )

        regions.sort(key=lambda r: r["confidence"], reverse=True)
        return regions

    def _classify_lesion_type(self, w: int, h: int, confidence: float) -> str:
        area = w * h
        aspect_ratio = (max(w, h) / max(1, min(w, h))) if min(w, h) > 0 else 1.0
        if area < 200 and aspect_ratio < 1.5:
            return "microaneurysm"
        if area < 500 and confidence > 0.7:
            return "hemorrhage"
        if area > 500 and aspect_ratio < 2:
            return "hard_exudate"
        if area > 300 and aspect_ratio > 2:
            return "cotton_wool_spot"
        return "abnormality"

    def create_confidence_chart(self, class_probabilities: Dict[str, float], severity_labels: List[str]) -> str:
        """
        Generate a horizontal bar chart PNG (base64 string without prefix).
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        classes = list(class_probabilities.keys())
        probs = [class_probabilities[c] for c in classes]

        colors = ['#10b981', '#84cc16', '#f59e0b', '#ef4444', '#dc2626']
        ax.barh(severity_labels[: len(probs)], probs, color=colors[: len(probs)], alpha=0.85)

        for y, prob in enumerate(probs):
            ax.text(prob + 0.01, y, f"{prob * 100:.1f}%", va='center', fontsize=10, fontweight='bold')

        ax.set_xlabel('Confidence Score', fontsize=12, fontweight='bold')
        ax.set_title('DR Severity Classification Confidence', fontsize=14, fontweight='bold')
        ax.set_xlim([0, 1.0])
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return b64

    def create_attention_map_overlay(
        self,
        original_img_rgb: np.ndarray,
        heatmap_bgr: np.ndarray,
        lesion_regions: List[Dict],
    ) -> str:
        """
        Create a composite figure with original, heatmap, and overlay with boxes. Returns base64 PNG.
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        axes[0].imshow(original_img_rgb)
        axes[0].set_title('Original Retinal Image', fontsize=12, fontweight='bold')
        axes[0].axis('off')

        heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
        axes[1].imshow(heatmap_rgb)
        axes[1].set_title('AI Attention Heatmap (GradCAM)', fontsize=12, fontweight='bold')
        axes[1].axis('off')

        overlay_img = cv2.addWeighted(original_img_rgb, 0.6, heatmap_rgb, 0.4, 0)
        axes[2].imshow(overlay_img)
        for region in lesion_regions[:5]:
            bbox = region['bbox']
            rect = Rectangle((bbox['x'], bbox['y']), bbox['width'], bbox['height'], linewidth=2, edgecolor='yellow', facecolor='none')
            axes[2].add_patch(rect)
            axes[2].text(
                bbox['x'],
                max(0, bbox['y'] - 5),
                f"{region['lesion_type']} ({region['confidence']:.2f})",
                color='yellow',
                fontsize=8,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7),
            )
        axes[2].set_title('Lesion Localization', fontsize=12, fontweight='bold')
        axes[2].axis('off')

        plt.tight_layout()
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return b64

    def create_temporal_progression_chart(self, patient_history: List[Dict]) -> str:
        """Create a temporal progression chart; returns base64 PNG."""
        fig, ax = plt.subplots(figsize=(12, 6))
        timestamps = [record['timestamp'] for record in patient_history]
        severity_scores = [record['severity_class'] for record in patient_history]
        confidences = [record.get('confidence', 1.0) for record in patient_history]

        ax.plot(timestamps, severity_scores, marker='o', linewidth=2, markersize=8, color='#3b82f6', label='DR Severity Class')

        lower = [s - (1 - c) * 0.5 for s, c in zip(severity_scores, confidences)]
        upper = [s + (1 - c) * 0.5 for s, c in zip(severity_scores, confidences)]
        ax.fill_between(timestamps, lower, upper, alpha=0.2, color='#3b82f6')

        ax.set_xlabel('Examination Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('DR Severity Class', fontsize=12, fontweight='bold')
        ax.set_title('Disease Progression Timeline', fontsize=14, fontweight='bold')
        ax.set_yticks([0, 1, 2, 3, 4])
        ax.set_yticklabels(['No DR', 'Mild', 'Moderate', 'Severe', 'PDR'])
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return b64

    def generate_comparative_heatmap(
        self,
        img1_rgb: np.ndarray,
        img2_rgb: np.ndarray,
        heatmap1_bgr: np.ndarray,
        heatmap2_bgr: np.ndarray,
        title1: str = "Before Treatment",
        title2: str = "After Treatment",
    ) -> str:
        """Create side-by-side comparison figure; returns base64 PNG."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes[0, 0].imshow(img1_rgb)
        axes[0, 0].set_title(f'{title1}\nOriginal', fontsize=11, fontweight='bold')
        axes[0, 0].axis('off')

        axes[0, 1].imshow(img2_rgb)
        axes[0, 1].set_title(f'{title2}\nOriginal', fontsize=11, fontweight='bold')
        axes[0, 1].axis('off')

        overlay1 = cv2.addWeighted(img1_rgb, 0.6, cv2.cvtColor(heatmap1_bgr, cv2.COLOR_BGR2RGB), 0.4, 0)
        overlay2 = cv2.addWeighted(img2_rgb, 0.6, cv2.cvtColor(heatmap2_bgr, cv2.COLOR_BGR2RGB), 0.4, 0)

        axes[1, 0].imshow(overlay1)
        axes[1, 0].set_title(f'{title1}\nAI Attention Map', fontsize=11, fontweight='bold')
        axes[1, 0].axis('off')

        axes[1, 1].imshow(overlay2)
        axes[1, 1].set_title(f'{title2}\nAI Attention Map', fontsize=11, fontweight='bold')
        axes[1, 1].axis('off')

        plt.suptitle('Comparative Analysis: Disease Progression/Treatment Response', fontsize=14, fontweight='bold')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return b64


