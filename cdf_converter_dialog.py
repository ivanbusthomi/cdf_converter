# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CdfConverterDialog
                                 A QGIS plugin
 This is a tool to convert a netcdf data to tiff raster file
                             -------------------
        begin                : 2016-06-14
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Ivan Busthomi
        email                : ivanbusthomi@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import uic, QtGui, QtCore
from qgis.core import *
from osgeo import gdal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'cdf_converter_dialog_base.ui'))


class CdfConverterDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CdfConverterDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
    
    def on_browse_input_pressed(self):
        """
        get input file
        """
        input_file = QtGui.QFileDialog.getOpenFileName(
            self, self.tr("Open File"), "",
            self.tr("netCDF Files(*.nc *.cdf *.nc2 *.nc4)"))
        if input_file is not None:
            self.input_path.setText(input_file)
            self.get_subdatasets()

    def on_browse_output_pressed(self):
        """
        define output location
        """
        output_file = QtGui.QFileDialog.getSaveFileName(
            self, self.tr("Output File"), "Volcanic_Ash.tif",
            self.tr("Raster File (*.tif)"));
        if output_file is not None:
            self.output_path.setText(output_file)

    def get_subdatasets(self):
        file_path = self.input_path.text()
        netcdf = gdal.Open(file_path)
        list_subdatasets = []
        for sd in netcdf.GetSubDatasets():
            list_subdatasets.append(sd[0].split(':')[-1])
        for sd in list_subdatasets:
            self.select_var.addItem(sd)

    def accept(self):
        """
        Handle OK button
        """
        print self.input_path.text()
        print self.output_path.text()