"""
Enhanced model training script for RetinaScan AI
Improvements:
- EfficientNet architecture
- Focal loss for class imbalance
- Class weighting
- Advanced augmentation
- Mixup augmentation
- Learning rate scheduling with warmup
- TensorBoard logging
- Better callbacks
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, 
    TensorBoard, LearningRateScheduler
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import logging
from pathlib import Path
from datetime import datetime

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MixupGenerator:
    """
    Mixup data augmentation generator
    Mixup: Beyond Empirical Risk Minimization (Zhang et al., 2017)
    """
    
    def __init__(self, generator, alpha=0.2):
        """
        Args:
            generator: Keras ImageDataGenerator
            alpha: Mixup interpolation coefficient
        """
        self.generator = generator
        self.alpha = alpha
    
    def __iter__(self):
        return self
    
    def __next__(self):
        # Get two batches
        batch_x1, batch_y1 = next(self.generator)
        batch_x2, batch_y2 = next(self.generator)
        
        # Generate mixup coefficient
        lam = np.random.beta(self.alpha, self.alpha, batch_x1.shape[0])
        
        # Reshape for broadcasting
        lam_x = lam.reshape((-1, 1, 1, 1))
        lam_y = lam.reshape((-1, 1))
        
        # Mix inputs and labels
        batch_x = lam_x * batch_x1 + (1 - lam_x) * batch_x2
        batch_y = lam_y * batch_y1 + (1 - lam_y) * batch_y2
        
        return batch_x, batch_y


class WarmUpLearningRateScheduler(tf.keras.callbacks.Callback):
    """
    Warmup learning rate scheduler
    Gradually increases learning rate from 0 to base_lr
    """
    
    def __init__(self, warmup_epochs, base_lr, verbose=0):
        super(WarmUpLearningRateScheduler, self).__init__()
        self.warmup_epochs = warmup_epochs
        self.base_lr = base_lr
        self.verbose = verbose
    
    def on_epoch_begin(self, epoch, logs=None):
        if epoch < self.warmup_epochs:
            lr = self.base_lr * (epoch + 1) / self.warmup_epochs
            tf.keras.backend.set_value(self.model.optimizer.lr, lr)
            if self.verbose > 0:
                logger.info(f'Epoch {epoch + 1}: WarmUp learning rate to {lr}')


class RetinaModelTrainer:
    """Enhanced model trainer for diabetic retinopathy detection"""
    
    def __init__(self, data_dir: str, model_architecture: str = 'efficientnetb3'):
        """
        Initialize trainer
        
        Args:
            data_dir: Directory containing training images
            model_architecture: Base architecture ('efficientnetb3', 'efficientnetb4', 'mobilenetv2')
        """
        self.data_dir = data_dir
        self.model_architecture = model_architecture
        self.model = None
        self.history = None
        self.class_weights = None
        
    def compute_class_weights(self, train_generator):
        """
        Compute class weights for imbalanced dataset
        
        Args:
            train_generator: Training data generator
            
        Returns:
            Dictionary of class weights
        """
        logger.info("Computing class weights for imbalanced dataset...")
        
        # Get class labels from generator
        class_labels = train_generator.classes
        
        # Compute class weights
        class_weights_array = compute_class_weight(
            'balanced',
            classes=np.unique(class_labels),
            y=class_labels
        )
        
        # Convert to dictionary
        self.class_weights = {i: weight for i, weight in enumerate(class_weights_array)}
        
        logger.info(f"Class weights: {self.class_weights}")
        return self.class_weights
    
    def focal_loss(self, alpha=0.25, gamma=2.0):
        """
        Focal Loss for addressing class imbalance
        
        Args:
            alpha: Weighting factor
            gamma: Focusing parameter
        """
        def focal_loss_fixed(y_true, y_pred):
            epsilon = tf.keras.backend.epsilon()
            y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
            
            # Calculate focal loss
            cross_entropy = -y_true * tf.math.log(y_pred)
            weight = alpha * y_true * tf.pow(1 - y_pred, gamma)
            loss = weight * cross_entropy
            
            return tf.reduce_mean(tf.reduce_sum(loss, axis=-1))
        
        return focal_loss_fixed
    
    def build_model(self) -> tf.keras.Model:
        """
        Build enhanced model with attention mechanism
        
        Returns:
            Compiled Keras model
        """
        logger.info(f"Building enhanced {self.model_architecture} model")
        
        # Select base model
        if self.model_architecture == 'efficientnetb3':
            base_model = tf.keras.applications.EfficientNetB3(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        elif self.model_architecture == 'efficientnetb4':
            base_model = tf.keras.applications.EfficientNetB4(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        elif self.model_architecture == 'mobilenetv2':
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        else:
            raise ValueError(f"Unsupported architecture: {self.model_architecture}")
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Build model with attention mechanism
        inputs = layers.Input(shape=(*Config.IMAGE_SIZE, 3))
        x = base_model(inputs, training=False)
        
        # Spatial attention mechanism
        attention = layers.Conv2D(1, kernel_size=1, activation='sigmoid', name='attention_map')(x)
        x = layers.Multiply()([x, attention])
        
        # Global pooling
        x = layers.GlobalAveragePooling2D()(x)
        
        # Dense layers with regularization
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(512, activation='relu', 
                        kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(256, activation='relu',
                        kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
        x = layers.Dropout(0.2)(x)
        
        # Output layer
        outputs = layers.Dense(Config.NUM_CLASSES, activation='softmax', name='predictions')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs)
        
        # Compile with focal loss
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=self.focal_loss(alpha=0.25, gamma=2.0),
            metrics=[
                'accuracy',
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall'),
                tf.keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')
            ]
        )
        
        logger.info("Model built successfully")
        logger.info(f"Total parameters: {model.count_params():,}")
        logger.info(f"Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
        
        self.model = model
        return model
    
    def create_data_generators(self, validation_split: float = 0.2, use_mixup: bool = False):
        """
        Create enhanced data generators with advanced augmentation
        
        Args:
            validation_split: Fraction of data to use for validation
            use_mixup: Whether to use mixup augmentation
            
        Returns:
            Tuple of (train_generator, validation_generator)
        """
        logger.info("Creating data generators with advanced augmentation")
        
        # Training data augmentation (aggressive for better generalization)
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=30,
            width_shift_range=0.25,
            height_shift_range=0.25,
            horizontal_flip=True,
            vertical_flip=True,
            zoom_range=0.25,
            shear_range=0.15,
            brightness_range=[0.8, 1.2],
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
        logger.info(f"Class indices: {train_generator.class_indices}")
        
        # Compute class weights
        self.compute_class_weights(train_generator)
        
        # Wrap with mixup if requested
        if use_mixup:
            logger.info("Applying Mixup augmentation")
            train_generator = MixupGenerator(train_generator, alpha=0.2)
        
        return train_generator, validation_generator
    
    def train(self, epochs: int = 50, fine_tune_epochs: int = 20, 
              warmup_epochs: int = 5, use_mixup: bool = False):
        """
        Train the model with advanced techniques
        
        Args:
            epochs: Number of epochs for initial training
            fine_tune_epochs: Number of epochs for fine-tuning
            warmup_epochs: Number of warmup epochs
            use_mixup: Whether to use mixup augmentation
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Create data generators
        train_gen, val_gen = self.create_data_generators(use_mixup=use_mixup)
        
        # Create log directory
        log_dir = f"logs/fit/{self.model_architecture}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        os.makedirs(log_dir, exist_ok=True)
        
        # Callbacks for stage 1
        callbacks_stage1 = [
            WarmUpLearningRateScheduler(
                warmup_epochs=warmup_epochs,
                base_lr=0.001,
                verbose=1
            ),
            ModelCheckpoint(
                Config.MODEL_PATH,
                monitor='val_auc',
                save_best_only=True,
                mode='max',
                verbose=1
            ),
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-7,
                verbose=1
            ),
            TensorBoard(
                log_dir=log_dir,
                histogram_freq=1,
                write_graph=True,
                write_images=True
            )
        ]
        
        # Stage 1: Train with frozen base
        logger.info("=" * 80)
        logger.info("STAGE 1: Training with frozen base model")
        logger.info("=" * 80)
        
        history1 = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks_stage1,
            class_weight=self.class_weights if not use_mixup else None,
            verbose=1
        )
        
        # Stage 2: Fine-tune with unfrozen base
        logger.info("=" * 80)
        logger.info("STAGE 2: Fine-tuning with unfrozen base model")
        logger.info("=" * 80)
        
        # Unfreeze base model layers (unfreeze last N layers)
        base_model = self.model.layers[1]  # Get base model
        base_model.trainable = True
        
        # Freeze early layers, unfreeze later layers
        fine_tune_at = len(base_model.layers) - 50  # Unfreeze last 50 layers
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False
        
        logger.info(f"Unfrozen layers: {sum([1 for layer in base_model.layers if layer.trainable])}")
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss=self.focal_loss(alpha=0.25, gamma=2.0),
            metrics=[
                'accuracy',
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall'),
                tf.keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')
            ]
        )
        
        # Callbacks for stage 2
        callbacks_stage2 = [
            ModelCheckpoint(
                Config.MODEL_PATH,
                monitor='val_auc',
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
                min_lr=1e-8,
                verbose=1
            ),
            TensorBoard(
                log_dir=log_dir,
                histogram_freq=1
            )
        ]
        
        # Continue training
        history2 = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=fine_tune_epochs,
            callbacks=callbacks_stage2,
            class_weight=self.class_weights if not use_mixup else None,
            verbose=1
        )
        
        logger.info("=" * 80)
        logger.info("Training complete!")
        logger.info("=" * 80)
        
        # Combine histories
        self.history = {
            'stage1': history1.history,
            'stage2': history2.history
        }
        
        # Print final metrics
        logger.info(f"Best validation AUC: {max(history1.history.get('val_auc', [0]) + history2.history.get('val_auc', [0])):.4f}")
        logger.info(f"Best validation accuracy: {max(history1.history.get('val_accuracy', [0]) + history2.history.get('val_accuracy', [0])):.4f}")
        
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
        
        logger.info("=" * 80)
        logger.info("Evaluating model on test data...")
        logger.info("=" * 80)
        
        results = self.model.evaluate(test_generator, verbose=1)
        
        metric_names = ['Loss', 'Accuracy', 'AUC', 'Precision', 'Recall', 'Top-2 Accuracy']
        for name, value in zip(metric_names, results):
            logger.info(f"Test {name}: {value:.4f}")
        
        return results


def main():
    """Main training function"""
    # Configuration
    DATA_DIR = "data/train"  # Update with your data directory
    MODEL_ARCH = "efficientnetb3"  # 'efficientnetb3', 'efficientnetb4', or 'mobilenetv2'
    EPOCHS = 30
    FINE_TUNE_EPOCHS = 15
    WARMUP_EPOCHS = 5
    USE_MIXUP = False  # Set to True for mixup augmentation
    
    logger.info("=" * 80)
    logger.info("RetinaScan AI - Enhanced Training Pipeline")
    logger.info("=" * 80)
    logger.info(f"Architecture: {MODEL_ARCH}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Epochs: {EPOCHS} + {FINE_TUNE_EPOCHS} (fine-tuning)")
    logger.info(f"Warmup epochs: {WARMUP_EPOCHS}")
    logger.info(f"Mixup augmentation: {USE_MIXUP}")
    logger.info("=" * 80)
    
    # Create trainer
    trainer = RetinaModelTrainer(DATA_DIR, MODEL_ARCH)
    
    # Build model
    trainer.build_model()
    
    # Train model
    trainer.train(
        epochs=EPOCHS,
        fine_tune_epochs=FINE_TUNE_EPOCHS,
        warmup_epochs=WARMUP_EPOCHS,
        use_mixup=USE_MIXUP
    )
    
    # Evaluate
    trainer.evaluate()
    
    logger.info("=" * 80)
    logger.info(f"Model saved to {Config.MODEL_PATH}")
    logger.info("Training complete! 🎉")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
