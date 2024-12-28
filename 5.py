import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLabel
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPainter
from PySide6.QtCore import Qt, QRect
from ui_form import Ui_Widget  # PySide6 ile oluşturulmuş arayüz sınıfını içe aktarıyoruz


class Widget(QWidget):
    def _init_(self, parent=None):
        super()._init_(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # Görüntü ve seçim işlemleri için değişkenler
        self.original_image = None
        self.display_image_data = None
        self.selected_region = None

        # Slider ve buton ayarları
        self.ui.slider_contrast.setMinimum(0)
        self.ui.slider_contrast.setMaximum(200)
        self.ui.slider_contrast.setValue(100)
        self.ui.slider_contrast.valueChanged.connect(self.adjust_contrast)

        self.ui.slider_zoom.setMinimum(10)
        self.ui.slider_zoom.setMaximum(200)
        self.ui.slider_zoom.setValue(100)
        self.ui.slider_zoom.valueChanged.connect(self.zoom_image)

        self.ui.slider_region_zoom.setMinimum(10)
        self.ui.slider_region_zoom.setMaximum(300)
        self.ui.slider_region_zoom.setValue(100)
        self.ui.slider_region_zoom.valueChanged.connect(self.zoom_selected_region)

        self.ui.button.clicked.connect(self.load_image)
        self.ui.button_fracture.clicked.connect(self.detect_fractures)

        # QLabel üzerinde fare olayları
        self.ui.label_image.mousePressEvent = self.get_region_start
        self.ui.label_image.mouseMoveEvent = self.update_region_selection
        self.ui.label_image.mouseReleaseEvent = self.get_region_end

        # Seçim ve çizim değişkenleri
        self.region_start = None
        self.region_end = None
        self.current_rect = None

    def load_image(self):
        """Bir resim dosyasını yükler ve ekrana gösterir."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.original_image = cv2.imread(file_name)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.display_image_data = self.original_image.copy()
            self.display_image(self.original_image)
        else:
            print("Resim dosyası seçilmedi veya yüklenemedi.")

    def adjust_contrast(self, value):
        """Kontrast ayarını yapar ve güncellenmiş görüntüyü gösterir."""
        if self.original_image is None:
            return
        contrast = value / 100
        self.display_image_data = cv2.convertScaleAbs(self.original_image, alpha=contrast, beta=0)
        self.display_image(self.display_image_data)

    def zoom_image(self, value):
        """Tüm görüntüyü belirtilen zoom faktörü ile yeniden boyutlandırır."""
        if self.original_image is None:
            return
        zoom_factor = value / 100
        h, w, _ = self.display_image_data.shape
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
        resized_image = cv2.resize(self.display_image_data, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        self.display_image(resized_image)

    def zoom_selected_region(self, value):
        """Seçilen bölgeyi zoom yapar."""
        if self.original_image is None or self.selected_region is None:
            return
        x1, y1, x2, y2 = self.selected_region
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        h, w, _ = self.display_image_data.shape
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            print("Geçersiz seçim bölgesi.")
            return

        region = self.display_image_data[y1:y2, x1:x2]
        zoom_factor = value / 100
        new_h, new_w = int(region.shape[0] * zoom_factor), int(region.shape[1] * zoom_factor)
        zoomed_region = cv2.resize(region, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        self.display_image(zoomed_region)

    def detect_fractures(self):
        """Kırık tespiti yapar ve görüntüye konturlar çizer."""
        if self.display_image_data is None:
            return
        gray_image = cv2.cvtColor(self.display_image_data, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray_image, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)
        contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        fracture_image = self.display_image_data.copy()
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                cv2.drawContours(fracture_image, [contour], -1, (255, 0, 0), 3)
        self.display_image(fracture_image)

    def display_image(self, image):
        """Verilen görüntüyü QLabel üzerinde gösterir."""
        image = np.ascontiguousarray(image)
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.ui.label_image.setPixmap(pixmap)
        self.ui.label_image.setAlignment(Qt.AlignCenter)

    def get_region_start(self, event: QMouseEvent):
        """Seçim başlangıç noktasını belirler."""
        if self.display_image_data is not None:
            self.region_start = event.position().toPoint()
            self.region_end = None
            self.current_rect = None

    def update_region_selection(self, event: QMouseEvent):
        """Seçim sırasında dikdörtgeni çizer."""
        if self.region_start is not None and self.display_image_data is not None:
            self.region_end = event.position().toPoint()
            self.current_rect = QRect(self.region_start, self.region_end)
            self.update()

    def get_region_end(self, event: QMouseEvent):
        """Seçim bitiş noktasını belirler."""
        if self.region_start is None or self.display_image_data is None:
            return
        self.region_end = event.position().toPoint()
        x1, y1 = self.region_start.x(), self.region_start.y()
        x2, y2 = self.region_end.x(), self.region_end.y()
        self.selected_region = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        self.current_rect = None
        self.update()

    def paintEvent(self, event):
        """Seçim sırasında çizilen dikdörtgeni ekrana çizer."""
        super().paintEvent(event)
        if self.current_rect is not None:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.drawRect(self.current_rect)
            painter.end()


if _name_ == "_main_":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
