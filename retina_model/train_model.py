import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import json
import os

from .model_architecture import RetinaScanModel
from .data_preprocessor import RetinaDataPreprocessor


class RetinaModelTrainer:
    """Handles complete training pipeline for RetinaScan AI"""

    def __init__(self, config):
        self.config = config
        self.model = None
        self.preprocessor = RetinaDataPreprocessor(
            img_size=config['img_size']
        )
        self.history = None

    def load_and_prepare_data(self):
        """Load and prepare the APTOS 2019 dataset"""

        df = pd.read_csv(self.config['data_csv_path'])

        diagnosis_mapping = {
            'No DR': 0,
            'Mild': 1,
            'Moderate': 2,
            'Severe': 3,
            'Proliferative DR': 4
        }

        df['diagnosis'] = df['diagnosis'].map(diagnosis_mapping)

        train_df, temp_df = train_test_split(
            df,
            test_size=0.3,
            random_state=42,
            stratify=df['diagnosis']
        )

        val_df, test_df = train_test_split(
            temp_df,
            test_size=0.5,
            random_state=42,
            stratify=temp_df['diagnosis']
        )

        print(f"Training samples: {len(train_df)}")
        print(f"Validation samples: {len(val_df)}")
        print(f"Test samples: {len(test_df)}")

        return train_df, val_df, test_df

    def train(self):
        """Complete training pipeline"""

        print("Starting RetinaScan AI Training Pipeline...")

        train_df, val_df, test_df = self.load_and_prepare_data()

        train_gen, val_gen, test_gen = self.preprocessor.create_data_generators(
            train_df, val_df, test_df,
            batch_size=self.config['batch_size']
        )

        class_weights = self.preprocessor.calculate_class_weights(
            train_df['diagnosis'].values
        )
        print("Class weights:", class_weights)

        self.model = RetinaScanModel(
            input_shape=(*self.config['img_size'], 3),
            num_classes=5
        )

        if self.config['use_pretrained']:
            _ = self.model.build_efficientnet_model()
        else:
            _ = self.model.build_custom_cnn()

        self.model.compile_model(learning_rate=self.config['learning_rate'])

        self.model.model.summary()

        print("Starting model training...")

        self.history = self.model.model.fit(
            train_gen,
            epochs=self.config['epochs'],
            validation_data=val_gen,
            class_weight=class_weights,
            callbacks=self.model.get_callbacks(),
            verbose=1
        )

        print("Evaluating model...")
        test_results = self.evaluate_model(test_gen)

        self.save_training_artifacts(test_results)

        return self.history, test_results

    def evaluate_model(self, test_generator):
        """Comprehensive model evaluation"""

        y_pred = self.model.model.predict(test_generator)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true = test_generator.classes

        test_loss, test_accuracy, test_precision, test_recall, test_auc = \
            self.model.model.evaluate(test_generator, verbose=0)

        class_report = classification_report(
            y_true,
            y_pred_classes,
            target_names=[
                'No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR'
            ],
            output_dict=True
        )

        cm = confusion_matrix(y_true, y_pred_classes)

        results = {
            'test_loss': test_loss,
            'test_accuracy': test_accuracy,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_auc': test_auc,
            'classification_report': class_report,
            'confusion_matrix': cm.tolist(),
            'predictions': y_pred.tolist(),
            'true_labels': y_true.tolist()
        }

        return results

    def save_training_artifacts(self, test_results):
        """Save model and training artifacts"""

        os.makedirs('models', exist_ok=True)
        os.makedirs('training_artifacts', exist_ok=True)

        self.model.model.save('models/retina_model_final.h5')

        converter = tf.lite.TFLiteConverter.from_keras_model(self.model.model)
        tflite_model = converter.convert()
        with open('models/retina_model.tflite', 'wb') as f:
            f.write(tflite_model)

        history_df = pd.DataFrame(self.history.history)
        history_df.to_csv('training_artifacts/training_history.csv', index=False)

        with open('training_artifacts/test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)

        self.plot_training_history()
        self.plot_confusion_matrix(test_results['confusion_matrix'])

        print("Training artifacts saved successfully!")

    def plot_training_history(self):
        """Plot training history"""

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        axes[0, 0].plot(self.history.history['accuracy'], label='Training Accuracy')
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()

        axes[0, 1].plot(self.history.history['loss'], label='Training Loss')
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()

        axes[1, 0].plot(self.history.history['precision'], label='Training Precision')
        axes[1, 0].plot(self.history.history['val_precision'], label='Validation Precision')
        axes[1, 0].set_title('Model Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()

        axes[1, 1].plot(self.history.history['auc'], label='Training AUC')
        axes[1, 1].plot(self.history.history['val_auc'], label='Validation AUC')
        axes[1, 1].set_title('Model AUC')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('AUC')
        axes[1, 1].legend()

        plt.tight_layout()
        plt.savefig('training_artifacts/training_history.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_confusion_matrix(self, cm):
        """Plot confusion matrix"""

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'],
            yticklabels=['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
        )
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.savefig('training_artifacts/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()


CONFIG = {
    'data_csv_path': 'data/train.csv',
    'img_size': (224, 224),
    'batch_size': 32,
    'epochs': 50,
    'learning_rate': 0.001,
    'use_pretrained': True
}


if __name__ == "__main__":
    trainer = RetinaModelTrainer(CONFIG)
    history, results = trainer.train()
    print("\n=== TRAINING COMPLETE ===")
    print(f"Test Accuracy: {results['test_accuracy']:.4f}")
    print(f"Test Precision: {results['test_precision']:.4f}")
    print(f"Test Recall: {results['test_recall']:.4f}")
    print(f"Test AUC: {results['test_auc']:.4f}")


