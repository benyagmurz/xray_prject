# This Python file uses the following encoding: utf-8
import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget,QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt




# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget




class Widget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self. original_image = None
        self.processed_image = None

        self.ui.slider.setMinimum(0)
        self.ui.slider.setMaximum(255)
        self.ui.slider.setValue(127)

        self.ui.button.clicked.connect(self.load_image)
        self.ui.slider.valueChanged.connect(self.adjust_contrast)

    def load_image(self):
        file_name,_=QFileDialog.getOpenFileName(
            self,
            "Resim Seç",
            "",
            "Resim Dosyaları(*.png , *.jpg , *.jpeg , *.bmp  )"
        )

        if file_name:
            self.original_image=cv2.imread(file_name)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.display_image(self.original_image)
            if self.original_image is not None:
                cv2.imwrite('sonuc.png',self.original_image)
                self.ui.widget2.setStyleSheet("border-image:url(sonuc.png);")
            else:
                print("Resim dosyası yüklenemedi.")

    def adjust_contrast(self, value):
        """Kontrast ayarını değiştirir."""
        if self.original_image is None:
            return
        # Kontrastı ayarla
        contrast = value / 100  # Slider'daki değer [0-200], bunu [0.0-2.0] aralığına dönüştürüyoruz
        self.processed_image = cv2.convertScaleAbs(self.original_image, alpha=contrast, beta=0)

        # İşlenmiş resmi QLabel'de görüntüle
        self.display_image(self.processed_image ,  target="processed")


    def display_image(self, image  ):
        """OpenCV resmini QLabel üzerinde göstermek için dönüştürür."""
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.ui.label_image.setPixmap(pixmap)
        self.ui.label_image.setAlignment(Qt.AlignCenter)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
