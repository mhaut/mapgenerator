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

from genericworker import *

añsdlkfjañdlfkja

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
		self.timer.timeout.connect(self.compute)
		self.Period = 100
		self.timer.start(self.Period)
		
		
		self.captures = []
		
		self.sceneLaser = MyGraphicsScene()
		self.maxRect = 5000
		self.sceneLaser.setSceneRect(0, 0, self.maxRect, self.maxRect)
		self.ui.graphicsViewLaser.setScene(self.sceneLaser)
		
		self.maxdistance = 5000
		self.ignoreControl = False
		self.ignoreActivation = False

	def setParams(self, params):
		return True

	@QtCore.Slot()
	def compute(self):
		self.sceneLaser.clear()
		w = 2500
		self.sceneLaser.addEllipse(-w/2,-w/2,w,w,QtGui.QPen(QtGui.QColor(200,100,0)))
		points = self.laser_proxy.getLaserData()
		rad = 1
		
		current = Capture('current', 'black', points)
		allCaptures = copy.deepcopy(self.captures)
		if self.ui.showCurrent.isChecked():
			allCaptures += [current]
		for capture in allCaptures:
			if capture.color == "not displayed": continue
		
			for point in capture.points:
				x = 0
				z = 0
				if float(point.dist) < self.maxdistance:
					# Convertimos de polares a cartesianas
					x = m.sin(point.angle)*point.dist
					z = m.cos(point.angle)*point.dist
					# Rotamos el punto una vez en cartesianas
					xp = x*m.cos(capture.ry) - z*m.sin(capture.ry)
					zp = z*m.cos(capture.ry) + x*m.sin(capture.ry)
					# Desplazamos el punto
					xpp = xp + capture.tx
					zpp = zp + capture.tz
					# Pintamos
					x = xpp /self.ui.zoom.value()
					z = -zpp /self.ui.zoom.value()
					if capture.color == "red":
						pen = QtGui.QPen(QtGui.QColor(255,0,0))
					elif capture.color == "green":
						pen = QtGui.QPen(QtGui.QColor(0,255,0))
					elif capture.color == "blue":
						pen = QtGui.QPen(QtGui.QColor(0,0,255))
					else:
						pen = QtGui.QPen(QtGui.QColor(0,0,0))					
					
					# TODO
					# Transform coordinates to QtSecene Reference
					# Check Scene Size
					print x-rad, z-rad
					self.sceneLaser.addEllipse(x-rad+500, z-rad+500, rad*2.0, rad*2.0,pen)					
					# Example point in 500,500
					self.sceneLaser.addEllipse(500,500,20,20,pen)

				
		self.sceneLaser.update()

		return True


	@QtCore.Slot()
	def on_saveButton_clicked(self):
		pickle.dump(self.captures, open('save.pck', 'w'))
	@QtCore.Slot()
	def on_loadButton_clicked(self):
		self.captures = pickle.load(open('save.pck', 'r'))
		for capture in self.captures:
			self.ui.activationBox.addItem(capture.name)
			self.ui.controlBox.addItem(capture.name)
			
	@QtCore.Slot()
	def on_captureButton_clicked(self):
		points = self.laser_proxy.getLaserData()
		name = self.ui.name.text()
		color = "not displayed"

		self.captures.append(Capture(name, color, points))
		self.ui.activationBox.addItem(name)
		self.ui.controlBox.addItem(name)

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
	
