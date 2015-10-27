#***************************************************************************
#*																		*
#*   Copyright (c) 2015													 *  
#*   <microelly2@freecadbuch.de>										 * 
#*																		 *
#*   This program is free software; you can redistribute it and/or modify*
#*   it under the terms of the GNU Lesser General Public License (LGPL)	*
#*   as published by the Free Software Foundation; either version 2 of	*
#*   the License, or (at your option) any later version.				*
#*   for detail see the LICENCE text file.								*
#*																		*
#*   This program is distributed in the hope that it will be useful,	*
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of		*
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the		*
#*   GNU Library General Public License for more details.				*
#*																		*
#*   You should have received a copy of the GNU Library General Public	*
#*   License along with this program; if not, write to the Free Software*
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#*   USA																*
#*																		*
#************************************************************************

__title__="Topological naming"
__author__ = "Thomas Gundermann"
__url__ = "http://www.freecadbuch.de"


#
# 
#
#
#


# Liste aller Ecken, Kanten, Flaechen
VX=[]
EX=[]
FX=[]

def registerVX(obj):
	print obj
	for v in obj.Shape.Vertexes:
		vv=FreeCAD.Vector(v.Point)
		gefunden=False
		for vx in VX:
			if vx['coords'] == vv:
				print "gefunden",vv
				gefunden=True
				break
		if not gefunden:
			VX.append({'coords':vv})

def registerEX(obj):
	for e in obj.Shape.Edges:
		v0=FreeCAD.Vector(e.Vertexes[0].Point)
		v1=FreeCAD.Vector(e.Vertexes[1].Point)
		p0=vindex(v0)
		p1=vindex(v1)
		if p1 < p0:  p0,p1 = p1,p0
		gefunden=False
		for vx in EX:
			if vx['points'] == [p0,p1]:
				print "gefunden",[p0,p1]
				gefunden=True
				break
		if not gefunden:
			EX.append({'points':[p0,p1]})

def registerFX(obj):
	for f in obj.Shape.Faces:
		fps=[]
		for v in f.Vertexes:
#			print v.Point
			p=vindex(FreeCAD.Vector(v.Point))
#			print p
			fps.append(p)
		fpss=set(fps)
		if not fpss in FX:
			FX.append(fpss)
		else:
				print "Doppelt ",fpss



def vindex(point):
	ix=0
	for vx in VX:
		if point == vx['coords']:
			return ix
		ix += 1
	return -1

def eindex(p0,p1):
	ix=0
	for ex in EX:
		if [p0,p1] == ex['points']:
			return ix
		ix += 1
	return -1

class MyObj():
	def __init__(self,obj):
		self.vx=[]
		for v in obj.Shape.Vertexes:
			vix=vindex(v.Point)
			self.vx.append(vix)
		self.ex=[]
		for e in obj.Shape.Edges:
			p0=vindex(e.Vertexes[0].Point)
			p1=vindex(e.Vertexes[1].Point)
			if p1 < p0:  p0,p1 = p1,p0
			eix=eindex(p0,p1)
			self.ex.append(eix)
		self.fx=[]
		for f in obj.Shape.Faces:
			fps=[]
			for v in f.Vertexes:
				p=vindex(FreeCAD.Vector(v.Point))
				fps.append(p)
			fpss=set(fps)
			self.fx.append(fpss)


#
# vergleiche zwei koerper
#
def compareVertexes(a,b):
	common=list(set(a.vx) & set(b.vx))
	missed=list(set(a.vx) - set(b.vx))
	added=list(set(b.vx) - set(a.vx))
	return [common,missed,added]

def compareEdges(a,b):
	common=list(set(a.ex) & set(b.ex))
	missed=list(set(a.ex) - set(b.ex))
	added=list(set(b.ex) - set(a.ex))
	return [common,missed,added]

def compareFaces(a,b):
	common=[]
	missed=[]
	added=[]
	for af in a.fx:
		if af in b.fx:
			common.append(af)
		elif af not in b.fx:
			missed.append(af)
	for b in b.fx:
		if b not in a.fx:
			added.append(b)
	return [common,missed,added]


#
# testprogramm
#

def myTest(ob1name,ob2name):
	#obj=App.ActiveDocument.Pad
	#obj2=App.ActiveDocument.Pad001
	
	obj=App.ActiveDocument.getObject("Pad")
	obj2=App.ActiveDocument.getObject("Pad001")

	print obj
	print obj2

	for os in [obj,obj2]:
		registerVX(os)
		registerEX(os)
		registerFX(os)

	myObj=MyObj(obj)
	myObj2=MyObj(obj2)

	# aenderungen der vertexes
	c,m,a=compareVertexes(myObj,myObj2)

	print a
	for vn in a:
		print VX[vn]

	# kantenindex
	print myObj.ex
	print myObj2.ex

	# Kantenveraenderungen
	ce,me,ae=compareEdges(myObj,myObj2)
	print ce
	print me
	print ae

	# welche punkte sind weg
	for mi in m:
		print EX[mi]['points']



	# neue und gewanderte kanten
	for ai in ae:
		s=str(EX[ai]['points'])
		[p0,p1]=EX[ai]['points']
		if p0 in a and p1 in a:
			print s, " neue strecke"
		elif p1 in a:
			#print "neuer punkt"
			# me untersuchen
			for mi in me:
				[q0,q1]=EX[mi]['points']
				if q0 == p0 or q1 == p0:
					print s," aufgetan durch extra punkt ",p1 ,", ursprungskante war ",EX[mi]['points']
		elif p0 in a:
			print "neuer punkt" 
			raise Exception("sollte nicht sein, weil neue punkte groesseren index haben")
		else:
			raise Exception("kante verloren" + str(EX[ai]))

	print "Flaechen ..."
	cf,mf,af=compareFaces(myObj,myObj2)
	print cf
	print mf
	print af
	return [
		len(c),len(m),len(a),
		len(ce),len(me),len(ae),
		len(cf),len(mf),len(af),
	]


# testfaelle

dir='/home/thomas/freecad_buch/b164_topological_naming/'

def test1():
	fn=dir+"gentopo.py"
	try:App.closeDocument(App.ActiveDocument.Name);
	except: pass
	try:FreeCAD.open(dir+"m06_dreieckprisma.fcstd");
	except: pass
	result=myTest('Pad','Pad001')
	print result
	assert([6, 0, 2, 7, 2, 5, 2, 3, 4] == result)
#	App.closeDocument( App.ActiveDocument.Name)


# meine tests

test1()
