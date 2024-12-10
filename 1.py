# Bu kodla istediğimiz xray fotograflarını kod kullanarak çağırdık.
#Farklı fotograflar kullanıp gözlemledik.

import cv2

im=cv2.imread('hand1.jpeg')
gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
blurred=cv2.GaussianBlur(gray, (15,15),0)
median=cv2.medianBlur(gray, 15)
cv2.imwrite('original_image.jpg', im)       
cv2.imwrite('gaussian_blur.jpg', blurred)
cv2.imwrite('median_blur.jpg', median)  
cv2.imshow('original image',im)
cv2.imshow('Gaussian Blur',blurred)
cv2.imshow('Median Blur',median)
cv2.waitKey(0)
cv2.destroyAllWindows()

# blur yapma denendi gaussian ve median blur çıkması ve orijinal fotografın da yanında çıması sağandı
