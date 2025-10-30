"""Quick demo of generative AI utilities.

Run:
  python examples/generative_demo.py
"""

from __future__ import annotations

import os
import sys
from typing import Dict

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from retina_model.generative_ai import (
    RetinaGAN,
    SyntheticDataGenerator,
    AdvancedDataAugmenter,
    GenerativeExplainer,
    GenerativeAnomalyDetector,
)


def main() -> None:
    # 1) Generate a few synthetic images per severity
    gan = RetinaGAN()
    synthetic_samples = {s: gan.generate_synthetic_retina_images(2, s) for s in range(5)}
    print({k: v.shape for k, v in synthetic_samples.items()})

    # 2) Balance a mock dataset
    generator = SyntheticDataGenerator()
    class_dist: Dict[int, int] = {0: 10, 1: 8, 2: 6, 3: 4, 4: 2}
    balanced = generator.generate_training_dataset(target_size_per_class=12, original_distribution=class_dist)
    print({k: v.shape[0] for k, v in balanced.items()})

    # 3) Augment rare cases
    rare_images = synthetic_samples[4]
    labels = np.array([4] * len(rare_images))
    augmenter = AdvancedDataAugmenter()
    aug_images, aug_labels = augmenter.augment_rare_cases(rare_images, labels, target_count=6)
    print("Augmented:", aug_images.shape, aug_labels.shape)

    # 4) Explain progression and simulate treatment
    explainer = GenerativeExplainer()
    base = synthetic_samples[2][0]
    progression = explainer.generate_disease_progression(base, current_severity=2, target_severity=4)
    treated = explainer.generate_what_if_scenarios(base, "laser_success")
    print(f"Progression steps: {len(progression)} | Treated shape: {treated.shape}")

    # 5) Anomaly detection
    detector = GenerativeAnomalyDetector()
    # Learn on a tiny synthetic normal-like set (for demo only)
    normals = gan.generate_synthetic_retina_images(4, severity_level=0).astype(np.float32) / 255.0
    detector.learn_normal_patterns(normals)
    test = (base.astype(np.float32) / 255.0)[None, ...]
    anomalies, scores = detector.detect_anomalies(test, threshold=0.01)
    print("Anomaly flagged:", bool(anomalies[0]), "Score:", float(scores[0]))


if __name__ == "__main__":
    main()


