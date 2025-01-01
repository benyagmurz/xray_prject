import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLabel
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPainter
from PySide6.QtCore import Qt, QRect
from ui_form import Ui_Widget  #Import the interface class created with PySide6.


class Widget(QWidget):
    def _init_(self, parent=None):
        super()._init_(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        #Variables for display and selection operations
        self.original_image = None
        self.display_image_data = None
        self.selected_region = None

        #Slider and button settings
        #Minimum Value (0): Indicates the situation where the contrast is completely off. In this case, a gray image is formed with all pixel values ​​in the image close to each other.
        #Maximum Value (200): Represents the situation where the contrast is at its highest level. This makes the image sharper and more distinct. The difference between pixel values ​​is at its highest level.
        #Default Value (100): Indicates the original, or "neutral", state of the contrast. This represents the state where no contrast changes are made to the image. The values ​​are normalized and a ratio is calculated on the contrast.
        self.ui.slider_contrast.setMinimum(0)
        self.ui.slider_contrast.setMaximum(200)
        self.ui.slider_contrast.setValue(100)
        self.ui.slider_contrast.valueChanged.connect(self.adjust_contrast)
        
        #The default value of 100 will initially make the image appear at its original size.
        #The user can increase the zoom (for example, 150-200) to enlarge the image or decrease it (for example, 10-99).
        #The range between 10 and 200 provides a scale that meaningfully represents the zoom setting.
        #10% reduction and 200% enlargement are generally sufficient ranges for most applications.
        #Working within this range provides easy control over the dimensions of the image. In general, the logic is 100 = original size, 50 = 50% reduction, 200 = 200% enlargement.
        self.ui.slider_zoom.setMinimum(10) #Minimum zoom (10%)
        self.ui.slider_zoom.setMaximum(200) #Maximum zoom(200%)
        self.ui.slider_zoom.setValue(100) #Default value (original size)
        self.ui.slider_zoom.valueChanged.connect(self.zoom_image)
        
    
        #10 is selected as the minimum because it allows the area to be reduced without completely disappearing.
        #A smaller minimum value may render the selected area meaningless.
        #300 is selected as the maximum because 300% magnification is usually sufficient for most scenarios. #A larger value may cause the image or area to become overly enlarged and lose detail.
        #Since the purpose of this slider is to enlarge/reduce an area, the range 10-300 allows the selected area to be manipulated proportionally.
        #This range is selected to provide users with greater zoom control.
        #A range between 10% and 300% is usually sufficient for reviewing or presenting a selected area.
        self.ui.slider_region_zoom.setMinimum(10)
        self.ui.slider_region_zoom.setMaximum(300)
        self.ui.slider_region_zoom.setValue(100)
        self.ui.slider_region_zoom.valueChanged.connect(self.zoom_selected_region)

        self.ui.button.clicked.connect(self.load_image)
        self.ui.button_fracture.clicked.connect(self.detect_fractures)

        #Added for selecting an area on an image with the mouse.
        self.ui.label_image.mousePressEvent = self.get_region_start
        self.ui.label_image.mouseMoveEvent = self.update_region_selection
        self.ui.label_image.mouseReleaseEvent = self.get_region_end

        #Selection and drawing variables
        self.region_start = None
        self.region_end = None
        self.current_rect = None
    #Loads an image file and displays it on the screen
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.original_image = cv2.imread(file_name)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.display_image_data = self.original_image.copy()
            self.display_image(self.original_image)
        else:
            print("Resim dosyası seçilmedi veya yüklenemedi.")
            
    #Adjusts the contrast and displays the updated image.
    def adjust_contrast(self, value):
        
        if self.original_image is None:
            return
        contrast = value / 100
        self.display_image_data = cv2.convertScaleAbs(self.original_image, alpha=contrast, beta=0)
        self.display_image(self.display_image_data)
        
    #Resizes the entire image by the specified zoom factor.
    def zoom_image(self, value):
        
        if self.original_image is None:
            return
        zoom_factor = value / 100
        h, w, _ = self.display_image_data.shape
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
        resized_image = cv2.resize(self.display_image_data, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        self.display_image(resized_image)
        
    #Zooms in on the selected area.
    def zoom_selected_region(self, value):
        
        if self.original_image is None or self.selected_region is None:
            return
        x1, y1, x2, y2 = self.selected_region #Holds the coordinates (x1, y1, x2, y2) of the selected region. This represents the start (x1, y1) and end (x2, y2) points of the selection.
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        h, w, _ = self.display_image_data.shape #The coordinates (x1, y1, x2, y2) are corrected to be within the boundaries of the image. 
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1: #If the width or height of the selected area is zero or negative (in the case of a reverse selection), the process is stopped.
            print("Geçersiz seçim bölgesi.")
            return

        region = self.display_image_data[y1:y2, x1:x2]
        zoom_factor = value / 100
        new_h, new_w = int(region.shape[0] * zoom_factor), int(region.shape[1] * zoom_factor)
        zoomed_region = cv2.resize(region, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        self.display_image(zoomed_region)
        
    #It detects fractures and draws contours on the image.
    def detect_fractures(self):
        if self.display_image_data is None:
            return
        gray_image = cv2.cvtColor(self.display_image_data, cv2.COLOR_RGB2GRAY) #The image is converted from RGB (color) format to grayscale format.
        #Edge detection and contour analysis generally perform better on grayscale images.
        #Grayscale format is used because color information is not important in this step.

        edges = cv2.Canny(gray_image, 50, 150)#This code highlights sudden intensity changes (edges) in a grayscale image:
            #White (255),
            #Black (0) marks the background.
            #Parameters (50, 150) provide a balance between sensitivity and accuracy in edge detection:
            #High threshold: Accurately identifies strong edges.
            #Low threshold: Evaluates weak edges connected to strong edges.
            #In this way, both important edges in the image are detected and false positives due to noise are reduced.

        kernel = np.ones((3, 3), np.uint8) 
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)
        #The edge image is thickened by a dilation operation:
        #The kernel (a 3x3 matrix) is used to dilate the edges.
        #Iterations=1 specifies to dilate once.
        #By dilating thin edges, it makes contour detection more consistent.
        #Small gaps are closed and edge joints become clearer.
        
        contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #cv2.RETR_EXTERNAL: Detects only external (outermost) contours.
        #cv2.CHAIN_APPROX_SIMPLE: Compresses contour points and represents them with less data.

        fracture_image = self.display_image_data.copy()
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                cv2.drawContours(fracture_image, [contour], -1, (255, 0, 0), 3)
        self.display_image(fracture_image) #Filtering:The cv2.contourArea(contour) function calculates the area of the contour.
        #Contours with an area smaller than 100 pixels are ignored.
        #Very small contours are usually noise or unimportant details.
        #Drawing Contours:The contour is drawn on the image using the cv2.drawContours function:
        #fracture_image: The image to draw.
        #[contour]: The contour to draw.
        #-1: Draw all points of the contour.
        #(255, 0, 0): Contour color (blue, in BGR format).
        #3: Line thickness.

    #Displays the given image on the QLabel.
    def display_image(self, image):
        image = np.ascontiguousarray(image)
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.ui.label_image.setPixmap(pixmap)
        self.ui.label_image.setAlignment(Qt.AlignCenter)
        
    #The selection determines the starting point.
    def get_region_start(self, event: QMouseEvent):
        if self.display_image_data is not None:
            self.region_start = event.position().toPoint()
            self.region_end = None
            self.current_rect = None
            
    #Draws a rectangle during selection.
    def update_region_selection(self, event: QMouseEvent):
        if self.region_start is not None and self.display_image_data is not None:
            self.region_end = event.position().toPoint()
            self.current_rect = QRect(self.region_start, self.region_end)
            self.update()
            
    #Determines the selection end point.
    def get_region_end(self, event: QMouseEvent):
        if self.region_start is None or self.display_image_data is None:
            return
        self.region_end = event.position().toPoint()
        x1, y1 = self.region_start.x(), self.region_start.y()
        x2, y2 = self.region_end.x(), self.region_end.y()
        self.selected_region = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        self.current_rect = None
        self.update()
        
    #Draws the rectangle drawn during selection to the screen.
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.current_rect is not None:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.drawRect(self.current_rect)
            painter.end()


if __name__ == "_main_":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
