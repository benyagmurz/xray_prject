# Bu kodla istediğimiz xray fotograflarını kod kullanarak çağırdık.
#Farklı fotograflar kullanıp gözlemledik.

import cv2
import numpy as np 

img=cv2.imread('hand1.jpeg')
cv2.imshow('Origonal image' ,img)
height, width = img.shape[:2]
print(f"size of the image:{width}x{height}")
pixel=img[100,100]
print(f"Pixel value:{pixel}")
cv2.waitKey(0)
cv2.destroyAllWindows()

# blur yapma denendi gaussian ve median blur çıkması ve orijinal fotografın da yanında çıması sağandı
# imwrite kodu ile açtığımız ve blurlaştığmız xray fotograflarını kaydetmeyi sağladı
