# import cv2
# import numpy as np
# from matplotlib import pyplot as plt
# image = cv2.imread("/home/mathieu/ProjetFeuille/ProjetClassificationDeFeuilles/base_donnee_feuille/chene/cheneAvecFond1.jpeg")
#
#
# # image en gris
# image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
# image_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# image_YUV = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
# edges = cv2.Canny(image_gray,100,150)
# edges1 = cv2.Canny(image,100,150)
# edges2 = cv2.Canny(image_HSV,100,150)
# edges3 = cv2.Canny(image_YUV,100,150)
#
#
# cv2.imshow('HSV', image_HSV)
# cv2.imshow('YUV', image_YUV)
# cv2.imshow('BGR', image)
# cv2.waitKey(0)
# plt.subplot(141), plt.imshow(edges, 'gray'), plt.title('gray')
# plt.subplot(142), plt.imshow(edges1, 'gray'), plt.title('BGR')
# plt.subplot(143), plt.imshow(edges2, 'gray'), plt.title('HSV')
# plt.subplot(144), plt.imshow(edges3, 'gray'), plt.title('YUV')
# plt.show()



import cv2
import numpy as np
from matplotlib import pyplot as plt


# img = cv2.imread('/home/mathieu/ProjetFeuille/ProjetClassificationDeFeuilles/base_donnee_feuille/bouleau/bouleau2.jpg')
# img = cv2.imread('/home/mathieu/ProjetFeuille/ProjetClassificationDeFeuilles/base_donnee_feuille/baobab/baobab6.jpg')
img = cv2.imread('/home/mathieu/ProjetFeuille/ProjetClassificationDeFeuilles/base_donnee_feuille/chene/cheneAvecFond1.jpeg')
# img = cv2.imread('/home/mathieu/ProjetFeuille/ProjetClassificationDeFeuilles/base_donnee_feuille/hetre/hetre1.jpg')
# img = cv2.imread('/home/mathieu/ProjetFeuille/ProjetClassificationDeFeuilles/base_donnee_feuille/margousier/margousier2.jpg')
# img = cv2.imread('/home/mathieu/ProjetFeuille/ProjetClassificationDeFeuilles/base_donnee_feuille/platane/platane5.jpg')




#Convert to HSV space
HSV_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hue = HSV_img[:, :, 0]
hue1 = HSV_img[:, :, 1]
hue2 = HSV_img[:, :, 2]


cany = cv2.Canny(hue1,100,150)
cv2.imshow('title', cany)


kernel = np.ones((2,2),np.uint8)
opening = cv2.morphologyEx(hue1,cv2.MORPH_CLOSE,kernel, iterations = 5)
opening = cv2.morphologyEx(opening,cv2.MORPH_OPEN,kernel, iterations = 5)
opening = cv2.medianBlur(opening,5)
cv2.imshow('opening', opening)

cany2 = cv2.Canny(opening,100,150)
cv2.imshow('title2', cany2)
cv2.waitKey(0)


# titles = ['HUE0', 'HUE1', 'Hue2', 'original']
# images = [hue, hue1, hue2, HSV_img]
# for i in range(4):
#     plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
#     plt.title(titles[i])
#     plt.xticks([]),plt.yticks([])
#
#
# plt.figure()
#
# YUV_img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
# Y = YUV_img[:, :, 0]
# U = YUV_img[:, :, 1]
# V = YUV_img[:, :, 2]
# titles = ['Y', 'U', 'V', 'Origin']
# images = [Y, U, V, YUV_img]
# for i in range(4):
#     plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
#     plt.title(titles[i])
#     plt.xticks([]),plt.yticks([])
#
# plt.show()

image_gray = cv2.cvtColor(HSV_img, cv2.COLOR_BGR2GRAY)
cv2.imshow('gray',cv2.Canny(image_gray,100,150))
image_gray_n = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow('gray_n',cv2.Canny(image_gray_n,100,150))


cv2.waitKey()
# plt.subplot(331), plt.imshow(edges, 'gray'), plt.title('Canny')
# plt.subplot(331), plt.imshow(edges, 'gray'), plt.title('Canny')
# plt.subplot(331), plt.imshow(edges, 'gray'), plt.title('Canny')
#
# plt.subplot(331), plt.imshow(edges, 'gray'), plt.title('Canny')
# plt.subplot(331), plt.imshow(edges, 'gray'), plt.title('Canny')
# plt.subplot(331), plt.imshow(edges, 'gray'), plt.title('Canny')


#
# laplacian = cv2.Laplacian(image_gray,cv2.CV_64F)
#
# plt.subplot(252), plt.imshow(laplacian, 'binary'), plt.title('Laplacien')
#
# ret, thresh = cv2.threshold(image_gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
#
# plt.subplot(253), plt.imshow(thresh, 'gray'), plt.title('thresh')
#
# edges_th = cv2.Canny(thresh,100,150)
#
# plt.subplot(254), plt.imshow(edges_th, 'gray'), plt.title('canny thresh')
#
# laplacian_th = cv2.Laplacian(thresh,cv2.CV_64F)
#
# plt.subplot(255), plt.imshow(laplacian_th, 'binary'), plt.title('lap thresh')
#
# [l,L,channel] = np.shape(image)
#
# #########  Test couleur verte  ############
#
# for i in range(0,l):
#     for j in range(0,L):
#         green = image[i,j,1]
#         blue = image[i,j,0]
#         red = image[i,j,2]
#         if ( green <= blue + 5 or green <= red + 5  ):
#
#             image_gray[i, j] = 0
#
# ######################################
#
# # kernel = np.ones((3,3),np.uint8)
# # opening = cv2.morphologyEx(image_gray,cv2.MORPH_OPEN,kernel, iterations = 2)
#
# edges = cv2.Canny(image_gray,100,150)
#
# plt.subplot(256), plt.imshow(edges, 'gray'), plt.title('canny V')
#
# laplacian = cv2.Laplacian(image_gray,cv2.CV_64F)
#
# plt.subplot(257), plt.imshow(laplacian, 'binary'), plt.title('laplacian V')
#
#
# ret, thresh = cv2.threshold(image_gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
#
# plt.subplot(258), plt.imshow(thresh, 'gray'), plt.title('thresh V')
#
# edges_th = cv2.Canny(thresh,100,150)
#
# plt.subplot(259), plt.imshow(edges_th, 'gray'), plt.title('canny thresh V')
#
# laplacian_th = cv2.Laplacian(thresh,cv2.CV_64F)
#
# plt.subplot(2,5,10), plt.imshow(laplacian_th, 'binary'), plt.title('lap thresh V')
#
# plt.show()
# # canny = cv2.Canny(thresh2,100,150)
# #
# # cv2.imshow('Canny', canny)
# # cv2.waitKey(0)
#
# # test = np.zeros([l,L])
# # for i in range(0,l):
# #     for j in range(0,L):
# #         test [i,j] = canny[i,j] and edges[i,j]
#
#
# # cv2.imshow('test', test)
# # cv2.waitKey(0)
#
# # cv2.imshow('Norm', opening)
# # cv2.waitKey(0)
#
# # cv2.imshow("image", thresh)
# # cv2.waitKey(0)
# # cv2.imshow("image", opening)
# #
# #
# # # sure background area
# # sure_bg = cv2.dilate(opening,kernel,iterations=3)
# # # Finding sure foreground area
# # dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
# #
# # ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
# # # Finding unknown region
# # sure_fg = np.uint8(sure_fg)
# # unknown = cv2.subtract(sure_bg, sure_fg)
# #
# # # Marker labelling
# #
# # ret, markers = cv2.connectedComponents(sure_fg)
# # # Add one to all labels so that sure background is not 0, but 1
# # markers = markers+1
# # # Now, mark the region of unknown with zero
# # markers[unknown == 255] = 0
# # cv2.imshow("test markers", markers)
# # cv2.waitKey(0)
# # markers = cv2.watershed(image,markers)
# # image[markers == -1] = [255,0,0]
# # cv2.imshow("fin", image)
# # cv2.waitKey(0)
#
#


