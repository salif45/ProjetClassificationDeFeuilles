import cv2
import numpy as np
from math import pi
import json
import copy

def dist(A,B):
    output = ((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2) ** 0.5
    return output

def calcAngle(a,b,c):
    vecBA = np.array([a[0] - b[0], a[1] - b[1]])
    vecBA = vecBA / np.linalg.norm(vecBA)
    vecBC = np.array([c[0] - b[0], c[1] - b[1]])
    vecBC = vecBC / np.linalg.norm(vecBC)
    # calcul de l'angle entre les vecteurs
    angle = np.arccos(np.dot(vecBA, vecBC)) * 180 / pi
    return angle

def detection_dent(segmentation, imageDeBase):
    dent = imageDeBase.copy();

    contours, hierarchy = cv2.findContours(segmentation, 1, cv2.CHAIN_APPROX_TC89_KCOS)
    # methode d'approximation (dernier argument : maybe CHAIN_APPROX_TC89_L1 resultats proches )
    #on considere que le contours de la feuille est le contour le plus long :

    contourUtile = max(contours, key=len)
    # cv2.drawContours(imageDeBase, contourUtile, -1, (0,0,255), 2)
    # cv2.imshow("contour utilise", segmentation)

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
    #Affichage des dents
    # cv2.drawContours(dent, list_contour, -1, (0, 0, 255), 3)
    # cv2.imshow("dents de la feuille", dent)

    #nombre de dents
    nombreDent = len(list_contour)
    #On fait un seuil a partir duquel on considere qu'il y a des dents
    presenceDent = False
    if nombreDent > 20 :
        presenceDent=True
    return presenceDent


def feuille_convexe(segmentation, imageDeBase):
    contours, hierarchy = cv2.findContours(segmentation, 1, cv2.CHAIN_APPROX_TC89_KCOS)
    # on considere que le contours de la feuille est le contour le plus long :
    contourUtile = max(contours, key=len)

    #On recupere le contour convexe de notre feuille
    hull = cv2.convexHull(contourUtile, returnPoints=False)
    #On recupere les defauts de convexite de notre contour
    defects = cv2.convexityDefects(contourUtile, hull)
    defautDetecte=0;
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contourUtile[s][0]) #point du contours convexe avant
        end = tuple(contourUtile[e][0])   #point du contours convexe d'apres
        far = tuple(contourUtile[f][0])   #defaut de convexite entre les deux
        #affichage du contour convexe
        cv2.line(imageDeBase, start, end, [0, 255, 0], 2)
        cv2.circle(imageDeBase, start, 5, [0, 255, 0], -1)

        #calcul des vecteurs normalises entre le defaut de convexite et le contour convexe
        angle = calcAngle(start,far,end)

        #on ne considere que les defauts de convexite qui forme un angle assez petit
        if (angle <100) :
            defautDetecte += 1
            #affichage des defauts selectionnes
            cv2.circle(imageDeBase, far, 5, [0, 0, 255], -1)

    # affichage defauts
    # cv2.imshow('fin', imageDeBase)

    convex=False
    if defautDetecte <2:
        convex=True

    return convex

#Fonction pour determiner le masque de la feuille sans la queue afin de determiner la forme
def masqueSansQueue(segmentation):
    # On recupere le contour de la feuille
    contours, hierarchy = cv2.findContours(segmentation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contourUtile = max(contours, key=len)
    index = 0
    for i in range(len(contours)):
        if len(contours[i]) == len(contourUtile):
            index = i
    # On dessine l'interieur du contour en blanc afin d'avoir un masque
    cv2.drawContours(segmentation, contours, index, (255, 255, 255), -1)
    # On applique ouverture et fermeture pour avoir un masque sans la queue de la feuille
    kernel = np.ones((10, 10), np.uint8)
    masque2 = cv2.morphologyEx(segmentation, cv2.MORPH_OPEN, kernel)
    kernel = np.ones((10, 10), np.uint8)
    masque2 = cv2.morphologyEx(masque2, cv2.MORPH_CLOSE, kernel)
    # On seuille le masque
    ret, masquethresh = cv2.threshold(masque2, 127, 255, 0)
    return masquethresh

#Fonction pour determiner si la feuille est en forme de triangle
def checkTriangle(masqueSansQueue, input):
    compteurdetriangle = 0
    height, width, channels = input.shape

    # On recupere le contour du masque
    contours, hierarchy = cv2.findContours(masqueSansQueue, 1, cv2.CHAIN_APPROX_SIMPLE)
    contourUtile = max(contours, key=len)
    # on recupere le contour convexe
    hull = cv2.convexHull(contourUtile)
    # cv2.drawContours(input, contourUtile, -1, (255, 0, 0), 2)
    # cv2.imshow("contour utilise", input)

    #On determine le 'centre' de la feuille
    M = cv2.moments(hull)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    # cv2.circle(input, (cX, cY), 5, [0, 2, 255], -1)


    #Avec le contour convex on calcul les angle en chaque point :
    listeAngle = np.array([])
    for i in range(len(hull) - 1):
        a = hull[i - 1][0]
        b = hull[i][0]
        c = hull[i + 1][0]
        angle = calcAngle(a, b, c)
        listeAngle = np.append(listeAngle, angle)
    # calcul de l'angle : avant-dernier,dernier,premier point du contour
    a = hull[len(hull) - 2][0]
    b = hull[len(hull) - 1][0]
    c = hull[0][0]
    angle = calcAngle(a, b, c)
    listeAngle = np.append(listeAngle, angle)

    #Liste des points pour lesquels l'angle est faible (<140)
    listeAngleFaible = []
    for i in range(len(listeAngle)):
        if listeAngle[i] < 140:
            # cv2.circle(input, tuple(hull[i][0]), 5, [0, 2, 255], -1)
            listeAngleFaible.append(hull[i][0])
        # cv2.imshow("sommets possible detectes", input)
    # print("il y a {} sommets detectes".format(len(listeAngleFaible)))

    # On retire les sommets trop proches
    aRetirer = [] #liste qui contient les indices des elements a retirer
    if len(listeAngleFaible) > 1:
        for i in range(len(listeAngleFaible)):
            if dist(listeAngleFaible[i - 1], listeAngleFaible[i]) < 20:
                # retirer un des points proches
                if (i-1 not in aRetirer):
                    aRetirer.append(i)
    aRetirer.reverse()
    for i in range(len(aRetirer)):
        del listeAngleFaible[aRetirer[i]]
    # print("il y a {} sommets restants".format(len(listeAngleFaible)))

    for i in range(len(listeAngleFaible)):
        pointAngle = listeAngleFaible[i]
        # calcul du vecteur entre le sommet et le centre
        vecSommetCentre = [cX - pointAngle[0], cY - pointAngle[1]]
        vecPerpendiculaire = [-vecSommetCentre[1], vecSommetCentre[0]]

        #Choix de 2 points base et sommet pour calculer la largeur a ces 2 endroits
        #Si le rapport est assez grand on considere qu'on a un triangle
        base = [cX+int(0.6*vecSommetCentre[0]), cY+int(0.6*vecSommetCentre[1])]
        sommet = [pointAngle[0]+int(0.3*vecSommetCentre[0]), pointAngle[1]+int(0.3*vecSommetCentre[1])]

        # cv2.circle(input, tuple(base), 5, [255,0, 255], -1)
        # cv2.circle(input, tuple(sommet), 5, [255, 2, 255], -1)
        # cv2.imshow("triangle", input)


        #pas avec lequel on parcours la perpendiculaire a la recherche de point du sommet dans cette direction
        pas=0.01
        #distance max pour conciderer qu'on est assez proche d'un point
        seuil = 10
        pDepart, sommetGauche = trouverPointContour(sommet, vecPerpendiculaire, 1, pas, seuil, contourUtile, input)
        # print("fin triangle 1/4")

        pDepart, sommetDroit = trouverPointContour(pDepart, vecPerpendiculaire, -1, pas, seuil, contourUtile, input)
        # print("fin triangle 2/4")

        pDepart, baseGauche = trouverPointContour(base, vecPerpendiculaire, 1, pas, seuil, contourUtile, input)
        # print("fin triangle 3/4")

        pDepart, baseDroit = trouverPointContour(pDepart, vecPerpendiculaire, -1, pas, seuil, contourUtile, input)
        # print("fin triangle 4/4")

        rapport = dist(baseDroit, baseGauche) / dist(sommetDroit, sommetGauche)
        print("rapport = {}".format(rapport))
        if rapport>1.8 :
            compteurdetriangle += 1
            # cv2.circle(input, tuple(pointAngle), 5, [255, 255, 0], -1)

        # cv2.imshow("triangle", input)
    return compteurdetriangle

def trouverPointContour(pDepart, vecteur, direction, pas, seuil, contour, input):
    height, width, channels = input.shape
    enCours = True
    baseD = copy.deepcopy(pDepart)
    baseD[0] += direction * 0.1 * vecteur[0]
    baseD[1] += direction * 0.1 * vecteur[1]
    while (enCours):
        baseD[0] += direction * pas * vecteur[0]
        baseD[1] += direction * pas * vecteur[1]
        if (baseD[0] < 0 or baseD[0] > width) or (baseD[1] < 0 or baseD[1] > height):
            pDepart[0] += -1*direction * 15 * pas * vecteur[0]
            pDepart[1] += -1 * direction * 15 * pas * vecteur[1]
            baseD = copy.deepcopy(pDepart)
        else:
            for j in range(len(contour)):
                pContour = contour[j][0]
                d = dist(baseD, pContour)
                if d < seuil:
                    pointOutput = pContour
                    enCours = False
    return (pDepart,pointOutput)

def redimension(imageDeBase):
    # changer la taille d'une image :
    # Choix a verifier : on veut une image qui fait du 500 de largeur
    # et on adapte la hauteur en consequence pour ne pas deformer
    LARGEUR = 500
    height, width, channels = imageDeBase.shape
    facteur = float(LARGEUR) / float(height)
    newInput = cv2.resize(imageDeBase, (0, 0), fx=facteur, fy=facteur)
    return newInput


def segmentation(input): #TODO : mettre la bonne segmentation
    image_gray = cv2.cvtColor(input, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(image_gray, 100, 150)

    ret, thresh = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    ret, thresh = cv2.threshold(opening, 127, 255, 0)
    return thresh


def etude_classificateur(convexite, dents, jsonPath):
    # ouverture du fichier JSON et mise sous forme de dictionnaire
    with open(jsonPath) as json_data:
        data_dict = json.load(json_data)

    #On stock les resultats sous forme de couple (espece, pourcentage de criteres remplis)
    listeResultat = []

    for cle in data_dict.items(): #on parcours les differents types d'arbres
        espece = cle[0]
        nbrAttribus = len(cle[1])
        nbrPositif = 0
        for cle2 in cle[1].items(): #On parcours les differents attrabuts et leurs valeurs
            if (cle2[0] == "convexe" and cle2[1] == convexite):
                nbrPositif += 1
            if (cle2[0] == "dent" and cle2[1] == dents):
                nbrPositif += 1

        listeResultat.append((espece, float(nbrPositif) / float(nbrAttribus) * 100))
    return listeResultat

def main():
    # input = cv2.imread("base_donnee_feuille/hetre/hetre1.jpg")
    # input = cv2.imread("base_donnee_feuille/hetre/hetre2.jpg")
    # input = cv2.imread("base_donnee_feuille/chene/chene2.jpg")
    # input = cv2.imread("base_donnee_feuille/margousier/margousier2.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau1.jpg")
    input = cv2.imread("base_donnee_feuille/bouleau/bouleau2.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau3.jpg")
    # input = cv2.imread("base_donnee_feuille/platane/platane1.jpg")


    input = redimension(input)

    thresh = segmentation(input)

    #Retirer la queue et avoir un masque utilisable pour determiner la forme
    masquethresh = masqueSansQueue(thresh)

    #TODO : Ameliorer la detection de cercle


    #On recupere le contour du masque
    contours, hierarchy = cv2.findContours(masquethresh, 1, cv2.CHAIN_APPROX_SIMPLE)
    contourUtile = max(contours, key=len)
    #on recupere le contour convexe
    hull = cv2.convexHull(contourUtile)
    cv2.drawContours(input, contourUtile, -1, (255,0,0), 2)
    cv2.imshow("contour utilise", input)

    #TODO : Etudier la forme a partir du masque sans la queue
    #centre de la feuille
    M = cv2.moments(hull)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    cv2.circle(input, (cX,cY), 5, [0, 2,255], -1)
    # cv2.imshow("centre", input)

    ## Detection d'un cercle
    #Calcul distance centre -> contour :
    listeDistance = np.array([])
    for i in range(len(hull)):
        point = hull[i][0]
        pX, pY = point
        distance = ((cX-pX)**2+(cY-pY)**2)**0.5
        listeDistance = np.append(listeDistance,distance)

    print(listeDistance.std())

    if (listeDistance.std() < 17 ): #17 : valeur a ajuster/diminuer
        print("cercle")







    # Detection forme : triangle
    nombreTriangle = checkTriangle(masquethresh, input)
    print("On a detecte {} triangle dans la forme".format(nombreTriangle))


    #detection dent :
    dents = detection_dent(thresh, input)

    #detection convexite :
    convexite= feuille_convexe(thresh, input)

    listeResultat = etude_classificateur(convexite, dents, 'arbre.json')
    print(listeResultat)

    cv2.waitKey(0)

main()
