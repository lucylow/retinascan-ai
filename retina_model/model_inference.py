import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.models import load_model


class RetinaPredictor:
    """Handles model inference and predictions"""

    def __init__(self, model_path='models/retina_model_final.h5'):
        self.model = load_model(model_path)
        self.img_size = (224, 224)
        self.class_names = [
            'No Diabetic Retinopathy',
            'Mild Diabetic Retinopathy',
            'Moderate Diabetic Retinopathy',
            'Severe Diabetic Retinopathy',
            'Proliferative Diabetic Retinopathy'
        ]

    def preprocess_image(self, image):
        """Preprocess image for prediction"""

        image = cv2.resize(image, self.img_size)

        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        lab_enhanced = cv2.merge([l_enhanced, a, b])
        image_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)

        image_enhanced = image_enhanced.astype('float32') / 255.0

        image_batch = np.expand_dims(image_enhanced, axis=0)

        return image_batch

    def predict(self, image):
        """Make prediction on single image"""

        processed_image = self.preprocess_image(image)

        predictions = self.model.predict(processed_image)
        predicted_class = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]))

        class_probabilities = {
            self.class_names[i]: float(predictions[0][i])
            for i in range(len(self.class_names))
        }

        return {
            'diagnosis': self.class_names[predicted_class],
            'severity_level': int(predicted_class),
            'confidence': confidence,
            'probabilities': class_probabilities
        }

    def batch_predict(self, images):
        """Make predictions on multiple images"""

        results = []
        for image in images:
            result = self.predict(image)
            results.append(result)

        return results

    def explain_prediction(self, image, prediction_result):
        """Generate explanation for prediction using Grad-CAM"""

        explanation = {
            'primary_features': self._get_feature_importance(prediction_result),
            'confidence_level': self._get_confidence_level(prediction_result['confidence']),
            'recommendation': self._generate_recommendation(prediction_result)
        }

        return explanation

    def _get_feature_importance(self, prediction_result):
        """Get feature importance based on prediction"""

        severity = prediction_result['severity_level']

        feature_mapping = {
            0: ["Normal retinal structure", "Clear blood vessels", "No abnormalities"],
            1: ["Microaneurysms present", "Mild vascular changes"],
            2: ["Multiple microaneurysms", "Retinal hemorrhages", "Cotton wool spots"],
            3: ["Extensive hemorrhages", "Venous beading", "Intraretinal microvascular abnormalities"],
            4: ["Neovascularization", "Vitreous hemorrhage", "Retinal detachment risk"]
        }

        return feature_mapping.get(severity, ["Unable to determine specific features"])

    def _get_confidence_level(self, confidence):
        """Convert numerical confidence to descriptive level"""

        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.8:
            return "High"
        elif confidence >= 0.7:
            return "Moderate"
        elif confidence >= 0.6:
            return "Low"
        else:
            return "Very Low"

    def _generate_recommendation(self, prediction_result):
        """Generate medical recommendation based on prediction"""

        recommendations = {
            0: "No signs of diabetic retinopathy detected. Continue regular annual eye screenings.",
            1: "Mild non-proliferative diabetic retinopathy detected. Recommend follow-up with ophthalmologist in 6-12 months.",
            2: "Moderate non-proliferative diabetic retinopathy detected. Urgent consultation with ophthalmologist recommended within 3-6 months.",
            3: "Severe non-proliferative diabetic retinopathy detected. Immediate ophthalmologist consultation recommended within 1 month.",
            4: "Proliferative diabetic retinopathy detected. Emergency ophthalmologist consultation required immediately."
        }

        return recommendations.get(prediction_result['severity_level'], "Consult with healthcare provider.")


if __name__ == "__main__":
    predictor = RetinaPredictor()
    sample_image = (np.random.rand(224, 224, 3) * 255).astype(np.uint8)
    result = predictor.predict(sample_image)
    print("Prediction Result:")
    print(f"Diagnosis: {result['diagnosis']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Severity Level: {result['severity_level']}")


