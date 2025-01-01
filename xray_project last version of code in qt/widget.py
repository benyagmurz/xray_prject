import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from ui_form import Ui_Widget  #Import the interface class created with PySide6.


class Widget(QWidget):
    def _init_(self, parent=None):
        super()._init_(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        #Variables for display and selection operations
        self.original_image = None
        self.display_image_data = None

        # Slider and button settings
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
        self.ui.slider_zoom.setMinimum(10)#minimum zoom(10%)
        self.ui.slider_zoom.setMaximum(200)#◙maximum zoom (200%)
        self.ui.slider_zoom.setValue(100)
        #Default value(original size)
        self.ui.slider_zoom.valueChanged.connect(self.zoom_image)

        #Blur slider settings
        #Values between 1 and 20 provide a visually adequate level of blur for most users.
        #This range of values offers reasonable flexibility without creating unnecessary complexity and helps balance visual effects from both an aesthetic and functional perspective.
        #This is generally a sufficient and practical choice for most applications.
        self.ui.slider_blur.setMinimum(1)
        self.ui.slider_blur.setMaximum(20)
        self.ui.slider_blur.setValue(1)
        self.ui.slider_blur.valueChanged.connect(self.blur_image)

        #Image upload button
        self.ui.button.clicked.connect(self.load_image)

        #Fracture detection button
        self.ui.button_fracture.clicked.connect(self.detect_fractures)

        #ROI selection button
        self.ui.button_roi.clicked.connect(self.select_roi)
    #Loads an image file and displays it on the screen
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            try:
                self.original_image = cv2.imread(file_name)
                if self.original_image is None:
                    raise ValueError("Geçersiz resim dosyası.")
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.display_image_data = self.original_image.copy()
                self.display_image(self.original_image, is_original=True)
                self.display_image(self.display_image_data, is_original=False)
            except Exception as e:
                QMessageBox.warning(self, "Yükleme Hatası", f"Resim yüklenemedi: {e}")

    #Adjusts the contrast and displays the updated image.
    def adjust_contrast(self, value):
        if self.original_image is None:
            return
        contrast = value / 100
        self.display_image_data = cv2.convertScaleAbs(self.original_image, alpha=contrast, beta=0)
        self.display_image(self.display_image_data, is_original=False)

    #Resizes the entire image by the specified zoom factor.
    def zoom_image(self, value):
        if self.display_image_data is None:
            return
        zoom_factor = value / 100
        h, w, _ = self.display_image_data.shape
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
        resized_image = cv2.resize(self.display_image_data, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        self.display_image(resized_image, is_original=False)
    #This function is written to apply a Gaussian Blur. The purpose of the function is to blur the image using the given value (taken from the slider)
    def blur_image(self, value):
        if self.original_image is None:
            return
        if value % 2 == 0:
            value += 1
            #The Gaussian blur function must use an odd number as the kernel size.
            # Therefore, if the value received from the slider is an even number, this value is increased by one. #For example, if value = 4, this value is changed to 5. This ensures that the kernel size is an odd number.

        self.display_image_data = cv2.GaussianBlur(self.original_image, (value, value), 0)
        #0: This parameter is the standard deviation (sigma) value.
        #Sigma indicates the degree of spread of the Gaussian function. When 0 is used, OpenCV automatically calculates an appropriate sigma value.
        self.display_image(self.display_image_data, is_original=False)

    #It detects fractures and draws contours on the image.
    def detect_fractures(self):
        if self.display_image_data is None:
            return
        gray_image = cv2.cvtColor(self.display_image_data, cv2.COLOR_RGB2GRAY) #The color image is converted to grayscale.
        #This is a common step for operations such as edge detection because the grayscale image can be processed more quickly and efficiently.
        edges = cv2.Canny(gray_image, threshold1=50, threshold2=150) #Using the Canny algorithm, edges in a grayscale image are detected. #This is a technique for finding sharp transitions or boundaries in an image.
        #threshold1=50 and threshold2=150: These values ​​are the lower and upper threshold values ​​for edge detection.
        #These thresholds determine how distinct the edges should be. By changing the threshold values, fewer or more edges can be detected.
        kernel = np.ones((3, 3), np.uint8)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1) #The dilation process is done to expand the edges a little more. This process is applied on the edges and is used to make the edges more distinct.
        #Kernel: np.ones((3, 3), np.uint8) creates a 3x3 matrix. This kernel helps expand the edges during the dilation process.
        #iterations=1: This parameter determines how many times the dilation process will be applied. In this case, the dilation is done only once.
        contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #cv2.RETR_EXTERNAL: This parameter takes only the outer contours. It ignores the nested contours.
        #cv2.CHAIN_APPROX_SIMPLE: This parameter is used to represent contours in a simpler way. That is, it keeps only the important points without losing too much detail about the shape of the contour.
        fracture_image = self.display_image_data.copy()
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                cv2.drawContours(fracture_image, [contour], -1, (255, 0, 0), 3)#cv2.contourArea(contour) > 100:: If the area of ​​the contour is larger than 100 pixels, this contour is considered a fracture. #This threshold ensures that the fracture is large enough to prevent small, unimportant shapes from being detected.
                #cv2.drawContours(fracture_image, [contour], -1, (255, 0, 0), 3): This function draws the contours where fractures are located on the image.
                #-1: Used to draw all contours.
                #(255, 0, 0): Drawn contours are red (in BGR format).
                #3: The thickness of the contours is 3 pixels, which makes the fractures more visible.
        self.display_image(fracture_image, is_original=False)
    #Selects ROI.
    def select_roi(self):
        """ROI seçimi yapar."""
        if self.original_image is None:
            QMessageBox.warning(self, "Uyarı", "Önce bir görüntü yükleyin.")
            return

        #ROI selection is done with OpenCV window.
        temp_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2BGR) #OpenCV uses the BGR (Blue, Green, Red) color format, but other libraries like PyQt use the RGB (Red, Green, Blue) format. #Therefore, self.original_image (probably in RGB format) is converted to BGR format.
        #This conversion is necessary for OpenCV to render the image correctly.
        roi = cv2.selectROI("ROI Seçimi", temp_image, showCrosshair=True, fromCenter=False) # cv2.selectROI function allows the user to select a rectangular area on the image.
        cv2.destroyWindow("ROI Seçimi")

        #ROI area is checked.
        if roi == (0, 0, 0, 0): # The roi variable is in the format of a tuple (x, y, width, height) containing four numbers selected by the user.
            QMessageBox.information(self, "Bilgi", "Geçerli bir alan seçilmedi.")
            return

        #Cropped area
        x, y, w, h = roi
        cropped_image = self.original_image[int(y):int(y + h), int(x):int(x + w)]

        self.display_image_data = cropped_image
        self.display_image(cropped_image, is_original=False) #The coordinates of the selected ROI region are extracted from the roi tuple.
        #This slicing is done with the numpy slicing method. #Here (int(y):int(y + h), int(x):int(x + w)) expression selects the ROI from y to y+h on the y-axis and from x to x+w on the x-axis.
    #Displays the given image on the QLabel.
    def display_image(self, image, is_original):
        image = np.ascontiguousarray(image)
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        if is_original:
            self.ui.label_image_original.setPixmap(pixmap)
            self.ui.label_image_original.setAlignment(Qt.AlignCenter)
        else:
            self.ui.label_image_processed.setPixmap(pixmap)
            self.ui.label_image_processed.setAlignment(Qt.AlignCenter)


if __name__ == "_main_":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
