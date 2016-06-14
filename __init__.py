# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CdfConverter
                                 A QGIS plugin
 This is a tool to convert a netcdf data to tiff raster file
                             -------------------
        begin                : 2016-06-14
        copyright            : (C) 2016 by Ivan Busthomi
        email                : ivanbusthomi@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CdfConverter class from file CdfConverter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .cdf_converter import CdfConverter
    return CdfConverter(iface)
