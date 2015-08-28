#
# Copyright (C) 2015 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, os, Ice, traceback
import math as m
import copy
import pickle
import gtk
import random
import matplotlib.colors as colors

from genericworker import *


ROBOCOMP = ''
try:
	ROBOCOMP = os.environ['ROBOCOMP']
except:
	print '$ROBOCOMP environment variable not set, using the default value /opt/robocomp'
	ROBOCOMP = '/opt/robocomp'
if len(ROBOCOMP)<1:
	print 'genericworker.py: ROBOCOMP environment variable not set! Exiting.'
	sys.exit()


preStr = "-I"+ROBOCOMP+"/interfaces/ --all "+ROBOCOMP+"/interfaces/"
Ice.loadSlice(preStr+"Laser.ice")
from RoboCompLaser import *


class Capture(object):
	def __init__(self, name, color, data):
		self.name = name
		self.color = color
		self.points = data
		# GET BASE STATE ?????????
		self.tx = 0
		self.tz = 0
		self.ry = 0

class MyGraphicsScene(QtGui.QGraphicsScene):
	def __init__(self):
		super(MyGraphicsScene, self).__init__()

	def mousePressEvent(self, event):
		x = event.scenePos().x()
		z = event.scenePos().y()
		print 'click', x, z

class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		### GET THE SCREEN SIZE IN ORDER TO SET THE WINDOW SIZE
		window = gtk.Window()
		screen = window.get_screen()
		# TODO detectar pantallas
		#self.setFixedSize(gtk.gdk.screen_width()-20,gtk.gdk.screen_height()-40)
		self.setFixedSize(gtk.gdk.screen_width()/2-20,gtk.gdk.screen_height()-20) 

		### PREPARE THE SCENE:		
		self.maxRect = 50
		self.sceneLaser = MyGraphicsScene()
		self.sceneLaser.setSceneRect(0, 0, self.maxRect, self.maxRect)
		self.ui.graphicsViewLaser.setScene(self.sceneLaser)
		###
		self.maxdistance = 5000
		self.ignoreControl = False
		self.ignoreActivation = False
		### ATRIBUTTES
		self.captureFiles =  dict()
		self.colorsDict = {'blue':'#0000FF', 'yellow':'#FFFF00', 'green':'#00FF00','red':'#FF0000', 'pink':'#FF00FF', 'orange':'#FF6600','brown':'#660000'}
		self.ui.colorBox.addItem("not displayed")
		for color in self.colorsDict.keys():
			self.ui.colorBox.addItem(color)
		self.captureColor = 0
		self.saveNumber = 0
		self.captureNumber = 0
		self.captures = [] # Array de capturas
		### CONNECT THE COMPUTE
		self.timer.timeout.connect(self.compute)
		self.Period = 100
		self.timer.start(self.Period)


	def setParams(self, params):
		return True


	@QtCore.Slot()
	def compute(self):
		self.sceneLaser.clear()			
		w = 2500
		self.sceneLaser.addEllipse(-w/2,-w/2,w,w,QtGui.QPen(QtGui.QColor(200,100,0)))
		points = self.laser_proxy.getLaserData()
		rad = 1
		current = Capture('current', 'black', points) # Guardamos putos en la captura actual
		allCaptures = copy.deepcopy(self.captures)    # Sacamos todas las capturas salvadas anteriormente
		# Guardamos en allCaptures  la captura actual (No la estamos metiendo en las capturas salvadas)
		if self.ui.showCurrent.isChecked(): allCaptures += [current]
		xr, zr =  self.getRadiusCapture(allCaptures)
		for capture in allCaptures:
			if capture.color == "not displayed": continue		
			for point in capture.points:
				x = 0
				z = 0
				if float(point.dist) < self.maxdistance:
					# Convertimos de polares (r, O) a cartesianas (x, y)
					x = m.sin(point.angle)*point.dist
					z = m.cos(point.angle)*point.dist

					## Rotamos el punto una vez en cartesianas
					#xp = x*m.cos(capture.ry) - z*m.sin(capture.ry)
					#zp = z*m.cos(capture.ry) + x*m.sin(capture.ry)
					## Desplazamos el punto
					#xpp = xp + capture.tx
					#zpp = zp + capture.tz
					##Pintamos
					#x = xpp /self.ui.zoom.value()
					#z = -zpp /self.ui.zoom.value()

					x = x /self.ui.zoom.value()
					z = z /self.ui.zoom.value()

					#if capture.color == "not displayed": pen = QtGui.QPen(QtGui.QColor(0,0,0))
					#else:
						#r = colors.hex2color(self.colorsDict[capture.color])[0]
						#g = colors.hex2color(self.colorsDict[capture.color])[1]
						#b = colors.hex2color(self.colorsDict[capture.color])[2]
						#print "RGB: ",r," ",g," ",b
						#pen = QtGui.QPen(QtGui.QColor(r,g,b))

					if capture.color == "red":     pen = QtGui.QPen(QtGui.QColor(255,0,0))
					elif capture.color == "green": pen = QtGui.QPen(QtGui.QColor(0,255,0))
					elif capture.color == "blue":  pen = QtGui.QPen(QtGui.QColor(0,0,255))
					else:                          pen = QtGui.QPen(QtGui.QColor(0,0,0))
					if str(self.ui.colorBox.currentText()) == "not displayed":
						pen = QtGui.QPen(QtGui.QColor(0,0,0))
					else:
						pen = QtGui.QPen(QtGui.QColor(self.colorsDict[str(self.ui.colorBox.currentText())]))					
					#if str(self.ui.colorBox.currentText()) == "not displayed":
						#pen = QtGui.QPen(QtGui.QColor(0,0,0))
					#else:
						#pen = QtGui.QPen(QtGui.QColor(self.colorsDict[str(self.ui.colorBox.currentText())]))
					#if str(self.ui.colorBox.currentText()) == "not displayed":
						#pen = QtGui.QPen(QtGui.QColor(0,0,0))
					#else:
						#pen = QtGui.QPen(QtGui.QColor(self.colorsDict[str(self.ui.colorBox.currentText())]))

					# TODO
					# Transform coordinates to QtSecene Reference
					# Check Scene Size
					self.sceneLaser.addEllipse(x-rad, -z-rad, rad*2.0, rad*2.0,pen) #FUNCIONA
					#self.sceneLaser.addEllipse(x-rad, z-rad+(radius/self.ui.zoom.value()), rad*2.0, rad*2.0,pen) #FUNCIONA
					# Example point in 0,0
					self.sceneLaser.addEllipse(0,0,5,5,pen)
		self.sceneLaser.update()



	##################################################
	### Returns the radius of the laser points captured
	### TODO CORREGIR PARA QUE LOS PUNTOS DEL LASER QUEDEN CENTRADOS EN EL WIDGET
	def getRadiusCapture(self, allCaptures):
		# TODO QUE SOLO COMPRUEBE EL MAYOR ANTERIOR CON LA CAPTURA ACTUAL
		maxXABS = -1
		maxZABS = -1
		maxX = -10000000000
		maxZ = -10000000000
		for capture in allCaptures:
			if capture.color == "not displayed": continue			
			for point in capture.points:
				x = m.sin(point.angle)*point.dist
				z = m.cos(point.angle)*point.dist
				
				# Pintamos
				x = x /self.ui.zoom.value()
				z = z /self.ui.zoom.value()
				
				if maxXABS < abs(x): 
					maxX    = x
					maxXABS = abs(x)
				if maxZABS < abs(z): 
					maxZ    = z
					maxZABS = abs(z)
		return maxXABS/2, maxZABS/2
		
		
	@QtCore.Slot()
	def on_saveButton_clicked(self):
            if not self.captures:
                QtGui.QMessageBox.critical(self, "ERROR", 
                    '''Not points capture!
                    ''', QtGui.QMessageBox.Ok)
            else:
		# ALERT : COMPROBAR
		### CALCULAR LAS LINEAS DEL CONTORNO, Y GUARDARLAS EN CAPTURE [(1-1)(2-2)]
				#TODO diccionario
		#if not self.ui.name.text() in self.captureFiles.keys():
			#self.captureFiles[self.ui.name.text()] = 0
		#else:
			#self.captureFiles[self.ui.name.text()] += 1		
		#from time import gmtime, strftime
		#timestamp = strftime("%Y-%m-%d_%H-%M", gmtime())
		#filename = self.ui.name.text() + "_" + str(self.captureFiles[self.ui.name.text()]) + timestamp
		#pickle.dump(self.captures, open(filename, 'w'))
		outfile = open("save_"+str(self.saveNumber)+".info", 'w')
		for capture in self.captures:
			outfile.write(capture.name +'\n')
			outfile.write(capture.color + '\n')
			outfile.write(str(capture.points) + '\n')
                    
		#pickle.dump(self.captures, open("save.pck"+str(self.saveNumber), 'w'))
		self.saveNumber += 1
		self.captures = []


	@QtCore.Slot()
	def on_loadButton_clicked(self):
            # TODO: captureNumber. Si el programa se cierra captureNumber sera 0, arreglar!!!!!
            for i in range(self.saveNumber):                
		self.captures = pickle.load(open("save"+str(self.saveNumber)+".info", 'r'))
		for capture in self.captures:
			self.ui.activationBox.addItem(capture.name)
			self.ui.controlBox.addItem(capture.name)


	@QtCore.Slot()
	def on_captureButton_clicked(self):
		name = "Capture_"+str(self.captureNumber)
		points = self.laser_proxy.getLaserData()
		color = self.colorsDict[str(self.ui.colorBox.currentText())]
		print color
		self.captures.append(Capture(name, color, points))
		self.ui.activationBox.addItem(name)
		self.ui.controlBox.addItem(name)
		self.captureNumber+=1

	@QtCore.Slot()
	def on_x_valueChanged(self):
		self.actualizaMedida()
	@QtCore.Slot()
	def on_z_valueChanged(self):
		self.actualizaMedida()
	@QtCore.Slot()
	def on_alpha_valueChanged(self):
		self.actualizaMedida()


	def actualizaMedida(self):
		if self.ignoreControl: return
		newx = self.ui.x.value()
		newz = self.ui.z.value()
		newa = self.ui.alpha.value()
		
		for c in self.captures:
			if self.ui.controlBox.currentText() == c.name:
				c.tx = newx
				c.tz = newz
				c.ry = newa
				print 'act', c.name, newx, newz, newa
		
		
	@QtCore.Slot()
	def on_controlBox_currentIndexChanged(self):
		self.ignoreControl = True
		for c in self.captures:
			if self.ui.controlBox.currentText() == c.name:
				self.ui.x.setValue(c.tx)
				self.ui.z.setValue(c.tz)
				self.ui.alpha.setValue(c.ry)
				print 'on_controlBox_currentIndexChanged', c.name, c.tx, c.tz, c.ry
		self.ignoreControl = False
	
	
	
	#Colores:
	@QtCore.Slot()
	def on_activationBox_currentIndexChanged(self):
		print 'Activation combo box: ', self.ui.activationBox.currentText()
		self.ignoreActivation = True
		for c in self.captures:
			if self.ui.activationBox.currentText() == c.name:
				if c.color == 'not displayed':
					self.ui.colorBox.setCurrentIndex(0)
				elif c.color == 'red':
					self.ui.colorBox.setCurrentIndex(1)
				elif c.color == 'green':
					self.ui.colorBox.setCurrentIndex(2)
				elif c.color == 'blue':
					self.ui.colorBox.setCurrentIndex(3)
		self.ignoreActivation = False
	
	
	@QtCore.Slot()
	def on_colorBox_currentIndexChanged(self):
		self.actualizarColor()
	
	
	def actualizarColor(self):
		if self.ignoreActivation: return
	
		newcolor = self.ui.colorBox.currentText()
		print 'nuevo color:', newcolor
	
		for c in self.captures:
			if self.ui.activationBox.currentText() == c.name:
				c.color = newcolor
				print 'actcolor' , c.name, c.color