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

import os, subprocess

from PyQt4 import uic, QtGui, QtCore
from PyQt4.QtCore import pyqtSlot, QFileInfo
from PyQt4.QtGui import QPushButton
from qgis.core import *
from qgis.gui import QgsGenericProjectionSelector, QgsMessageBar
from qgis.utils import reloadPlugin, iface
from osgeo import gdal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'cdf_converter_dialog_base.ui'))


class CdfConverterDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None, ):
        """Constructor."""
        #QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        super(CdfConverterDialog, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface

    def on_browse_input_pressed(self):
        """
        get input file
        """
        input_file = QtGui.QFileDialog.getOpenFileName(
            self, self.tr("Open File"), "",
            self.tr("netCDF Files(*.nc *.cdf *.nc2 *.nc4)"))
        if input_file is not None:
            self.input_path.setText(input_file)


    def on_browse_input_crs_pressed(self):
        """
        define input crs
        :return:
        """
        crs_selector = QgsGenericProjectionSelector()
        crs_selector.show()
        crs_selector.exec_()
        self.input_authid = str(crs_selector.selectedAuthId())
        selected_crs = QgsCoordinateReferenceSystem()
        selected_crs.createFromString(self.input_authid)
        self.input_crs.setText(selected_crs.description() + "    (" + self.input_authid+")")
        # check if same crs in output crs is checked
        # if self.use_input_crs.isChecked():
        #     self.output_crs.setText(selected_crs.description() + "    (" + self.input_authid+")")

    # def on_browse_output_crs_pressed(self):
    #     """
    #     define output crs
    #     :return:
    #     """
    #     crs_selector = QgsGenericProjectionSelector()
    #     crs_selector.show()
    #     crs_selector.exec_()
    #     self.output_authid = str(crs_selector.selectedAuthId())
    #     selected_crs = QgsCoordinateReferenceSystem()
    #     selected_crs.createFromString(self.output_authid)
    #     self.output_crs.setText(selected_crs.description() + "    (" + self.output_authid+")")

    def on_browse_output_pressed(self):
        """
        define output location
        """
        layer_title = self.input_title.text()
        output_file = QtGui.QFileDialog.getSaveFileName(
            self, self.tr("Output File"), layer_title+".tif",
            self.tr("GeoTiff File (*.tif)"));
        if output_file is not None:
            self.output_path.setText(output_file)

    def on_input_path_textChanged(self):
        """
        Check input path from browse dialog
        :return:
        """
        if not os.path.exists(self.input_path.text()):
            #self.display_log.append("Input file does not exist")
            QgsMessageLog.logMessage("Input file directory is empty or does not exist")
        else:
            #self.display_log.clear()
            #self.display_log.append("Input file loaded")
            self.file_path = self.input_path.text()
            self.file_dir = os.path.dirname(self.file_path)
            self.output_path.setText(self.file_dir)
            self.get_subdatasets()

    def get_subdatasets(self):
        """
        get subdataset
        :return:
        """
        self.select_subdataset.clear()
        netcdf = gdal.Open(self.file_path)
        list_subdatasets = []
        for sd in netcdf.GetSubDatasets():
            list_subdatasets.append(sd[0].split(':')[-1])
        for sd in list_subdatasets:
            self.select_subdataset.addItem(sd)

    @pyqtSlot(int)  # avoid currentIndexChanged signal to be emitted twice
    def on_select_subdataset_currentIndexChanged(self):
        """
        call get band
        :return:
        """
        self.subdataset = self.select_subdataset.currentText()
        self.get_bands()

    def get_bands(self):
        """
        Get band from subdataset
        :return:
        """
        #self.select_band.clear()
        netcdf_sd_path = 'NETCDF:"' + self.file_path + '":' + self.subdataset
        #self.display_log.append(netcdf_sd_path)
        self.select_band.clear()
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
            pass
            #self.display_log.append("No Timeslice detected")

    @pyqtSlot(int) # avoid currentIndexChanged signal to be emitted twice
    def on_select_band_currentIndexChanged(self):
        """
        update band and set it as output name
        :return:
        """
        self.band = str(self.select_band.currentIndex() + 1)
        self.input_title.setText(self.select_subdataset.currentText()+"_"+self.select_band.currentText())
        #self.display_log.clear()
        #self.display_log.append("NetCDF path " + self.file_path)
        #self.display_log.append("Current SubDataset is " + self.subdataset)
        #self.display_log.append("Current Band is " + self.band)

    def accept(self):
        """
        Handle OK button
        """
        layer_title = self.input_title.text()
        netcdf_uri = 'NETCDF:"'+self.file_path+'":'+self.subdataset
        output_uri = self.file_dir + "/" + layer_title + ".tif"
        # check if default folder is used
        if not self.use_default_dir.isChecked():
            self.file_dir = self.output_path.text()
            output_uri = self.file_dir
        #self.display_log.append("Result path " + output_uri)
        full_cmd = 'gdal_translate -b ' + self.band + ' -a_srs ' + self.input_authid +' -of GTiff ' + netcdf_uri + ' "' + output_uri +'"'
        subprocess.Popen(full_cmd, shell=True)
        # if not self.use_input_crs.isChecked():
        #     transformed_uri = self.file_dir + "/" + layer_title + "_transformed.tif"
        #     transform_cmd = 'gdalwarp -overwrite -s_srs ' + self.input_authid + ' -t_srs '+ self.output_authid +' -of GTiff ' + output_uri + '' + transformed_uri +''
        #     subprocess.Popen(transform_cmd, shell=True)
        #     output_uri = transformed_uri
        file_info = QFileInfo(output_uri)
        base_name = file_info.baseName()
        result_layer = QgsRasterLayer(output_uri, base_name)
        result_layer.isValid()
        if not result_layer.isValid():
            QgsMessageLog.logMessage("Layer is invalid")
            msg_bar = self.iface.messageBar().createMessage("Warning", "Layer is not loaded automatically")
            self.uri = output_uri
            self.base_name = base_name
            button_load_result = QPushButton(msg_bar)
            button_load_result.setText("Load Result")
            button_load_result.pressed.connect(self.load_manually)
            msg_bar.layout().addWidget(button_load_result)
            self.iface.messageBar().pushWidget(msg_bar, QgsMessageBar.WARNING, duration=30)
        else:
            QgsMapLayerRegistry.instance().addMapLayer(result_layer)

    def load_manually(self):
        QgsMessageLog.logMessage("Loading result manually")
        result = QgsRasterLayer(self.uri, self.base_name)
        if not result.isValid():
            QgsMessageLog.logMessage("Result layer is still invalid")
        else:
            QgsMapLayerRegistry.instance().addMapLayers([result])

    def closeEvent(self, QCloseEvent):
        """
        handle close event
        :param QCloseEvent:
        :return:
        """
        self.reject()

    def reject(self):
        """
        clear widget
        :return:
        """
        self.input_path.clear()
        self.output_path.clear()
        self.select_band.clear()
        self.select_subdataset.clear()
        self.input_title.clear()
        self.input_crs.clear()
        #self.display_log.clear()
        self.close()
        reloadPlugin('CdfConverter')
        