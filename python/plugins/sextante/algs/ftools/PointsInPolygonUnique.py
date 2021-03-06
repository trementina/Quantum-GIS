# -*- coding: utf-8 -*-

"""
***************************************************************************
    PointsInPolygon.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from sextante.parameters.ParameterTableField import ParameterTableField

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt4 import QtGui
from PyQt4.QtCore import *

from qgis.core import *

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.QGisLayers import QGisLayers

from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterString import ParameterString

from sextante.outputs.OutputVector import OutputVector

from sextante.algs.ftools import FToolsUtils as utils

class PointsInPolygonUnique(GeoAlgorithm):

    POLYGONS = "POLYGONS"
    POINTS = "POINTS"
    OUTPUT = "OUTPUT"
    FIELD = "FIELD"
    CLASSFIELD = "CLASSFIELD"

    #===========================================================================
    # def getIcon(self):
    #    return QtGui.QIcon(os.path.dirname(__file__) + "/icons/sum_points.png")
    #===========================================================================

    def defineCharacteristics(self):
        self.name = "Count unique points in polygon"
        self.group = "Vector analysis tools"
        self.addParameter(ParameterVector(self.POLYGONS, "Polygons", ParameterVector.VECTOR_TYPE_POLYGON))
        self.addParameter(ParameterVector(self.POINTS, "Points", ParameterVector.VECTOR_TYPE_POINT))
        self.addParameter(ParameterTableField(self.CLASSFIELD, "Class field", self.POINTS))
        self.addParameter(ParameterString(self.FIELD, "Count field name", "NUMPOINTS"))
        self.addOutput(OutputVector(self.OUTPUT, "Result"))

    def processAlgorithm(self, progress):
        polyLayer = QGisLayers.getObjectFromUri(self.getParameterValue(self.POLYGONS))
        pointLayer = QGisLayers.getObjectFromUri(self.getParameterValue(self.POINTS))
        fieldName = self.getParameterValue(self.FIELD)
        classFieldName = self.getParameterValue(self.CLASSFIELD)

        polyProvider = polyLayer.dataProvider()

        classFieldIndex = pointLayer.fieldNameIndex(classFieldName)
        idxCount, fieldList = utils.findOrCreateField(polyLayer, polyLayer.pendingFields(), fieldName)

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(fieldList.toList(),
                     polyProvider.geometryType(), polyProvider.crs())

        spatialIndex = utils.createSpatialIndex(pointLayer)

        ftPoint = QgsFeature()
        outFeat = QgsFeature()
        geom = QgsGeometry()

        current = 0
        hasIntersections = False

        features = QGisLayers.features(polyLayer)
        total = 100.0 / float(len(features))
        for ftPoly in features:
            geom = ftPoly.geometry()
            attrs = ftPoly.attributes()

            classes = []
            hasIntersections = False
            points = spatialIndex.intersects(geom.boundingBox())
            if len(points) > 0:
                hasIntersections = True

            if hasIntersections:
                for i in points:
                    request = QgsFeatureRequest().setFilterFid(i)
                    ftPoint = pointLayer.getFeatures(request).next()
                    tmpGeom = QgsGeometry(ftPoint.geometry())
                    if geom.contains(tmpGeom):
                        clazz = ftPoint.attributes()[classFieldIndex]
                        if not clazz in classes:
                            classes.append(clazz)

            outFeat.setGeometry(geom)
            if idxCount == len(attrs):
                attrs.append(len(classes))
            else:
                attrs[idxCount] =  len(classes)
            outFeat.setAttributes(attrs)
            writer.addFeature(outFeat)

            current += 1
            progress.setPercentage(current / total)

        del writer
