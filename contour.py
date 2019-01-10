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

def detection_dent(contourUtile, imageDeBase ):
    dent = imageDeBase.copy();

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


def feuille_convexe(contourUtile, hull, imageDeBase):

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
    contours, hierarchy = cv2.findContours(masquethresh, 1, cv2.CHAIN_APPROX_SIMPLE)
    contourUtile = max(contours, key=len)
    contourConvex = cv2.convexHull(contourUtile)
    M = cv2.moments(contourConvex)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    centre = [cX, cY]

    return masquethresh, contourUtile, contourConvex, centre

#Fonction pour determiner si la feuille est en forme de triangle
#TODO : ATTENTION ca ne marche que pour les feuille convexe car on utilie le vrai contour de la feuille pas le contour convexe
def checkTriangle(input, contourUtile, contourConvex, centre):
    compteurdetriangle = 0

    height, width, channels = input.shape
    cX, cY = centre

    #Avec le contour convex on calcul les angle en chaque point :
    listeAngle = np.array([])
    for i in range(len(contourConvex) - 1):
        a = contourConvex[i - 1][0]
        b = contourConvex[i][0]
        c = contourConvex[i + 1][0]
        angle = calcAngle(a, b, c)
        listeAngle = np.append(listeAngle, angle)
        # calcul de l'angle : avant-dernier,dernier,premier point du contour
    a = contourConvex[len(contourConvex) - 2][0]
    b = contourConvex[len(contourConvex) - 1][0]
    c = contourConvex[0][0]
    angle = calcAngle(a, b, c)
    listeAngle = np.append(listeAngle, angle)

    # Liste des points pour lesquels l'angle est faible (<140)
    listeAngleFaible = []
    for i in range(len(listeAngle)):
        if listeAngle[i] < 140:
            # cv2.circle(input, tuple(hull[i][0]), 5, [0, 2, 255], -1)
            listeAngleFaible.append(contourConvex[i][0])
            # cv2.imshow("sommets possible detectes", input)
    # print("il y a {} sommets detectes".format(len(listeAngleFaible)))

    # On retire les sommets trop proches
    aRetirer = []  # liste qui contient les indices des elements a retirer
    if len(listeAngleFaible) > 1:
        for i in range(len(listeAngleFaible)):
            if dist(listeAngleFaible[i - 1], listeAngleFaible[i]) < 20:
                # retirer un des points proches
                if (i - 1 not in aRetirer):
                    aRetirer.append(i)
    aRetirer.reverse()
    for i in range(len(aRetirer)):
        del listeAngleFaible[aRetirer[i]]
        # print("il y a {} sommets restants".format(len(listeAngleFaible)))


    for i in range(len(listeAngleFaible)):
        pointAngle = listeAngleFaible[i]
        pointAngle = [float(pointAngle[0]), float(pointAngle[1])]
        # calcul du vecteur entre le sommet et le centre
        vecSommetCentre = [cX - pointAngle[0], cY - pointAngle[1]]
        vecPerpendiculaire = [-vecSommetCentre[1], vecSommetCentre[0]]

        #Choix de 2 points base et sommet pour calculer la largeur a ces 2 endroits
        #Si le rapport est assez grand on considere qu'on a un triangle

        pDepart, baseEnd = trouverPointContour(pointAngle, vecSommetCentre, 1, 0.01, 5, contourUtile, height, width)

        # cv2.circle(input, tuple([int(baseEnd[0]), int(baseEnd[1])]), 5, [255, 0, 0], -1)
        # cv2.circle(input, tuple([int(pointAngle[0]), int(pointAngle[1])]), 5, [0, 0, 255], -1)
        vecSommetBase = [baseEnd[0]-pointAngle[0], baseEnd[1]-pointAngle[1]]
        vbase = [0.9*vecSommetBase[0], 0.9*vecSommetBase[1]]
        base = [pointAngle[0]+vbase[0], pointAngle[1]+vbase[1]]
        vsommet = [0.1*vecSommetBase[0], 0.1*vecSommetBase[1]]
        sommet = [pointAngle[0] + vsommet[0], pointAngle[1] + vsommet[1]]

        # cv2.circle(input, tuple([int(base[0]),int(base[1])]), 5, [255,0, 255], -1)
        # cv2.circle(input, tuple([int(sommet[0]),int(sommet[1])]), 5, [255, 2, 255], -1)
        # cv2.imshow("triangle", input)

        #pas avec lequel on parcours la perpendiculaire a la recherche de point du sommet dans cette direction
        pas=0.02
        #distance max pour conciderer qu'on est assez proche d'un point
        seuil = 7
        pDepart, sommetGauche = trouverPointContour(sommet, vecPerpendiculaire, 1, pas, seuil, contourUtile, height, width)
        # print("fin triangle 1/4")

        x, sommetDroit = trouverPointContour(sommet, vecPerpendiculaire, -1, pas, seuil, contourUtile, height, width)
        # print("fin triangle 2/4")

        x, baseGauche = trouverPointContour(base, vecPerpendiculaire, 1, pas, seuil, contourUtile, height, width)
        # print("fin triangle 3/4")

        x, baseDroit = trouverPointContour(base, vecPerpendiculaire, -1, pas, seuil, contourUtile, height, width)
        # print("fin triangle 4/4")

        rapport = dist(baseDroit, baseGauche) / dist(sommetDroit, sommetGauche)
        print("rapport = {}".format(rapport))
        if rapport>2.7 :
            compteurdetriangle += 1
            # cv2.circle(input, tuple(pointAngle), 5, [255, 255, 0], -1)

        cv2.imshow("triangle", input)
    return compteurdetriangle


## trouverPointContour ##
#Determiner le point du contour le plus proche dans une certaine direction (intersection contour/segment)
#Parametre :
    #pDepart : point de depart d'ou on part pour chercher le point
    #vecteur : vecteur directeur pour la direction dans laquelle on cherche le point
    #direction : 1 ou -1 : (si on veux aller dnas la direction opposee du vecteur)
    #pas : vitesse a laquelle on s'eloigne du depart
    #seuil : eloignement max du point par rapport au vecteur plus c'est petit plus ca sera precis mais on peut se retrouver avec une boucle infini si c'es trop grand
    #contour : contour ou on veut trouver le point
    #input : image
#Retour :
    #pDepart2 : je ne sais pas si c'est utile : parfois l'algo doit decaller le point de depart pour converger => retourne ce nouveau point de departt
    #pointOutput : Point d'intersection
def trouverPointContour(pDepart, vecteur, direction, pas, seuil, contour, height, width):
    # height, width, channels = input.shape
    enCours = True
    baseD = copy.deepcopy(pDepart)
    pDepart2 = copy.deepcopy(pDepart)
    baseD[0] += direction * 0.15 * vecteur[0]
    baseD[1] += direction * 0.15 * vecteur[1]
    # cv2.circle(input, tuple([int(baseD[0]), int(baseD[1])]), 1, [255, 255, 0], -1)
    while (enCours):
        baseD[0] += direction * pas * vecteur[0]
        baseD[1] += direction * pas * vecteur[1]

        if (baseD[0] < 0 or baseD[0] > width) or (baseD[1] < 0 or baseD[1] > height):
            pDepart2[0] += -1*direction * 10 * pas * vecteur[0]
            pDepart2[1] += -1 * direction * 10 * pas * vecteur[1]
            baseD = copy.deepcopy(pDepart2)
        else:
            for j in range(len(contour)):
                pContour = contour[j][0]
                d = dist(baseD, pContour)
                if d < seuil:
                    pointOutput = pContour
                    enCours = False
    # cv2.circle(input, tuple([int(pointOutput[0]), int(pointOutput[1])]), 5, [255,255,255], -1)

    return pDepart2,pointOutput

#methode cercle :
    #la feuille est supposee symetrique
    #On parcours la moitie des points et 1 point sur 4 (d'ou le /8 et le i+4)
    #Pour chaque point on cherche celui en face par rapport au centre
    #On mesure la distance entre les 2 points opposes
    #On regarde si c'est constant
    #(plus precis que regarder les distance centre-bord mais plus long a calculer)
def checkCercle(contourUtile, centre, input):
    cX, cY = centre
    cercle = False
    height, width, channels = input.shape
    listeDiametre = np.array([])
    for i in range(int(len(contourUtile) / 8)):
        point = contourUtile[i + 4][0]
        pX, pY = point
        vPointCentre = [cX - pX, cY - pY]
        x, p2 = trouverPointContour([cX, cY], vPointCentre, 1, 0.02, 25, contourUtile, height, width)
        d = dist(point, p2)
        listeDiametre = np.append(listeDiametre, d)

    print("cercle : ecart type des diametres : {}".format(listeDiametre.std()))
    if (listeDiametre.std() < 15):  # 20 : valeur a ajuster
        print("!!!! cercle")
        cercle = True

    return cercle


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

    ## Pour eviter de recalculer les contours regulierement :
    contours, hierarchy = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_TC89_KCOS)
    contourFeuille = max(contours, key=len)
    contourConvex = cv2.convexHull(contourFeuille, returnPoints=False)
    return thresh, contourFeuille, contourConvex


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
    input = cv2.imread("base_donnee_feuille/chene/chene1.jpg")
    # input = cv2.imread("base_donnee_feuille/margousier/margousier2.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau1.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau2.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau3.jpg")
    # input = cv2.imread("base_donnee_feuille/platane/platane1.jpg")


    input = redimension(input)

    thresh, contourUtileBase, contourConvexBase = segmentation(input)

    height, width, channels = input.shape

    #Retirer la queue et avoir un masque utilisable pour determiner la forme
    masquethresh, contourUtileMasque, contourConvexMasque, centreMasque = masqueSansQueue(thresh)

    #TODO : Ameliorer la detection de cercle

    cX, cY = centreMasque

    #TODO : Etudier la forme a partir du masque sans la queue

    ## Detection d'une elipse/rectangle


    #methode rectangle :
    #Calcul distance centre -> contour :
    listeDistanceCentreContour = np.array([])
    for i in range(len(contourUtileMasque)):
        point = contourUtileMasque[i][0]
        pX, pY = point
        distance = ((cX-pX)**2+(cY-pY)**2)**0.5
        listeDistanceCentreContour = np.append(listeDistanceCentreContour,distance)


    #On cherche le grand axe
    indiceGrandAxe1 = listeDistanceCentreContour.argmax() #le point le plus loin du centre
    pointGrandAxe1 = contourUtileMasque[indiceGrandAxe1][0]
    cv2.circle(input, tuple(pointGrandAxe1), 7, [100,100,100], -1)

    #le point de l'autre cote -> celui qui a la plus grande distance avec lui
    dMax = -1
    for i in range(len(contourUtileMasque)):
        point = contourUtileMasque[i][0]
        pX, pY = point
        distance = dist(pointGrandAxe1, [pX,pY])
        if distance > dMax :
            dMax = distance
            pointGrandAxe2 = contourUtileMasque[i][0]

    cv2.circle(input, tuple(pointGrandAxe2), 7, [100,100,100], -1)


    vecGrandAxe = [pointGrandAxe2[0]-pointGrandAxe1[0], pointGrandAxe2[1]-pointGrandAxe1[1]]
    vecPerpGrandAxe = [-vecGrandAxe[1], vecGrandAxe[0]]
    pas, seuil = 0.01,10
    listeDistPerp = np.array([])
    #On parcours le grand axe et on mesure les longueurs sur a peu pres tout l'axe (on ignore les extremites
    # car les feuilles rectangulaires le sont vers le centre)
    #EX : Si la feuille est entre 0 et 10, on va regarder entre 2 et 8 pour enlever la pointe
    for i in range(0,41):
        pourcent = 0.20 + i*0.015
        pDepart = [float(pointGrandAxe1[0]) + pourcent * vecGrandAxe[0],
                   float(pointGrandAxe1[1]) + pourcent * vecGrandAxe[1]]
        x, sommetA = trouverPointContour(pDepart, vecPerpGrandAxe, 1, pas, seuil, contourUtileMasque, height, width)
        x, sommetB = trouverPointContour(pDepart, vecPerpGrandAxe, -1, pas, seuil, contourUtileMasque, height, width)
        d = dist(sommetA, sommetB)
        listeDistPerp = np.append(listeDistPerp, d)

    print("std liste des distance perp = {}".format(listeDistPerp.std()))
    #Si les longueur perpendiculaires au grand axe sont 'constantes' c'est un rectangle
    if listeDistPerp.std() <  20 :
        print("!!!!! c'est un rectangle")


    #Si ce n'est pas un rectangle : on regarde le demi grand axe et on regarde si c'est un carre (sinon on regarde si c'est ellipse)
    #TODO : ENLEVER LES POINTS AUX EXTREMITE DU GRAND AXE POUR NE PAS LES PRENDRE EN COMPTE LORS DU CALCUL POUR ELLIPSE

    #Demi grand axe : On va au centre du grand axe et on cherche les points
    centreGrandAxe=[float(pointGrandAxe1[0]) + 0.5 * vecGrandAxe[0],
                    float(pointGrandAxe1[1]) + 0.5 * vecGrandAxe[1]]
    x, pointPetitAxe1 = trouverPointContour(centreGrandAxe, vecPerpGrandAxe, 1, pas, seuil, contourUtileMasque, height, width)
    x, pointPetitAxe2 = trouverPointContour(centreGrandAxe, vecPerpGrandAxe, -1, pas, seuil, contourUtileMasque, height, width)
    cv2.circle(input, tuple(pointPetitAxe1), 7, [200,200,200], -1)
    cv2.circle(input, tuple(pointPetitAxe2), 7, [200,200,200], -1)


    p=dist(pointGrandAxe1, pointGrandAxe2) #longueur grand axe
    q=dist(pointPetitAxe1,pointPetitAxe2) #longueur petit axe

    #On regarde si c'est un carre (petit grand axe = grand axe +-10%):
    if (p*0.9<=q)and(q>=p*1.1):
        print "c'est un carre"


    #On regarde si c'est une ellipse
    c=((p/2.0)**2-(q/2.0)**2)**0.5
    #calcul des foyers
    vGrandAxeNorm= np.array(vecGrandAxe)

    vGrandAxeNorm = vGrandAxeNorm / np.linalg.norm(vGrandAxeNorm)
    foyer1 = [int(centreGrandAxe[0] + c * vGrandAxeNorm[0]),
              int(centreGrandAxe[1] + c * vGrandAxeNorm[1])]
    foyer2 = [int(centreGrandAxe[0] - c * vGrandAxeNorm[0]),
              int(centreGrandAxe[1] - c * vGrandAxeNorm[1])]



    cv2.circle(input, tuple(foyer1), 7, [200, 200, 0], -1)
    cv2.circle(input, tuple(foyer2), 7, [200, 200, 0], -1)
    #Ellipse si en tout point du contour : distance(foyer1-contour)+distance(foyer2-contour) = cte


    listeDistanceEllipse = np.array([])
    for i in range(len(contourUtileMasque)):
        pt=contourUtileMasque[i][0]
        d1 = dist(pt,foyer1)
        d2 = dist(pt,foyer2)
        dtot=d1+d2
        listeDistanceEllipse = np.append(listeDistanceEllipse, dtot)

    #On peut regarder aussi si petit et grd axe sont axes de symetrie
    p1 = [int(float(pointGrandAxe1[0]) + 0.2 * vecGrandAxe[0]),
          int(float(pointGrandAxe1[1]) + 0.2 * vecGrandAxe[1])]
    p2 = [int(float(pointGrandAxe1[0]) + 0.8 * vecGrandAxe[0]),
          int(float(pointGrandAxe1[1]) + 0.8 * vecGrandAxe[1])]
    vecPetitAxe=[pointPetitAxe2[0]-pointPetitAxe1[0],pointPetitAxe2[1]-pointPetitAxe1[1]]
    p3 = [int(float(pointPetitAxe1[0]) + 0.2 * vecPetitAxe[0]),
          int(float(pointPetitAxe1[1]) + 0.2 * vecPetitAxe[1])]
    p4 = [int(float(pointPetitAxe1[0]) + 0.8 * vecPetitAxe[0]),
          int(float(pointPetitAxe1[1]) + 0.8 * vecPetitAxe[1])]
    cv2.circle(input, tuple(p1), 7, [0, 200, 200], -1)
    cv2.circle(input, tuple(p2), 7, [0, 200, 200], -1)
    cv2.circle(input, tuple(p3), 7, [0, 200, 200], -1)
    cv2.circle(input, tuple(p4), 7, [0, 200, 200], -1)

    #on cherche les points sur le bord pour calcul les distances pour les comparer et regarder s'il y a symetrie
    x, s1a = trouverPointContour(p1, vecPetitAxe, -1, 0.01, 10, contourUtileMasque, height, width)
    x, s1b = trouverPointContour(x, vecPetitAxe, 1, 0.01, 10, contourUtileMasque, height, width)
    x, s2a = trouverPointContour(p2, vecPetitAxe, -1, 0.01, 10, contourUtileMasque, height, width)
    x, s2b = trouverPointContour(x, vecPetitAxe, 1, 0.01, 10, contourUtileMasque, height, width)
    x, s3a = trouverPointContour(p3, vecGrandAxe, -1, 0.01, 10, contourUtileMasque, height, width)
    x, s3b = trouverPointContour(x, vecGrandAxe, 1, 0.01, 10, contourUtileMasque, height, width)
    x, s4a = trouverPointContour(p4, vecGrandAxe, -1, 0.01, 10, contourUtileMasque, height, width)
    x, s4b = trouverPointContour(x, vecGrandAxe, 1, 0.01, 10, contourUtileMasque, height, width)

    l1 = dist(s1a,s1b)
    l2 = dist(s2a, s2b)
    l3 = dist(s3a, s3b)
    l4 = dist(s4a, s4b)

    #Parfois la detection de point pose probleme car la fonction detecte 2 points au meme endroit si la largeur de la feuille est faible
    #Ce qui donne une distance nulle
    #On calcule le rapport r=l1/l2 sauf si l1 et/ou l2=0
    #On suppose que si les 2 longueur du rapport sont nuls alors la feuille est fine des 2 cotes => r=1
    #Si (l2 =0 et l1!=0)=> r=0 pour eviter les divisions par 0
    if (l1<1 and l2<1):
        r1=1
    elif (l2 == 0): #eviter la division par 0
        r1=0
    else :
        r1 = l1/l2

    if (l1<1 and l2<1):
        r2=1
    elif (l4 == 0):
        r2=0
    else :
        r2 = l3/l4
    print("ellipse test symetrie : rapport1 = {}, rapport2 {}".format(r1, r2))
    print("ellipse std : {}".format(listeDistanceEllipse.std()))
    #Si les longueurs sont proches et qu'on a une symetrie (approximatoin, on a pas des formes parfaites)
    if (listeDistanceEllipse.std() < 30) and (0.8<=r1 and r1 <= 1.2) and (0.8<=r2 and r2<=1.2) :
        print "!!!!!!!! c'est une ellipse"



    cv2.imshow("point loin", input)




    #TODO : regarder pour les feuille pas entiere si les bord sont pointu (platane) ou arrondi (chene)






    # Detection forme : triangle
    nombreTriangle = checkTriangle(input, contourUtileMasque, contourConvexMasque, centreMasque)
    print("On a detecte {} triangle dans la forme".format(nombreTriangle))
    # Detection forme : cercle
    cercle = checkCercle(contourUtileMasque, centreMasque, input)
    print("Forme cercle : {}".format(cercle))

    #detection dent :
    dents = detection_dent(contourUtileBase, input)
    print("presence de dent : {}".format(dents))

    #detection convexite :
    convexite= feuille_convexe(contourUtileBase, contourConvexBase, input)
    print("feuille entiere : {}".format(convexite))

    listeResultat = etude_classificateur(convexite, dents, 'arbre.json')
    print(listeResultat)

    cv2.waitKey(0)

main()
