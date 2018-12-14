import cv2
import numpy as np

image = cv2.imread("arbre.jpg")

image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


edges = cv2.Canny(image_gray,100,150)

ret, thresh = cv2.threshold(image_gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

kernel = np.ones((3,3),np.uint8)
opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
#cv2.imshow("image", edges)
cv2.imshow("image", opening)


cv2.waitKey(0)

