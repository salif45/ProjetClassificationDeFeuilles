import cv2
import numpy as np
from matplotlib import pyplot as plt
import glob as glob


####### Gegmentatipon
names = glob.glob("base_donnee_feuille/FondUni/*")
# names = glob.glob("base_donnee_feuille/All/*")

img = []
img_seg = []
for name in names:
    image = cv2.imread(name)
    height, width, channel = image.shape
    while (width > 600 or height > 600):
        image = cv2.resize(image, (int(width / 3), int(height / 3)), interpolation=cv2.INTER_CUBIC)
        height, width, channel = image.shape
    img.append(image)

    ROI = cv2.selectROI(image)

    if ROI != (0, 0, 0, 0):
        image = image[int(ROI[1]):int(ROI[1] + ROI[3]), int(ROI[0]):int(ROI[0] + ROI[2])]
    height, width, channel = image.shape

    # ### Fond Naturel
    # color_mean_row = np.average(image,axis=0)
    # color_mean = np.average(color_mean_row,axis=0)
    #
    # print(color_mean)
    # color = color_mean.argmax()
    # print(color)

    for i in range(0, height):
        for j in range(0, width):
            green = image[i, j, 1]
            blue = image[i, j, 0]
            red = image[i, j, 2]
            if (green <= blue + 5 or green <= red + 5):
                image[i, j, 0] = 0
                image[i, j, 1] = 0
                image[i, j, 2] = 0

    image = cv2.medianBlur(image,5)

    cv2.imshow('image',cv2.Canny(image,100,150))

    image_HSV = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    H = image_HSV[:, :, 0]
    S = image_HSV[:, :, 1]
    V = image_HSV[:, :, 2]
    cv2.imshow('imageHSV',cv2.Canny(image_HSV, 100, 150))
    cv2.imshow('H',cv2.Canny(H, 100, 150))
    # cv2.imshow('S',cv2.Canny(S, 100, 150))
    # cv2.imshow('V',cv2.Canny(V, 100, 150))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #########  Test couleur verte  ############



    ######################################

