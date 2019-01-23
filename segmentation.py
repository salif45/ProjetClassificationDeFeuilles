import cv2
import numpy as np
import copy



def build_filters():
    filters = []
    ksize = 1
    for theta in np.arange(0, np.pi, np.pi/8):
        if theta == 0 or theta == np.pi/2 or theta == np.pi:
            pass
        else:
            kern = cv2.getGaborKernel((ksize, ksize), 3.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
            kern /= 1.5 * kern.sum()
            filters.append(kern)
    return filters


def process(img, filters):
    accum = np.zeros_like(img)
    for kern in filters:
        fimg = cv2.filter2D(img, cv2.CV_8U, kern)
        np.maximum(accum, fimg, accum)
    return accum


def ImgToSegmentate(image_path, LeftCoordinate, height_mask, width_mask, borders):
    image = cv2.imread(image_path)
    height, width, _ = image.shape


    mask = np.zeros(image.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (0, 0, width - 1, height - 1)
    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    image = image * mask2[:, :, np.newaxis]
    # newmask is the mask image I manually labelled
    newmask = np.zeros(image.shape[:2], np.uint8)
    newmask.fill(125)

    cv2.rectangle(newmask, (LeftCoordinate[0], LeftCoordinate[1]),
                  (LeftCoordinate[0] + height_mask, LeftCoordinate[1] + width_mask), (255, 255, 255), -1)
    # kernel = np.ones((5, 5), np.uint8)
    for coord in borders:
        newmask[coord[1], coord[0]] = 0

    # cv2.imshow('New mask', newmask)
    # wherever it is marked white (sure foreground), ce mask=1
    # wherever it is marked black (sure background), change mask=0
    mask[newmask == 0] = 0
    mask[newmask == 255] = 1
    mask, bgdModel, fgdModel = cv2.grabCut(image, mask, None, bgdModel, fgdModel, 5,
                                           cv2.GC_INIT_WITH_MASK | cv2.GC_INIT_WITH_RECT)
    mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    image = image * mask[:, :, np.newaxis]
    # Color treatement
    for i in range(0, height):
        for j in range(0, width):
            green = image[i, j, 1]
            blue = image[i, j, 0]
            red = image[i, j, 2]
            if (blue >= 230 and green >= 230 and red >= 230):
                image[i, j, 0] = 0
                image[i, j, 1] = 0
                image[i, j, 2] = 0


    image_contour = copy.deepcopy(image)
    filters = build_filters()
    res1 = process(image_contour, filters)
    # cv2.imshow("Gabor", res1)
    image_gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Gabor_GRAy", image_gray)
    ret, thresh = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contourUtile = max(contours, key=len)

    for i in range(len(contourUtile)):
        #cv2.circle(image_contour, tuple(contourUtile[i][0]), 2, [255, 0, 255], 3)
        cv2.line(image_contour, tuple(contourUtile[i-1][0]), tuple(contourUtile[i][0]), [255, 255, 0], 2)
    cv2.imshow("contour", image_contour)
    return image, thresh