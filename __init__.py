# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RFMPlanner
                                 A QGIS plugin
 Regional Fire Management Plan tool
                             -------------------
        begin                : 2018-07-23
        copyright            : (C) 2018 by Patrick Maslen, Department of Biodiversity, Conservation and Attractions, Western Australia
        email                : Patrick.Maslen@dbca.wa.gov.au
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
    """Load RFMPlanner class from file RFMPlanner.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .rfm_planner import RFMPlanner
    return RFMPlanner(iface)
