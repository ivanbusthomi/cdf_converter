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
from PyQt4.QtCore import pyqtSlot
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


    def on_browse_output_pressed(self):
        """
        define output location
        """
        output_file = QtGui.QFileDialog.getSaveFileName(
            self, self.tr("Output File"), "Volcanic_Ash.tif",
            self.tr("Raster File (*.tif)"));
        if output_file is not None:
            self.output_path.setText(output_file)

    def on_input_path_textChanged(self):
        self.file_path = self.input_path.text()
        self.get_subdatasets()

    def get_subdatasets(self):
        self.select_subdataset.clear()
        netcdf = gdal.Open(self.file_path)
        list_subdatasets = []
        for sd in netcdf.GetSubDatasets():
            list_subdatasets.append(sd[0].split(':')[-1])
        for sd in list_subdatasets:
            self.select_subdataset.addItem(sd)

    @pyqtSlot(int)  # avoid currentIndexChanged signal to be emitted twice
    def on_select_subdataset_currentIndexChanged(self):
        self.subdataset = self.select_subdataset.currentText()
        self.get_bands()

    def get_bands(self):
        self.select_band.clear()
        netcdf_sd_path = 'NETCDF:"' + self.file_path + '":' + self.subdataset
        print netcdf_sd_path
        netcdf_sd = gdal.Open(netcdf_sd_path)
        metadata = netcdf_sd.GetMetadata()
        metadata_list = []
        for key,value in metadata.iteritems():
            metadata_list.append(key)
        if 'NETCDF_DIM_time_VALUES' in metadata_list:
            bands = metadata['NETCDF_DIM_time_VALUES'].translate(None,'{}')
            bands_list = bands.split(',')
            for band in bands_list:
                self.select_band.addItem(band)
        else:
            print "No Timeslice detected"

    @pyqtSlot(int) # avoid currentIndexChanged signal to be emitted twice
    def on_select_band_currentIndexChaned(self):
        self.band = self.select_band.currentText()


    def accept(self):
        """
        Handle OK button
        """
        # check if default folder is used
        if not self.use_default_dir.isChecked():
            file_dir = self.output_path.text()
        self.layer_title = self.input_title.text()
        self.layer_source = self.input_source.text()
        self.file_dir = os.path.dirname(self.file_path)


