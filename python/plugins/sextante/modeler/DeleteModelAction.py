# -*- coding: utf-8 -*-

"""
***************************************************************************
    DeleteModelAction.py
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

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from sextante.gui.ContextAction import ContextAction
from sextante.modeler.ModelerAlgorithm import ModelerAlgorithm
import os
from PyQt4 import QtGui

class DeleteModelAction(ContextAction):

    def __init__(self):
        self.name="Delete model"

    def isEnabled(self):
        return isinstance(self.alg, ModelerAlgorithm)

    def execute(self):
        reply = QtGui.QMessageBox.question(None, 'Confirmation',
                            "Are you sure you want to delete this model?", QtGui.QMessageBox.Yes |
                            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            os.remove(self.alg.descriptionFile)
            self.toolbox.updateTree()