import cv2
import numpy as np
from math import pi
import json
import copy

def dist(A,B):
    output = ((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2) ** 0.5
    return output

def calcAngle(a,b,c):
    #normalisation des vecteurs
    vecBA = np.array([a[0] - b[0], a[1] - b[1]])
    vecBA = vecBA / np.linalg.norm(vecBA)
    vecBC = np.array([c[0] - b[0], c[1] - b[1]])
    vecBC = vecBC / np.linalg.norm(vecBC)
    # calcul de l'angle entre les vecteurs
    angle = np.arccos(np.dot(vecBA, vecBC)) * 180 / pi
    return angle

def detection_dent(contourUtile, imageDeBase, debug = False ):
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

            # nombre de dents
            nombreDent = len(list_contour)

    #Affichage des dents
    if debug == True :
        cv2.drawContours(dent, list_contour, -1, (0, 0, 255), 3)
        cv2.imshow("dents de la feuille", dent)
        print("Nombre de dents detectees : {}".format(nombreDent))


    #On fait un seuil a partir duquel on considere qu'il y a des dents
    presenceDent = False
    if nombreDent > 20 :
        presenceDent=True
    return presenceDent


def feuille_convexe(contourUtile, hull, imageDeBase, debug = False):

    #On recupere les defauts de convexite de notre contour
    defects = cv2.convexityDefects(contourUtile, hull)
    defautDetecte=0;
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contourUtile[s][0]) #point du contours convexe avant
        end = tuple(contourUtile[e][0])   #point du contours convexe d'apres
        far = tuple(contourUtile[f][0])   #defaut de convexite entre les deux

        # calcul de l'angle
        angle = calcAngle(start, far, end)

        #affichage du contour convexe
        if debug == True :
            cv2.line(imageDeBase, start, end, [0, 255, 0], 2)
            cv2.circle(imageDeBase, start, 5, [0, 255, 0], -1)
            cv2.circle(imageDeBase, far, 5, [255, 0, 0], -1)
            print("angle : {}".format(angle))



        #on ne considere que les defauts de convexite qui forme un angle assez petit
        if (angle <115) :
            defautDetecte += 1
            #affichage des defauts selectionnes
            if debug == True :
                cv2.circle(imageDeBase, far, 5, [0, 0, 255], -1)
    print("nb defaut = {}".format(defautDetecte))
    convex = False
    if defautDetecte < 3:
        convex = True

    if debug == True :
        cv2.imshow('feuille entiere', imageDeBase)
        print("Feuille entiere : {}".format(convex))

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
    contours, hierarchy = cv2.findContours(masquethresh, 1, cv2.CHAIN_APPROX_NONE)
    contourUtile = max(contours, key=len)
    contourConvex = cv2.convexHull(contourUtile)
    M = cv2.moments(contourConvex)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    centre = [cX, cY]

    return masquethresh, contourUtile, contourConvex, centre

#Fonction pour determiner si la feuille est en forme de triangle
def checkTriangle(input, contourUtile, contourConvex, centre, debug = False):
    triangle = False
    compteurdetriangle = 0
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
            if debug==True :
                cv2.circle(input, tuple(contourConvex[i][0]), 5, [0, 0, 255], -1)
            listeAngleFaible.append(contourConvex[i][0])
    if debug == True :
        print("il y a {} sommets detectes avant de reduire".format(len(listeAngleFaible)))

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
    if debug == True :
        print("Il y a {} sommets quand on retire les sommets trop proches".format(len(listeAngleFaible)))

    for i in range(len(listeAngleFaible)):
        pointAngle = listeAngleFaible[i]
        pointAngle = [float(pointAngle[0]), float(pointAngle[1])]
        # calcul du vecteur entre le sommet et le centre
        vecSommetCentre = [cX - pointAngle[0], cY - pointAngle[1]]
        vecPerpendiculaire = [-vecSommetCentre[1], vecSommetCentre[0]]

        #Choix de 2 points base et sommet pour calculer la largeur a ces 2 endroits
        #Si le rapport est assez grand on considere qu'on a un triangle
        b1, b2 = trouverPointContour(pointAngle, vecSommetCentre, contourUtile, input)
        d1,d2 = dist(b1, pointAngle), dist(b2, pointAngle)
        if d1>d2 :
            baseEnd = b1
        else :
            baseEnd = b2


        vecSommetBase = [baseEnd[0]-pointAngle[0], baseEnd[1]-pointAngle[1]]
        vbase = [0.9*vecSommetBase[0], 0.9*vecSommetBase[1]]
        base = [pointAngle[0]+vbase[0], pointAngle[1]+vbase[1]]
        vsommet = [0.1*vecSommetBase[0], 0.1*vecSommetBase[1]]
        sommet = [pointAngle[0] + vsommet[0], pointAngle[1] + vsommet[1]]



        sommetGauche, sommetDroit = trouverPointContour(sommet, vecPerpendiculaire, contourUtile, input)

        baseGauche, baseDroit= trouverPointContour(base, vecPerpendiculaire, contourUtile, input)

        rapport = dist(baseDroit, baseGauche) / dist(sommetDroit, sommetGauche)
        if debug == True :
            cv2.circle(input, tuple([int(baseEnd[0]), int(baseEnd[1])]), 5, [255, 0, 0], -1)
            cv2.circle(input, tuple([int(pointAngle[0]), int(pointAngle[1])]), 5, [255, 0, 0], -1)
            cv2.circle(input, tuple([int(base[0]),int(base[1])]), 5, [255,0, 255], -1)
            cv2.circle(input, tuple([int(sommet[0]),int(sommet[1])]), 5, [255, 0, 255], -1)
            print("rapport = {}".format(rapport))
            cv2.imshow("triangle", input)

        if rapport>2.7 :
            compteurdetriangle += 1

    if compteurdetriangle >0:
        triangle = True

    return triangle


## trouverPointContour ##
#Determiner le point du contour le plus proche dans une certaine direction (intersection contour/segment)
#Parametre :
    #pDepart : point de depart d'ou on part pour chercher le point
    #vecteur : vecteur directeur pour la direction dans laquelle on cherche le point
    #contour : contour ou on veut trouver le point
    #input : image
    #debug : pour afficher le point de depart et les points detectes
#Retour :
    #Les 2 points du contous
def trouverPointContour(pDepart, vecteurDirecteur, contour, input, debug=False):
    vecteurPerpendiculaire = [-vecteurDirecteur[1], vecteurDirecteur[0]]
    v1 = np.array(vecteurPerpendiculaire)
    v1 = v1 / np.linalg.norm(v1)
    listePoint = []
    #On regarde le produit scalaire en le vecteur pDepart-Contour et le vecteur perpendiculaire au vecteur directeur:
    #Si le produit scalaire est assez proche de 0 on stocke le point comme un point du contour qui peut correpondre
    s=0.01
    listeReduite = []
    while(len(listeReduite)<2):
        #on recupere tous les points
        for i in range(len(contour)):
            pt = contour[i][0]
            v2 = np.array([pt[0] - pDepart[0], pt[1] - pDepart[1]])
            if (np.linalg.norm(v2)!=0):
                v2 = v2 / np.linalg.norm(v2)
                produitScalaire = np.dot(v1, v2)
                if (produitScalaire > -s and produitScalaire < s):
                    listePoint.append(pt)

        #on retire les points qui sont trop proche
        #on stocke le premier point puis pour chaque point on compare aux points dans listeReduite
        #S'ils sont assez proche -> On fait la moyenne avec le point qui correspond histoire de decaller un peu le point stocke
        #Sinon -> on ajoute le point a la listeReduite
        listeReduite = [listePoint[0]]
        for i in range(1,len(listePoint)):
            point = listePoint[i]
            test = False
            for j in range(len(listeReduite)):
                d = dist(point, listeReduite[j])
                if (d < 15 and (test == False)) :
                    p=listeReduite[j]
                    moyenne= [(p[0]+point[0])/2, (p[1]+point[1])/2]
                    listeReduite[j]=moyenne
                    test = True
            if test == False : #Pour  ne pas ajouter un point a 2 groupes
                listeReduite.append(point)
        #Si on n'a pas assez de valeur a la fin pour selectionner les points du contour, on augmente le seuil
        s+=0.1

    #on va selectionner les 2 points
    #On normalise le vecteur directeur
    vecteur2 = vecteurDirecteur
    vecteur2 = np.array(vecteur2)
    vecteur2 = vecteur2 / np.linalg.norm(vecteur2)
    #on stocke les pt en fonction du signe du produit scalaire.
    #Si tous les produit scalaires sont du meme signe : On prend le pt le plus proche et le plus eloigne du pt de depart (on est a l'exterieur du contour
    #Si ils sont de signe different : on prend le pr le plus eloigne dans lNegatif et dans lPositif
    lPositif = []
    lNegatif = []
    for i in range(len(listeReduite)):
        p=listeReduite[i]
        vecteur3=[p[0]-pDepart[0],p[1]-pDepart[1]]
        vecteur3 = np.array(vecteur3)
        vecteur3 = vecteur3 / np.linalg.norm(vecteur3)
        produitScalaire = np.dot(vecteur2, vecteur3)
        d = dist(p, pDepart)
        #On regarde si tous les produit scalaire sont du meme signe ou pas:
        if (produitScalaire>=0):
            lPositif.append([p,d])
        else :
            lNegatif.append([p,d])



    if (len(lPositif)>0 and len(lNegatif)>0):
        dmax1 = -1
        dmax2 = -1
        for j in range(len(lPositif)):
            dActuel = lPositif[j][1]
            if dActuel>dmax1:
                pContour1=lPositif[j][0]
                dmax1=dActuel
        for j in range(len(lNegatif)):
            dActuel = lNegatif[j][1]
            if dActuel>dmax2:
                pContour2=lNegatif[j][0]
                dmax2=dActuel
    else :
        if len(lPositif)==0:
            listeNonVide = lNegatif
        else :
            listeNonVide = lPositif
        #on prend + proche et + loin
        dmax=-1
        dmin=999999999999
        for j in range(len(listeNonVide)):
            dActuel = listeNonVide[j][1]
            if dActuel>dmax:
                pContour1=listeNonVide[j][0]
                dmax=dActuel
            if dActuel<dmin:
                pContour2=listeNonVide[j][0]
                dmin=dActuel


    if debug == True :
        cv2.circle(input, tuple([int(pDepart[0]), int(pDepart[1])]), 1, [0, 255, 0], -1)
        cv2.circle(input, tuple([int(pContour1[0]), int(pContour1[1])]), 7, [0, 0,255], -1)
        cv2.circle(input, tuple([int(pContour2[0]), int(pContour2[1])]), 7, [0, 0, 255], -1)
        cv2.imshow("detection point contour", input)
        print("debug")


    return pContour1, pContour2





#methode cercle :
    #la feuille est supposee symetrique
    #On parcours la moitie des points et 1 point sur 5 (d'ou le /10 et le i*5)
    #Pour chaque point on cherche celui en face par rapport au centre
    #On mesure la distance entre les 2 points opposes
    #On regarde si c'est constant
    #(plus precis que regarder les distance centre-bord mais plus long a calculer)
def checkCercle(contourUtile, centre, input, debug = False):
    cX, cY = centre
    cercle = False

    listeDiametre = np.array([])
    print "Cercle-progres :",
    for i in range(int(len(contourUtile)/10.0)):
        point = contourUtile[5*i][0]
        if debug == True :
            cv2.circle(input, tuple(point), 2, [0, 0, 100], -1)
        pX, pY = point
        vPointCentre = [cX - pX, cY - pY]
        p1, p2 = trouverPointContour([cX, cY], vPointCentre, contourUtile, input)
        d = dist(p1, p2)
        listeDiametre = np.append(listeDiametre, d)
        if (int(i/(len(contourUtile)/10.0)*100)%10 ==0):
            print "{} %  ".format(int(i/(len(contourUtile)/10.0)*100)),
    print ""

    if debug == True :
        print("cercle : ecart type des diametres : {}".format(listeDiametre.std()))
        cv2.circle(input, tuple(centre), 7, [0, 0, 255], -1)
        cv2.imshow("cercle", input)

    if (listeDiametre.std() < 15):  # 20 : valeur a ajuster
        cercle = True

    return cercle

def checkRectangle(contourUtile, centre, input, debug = False):
    # methode rectangle :
    # Calcul distance centre -> contour :
    cX, cY = centre
    rectangle = False
    listeDistanceCentreContour = np.array([])
    for i in range(len(contourUtile)):
        point = contourUtile[i][0]
        pX, pY = point
        distance = ((cX - pX) ** 2 + (cY - pY) ** 2) ** 0.5
        listeDistanceCentreContour = np.append(listeDistanceCentreContour, distance)

    # On cherche le grand axe
    indiceGrandAxe1 = listeDistanceCentreContour.argmax()  # le point le plus loin du centre
    pointGrandAxe1 = contourUtile[indiceGrandAxe1][0]


    # le point de l'autre cote -> celui qui a la plus grande distance avec lui
    dMax = -1
    for i in range(len(contourUtile)):
        point = contourUtile[i][0]
        pX, pY = point
        distance = dist(pointGrandAxe1, [pX, pY])
        if distance > dMax:
            dMax = distance
            pointGrandAxe2 = contourUtile[i][0]

    vecGrandAxe = [pointGrandAxe2[0] - pointGrandAxe1[0], pointGrandAxe2[1] - pointGrandAxe1[1]]
    vecPerpGrandAxe = [-vecGrandAxe[1], vecGrandAxe[0]]


    # On parcours le grand axe et on mesure les longueurs sur a peu pres tout l'axe (on ignore les extremites
    # car les feuilles rectangulaires le sont vers le centre)
    # EX : Si la feuille est entre 0 et 10, on va regarder entre 2 et 8 pour enlever la pointe
    listeDistPerp = np.array([])
    for i in range(0, 41):
        pourcent = 0.20 + i * 0.015
        pDepart = [float(pointGrandAxe1[0]) + pourcent * vecGrandAxe[0],
                   float(pointGrandAxe1[1]) + pourcent * vecGrandAxe[1]]
        sommetA, sommetB = trouverPointContour(pDepart, vecPerpGrandAxe, contourUtile, input)
        d = dist(sommetA, sommetB)
        listeDistPerp = np.append(listeDistPerp, d)

    if debug == True :
        cv2.circle(input, tuple(pointGrandAxe1), 7, [0,0,255], -1)
        cv2.circle(input, tuple(pointGrandAxe2), 7, [0,0,255], -1)
        print("Rectangle : std des distance perpendiculaire = {}".format(listeDistPerp.std()))

    # Si les longueur perpendiculaires au grand axe sont 'constantes' c'est un rectangle
    if listeDistPerp.std() < 15:
        rectangle = True

    return rectangle, pointGrandAxe1, pointGrandAxe2

def checkCarre(pointGrandAxe1, pointGrandAxe2, contourUtile, input, debug = False):
    carre = False
    vecGrandAxe = [pointGrandAxe2[0] - pointGrandAxe1[0], pointGrandAxe2[1] - pointGrandAxe1[1]]
    vecPetitAxe = [-vecGrandAxe[1], vecGrandAxe[0]]
    centreGrandAxe = [float(pointGrandAxe1[0]) + 0.5 * vecGrandAxe[0],
                      float(pointGrandAxe1[1]) + 0.5 * vecGrandAxe[1]]
    pointPetitAxe1, pointPetitAxe2 = trouverPointContour(centreGrandAxe, vecPetitAxe, contourUtile, input)
    p = dist(pointGrandAxe1, pointGrandAxe2)  # longueur grand axe
    q = dist(pointPetitAxe1, pointPetitAxe2)  # longueur petit axe

    if debug == True:
        print("Longueur grand axe (p): {}".format(p))
        print("Longueur petit axe (q): {}".format(q))
        print("q/p= {}".format(q/p))

    # On regarde si c'est un carre (petit grand axe = grand axe +-10%):
    if (0.9 <= q/p) and (q/p <= 1.1):
        carre = True

    return carre

def checkEllipse(pointGrandAxe1, pointGrandAxe2, contourUtile, input, debug = False):
    ellipse = False
    vecGrandAxe = [pointGrandAxe2[0] - pointGrandAxe1[0], pointGrandAxe2[1] - pointGrandAxe1[1]]
    vecPerp =[-vecGrandAxe[1], vecGrandAxe[0]]
    # Demi grand axe : On va au centre du grand axe et on cherche les points
    centreGrandAxe = [float(pointGrandAxe1[0]) + 0.5 * vecGrandAxe[0],
                      float(pointGrandAxe1[1]) + 0.5 * vecGrandAxe[1]]
    pointPetitAxe1, pointPetitAxe2 = trouverPointContour(centreGrandAxe, vecPerp, contourUtile, input)
    vecPetitAxe = [pointPetitAxe2[0] - pointPetitAxe1[0], pointPetitAxe2[1] - pointPetitAxe1[1]]

    p = dist(pointGrandAxe1, pointGrandAxe2)  # longueur grand axe
    q = dist(pointPetitAxe1, pointPetitAxe2)  # longueur petit axe

    # calcul des foyers
    c = ((p / 2.0) ** 2 - (q / 2.0) ** 2) ** 0.5
    vecGrandAxeNorm = np.array(vecGrandAxe)
    vecGrandAxeNorm = vecGrandAxeNorm / np.linalg.norm(vecGrandAxeNorm)

    foyer1 = [int(centreGrandAxe[0] + c * vecGrandAxeNorm[0]),
              int(centreGrandAxe[1] + c * vecGrandAxeNorm[1])]
    foyer2 = [int(centreGrandAxe[0] - c * vecGrandAxeNorm[0]),
              int(centreGrandAxe[1] - c * vecGrandAxeNorm[1])]

    # Ellipse si en tout point du contour : distance(foyer1-contour)+distance(foyer2-contour) = cte
    listeDistanceEllipse = np.array([])
    for i in range(len(contourUtile)):
        pt = contourUtile[i][0]
        d1 = dist(pt, foyer1)
        d2 = dist(pt, foyer2)
        dsomme = d1 + d2
        listeDistanceEllipse = np.append(listeDistanceEllipse, dsomme)

    # On peut regarder aussi si petit et grd axe sont axes de symetrie
    # On prend 2 point sur le grd axe symetrique par rapport au centre
    # On regarde la largeur au niveau de ces point et on verifie que c'est semblable
    p1 = [int(float(pointGrandAxe1[0]) + 0.2 * vecGrandAxe[0]),
          int(float(pointGrandAxe1[1]) + 0.2 * vecGrandAxe[1])]
    p2 = [int(float(pointGrandAxe1[0]) + 0.8 * vecGrandAxe[0]),
          int(float(pointGrandAxe1[1]) + 0.8 * vecGrandAxe[1])]
    p1a, p1b = trouverPointContour(p1, vecPetitAxe, contourUtile, input)
    p2a, p2b = trouverPointContour(p2, vecPetitAxe, contourUtile, input)
    l1 = dist(p1a, p1b)
    l2 = dist(p2a, p2b)
    r1 = l1 / l2

    #On fait pareil mais selon le petit axe
    p3 = [int(float(pointPetitAxe1[0]) + 0.2 * vecPetitAxe[0]),
          int(float(pointPetitAxe1[1]) + 0.2 * vecPetitAxe[1])]
    p4 = [int(float(pointPetitAxe1[0]) + 0.8 * vecPetitAxe[0]),
          int(float(pointPetitAxe1[1]) + 0.8 * vecPetitAxe[1])]
    p3a, p3b = trouverPointContour(p3, vecGrandAxe, contourUtile, input)
    p4a, p4b = trouverPointContour(p4, vecGrandAxe, contourUtile, input)
    l3 = dist(p3a, p3b)
    l4 = dist(p4a, p4b)
    r2 = l3 / l4

    if debug == True :
        cv2.circle(input, tuple(pointGrandAxe1), 7, [0,0,255], -1)
        cv2.circle(input, tuple(pointGrandAxe2), 7, [0,0,255], -1)
        cv2.circle(input, tuple(pointPetitAxe1), 7, [0,0,255], -1)
        cv2.circle(input, tuple(pointPetitAxe2), 7, [0,0,255], -1)
        cv2.circle(input, tuple(foyer1), 7, [0,0,170], -1)
        cv2.circle(input, tuple(foyer2), 7, [0,0,170], -1)
        #Les points pour verifier la symetrie
        cv2.circle(input, tuple(p1), 7, [255,0,0], -1)
        cv2.circle(input, tuple(p2), 7, [255,0,0], -1)
        cv2.circle(input, tuple(p3), 7, [255,0,0], -1)
        cv2.circle(input, tuple(p4), 7, [255,0,0], -1)
        print("rapport pour symetrie: r1= {}, r2={}".format(r1,r2))
        print("std distance: {}".format(listeDistanceEllipse.std()))
        cv2.imshow("Ellipse", input)

    # Si les longueurs sont proches et qu'on a une symetrie (approximatoin, on a pas des formes parfaites)
    if (listeDistanceEllipse.std() < 30) and (0.8 <= r1 and r1 <= 1.2) and (0.8 <= r2 and r2 <= 1.2):
        ellipse = True

    return ellipse


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


def etude_classificateur(convexite, dents, triangle, cercle, rectangle, carre, ellipse, jsonPath):
    # ouverture du fichier JSON et mise sous forme de dictionnaire
    with open(jsonPath) as json_data:
        data_dict = json.load(json_data)

    #On stock les resultats sous forme de couple (espece, pourcentage de criteres remplis)
    listeResultat = []

    for cle in data_dict.items(): #on parcours les differents types d'arbres
        espece = cle[0]
        nbrAttribus = len(cle[1])
        nbrPositif = 0

        convexiteTheorique = cle[1].get("convexe")

        for cle2 in cle[1].items(): #On parcours les differents attrabuts et leurs valeurs
            if (cle2[0] == "convexe" and cle2[1] == convexite):
                nbrPositif += 1
            if (cle2[0] == "dent" and cle2[1] == dents):
                nbrPositif += 1
            if (convexiteTheorique == True):
                if (cle2[0] == "triangle" and cle2[1] == triangle):
                    nbrPositif += 1
                if (cle2[0] == "cercle" and cle2[1] == cercle):
                    nbrPositif += 1
                if (cle2[0] == "rectangle" and cle2[1] == rectangle):
                    nbrPositif += 1
                if (cle2[0] == "carre" and cle2[1] == carre):
                    nbrPositif += 1
                    print("carre")
                if (cle2[0] == "ellipse" and cle2[1] == ellipse):
                    print("ellipse")
                    nbrPositif += 1

        listeResultat.append((espece, float(nbrPositif) / float(nbrAttribus) * 100))
    listeResultat = sorted(listeResultat, key=lambda colonnes: colonnes[1], reverse= True)
    return listeResultat

def main():
    # input = cv2.imread("base_donnee_feuille/hetre/hetre1.jpg")
    # input = cv2.imread("base_donnee_feuille/hetre/hetre2.jpg")
    # input = cv2.imread("base_donnee_feuille/chene/chene1.jpg")
    input = cv2.imread("base_donnee_feuille/chene/chene2.jpg")
    # input = cv2.imread("base_donnee_feuille/margousier/margousier2.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau1.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau2.jpg")
    # input = cv2.imread("base_donnee_feuille/bouleau/bouleau3.jpg")
    # input = cv2.imread("base_donnee_feuille/platane/platane1.jpg")


    input = redimension(input)
    cv2.imshow("feuille", input)

    thresh, contourUtileBase, contourConvexBase = segmentation(input)

    height, width, channels = input.shape

    #Retirer la queue et avoir un masque utilisable pour determiner la forme
    masquethresh, contourUtileMasque, contourConvexMasque, centreMasque = masqueSansQueue(thresh)



    #TODO : regarder pour les feuille pas entiere si les bord sont pointus (platane) ou arrondi (chene)
    #TODO : regarde la largeur des feuilles : pour difference le margousier et le bouleau


    # Detection forme : triangle
    triangle = checkTriangle(input, contourUtileMasque, contourConvexMasque, centreMasque)
    print("Forme triangle : {}".format(triangle))
    # Detection forme : cercle
    cercle = checkCercle(contourUtileMasque, centreMasque, input)
    print("Forme cercle : {}".format(cercle))
    # Detection forme : rectangle
    rectangle, grandAxe1, grandAxe2 = checkRectangle(contourUtileMasque, centreMasque, input)
    print("Forme rectangle : {}".format(rectangle))
    # Detection forme : carre
    carre = checkCarre(grandAxe1, grandAxe2, contourUtileMasque, input)
    print("Forme carre : {}".format(carre))
    # Detection forme : ellipse
    ellipse = checkEllipse(grandAxe1, grandAxe2, contourUtileMasque, input)
    print("Forme ellipse : {}".format(ellipse))

    #detection dent :
    dents = detection_dent(contourUtileBase, input)
    print("presence de dent : {}".format(dents))

    #detection convexite :
    convexite= feuille_convexe(contourUtileBase, contourConvexBase, input, True)
    print("feuille entiere : {}".format(convexite))

    listeResultat = etude_classificateur(convexite, dents, triangle, cercle, rectangle, carre, ellipse, 'arbre.json')
    print(listeResultat)

    cv2.waitKey(0)

main()
