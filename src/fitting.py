#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  ------------------------
#  -----  fitting.py  -----
#  ------------------------
#  An implementation of several line fitting methods.
#
#  Copyright (C) 2009 Luis J. Manso <luisDOTmanso gmailDOTcom>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

"""
Author: Luis J. Manso
Program: fitting.py
Date: 2009-08-06
Description: Python implmentation of Least Squares fitting, RANSAC, and an extension of RANSAC. Points are introduced by clicking on the window. The red line is the result of the Least Squares algorithm, the green line is the result of the RANSAC algorithm (discarded models are drawn in grey). The results of the RANSAC extension are in dashed blue. You may want to edit the configuration section of the file.
"""

# CONFIGURATION SECTION
# RANSAC related variables
cfg_iterations = 50.
cfg_minimum_description_length = 2.
cfg_inlier_threshold = 35.
cfg_good_description_length = 11.
# RANSAC Extension related variables
cfg_intersection = 0.3 # Intersection range [0..1]


# CODE SECTION
import sys, math, random
from PyQt4 import QtCore, QtGui, Qt

def least_squares(points):
	# Mean
	xm = 0.
	ym = 0.
	sumx = 0.
	sumxx = 0.
	sumy = 0.
	i = 0
	while i < len(points):
		sumx += float(points[i].x)
		sumy += float(points[i].y)
		i += 1
	xm = float(sumx) / float(i)
	ym = float(sumy) / float(i)

	# D y sumEtimesY
	D = 0.
	sumEtimesY = 0.
	i = 0
	while i < len(points):
		D += float(points[i].x-xm)**2.
		sumEtimesY += float(float(points[i].x)-float(xm))*float(points[i].y)
		i += 1

	if D == 0.:
		D = 0.000000001
	a = float(sumEtimesY/D)
	b = float(ym-a*xm)
	return a, b

def dist_point2line(a, b, x, y):
	a = float(a)
	b = float(b)
	x = float(x)
	y = float(y)
	return math.fabs(a*x-y+b)/math.sqrt(a*a+1.)

def error_points2line(a, b, pts):
	s = 0.
	for i in range(len(pts)):
		s += dist_point2line(a, b, pts[i].x, pts[i].y)**2.
	return s
	
def ransac(points, iterations, card_initial_guess, threshold_inlier, card_inliers_min):
	# Initialice lists
	retA = list()
	retB = list()
	pts = list()
	errors = list()

	for itera in range(int(iterations)):
		# Randomize points
		index = range(len(points))
		random.shuffle(index)
		# Split initial model points from the rest
		S1 = index[0:int(card_initial_guess)]
		index = index[int(card_initial_guess):]
		currentPoints = list()
		for p in S1: currentPoints.append(points[p])

		a, b = least_squares(currentPoints)

		inserted = 1
		while inserted == 1:
			inserted = 0
			ii = 0
			while ii < len(index):
				i = index[ii]
				if dist_point2line(a, b, points[i].x, points[i].y) < threshold_inlier:
					currentPoints.append(points[i])
					index.pop(ii)
					a, b = least_squares(currentPoints)
					inserted += 1
				else:
					ii += 1

		if len(currentPoints) >= card_inliers_min:
			retA.append(a)
			retB.append(b)
			currentPoints.sort()
			pts.append(currentPoints)
			errors.append(error_points2line(a, b, currentPoints))

	return retA, retB, pts, errors

class Point2D:
	def __init__(self, x=0., y=0.):
		self.x = float(x)
		self.y = float(y)
	def __repr__(self):
		return '('+str(self.x)+', '+str(self.y)+')'
	def __cmp__(self, other):
		return cmp(self.x, other.x)

class RANSACLine:
	def __init__(self, a, b, points, error):
		self.a = float(a)
		self.b = float(b)
		self.points = points
		self.points.sort()
		self.error = error
	def __cmp__(self, other):
		return cmp(self.error, other.error)
	def __repr__(self):
		return '( '+str(self.a)+', '+str(self.b)+ '  <<'+str(self.points)+'>>  '+str(self.error)+' )\n'


class Pintaol(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.points = []
		self.maxX = 0.
		self.maxY = 0.

		self.run()
		self.timer = QtCore.QTimer()
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.run)
		self.timer.start(1000)

	def mousePressEvent(self, event):
		w = float(self.width())
		h = float(self.height())
		p = Point2D(event.x()-6, (h-event.y())-6)
		self.points.append(p)
		self.run()

	def drawLine(self, a, b):
		w = float(self.width())
		h = float(self.height())
		ya = h-(a*(0)+b)
		yb = h-(a*(w)+b)
		self.painter.drawLine(0+6, ya-6, w+6, yb-6)

	def paintEvent(self, event=None):
		w = float(self.width())
		h = float(self.height())

		self.painter = QtGui.QPainter(self)
		self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
		self.painter.drawLine(6,0,6,h)
		self.painter.drawLine(0,h-6,w, h-6)


		# Standard RANSAC
		if len(self.points) >= cfg_good_description_length:
			pen = QtGui.QPen(QtGui.QColor(120, 120, 120))
			pen.setWidth(2)
			self.painter.setPen(pen)
			idx = 0
			while idx < len(self.a):
				self.drawLine(self.a[idx], self.b[idx])
				idx += 1
			pen = QtGui.QPen(QtGui.QColor(0, 255, 0))
			pen.setWidth(3)
			self.painter.setPen(pen)
			self.drawLine(self.bestA, self.bestB)

		#RANSAC Extension
		if len(self.points) >= cfg_good_description_length:
			for idx in range(len(self.superRansacs)):
				pen = QtGui.QPen(QtGui.QColor(0, 0, 255))
				pen.setWidth(2)
				pen.setStyle(2)
				self.painter.setPen(pen)
				self.drawLine(self.superRansacs[idx].a, self.superRansacs[idx].b)

		# Least Squares
		if len(self.points) > 1:
			self.painter.setPen(QtGui.QColor(255, 0, 0))
			self.drawLine(self.minc_a, self.minc_b)

		# Points
		for p in self.points:
			self.painter.setBrush(QtGui.QColor(0, 0, 255, 127))
			self.painter.setPen(QtGui.QColor(0, 0, 255, 127))
			self.painter.drawEllipse(p.x+3, h-p.y-9, 6, 6)

		# End
		self.painter = None


	def run(self):
		# Puntos
		if len(self.points) > 0:
			print '\nPoints:'
			print '------------------------------'
			for p in self.points:
				print p


		# Minimos cuadrados
		if len(self.points) > 1:
			print '\nLeast Squares:'
			print '------------------------------'
			self.minc_a, self.minc_b = least_squares(self.points)
			print 'y =', self.minc_a, '* x +', self.minc_b
			print 'Error:', error_points2line(self.minc_a, self.minc_b, self.points)


		# RANSAC
		if len(self.points) >= cfg_good_description_length:
			print '\nStandard RANSAC:'
			print '------------------------------'
			self.a, self.b, self.pointsLists, self.errors = ransac(self.points, cfg_iterations, cfg_minimum_description_length, cfg_inlier_threshold, cfg_good_description_length)
			self.bestA = 0
			self.bestB = 0
			self.bestError = 999999999999.
			idx = 0
			print str(len(self.a))+' valid models.'
			while idx < len(self.a):
				if self.bestError > self.errors[idx]:
					self.bestA = self.a[idx]
					self.bestB = self.b[idx]
					self.bestError = self.errors[idx]
				idx += 1
			print 'Best one: y =', self.bestA, '* x +', self.bestB
			print 'Error:', self.bestError


		# RANSAC M
		if len(self.points) >= cfg_good_description_length:
			print '\nRANSAC Extension:'
			print '------------------------------'
			# Fill the 'ransacs' vector with the solution of each RANSAC iteration. Sort it by error.
			ransacs = list()
			for idx in range(len(self.a)):
				ransacs.append(RANSACLine(self.a[idx], self.b[idx], self.pointsLists[idx], self.errors[idx]))
			ransacs.sort()

			# Fill the  'superRansacs' with the "good" solutions of the 'ransacs' vector.
			self.superRansacs = list()
			if len(ransacs) > 0:
				self.superRansacs.append(ransacs[0])
				superError = ransacs[0].error
				print 'y =', ransacs[0].a, '* x +', ransacs[0].b

				idx = 1
				while idx < len(ransacs):
					accepted = True
					if ransacs[idx].error > 40000: accepted = False
					idx2 = 0
					while idx2 < idx and accepted:
						big = len(ransacs[idx].points)
						if len(ransacs[idx2].points) > len(ransacs[idx].points):
							big = len(ransacs[idx2].points)
						intersection = len([val for val in ransacs[idx].points if val in ransacs[idx2].points])
						if float(intersection)/float(big) > cfg_intersection:
							accepted = False
						idx2 += 1
					if accepted:
						self.superRansacs.append(ransacs[idx])
						print 'y =', ransacs[idx].a, '* x +', ransacs[idx].b
					idx += 1
			print str(len(self.superRansacs))+' models.'


		self.update()


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	clase = Pintaol()
	QtGui.QMessageBox.information(clase, 'Message', 'Click in the window to add points. Take into account that the program needs '+str(int(cfg_good_description_length))+' points in order to get RANSAC working. Check the first lines of code in order to change the configuration.')
	clase.resize(800,600);
	clase.show()
	app.exec_()

