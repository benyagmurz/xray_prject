# This Python file uses the following encoding: utf-8
import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

from ui_form import Ui_Widget


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.original_image = None
        self.processed_image = None

        # Kontrast ayarı slider
        self.ui.slider.setMinimum(0)
        self.ui.slider.setMaximum(255)
        self.ui.slider.setValue(127)
        self.ui.slider.valueChanged.connect(self.adjust_contrast)

        # Boyutlandırma slider
        self.ui.slider.setMinimum(10)  # %10 minimum boyut
        self.ui.slider.setMaximum(200)  # %200 maksimum boyut
        self.ui.slider.setValue(100)  # Varsayılan %100 (orijinal boyut)
        self.ui.slider.valueChanged.connect(self.resize_image)

        # Blur efekti slider
        self.ui.blur_slider.setMinimum(1)  # Minimum kernel boyutu (1)
        self.ui.blur_slider.setMaximum(49)  # Maksimum kernel boyutu (49)
        self.ui.blur_slider.setValue(1)  # Varsayılan kernel boyutu (1)
        self.ui.blur_slider.setSingleStep(2)  # Sadece tek sayılar (1, 3, 5, ...)
        self.ui.blur_slider.valueChanged.connect(self.apply_blur)

        # Buton bağlantıları
        self.ui.button.clicked.connect(self.load_image)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Resim Seç",
            "",
            "Resim Dosyaları(*.png , *.jpg , *.jpeg , *.bmp)"
        )

        if file_name:
            self.original_image = cv2.imread(file_name)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.display_image(self.original_image)
            if self.original_image is not None:
                cv2.imwrite('sonuc.png', self.original_image)
                self.ui.widget2.setStyleSheet("border-image:url(sonuc.png);")
            else:
                print("Resim dosyası yüklenemedi.")

    def adjust_contrast(self, value):
        """Kontrast ayarını değiştirir."""
        if self.original_image is None:
            return
        contrast = value / 100  # Slider'daki değer [0-200], bunu [0.0-2.0] aralığına dönüştürüyoruz
        self.processed_image = cv2.convertScaleAbs(self.original_image, alpha=contrast, beta=0)
        self.display_image(self.processed_image, target="processed")

    def resize_image(self, value):
        """Resmin boyutlarını değiştirir."""
        if self.original_image is None:
            return
        scale_percent = value
        width = int(self.original_image.shape[1] * scale_percent / 100)
        height = int(self.original_image.shape[0] * scale_percent / 100)
        dimensions = (width, height)
        resized_image = cv2.resize(self.original_image, dimensions, interpolation=cv2.INTER_AREA)
        self.display_image(resized_image)

    def apply_blur(self, value):
        """Blur efekti uygular."""
        if self.original_image is None:
            return

        # Slider'ın değeri tek sayıya ayarlanır (Blur kernel boyutu için)
        if value % 2 == 0:
            value += 1

        blurred_image = cv2.GaussianBlur(self.original_image, (value, value), 0)
        self.display_image(blurred_image, target="processed")

    def display_image(self, image, target="original"):
        """OpenCV resmini QLabel üzerinde göstermek için dönüştürür."""
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        if target == "original":
            self.ui.label_image.setPixmap(pixmap)
            self.ui.label_image.setAlignment(Qt.AlignCenter)
        elif target == "processed":
            self.ui.label_processed.setPixmap(pixmap)
            self.ui.label_processed.setAlignment(Qt.AlignCenter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
