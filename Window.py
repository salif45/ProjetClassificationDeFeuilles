# Documentation: http://zetcode.com/gui/pyqt5/

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import math
import glob
import string

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.name = ""
        self.CurrentFolder = ""
        self.listImageCurrentFolder = []
        self.listFolder = []
        self.begin = [-1,-1]
        self.end = [-1,-1]
        self.CentralWidget = QWidget()
        self.lbl = QLabel()
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
        
        QuitButton = QPushButton('Quit', self)

        QuitButton.clicked.connect(self.close)

        OpenButton = QPushButton('Open', self)
        OpenButton.clicked.connect(self.addImage)

        CropButton = QPushButton('Crop', self)
        CropButton.clicked.connect(self.getContour)

        hbox = QHBoxLayout()
        hbox.addWidget(QuitButton)
        hbox.addStretch(1)
        hbox.addWidget(CropButton)
        hbox.addStretch(1)
        hbox.addWidget(OpenButton)


        hbox1 = QHBoxLayout()
        pixmap = QPixmap()
        self.lbl.setPixmap(pixmap)

        hbox1.addWidget(self.lbl)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.CentralWidget.setLayout(vbox)

        self.setCentralWidget(self.CentralWidget)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Tooltips')
        self.show()

    def showDialog(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file', self.directory)

        if fname[0]:
            self.name = fname[0]
            self.CurrentFolder = (self.name.rsplit('/',1))[0] + '/'
            self.listAllImage()
            self.listAllFolder()

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
        print(self.listFolder)

    def printImage(self):
        pixmap = QPixmap(self.name)
        height = pixmap.height()
        width = pixmap.width()
        LARGEUR = 500

        facteur = float(LARGEUR) / float(width)

        pixmap = pixmap.scaled(width*facteur, height*facteur)
        height = pixmap.height()
        width = pixmap.width()
        self.lbl.clear()
        self.lbl.resize(width, height)
        self.lbl.setPixmap(pixmap)
        self.setGeometry(300, 300, width, height)
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

    def mouseMoveEvent(self, e):

        self.printImage()
        x = e.x() - 10
        y = e.y() - 10
        pic = self.lbl.pixmap()
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
        qp.setPen(pen)
        Rect = QRect(self.begin[0], self.begin[1], x - self.begin[0], y - self.begin[1]);
        qp.drawRect(Rect)
        self.lbl.setPixmap(pic)

    def mousePressEvent(self, e):
        self.printImage()
        x = e.x() - 10
        y = e.y() - 10
        pic = self.lbl.pixmap()
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

    def mouseReleaseEvent(self, QMouseEvent):

        x = QMouseEvent.x() - 10
        y = QMouseEvent.y() - 10
        pic = self.lbl.pixmap()
        if ( x >= -10 and x <= pic.width() + 10 and y >= -10 and y <= pic.height() + 10):
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
            qp.setPen(pen)
            Rect = QRect(self.begin[0], self.begin[1], x - self.begin[0], y - self.begin[1]);
            qp.drawRect(Rect)
            self.lbl.setPixmap(pic)
            self.end = [x,y]

    def getContour(self):

        if (self.begin[0] != -1 and self.begin[1] != -1 and self.end[0] != -1 and self.end[1] !=-1):
            print('getcontour',self.begin,self.end)

    # def paintEvent(self, paint_event):
    #     qp = QPainter(self)
    #     if (self.begin[0] != -1 and self.begin[0] != 1):
    #         qp.drawPixmap(self.rect(),self.lbl.pixmap())
    #         pen = QPen()
    #         pen.setWidth(20)
    #         pen.setColor(QColor(255,0,0))
    #         qp.setPen(pen)
    #         qp.setRenderHint(QPainter.Antialiasing, True)
    #         qp.drawPoint(self.begin[0], self.begin[1])


    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Q:
            index = self.listImageCurrentFolder.index(self.name)
            length = len(self.listImageCurrentFolder)
            if index == 0:
                index = length - 1
                self.name = self.listImageCurrentFolder[index]
            else:
                index -= 1
                self.name = self.listImageCurrentFolder[index]
            self.printImage()

        elif key == Qt.Key_D:
            index = self.listImageCurrentFolder.index(self.name)
            length = len(self.listImageCurrentFolder)
            if index == length - 1:
                index = 0
                self.name = self.listImageCurrentFolder[index]
            else:
                index += 1
                self.name = self.listImageCurrentFolder[index]
            self.printImage()

        elif key == Qt.Key_S:
            index = self.listFolder.index(self.CurrentFolder)
            length = len(self.listFolder)
            if index == 0:
                index = length - 1
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]
            else:
                index -= 1
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]

            print(self.CurrentFolder)
            self.printImage()

        elif key == Qt.Key_Z:
            index = self.listFolder.index(self.CurrentFolder)
            length = len(self.listFolder)
            if index == length - 1:
                index = 0
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]
            else:
                index += 1
                self.CurrentFolder = self.listFolder[index]
                self.listAllImage()
                self.name = self.listImageCurrentFolder[0]
            self.printImage()
            print(self.CurrentFolder)

        elif key == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
