import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from ui_form import Ui_Widget


class Widget(QWidget):
    def _init_(self, parent=None):
        super()._init_(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.original_image = None
        self.processed_image = None

        # for arrenging the contrast the slider called slider_contrast was added in the range of [0-200]
        self.ui.slider_contrast.setMinimum(0)
        self.ui.slider_contrast.setMaximum(200)
        self.ui.slider_contrast.setValue(100)
        self.ui.slider_contrast.valueChanged.connect(self.adjust_contrast)

        # for arrenging the resizing a slider called slider_zoom was added in the range of [10-200]
        self.ui.slider_zoom.setMinimum(10)  # Minimum %10 boyut
        self.ui.slider_zoom.setMaximum(200)  # Maksimum %200 boyut
        self.ui.slider_zoom.setValue(100)  # Varsayılan %100
        self.ui.slider_zoom.valueChanged.connect(self.zoom_image)


        # Blur Slider
        self.ui.slider_blur.setMinimum(1)  # Minimum kernel size
        self.ui.slider_blur.setMaximum(50)  # Maximum kernel size
        self.ui.slider_blur.setValue(1)  # Default value (no blur)
        self.ui.slider_blur.valueChanged.connect(self.apply_blur)

        # for uploading the x-ray image a buton was added
        self.ui.button.clicked.connect(self.load_image)

    def apply_blur(self, value):
        """Applies Gaussian blur to the processed image."""
        if self.original_image is None:
            return


        # Gaussian kernel size must be odd; ensure odd value
        kernel_size = value if value % 2 != 0 else value + 1

        self.processed_image = cv2.GaussianBlur(self.original_image, (kernel_size, kernel_size), 0)
        self.display_images(self.original_image, self.processed_image)



    #for adding a picture in diffrent formats other versions of the files was added
    def load_image(self):
        """Resim dosyasını yükler."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Resim Seç",
            "",
            "Resim Dosyaları(*.png , *.jpg , *.jpeg )"
        )
        #the uploaded picture saves in the memory and the original photo is  protected
        if file_name:
            self.original_image = cv2.imread(file_name)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.processed_image = self.original_image.copy()  # Initialize processed image as a copy of the original
            self.display_images(self.original_image, self.processed_image)
        else:
            print("Resim dosyası yüklenemedi.")

    def adjust_contrast(self, value):
        """Resmin kontrastını ayarlar."""
        if self.original_image is None:
            return

        contrast = value / 100  # Slider değeri [0-200], bunu [0.0-2.0] aralığına dönüştür
        self.processed_image = cv2.convertScaleAbs(self.original_image, alpha=contrast, beta=0)

        #the pixel of the original image is protected and ensure pixel values are within the range of [0, 255]
        self.processed_image = np.clip(self.processed_image, 0, 255)

        # Display both the original and processed images
        self.display_images(self.original_image, self.processed_image)

    def zoom_image(self, value):
        """Resmi bir kare içerisinde yakınlaştırır veya uzaklaştırır."""
        if self.original_image is None:
            return

        # to calculate the zoom factor
        zoom_factor = value / 100  # Slider değeri [10-200], zoom_factor [0.1-2.0]

        #to determine the frame size to be taken from the original size
        h, w, _ = self.original_image.shape
        new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)

        # to get the middle point of the x-ray image the start and end points are calculated
        start_x = max((w - new_w) // 2, 0)
        start_y = max((h - new_h) // 2, 0)
        end_x = min(start_x + new_w, w)
        end_y = min(start_y + new_h, h)

        # zoom-in and  zoom-out process
        if zoom_factor >= 1.0:
            # Zoom-in: Use INTER_CUBIC for better results when enlarging
            self.processed_image = cv2.resize(self.original_image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        else:
            # Zoom-out: Use INTER_AREA for better results when shrinking
            self.processed_image = cv2.resize(self.original_image, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # If zooming out, add black borders to maintain original aspect ratio
            top = max((h - new_h) // 2, 0)
            bottom = max(h - new_h - top, 0)
            left = max((w - new_w) // 2, 0)
            right = max(w - new_w - left, 0)
            self.processed_image = cv2.copyMakeBorder(self.processed_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        # Display both the original and processed images
        self.display_images(self.original_image, self.processed_image)



    def display_images(self, original_image, processed_image):
        """OpenCV resmini QLabel üzerinde göstermek için dönüştürür ve her iki resmi gösterir."""

        # Create the side-by-side layout of the original and processed images
        original_pixmap = self.convert_to_pixmap(original_image)
        processed_pixmap = self.convert_to_pixmap(processed_image)

        # Set the images in the QLabel widgets
        self.ui.label_image.setPixmap(original_pixmap)
        self.ui.label_image.setAlignment(Qt.AlignCenter)

        self.ui.label_processed.setPixmap(processed_pixmap)
        self.ui.label_processed.setAlignment(Qt.AlignCenter)

    def convert_to_pixmap(self, image):
        """Converts the image into a QPixmap for display."""
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)


if _name_ == "_main_":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
