"""
Model training script for RetinaScan AI
Trains a diabetic retinopathy detection model using transfer learning
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
import logging
from pathlib import Path

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetinaModelTrainer:
    """Handles model training for diabetic retinopathy detection"""
    
    def __init__(self, data_dir: str, model_architecture: str = 'mobilenetv2'):
        """
        Initialize trainer
        
        Args:
            data_dir: Directory containing training images
            model_architecture: Base architecture ('mobilenetv2' or 'resnet50')
        """
        self.data_dir = data_dir
        self.model_architecture = model_architecture
        self.model = None
        self.history = None
        
    def build_model(self) -> tf.keras.Model:
        """
        Build model using transfer learning
        
        Returns:
            Compiled Keras model
        """
        logger.info(f"Building model with {self.model_architecture} architecture")
        
        # Select base model
        if self.model_architecture == 'mobilenetv2':
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        elif self.model_architecture == 'resnet50':
            base_model = tf.keras.applications.ResNet50(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        else:
            raise ValueError(f"Unsupported architecture: {self.model_architecture}")
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Build complete model
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(Config.NUM_CLASSES, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        logger.info("Model built successfully")
        logger.info(f"Total parameters: {model.count_params():,}")
        
        self.model = model
        return model
    
    def create_data_generators(self, validation_split: float = 0.2):
        """
        Create data generators with augmentation
        
        Args:
            validation_split: Fraction of data to use for validation
            
        Returns:
            Tuple of (train_generator, validation_generator)
        """
        logger.info("Creating data generators with augmentation")
        
        # Training data augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            zoom_range=0.2,
            shear_range=0.1,
            fill_mode='nearest',
            validation_split=validation_split
        )
        
        # Validation data (only rescaling)
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split
        )
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            self.data_dir,
            target_size=Config.IMAGE_SIZE,
            batch_size=32,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        validation_generator = val_datagen.flow_from_directory(
            self.data_dir,
            target_size=Config.IMAGE_SIZE,
            batch_size=32,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        logger.info(f"Training samples: {train_generator.samples}")
        logger.info(f"Validation samples: {validation_generator.samples}")
        
        return train_generator, validation_generator
    
    def train(self, epochs: int = 50, fine_tune_epochs: int = 20):
        """
        Train the model with two-stage training
        
        Args:
            epochs: Number of epochs for initial training
            fine_tune_epochs: Number of epochs for fine-tuning
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Create data generators
        train_gen, val_gen = self.create_data_generators()
        
        # Callbacks
        callbacks = [
            ModelCheckpoint(
                Config.MODEL_PATH,
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            ),
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        # Stage 1: Train with frozen base
        logger.info("Stage 1: Training with frozen base model")
        history1 = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        # Stage 2: Fine-tune with unfrozen base
        logger.info("Stage 2: Fine-tuning with unfrozen base model")
        
        # Unfreeze base model
        self.model.layers[0].trainable = True
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        # Continue training
        history2 = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=fine_tune_epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Training complete!")
        
        # Combine histories
        self.history = {
            'stage1': history1.history,
            'stage2': history2.history
        }
        
        return self.history
    
    def evaluate(self, test_data_dir: str = None):
        """
        Evaluate model on test data
        
        Args:
            test_data_dir: Directory with test images (uses training dir if None)
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        test_dir = test_data_dir or self.data_dir
        
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=Config.IMAGE_SIZE,
            batch_size=32,
            class_mode='categorical',
            shuffle=False
        )
        
        logger.info("Evaluating model on test data...")
        results = self.model.evaluate(test_generator, verbose=1)
        
        logger.info(f"Test Loss: {results[0]:.4f}")
        logger.info(f"Test Accuracy: {results[1]:.4f}")
        logger.info(f"Test AUC: {results[2]:.4f}")
        
        return results


def main():
    """Main training function"""
    # Configuration
    DATA_DIR = "data/train"  # Update with your data directory
    MODEL_ARCH = "mobilenetv2"  # or "resnet50"
    EPOCHS = 30
    FINE_TUNE_EPOCHS = 15
    
    # Create trainer
    trainer = RetinaModelTrainer(DATA_DIR, MODEL_ARCH)
    
    # Build model
    trainer.build_model()
    
    # Train model
    trainer.train(epochs=EPOCHS, fine_tune_epochs=FINE_TUNE_EPOCHS)
    
    # Evaluate
    trainer.evaluate()
    
    logger.info(f"Model saved to {Config.MODEL_PATH}")


if __name__ == "__main__":
    main()
