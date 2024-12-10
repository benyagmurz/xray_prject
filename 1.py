# Bu kodla istediğimiz xray fotograflarını kod kullanarak çağırdık.
#Farklı fotograflar kullanıp gözlemledik.

import cv2

im=cv2.imread('brain.jpg')
cv2.imshow('original image',im)
cv2.waitKey(0)
cv2.destroyAllWindows()
