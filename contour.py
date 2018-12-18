import cv2
import numpy as np
from math import pi



def detection_dent(image, image_input):
    input_modifie = image_input.copy();

    contours, hierarchy = cv2.findContours(image, 1, cv2.CHAIN_APPROX_TC89_KCOS)
    # methode d'approximation (dernier argument : maybe CHAIN_APPROX_TC89_L1 resultats proches )

    #on considere que le contours de la feuille est le contour le plus long :
    contourUtile = max(contours, key=len)
    cv2.drawContours(image_input, contourUtile, -1, (0,0,255), 2)
    cv2.imshow("contour utilise", image_input)

    list_contour = [] #pour stocker les points qui sont consideres comme des dents
    #on parcourt tous les points du contour et on regarde s'ils sont a peu pres alignes
    #si l'angle entre les points est trop important on considere qu'il y a une dent
    #On regarde si les points sont alignes en utilisant l'inegalite triangulaire (aligne si AB+BC = AC)
    for i in range(len(contourUtile) - 2):
        a = contourUtile[i]
        b = contourUtile[i + 1]
        c = contourUtile[i + 2]
        AB = np.linalg.norm(b - a)
        BC = np.linalg.norm(c - b)
        AC = np.linalg.norm(c - a)

        if ((AC / (AB + BC)) < 0.926): #valeur determiner par l'experience : seuil a partir duquel on considere que les points ne sont pas alignes
            list_contour.append(b)
            # print (AC / (AB + BC))

    cv2.drawContours(input_modifie, list_contour, -1, (0, 0, 255), 3) #affichage des dents

    cv2.imshow("dents de la feuille", input_modifie)
    nombre_dent = len(list_contour)

    return nombre_dent



def main():
    # image_input = cv2.imread("base_donnee_feuille/hetre/hetre1.jpg") #Pas de dent
    #image_input = cv2.imread("base_donnee_feuille/chene/chene2.jpg") #Pas de dents
    #image_input = cv2.imread("base_donnee_feuille/margousier/margousier2.jpg") #avec des dents
    #image_input = cv2.imread("base_donnee_feuille/bouleau/bouleau2.jpg") #avec des dents
    image_input = cv2.imread("base_donnee_feuille/platane/platane1.jpg") #avec des dents

    # changer la taille d'une image
    small = cv2.resize(image_input, (0, 0), fx=0.5, fy=0.5)
    image_input = small

    #SEGMENTATION (a modifier)
    image_gray = cv2.cvtColor(image_input, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(image_gray,100,150)

    ret, thresh = cv2.threshold(image_gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

    ret,thresh = cv2.threshold(opening,127,255,0)

    #detection dent :  TODO : ne pas dependre de la taille de l'image :(
    nombre_dent = detection_dent(thresh, image_input)
    print("nombre de dents = ", nombre_dent)



    contours, hierarchy = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_TC89_KCOS)

    # on considere que le contours de la feuille est le contour le plus long :
    contourUtile = max(contours, key=len)

    #contour convexe mais c'est nul...
    hull = cv2.convexHull(contourUtile, returnPoints=False)
    defects = cv2.convexityDefects(contourUtile, hull)

    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contourUtile[s][0])
        end = tuple(contourUtile[e][0])
        far = tuple(contourUtile[f][0])
        cv2.line(image_input, start, end, [0, 255, 0], 2)
        cv2.circle(image_input, start, 5, [0, 255, 0], -1)
        cv2.circle(image_input, far, 5, [0, 0, 255], -1)  # start - far - end

        vecBA = np.array([far[0]-start[0],far[1]-start[1]])
        vecBA = vecBA / np.linalg.norm(vecBA)

        vecBC = np.array([far[0] - end[0], far[1] - end[1]])

        vecBC = vecBC / np.linalg.norm(vecBC)
        angle = np.arccos(np.dot(vecBA,vecBC))
        print(angle*180/pi)
        # if (angle > 80) : #TODO : traiter les points rouges


        #TODO : etudier angle convexite/defaut convexite

    cv2.imshow('convexite', image_input)



    cv2.waitKey(0)

main()
