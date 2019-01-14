import cv2
import numpy as np



def __auto_canny(image, sigma=0.33): #By Adrian (www.pyimagesearch.com)
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged

def __open_resize_image (name):
    image = cv2.imread(name)
    height, width, channel = image.shape
    if (width > 600 or height > 600):
        image = cv2.resize(image, (int(width / 3), int(height / 3)), interpolation=cv2.INTER_CUBIC)
    return image

def __ROI_selector(image):

    if(cv2.__version__[0] == "3"): #OpenCV 3.XXX
        ROI = cv2.selectROI(image)
        if ROI != (0, 0, 0, 0):
            image_roi = image[int(ROI[1]):int(ROI[1] + ROI[3]), int(ROI[0]):int(ROI[0] + ROI[2])]
            coordinates = [int(ROI[1]), int(ROI[0])]
        else:
            image_roi = image
            coordinates = [0, 0]
    elif(cv2.__version__[0] == "2"): #OpenCV 2.XXX
        image_roi = image
        coordinates = [0, 0]


    return image_roi, coordinates


def FondUniSegmentation(image_path):
    image = __open_resize_image(image_path)
    image, top_left_coord = __ROI_selector(image)
    height, width, channel = image.shape
    #Color treatement
    for i in range(0, height):
        for j in range(0, width):
            green = image[i, j, 1]
            blue = image[i, j, 0]
            red = image[i, j, 2]
            if (green <= blue + 5 or green <= red + 5):
                image[i, j, 0] = 0
                image[i, j, 1] = 0
                image[i, j, 2] = 0
    #Smoothing the image
    image = cv2.GaussianBlur(image, (3, 3), 0)

    image_Lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    #Morphological operation
    kernel = np.ones((5, 5), np.uint8)
    closing = cv2.morphologyEx(image_Lab, cv2.MORPH_CLOSE, kernel)

    img_seg = __auto_canny(closing)

    return img_seg