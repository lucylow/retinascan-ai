import tensorflow as tf
import numpy as np
import cv2
from sklearn.utils import class_weight
import albumentations as A
from tensorflow.keras.preprocessing.image import ImageDataGenerator


class RetinaDataPreprocessor:
    """Handles data preprocessing and augmentation for retinal images"""

    def __init__(self, img_size=(224, 224)):
        self.img_size = img_size
        self.augmentation_pipeline = self._create_augmentation_pipeline()

    def _create_augmentation_pipeline(self):
        """Create advanced augmentation pipeline using Albumentations"""

        return A.Compose([
            A.Rotate(limit=30, p=0.5),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.3),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.1,
                rotate_limit=20,
                p=0.5
            ),
            A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.5
            ),
            A.HueSaturationValue(
                hue_shift_limit=10,
                sat_shift_limit=20,
                val_shift_limit=10,
                p=0.5
            ),
            A.CLAHE(clip_limit=4.0, p=0.3),
            A.GaussianBlur(blur_limit=3, p=0.3),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.ISONoise(color_shift=(0.01, 0.05), p=0.2),
            A.RandomGamma(gamma_limit=(80, 120), p=0.3),
        ])

    def preprocess_retinal_image(self, image_path):
        """
        Advanced preprocessing for retinal images
        """
        try:
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image = image_path

            image = cv2.resize(image, self.img_size)

            image = self._enhance_retinal_image(image)

            image = image.astype('float32') / 255.0

            return image

        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None

    def _enhance_retinal_image(self, image):
        """Apply retinal image enhancement techniques"""

        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)

        lab_enhanced = cv2.merge([l_enhanced, a, b])
        image_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)

        image_enhanced = cv2.GaussianBlur(image_enhanced, (3, 3), 0)

        return image_enhanced

    def augment_image(self, image):
        """Apply augmentation to image"""
        augmented = self.augmentation_pipeline(image=image)
        return augmented['image']

    def create_data_generators(self, train_df, val_df, test_df, batch_size=32):
        """Create data generators for training, validation, and testing"""

        train_datagen = ImageDataGenerator(
            preprocessing_function=lambda x: self.preprocess_retinal_image(x),
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            brightness_range=[0.8, 1.2],
            fill_mode='nearest'
        )

        test_datagen = ImageDataGenerator(
            preprocessing_function=lambda x: self.preprocess_retinal_image(x)
        )

        train_generator = train_datagen.flow_from_dataframe(
            dataframe=train_df,
            x_col='image_path',
            y_col='diagnosis',
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='raw',
            shuffle=True
        )

        val_generator = test_datagen.flow_from_dataframe(
            dataframe=val_df,
            x_col='image_path',
            y_col='diagnosis',
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='raw',
            shuffle=False
        )

        test_generator = test_datagen.flow_from_dataframe(
            dataframe=test_df,
            x_col='image_path',
            y_col='diagnosis',
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='raw',
            shuffle=False
        )

        return train_generator, val_generator, test_generator

    def calculate_class_weights(self, y_train):
        """Calculate class weights for imbalanced dataset"""
        class_weights = class_weight.compute_class_weight(
            'balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        return dict(enumerate(class_weights))


