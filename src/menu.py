# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/mainUI.ui'
#
# Created: Mon Jul 20 18:34:26 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_guiDlg(object):
    def setupUi(self, guiDlg):
        guiDlg.setObjectName("guiDlg")
        guiDlg.resize(400, 300)

        self.retranslateUi(guiDlg)
        QtCore.QMetaObject.connectSlotsByName(guiDlg)

    def retranslateUi(self, guiDlg):
        guiDlg.setWindowTitle(QtGui.QApplication.translate("guiDlg", "mapgenerator", None, QtGui.QApplication.UnicodeUTF8))
        
        self.menu = QtGui.QMenuBar(guiDlg)
	self.menu.setFixedWidth(300);
	self.menuFile = self.menu.addMenu('File')
	self.menuSim = self.menu.addMenu('Simulation')
	
	self.actionOpen = self.menuFile.addAction('Open')
	self.actionSave = self.menuFile.addAction('Save')
	self.actionEdit = self.menuFile.addAction('Edit')
	self.actionDock = self.menuFile.addAction('Dock')
	self.actionExit = self.menuFile.addAction('Exit')
	
	
	#self.connect(self.actionOpen, QtCore.SIGNAL("triggered(bool)"), self.openFile)
	#self.connect(self.actionSave, QtCore.SIGNAL("triggered(bool)"), self.saveFile)
	#self.connect(self.actionEdit, QtCore.SIGNAL("triggered(bool)"), self.runEditor)
	#self.connect(self.actionDock, QtCore.SIGNAL("triggered(bool)"), self.changeDock)
	#self.connect(self.actionExit, QtCore.SIGNAL("triggered(bool)"), self.forceExit)