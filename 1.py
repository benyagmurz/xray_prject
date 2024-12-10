# Bu kodla istediğimiz xray fotograflarını kod kullanarak çağırdık.
#Farklı fotograflar kullanıp gözlemledik.

import cv2
import numpy as np 

img=cv2.imread('hand1.jpeg')
cv2.imshow('Origonal image' ,img)
edges=cv2.Canny(img, 100,200)
cv2.imshow('Edge Detection', edges)

cv2.waitKey(0)
cv2.destroyAllWindows()

# blur yapma denendi gaussian ve median blur çıkması ve orijinal fotografın da yanında çıması sağandı
# imwrite kodu ile açtığımız ve blurlaştığmız xray fotograflarını kaydetmeyi sağladı
