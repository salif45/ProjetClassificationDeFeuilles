# Documentation: http://zetcode.com/gui/pyqt5/

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import math
import glob
import string
import contour
import numpy as np
import cv2 as cv2



class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.name = ""
        self.CurrentFolder = ""
        self.listImageCurrentFolder = []
        self.listFolder = []
        self.begin = [-1,-1]
        self.beginColor = [-1,-1]
        self.end = [-1,-1]
        self.endColor = [-1,-1]
        self.crop = False
        self.LPen = 0
        self.currentImage = None
        self.CentralWidget = QWidget()
        self.lbl_down = QLabel()
        self.lbl_top = QLabel()
        self.initUI()

    def initUI(self):

        ##### Action & Shortcut #####
        ExitApp = QAction(QIcon('exit.png'), '&Exit', self)
        ExitApp.setShortcut('Ctrl+Q')
        ExitApp.setStatusTip('Exit application')
        ExitApp.triggered.connect(self.close)

        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.addImage)

        ##### Menubar #####
        
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(ExitApp)

        ##### Buttons #####
        
        # QuitButton = QPushButton('Quit', self)
        #
        # QuitButton.clicked.connect(self.close)

        OpenButton = QPushButton('Open', self)
        OpenButton.clicked.connect(self.addImage)

        CropButton = QPushButton('Crop', self)
        CropButton.clicked.connect(self.cropImage)

        AnalyseButton = QPushButton('Analyse', self)
        AnalyseButton.clicked.connect(self.Analyse)

        SegmentationButton = QPushButton('Segmentation', self)
        SegmentationButton.clicked.connect(self.Segmentation)

        RestartButton = QPushButton('Restart', self)
        RestartButton.clicked.connect(self.Restart)

        hbox_top = QHBoxLayout()
        hbox_top.addStretch(1)
        hbox_top.addWidget(self.lbl_top)
        hbox_top.addStretch(1)


        hbox1 = QHBoxLayout()
        pixmap = QPixmap()
        self.lbl_down.setPixmap(pixmap)

        hbox1.addWidget(self.lbl_down)

        hbox = QHBoxLayout()
        hbox.addWidget(OpenButton)
        hbox.addStretch(1)
        hbox.addWidget(CropButton)
        hbox.addStretch(1)
        hbox.addWidget(SegmentationButton)
        hbox.addStretch(1)
        hbox.addWidget(AnalyseButton)
        hbox.addStretch(1)
        hbox.addWidget(RestartButton)


        self.lbl_top.setText("Choisir votre image")

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_top)
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.CentralWidget.setLayout(vbox)

        self.setCentralWidget(self.CentralWidget)
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('Tooltips')
        self.show()

    def showDialog(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file', self.directory)

        if fname[0]:
            self.name = fname[0]
            self.CurrentFolder = (self.name.rsplit('/',1))[0] + '/'
            self.listAllImage()
            self.listAllFolder()
            self.crop = False
            self.currentImage = QPixmap(self.name)

    def listAllImage(self):
        test = self.CurrentFolder + "*.jpg"
        test1 = self.CurrentFolder + "*.jpeg"
        test2 = self.CurrentFolder + "*.png"
        self.listImageCurrentFolder.clear()
        self.listImageCurrentFolder = glob.glob(test) + glob.glob(test1) + glob.glob(test2)

    def listAllFolder(self):

        folder = self.CurrentFolder.rsplit('/',2)[0]
        test = folder + "/*/"
        self.listFolder = glob.glob(test)
        for dossier in self.listFolder:
            test = dossier + "/*.jpg"
            test1 = dossier + "/*.jpeg"
            test2 = dossier + "/*.png"
            Images = glob.glob(test) + glob.glob(test1) + glob.glob(test2)
            if len(Images) <= 0:
                self.listFolder.remove(dossier)

    def printImage(self):

        pixmap = self.currentImage

        height = pixmap.height()
        width = pixmap.width()
        LARGEUR = 500
        facteur = float(LARGEUR) / float(width)

        pixmap = pixmap.scaled(width*facteur, height*facteur)
        height = pixmap.height()
        width = pixmap.width()

        self.currentImage = pixmap
        self.lbl_down.clear()
        self.lbl_down.resize(width, height)
        self.lbl_down.setPixmap(pixmap)
        self.setGeometry(100, 100, width, height)
        self.show()

    def addImage(self):

        self.showDialog()
        self.printImage()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:

            self.printImage()
            x = e.x() - 10
            y = e.y() - 10
            pic = self.lbl_down.pixmap()
            if ( x >= -10 and x <= pic.width() + 10 and y >= -10 and y <= pic.height() + 10):
                if (x < 0):
                    x = 0
                if (x >=pic.width()):
                    x = pic.width() - 1
                if (y < 0):
                    y = 0
                if (y >= pic.height()):
                    y = pic.height() - 1

                self.begin =[x,y]
                self.LPen = 0

        elif e.button() == Qt.RightButton:

            self.printImage()
            x = e.x() - 10
            y = e.y() - 10
            pic = self.lbl_down.pixmap()
            if (x >= -10 and x <= pic.width() + 10 and y >= -10 and y <= pic.height() + 10):
                if (x < 0):
                    x = 0
                if (x >= pic.width()):
                    x = pic.width() - 1
                if (y < 0):
                    y = 0
                if (y >= pic.height()):
                    y = pic.height() - 1
                self.LPen = 1
                self.beginColor = [x, y]

    def mouseMoveEvent(self, e):

        if self.LPen == 0:

            self.printImage()
            x = e.x() - 10
            y = e.y() - 10
            pic = self.lbl_down.pixmap()
            if (x < 0):
                x = 0
            if (x >= pic.width()):
                x = pic.width() - 1
            if (y < 0):
                y = 0
            if (y >= pic.height()):
                y = pic.height() - 1

            qp = QPainter(pic)
            pen = QPen()
            pen.setWidth(2)
            pen.setColor(QColor(255,0,0))
            qp.setPen(pen)
            Rect = QRect(self.begin[0], self.begin[1], x - self.begin[0], y - self.begin[1]);
            qp.drawRect(Rect)
            self.lbl_down.setPixmap(pic)

        else:

            self.printImage()
            x = e.x() - 10
            y = e.y() - 10
            pic = self.lbl_down.pixmap()
            if (x < 0):
                x = 0
            if (x >= pic.width()):
                x = pic.width() - 1
            if (y < 0):
                y = 0
            if (y >= pic.height()):
                y = pic.height() - 1

            qp = QPainter(pic)
            pen = QPen()
            pen.setWidth(2)
            pen.setColor(QColor(0, 0, 255))
            qp.setPen(pen)
            Rect = QRect(self.beginColor[0], self.beginColor[1], x - self.beginColor[0], y - self.beginColor[1]);
            qp.drawRect(Rect)
            self.lbl_down.setPixmap(pic)

    def mouseReleaseEvent(self, e):

        if e.button() == Qt.LeftButton:
            x = e.x() - 10
            y = e.y() - 10
            pic = self.lbl_down.pixmap()
            if (x < 0):
                x = 0
            if (x >=pic.width()):
                x = pic.width() - 1
            if (y < 0):
                y = 0
            if (y >= pic.height()):
                y = pic.height() - 1
            qp = QPainter(pic)
            pen = QPen()
            pen.setWidth(2)
            pen.setColor(QColor(255,0,0))
            qp.setPen(pen)
            Rect = QRect(self.begin[0], self.begin[1], x - self.begin[0], y - self.begin[1]);
            qp.drawRect(Rect)
            self.lbl_down.setPixmap(pic)
            self.end = [x,y]

        elif e.button() == Qt.RightButton:

            x = e.x() - 10
            y = e.y() - 10
            pic = self.lbl_down.pixmap()
            if (x < 0):
                x = 0
            if (x >=pic.width()):
                x = pic.width() - 1
            if (y < 0):
                y = 0
            if (y >= pic.height()):
                y = pic.height() - 1
            qp = QPainter(pic)
            pen = QPen()
            pen.setWidth(2)
            pen.setColor(QColor(0,0,255))
            qp.setPen(pen)
            Rect = QRect(self.beginColor[0], self.beginColor[1], x - self.beginColor[0], y - self.beginColor[1]);
            qp.drawRect(Rect)
            self.lbl_down.setPixmap(pic)
            self.endColor = [x,y]

    def cropImage(self):

        if self.begin[0] != -1 and self.begin[1] != -1 and self.end[0] != -1 and self.end[1] !=-1:
            pixmap = self.currentImage
            x, y = self.begin
            x1, y1 = self.end
            width = x1 - x
            height = y1 - y

            if width < 0:
                a = x1
                x1 = x
                x = a
            if height < 0:
                a = y1
                y1 = x
                y = a
            copy = pixmap.copy(x, y, abs(width), abs(height))

            LARGEUR = 500
            facteur = float(LARGEUR) / float(abs(width))
            pixmap = copy.scaled(abs(width) * facteur, abs(height) * facteur)
            height = pixmap.height()
            width = pixmap.width()

            self.currentImage = pixmap
            self.crop = True
            self.lbl_down.clear()
            self.lbl_down.resize(width, height)
            self.lbl_down.setPixmap(copy)
            self.setGeometry(100, 100, width, height)
            self.show()
            
    def keyPressEvent(self, event):

        self.crop = False
        key = event.key()
        self.begin = [-1,-1]
        self.end = [-1,-1]
        if key == Qt.Key_Q:
            index = self.listImageCurrentFolder.index(self.name)
            length = len(self.listImageCurrentFolder)
            if index == 0:
                index = length - 1
                self.name = self.listImageCurrentFolder[index]
                self.currentImage = QPixmap(self.name)

            else:
                index -= 1
                self.name = self.listImageCurrentFolder[index]
                self.currentImage = QPixmap(self.name)

            self.printImage()

        elif key == Qt.Key_D:
            index = self.listImageCurrentFolder.index(self.name)
            length = len(self.listImageCurrentFolder)
            if index == length - 1:
                index = 0
                self.name = self.listImageCurrentFolder[index]
                self.currentImage = QPixmap(self.name)

            else:
                index += 1
                self.name = self.listImageCurrentFolder[index]
                self.currentImage = QPixmap(self.name)

            self.printImage()

        elif key == Qt.Key_S:
            index = self.listFolder.index(self.CurrentFolder)
            length = len(self.listFolder)
            if index == 0:
                index = length - 1
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]
                self.currentImage = QPixmap(self.name)

            else:
                index -= 1
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]
                self.currentImage = QPixmap(self.name)

            self.printImage()

        elif key == Qt.Key_Z:
            index = self.listFolder.index(self.CurrentFolder)
            length = len(self.listFolder)
            if index == length - 1:
                index = 0
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]
                self.currentImage = QPixmap(self.name)

            else:
                index += 1
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]
                self.currentImage = QPixmap(self.name)

            self.printImage()

        elif key == Qt.Key_Escape:
            self.close()


    def Segmentation(self):
        print("coucou")
        
    def Analyse(self):
        # contour.main()
        Image = self.currentImage.toImage()
        if os. path. isfile("image_to_analyse.bmp"):
            os.remove("image_to_analyse.bmp")
            print("removed")
        Image.save("image_to_analyse.bmp", quality=100)
        # im = cv2.imread('image_to_analyse.bmp')
        listResult = contour.analyse("image_to_analyse.bmp")
        self.currentImage = QPixmap("image_to_analyse.bmp")
        self.printImage
        self.lbl_top.setText("Resultat : {} ({}%) ou {} ({}%)".format(listResult[0][0],listResult[0][1], listResult[1][0], listResult[1][1]))
        Image = None

    def Restart(self):
        self.currentImage = QPixmap(self.name)
        self.printImage()
        self.begin = [-1, -1]
        self.beginColor = [-1, -1]
        self.end = [-1, -1]
        self.endColor = [-1, -1]
        self.crop = False
        self.LPen = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
