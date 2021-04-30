# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RFMPlannerDialog
                                 A QGIS plugin
 Regional Fire Management Plan tool
                             -------------------
        begin                : 2018-07-23
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Patrick Maslen, Department of Biodiversity, Conservation and Attractions, Western Australia
        email                : Patrick.Maslen@dbca.wa.gov.au
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
import subprocess
import ogr2ogr
import processing
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QApplication, QBrush, QColor, QCursor, QDialog, QFileDialog, QFont, QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QTableWidgetItem
import qgis.utils
from qgis.core import QGis, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsDataSourceURI, QgsExpression, QgsFeatureRequest, QgsMapLayerRegistry, QgsVectorLayer
from qgis.gui import QgsFieldProxyModel, QgsHighlight, QgsMapLayerProxyModel
from forms import add_existing_data, asset_name_selector, asset_table_selector, brmzs_report, create_region_assets, delete_assets, detailed_editor, edit_record, group_editor, fma_grouping_selector, region_report, show_thresholds, update_threshold
import rfm_library
from rfm_library import debug_msg_box as debug
import globals
from win32com.client import Dispatch    #Used for exporting report csvs
import win32gui                         #Used for exporting report csvs


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'rfm_planner_dialog_base.ui'))
albers_wa_string = 'proj4: +proj=aea +lat_1=-17.5 +lat_2=-31.5 +lat_0=0 +lon_0=121 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'

def window_enumeration_handler(hwnd, top_windows):
    # Called by bring_excel_to_front
    # Used to bring Excel to front after report export
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    
def bring_excel_to_front():
    results = []
    top_windows = []
    win32gui.EnumWindows(window_enumeration_handler, top_windows)
    for i in top_windows:
        if "excel" in i[1].lower():
            #print i
            win32gui.ShowWindow(i[0],5)
            win32gui.SetForegroundWindow(i[0])
            break

def show_db_tables(cbx, pref_rgn_only=True):
    tables = rfm_library.get_regional_asset_layers(pref_rgn_only)
    cbx.clear()
    if pref_rgn_only and globals.preferred_region != "All of WA":
        cbx.addItems([t for t in tables if t.lower().startswith(globals.preferred_region.lower().replace(" ", "_"))])
    else:
        cbx.addItems(tables)


# Following over-ride used to enable numerical sorting in table columns.
# Based on http://stackoverflow.com/questions/25533140/sorting-qtablewidget-items-numerically
class QCustomTableWidgetItem (QTableWidgetItem):
    def __init__ (self, value):
        super(QCustomTableWidgetItem, self).__init__(str('%s' % value))

    def __lt__ (self, other):
        if (isinstance(other, QCustomTableWidgetItem)):
            self_data_value  = float(str(self.data(Qt.EditRole)))
            other_data_value = float(str(other.data(Qt.EditRole)))
            return self_data_value < other_data_value
        else:
            return QTableWidgetItem.__lt__(self, other)      

        
class AddExistingAssetsDialog(QDialog, add_existing_data.Ui_AddAssetsDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.filter_layers()
        show_db_tables(self.cbx_postgis_tables)
        self.update_postgis_default()
        self.cbx_map_layers.currentIndexChanged.connect(self.update_postgis_default)
        for cbx in [self.cbx_asset_name_field, self.cbx_asset_fma_field, self.cbx_asset_resilience_field, self.cbx_asset_class_field]:
            cbx.setFilters(QgsFieldProxyModel.String)
            cbx.setLayer(self.cbx_map_layers.currentLayer())
            self.cbx_map_layers.layerChanged.connect(cbx.setLayer)
        
    def filter_layers(self):
        self.cbx_map_layers.setFilters(QgsMapLayerProxyModel.HasGeometry)
        rfmp_postgis_layers = []
        registry = QgsMapLayerRegistry.instance()
        layers = registry.mapLayers()
        for layer in layers:
            if layers[layer].source().startswith("dbname='" + globals.rfmp_db + "'") or layers[layer].source().startswith("dbname='" + globals.spatialite_db + "'"):
                rfmp_postgis_layers.append(layers[layer])
        self.cbx_map_layers.setExceptedLayerList(rfmp_postgis_layers)
        
    def update_postgis_default(self):
        # name of this function dates from pre-spatialite inclusion for offline work but also applies to spatialite
        if self.cbx_map_layers.currentLayer() is not None:
            if self.cbx_map_layers.currentLayer().geometryType() == QGis.Point:
                for i in range(self.cbx_postgis_tables.count()):
                    if self.cbx_postgis_tables.itemText(i).endswith("_asset_points"):
                        self.cbx_postgis_tables.setCurrentIndex(i)
                        break
            elif self.cbx_map_layers.currentLayer().geometryType() == QGis.Line:
                for i in range(self.cbx_postgis_tables.count()):
                    if self.cbx_postgis_tables.itemText(i).endswith("_asset_lines"):
                        self.cbx_postgis_tables.setCurrentIndex(i)
                        break
            elif self.cbx_map_layers.currentLayer().geometryType() == QGis.Polygon:
                for i in range(self.cbx_postgis_tables.count()):
                    if self.cbx_postgis_tables.itemText(i).endswith("_asset_polys"):
                        self.cbx_postgis_tables.setCurrentIndex(i)
                        break
        
    def accept(self):
        #debug("globals.connection_string: " + globals.connection_string)
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        self.layer = self.cbx_map_layers.currentLayer()
        original_lyr_name = self.layer.name()
        self.layer_in_albers = QgsVectorLayer(processing.runalg("qgis:reprojectlayer", self.layer, albers_wa_string, None)["OUTPUT"], "layer_in_albers", "ogr")
        ##self.postgis_table = self.cbx_postgis_tables.currentText()
        ##region_prelim = self.postgis_table[:self.postgis_table.find("_asset")]
        self.spatial_table = self.cbx_postgis_tables.currentText()
        region_prelim = self.spatial_table[:self.spatial_table.find("_asset")]
        self.region_name = region_prelim.upper().replace("_", " ")

        if not self.check_matching_geom_types():
            return
        field_mapping_needed = False
        asset_name_field = self.cbx_asset_name_field.currentField()
        asset_class_field = self.cbx_asset_class_field.currentField()
        asset_fma_field = self.cbx_asset_fma_field.currentField()
        asset_resilience_field = self.cbx_asset_resilience_field.currentField()
        
        proceed = self.selection_and_out_of_region_checks()
        if not proceed:
            QApplication.restoreOverrideCursor()
            self.close()
            return
      
        selected_ids = []
        if self.layer.selectedFeatureCount() > 0:
            selected_ids = self.layer.selectedFeaturesIds()
            
        # Get feature count
        if self.layer.selectedFeatureCount() == 0:
            total_features = self.layer.featureCount()
        else:
            total_features = self.layer.selectedFeatureCount()
    
        # Identify any fields which will need editing once copied to database
        issues = []
        if asset_name_field != "" or asset_class_field != "" or asset_fma_field != "" or asset_resilience_field != "" :
            field_mapping_needed = True
            if asset_class_field != "" :
                value_check = self.check_feature_class_values(asset_class_field, "asset_class")
                if value_check is not None:
                    issues.append(value_check)
            else:
                issues.append(("asset_class", total_features, 0))
            if asset_fma_field != "" :
                value_check = self.check_feature_class_values(asset_fma_field, "fma")
                if value_check is not None:
                    issues.append(value_check)
            else:
                issues.append(("fma", total_features, 0))
            if asset_resilience_field != "" :
                value_check = self.check_feature_class_values(asset_resilience_field, "resilience")
                if value_check is not None:
                    issues.append(value_check)
            else:
                issues.append(("resilience", total_features, 0))

        geom_type = self.get_qgis_geom_type()
        src_crs = self.layer.crs().toProj4()
        
        #get location of this script
        #ogr2ogr_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'rfm_resources', 'ogr2ogr.exe'))
        #ogr2ogr_parameters = [globals.ogr2ogr_path,
        ogr2ogr_parameters = ["ogr2ogr",
                "-update",
                "-append"]
        if globals.db == "postgis":
            ogr2ogr_parameters += ["-f", "PostgreSQL",
                                    "PG:" + globals.connection_string]
        elif globals.db == "spatialite":
            ogr2ogr_parameters += ["-f", "SQLite",
                                    globals.spatialite_db,
                                    "-dsco", "SPATIALITE=YES"]
        ogr2ogr_parameters += ["-nln", self.spatial_table, 
                "-a_srs", src_crs,
                "-t_srs", albers_wa_string,
                self.layer.source().replace("\\", "/")
                ]
        if self.layer.selectedFeatureCount() > 0:
            ogr2ogr_parameters.append("-where")
            ogr2ogr_parameters.append("FID IN {}".format(tuple(selected_ids)).replace("L", ""))
                
        if geom_type == "POINT":
            ogr2ogr_parameters.append("-explodecollections")
        
        elif geom_type in ["LINE", "POLYGON"]:
            ogr2ogr_parameters.append("-nlt")
            ogr2ogr_parameters.append("PROMOTE_TO_MULTI")
            
        if field_mapping_needed:
            field_map = self.get_field_map(self.layer, asset_name_field, asset_class_field, asset_fma_field, asset_resilience_field)
            #debug(field_map)
            ogr2ogr_parameters.append("-fieldmap")
            ogr2ogr_parameters.append(field_map)

        ogr2ogr.main(ogr2ogr_parameters)
        # Following commented out once ogr2ogr.py had been hacked to accept field map
        # Call ogr2ogr.exe, with DETACHED_PROCESS flag so that console does not appear
        #DETACHED_PROCESS = 0x00000008
        #try:
        #    subprocess.check_call(ogr2ogr_parameters, creationflags=DETACHED_PROCESS)
        #except:
        #    ogr2ogr_parameters[0] = '"C:/Program Files/QGIS 2.18/bin/ogr2ogr.exe"'
        #    subprocess.check_call(ogr2ogr_parameters, creationflags=DETACHED_PROCESS)
        #debug(ogr2ogr_parameters)

        validate_geom_sql = ""
        # Snap to grid and repair any invalid polygon geometries
        if geom_type == "POLYGON":
            validate_geom_sql = "UPDATE " + self.spatial_table + " SET geometry = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_SnapToGrid(geometry, 1)), 3)) WHERE NOT ST_IsValid(geometry); COMMIT;"
        vac_sql = "VACUUM ANALYZE " + self.spatial_table + ";"
        #rfm_library.run_nonselect_sql([validate_geom_sql, " COMMIT;", vac_sql])
                
        if len(issues) > 0:
            issues_string = ""
            for issue in issues:
                issues_string += issue[0] + " column has " + str(issue[1]) + " missing value(s) and " + str(issue[2]) + " invalid value(s)\n"
            response = QMessageBox.information(None, "Attribute editing required!", str(total_features) + " features were copied from  " + self.layer.name() + " to " + self.spatial_table + " but some attributes need to be added or edited.  Within the new rows:\n\n" + issues_string + "\nDo you want to open the attribute table and begin editing?", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if response == QMessageBox.Yes:
                qgis.utils.iface.mapCanvas().refresh() 
                self.call_load_attr_table()
        else:
            QMessageBox.information(None, "Complete", str(total_features) + " features successfully copied from " + original_lyr_name + " to " + self.spatial_table)
        self.close()
        layer_if_present = QgsMapLayerRegistry.instance().mapLayersByName(self.spatial_table)
        if not layer_if_present:
            if globals.db == "postgis": 
                rfm_library.load_postgis_layer(self.spatial_table)
            elif globals.db == "spatialite": 
                rfm_library.load_spatialite_layer(self.spatial_table)
        else:
            qgis.utils.iface.mapCanvas().refreshAllLayers()
        QApplication.restoreOverrideCursor()
        
    def selection_and_out_of_region_checks(self):
        proceed = True
        outside_region_count = self.within_region_check()
        if self.layer.selectedFeatureCount() == 0:
            if outside_region_count > 0:
                #ask about selection
                msg = QMessageBox(QMessageBox.Information, "No features selected!", "No features have been selected; if you continue then all of the " + str(self.layer.featureCount()) + " features in " + self.layer.name() + " will be copied to " + self.spatial_table + ".\n\nNote also that " +  str(outside_region_count) + " features extend outside the " + self.region_name + " region.  Do you want to crop to the region boundary before copying?")
                clip_btn = QPushButton("Crop input to \nregion boundary")
                continue_btn = QPushButton("Add all features \nfrom input layer")
                msg.addButton(clip_btn, QMessageBox.YesRole)
                msg.addButton(continue_btn, QMessageBox.NoRole)
                msg.addButton(QMessageBox.Cancel)
                reply = msg.exec_()
                if msg.clickedButton() == clip_btn:
                    self.clip()
                elif reply == QMessageBox.Cancel:
                    proceed = False
            else:   # i.e. no selection but whole feature class in within region
                msg = QMessageBox.information(None, "No features selected!", "No features have been selected; if you continue then all of the " + str(self.layer.featureCount()) + " features in " + self.layer.name() + " will be copied to " + self.spatial_table + ".  Do you want to continue?", buttons=QMessageBox.Yes|QMessageBox.No)
                if msg == QMessageBox.No:
                    proceed = False
        else:       # i.e. there are selected features
            if outside_region_count > 0:
                msg = QMessageBox(QMessageBox.Information, "Features extend beyond region!", str(outside_region_count) + " of your input features extend outside " + self.region_name + " region.  You can continue, crop inputs to the region boundary, or cancel.")
                clip_btn = QPushButton("Crop input to \nregion boundary")
                continue_btn = QPushButton("Add all selected \nfeatures from input layer")
                msg.addButton(clip_btn, QMessageBox.YesRole)
                msg.addButton(continue_btn, QMessageBox.NoRole)
                msg.addButton(QMessageBox.Cancel)
                reply = msg.exec_()
                if msg.clickedButton() == clip_btn:
                    self.clip()
                elif reply == QMessageBox.Cancel:
                    proceed = False
        return proceed
            
    def selection_check(self):
        # Check user wants to go ahead if no features selected
        if self.layer.selectedFeatureCount() == 0:
            reply = QMessageBox.information(None, "No features selected!", "No features have been selected; if you continue then all of the " + str(self.layer.featureCount()) + " features in " + self.layer.name() + " will be copied to " + self.postgis_table + ".  Do you want to continue?", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        else:
            reply = QMessageBox.information(None, str(self.layer.selectedFeatureCount()) + " features selected for copying.", "If you continue then " + str(self.layer.selectedFeatureCount()) + " of the " + str(self.layer.featureCount()) + " features in " + self.layer.name() + " will be copied to " + self.postgis_table + ".  Do you want to continue?", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        return reply
        
    def within_region_check(self):
        # Returns count of features which are (or extend) outside region
        if globals.db == "postgis":
            uri = QgsDataSourceURI()
            uri.setConnection(globals.rfmp_host, globals.rfmp_port, globals.rfmp_db, globals.rfmp_user, globals.rfmp_pw)
            uri.setDataSource("public", "regions", "geometry", "region='" + self.region_name + "'")
            self.regions_layer = QgsVectorLayer(uri.uri(), "region", "postgres")
        elif globals.db == "spatialite":
            uri = "dbname='" + globals.spatialite_db + "' table='regions' (geometry) sql=""region""='" + self.region_name + "'"
            #debug(uri)
            self.regions_layer = QgsVectorLayer(uri, "region", "spatialite")
        all_within = True
        count = 0
        for region in self.regions_layer.getFeatures():
            region_geom = region.geometry()
            features = self.layer_in_albers.getFeatures()
            for feature in features:
                if not feature.geometry().within(region_geom):
                    all_within = False
                    #break
                    count += 1
        return count
    
    def clip(self):
        if globals.db == "postgis":
            self.layer = QgsVectorLayer(processing.runalg("qgis:clip", self.layer_in_albers, self.regions_layer , None)["OUTPUT"], "clipped_input", "ogr")
        elif globals.db == "spatialite":
            # QGIS asks for sqlite credentials (nonsensical) unless regions layer is added to map
            QgsMapLayerRegistry.instance().addMapLayer(self.regions_layer)
            self.layer = QgsVectorLayer(processing.runalg("qgis:clip", self.layer_in_albers, "region" , None)["OUTPUT"], "clipped_input", "ogr")
            QgsMapLayerRegistry.instance().removeMapLayer(self.regions_layer)
    
    def get_table_geom_type(self):
        self.spatial_table = self.cbx_postgis_tables.currentText()
        if globals.db == "postgis":
            sql = "SELECT type FROM geometry_columns WHERE f_table_schema = 'public' AND f_table_name = '" + self.spatial_table + "' and f_geometry_column = 'geometry';"
        elif globals.db == "spatialite":
            sql = "SELECT geometry_type FROM geometry_columns WHERE f_table_name = '" + self.spatial_table + "' and f_geometry_column = 'geometry';"
        result = rfm_library.run_select_sql(sql)[0][0]
        if globals.db == "postgis":
            if 'POINT' in result:
                return 'POINT'
            elif 'LINE' in result:
                return 'LINE'
            elif 'POLYGON' in result:
                return 'POLYGON'
            else:
                return 'NO'
        elif globals.db == "spatialite":
            if result == 1:
                return 'POINT'
            elif result == 5:
                return 'LINE'
            elif result == 6:
                return 'POLYGON'
            else:
                return 'NO'
        else:
            return 'NO'
            
    def get_qgis_geom_type(self):
            qgis_layer = self.layer
            if qgis_layer.hasGeometryType():
                if qgis_layer.geometryType() == QGis.Point:
                    return "POINT"
                elif qgis_layer.geometryType() == QGis.Line:
                    return "LINE"
                elif qgis_layer.geometryType() == QGis.Polygon:
                    return "POLYGON"
                else:
                    return "UNKNOWN"
            else:
                return "NO GEOMETRY"
        
    def check_matching_geom_types(self):
        table_geom_type = self.get_table_geom_type()
        qgis_geom_type = self.get_qgis_geom_type()
        if table_geom_type != qgis_geom_type:
            QMessageBox.information(None, "Geometry mismatch!", "This map layer has " + qgis_geom_type + " geometry but you have selected a database layer with " + table_geom_type + " geometry.  The layer will not be added.")
            return False
        else:
            return True
            
    def get_field_map(self, layer, asset_name_field, asset_class_field, asset_fma_field, asset_resilience_field):
        #get source field count
        fields = layer.fields()
        field_count = fields.count()
        #get index of each specified field
        asset_name_field_index = fields.indexFromName(asset_name_field)
        asset_class_field_index = fields.indexFromName(asset_class_field)
        asset_fma_field_index = fields.indexFromName(asset_fma_field)
        asset_resilience_field_index = fields.indexFromName(asset_resilience_field)
        #get index of each relevant postgis column
        if globals.db == "postgis":
            sql = "select column_name from INFORMATION_SCHEMA.COLUMNS where table_name = '" + self.spatial_table + "';"
        elif globals.db == "spatialite":
            sql = "select column_name from vector_layers_field_infos where table_name = '" + self.spatial_table + "' and column_name NOT IN ('geometry', 'gid');"
            # NB returns empty result if no features yet in self.spatial_table
        columns = rfm_library.run_select_sql(sql)
        if len(columns) > 0:
            for i in range(len(columns)):
                if str(columns[i][0]) == "asset_name":
                    asset_name_column = i
                elif str(columns[i][0]) == "asset_class":
                    asset_class_column = i
                elif str(columns[i][0]) == "fma":
                    fma_column = i
                elif str(columns[i][0]) == "resilience":
                    resilience_column = i
        elif globals.db == "spatialite":
            # take default column numbers if fc is empty
            asset_name_column = 2
            asset_class_column = 1
            fma_column = 5
            resilience_column = 3
            
        #build string 
        field_map_list = []
        for i in range(field_count):
            field_map_list.append(-1)
        if asset_name_field_index != -1:
            field_map_list[asset_name_field_index] = asset_name_column
        if asset_class_field_index != -1:
            field_map_list[asset_class_field_index] = asset_class_column
        if asset_fma_field_index != -1:
            field_map_list[asset_fma_field_index] = fma_column
        if asset_resilience_field_index != -1:
            field_map_list[asset_resilience_field_index] = resilience_column
        return str(field_map_list)[1:-1].replace(" ", "")
        
    def check_feature_class_values(self, field, column):
        expected_values = globals.expected_values[column]
        missing_count = 0
        invalid_count = 0
        # Check for missing values and invalid values
        for feature in self.layer.getFeatures():
            if str(feature[field]).strip() in ["", "NULL"]:
                missing_count += 1
            elif str(feature[field]).strip() not in expected_values:
                invalid_count += 1
        if missing_count > 0 or invalid_count > 0:
            return (column, missing_count, invalid_count)
            
    def call_load_attr_table(self):
        layer_if_present = QgsMapLayerRegistry.instance().mapLayersByName(self.spatial_table)
        #debug(layer_if_present)
        if not layer_if_present:
            if globals.db == "postgis":
                rfm_library.load_postgis_layer(self.spatial_table)
            elif globals.db == "spatialite":
                rfm_library.load_spatialite_layer(self.spatial_table)
        else:
            qgis.utils.iface.setActiveLayer(layer_if_present[0])
        qgis.utils.iface.showAttributeTable(qgis.utils.iface.activeLayer())
        if not qgis.utils.iface.activeLayer().isEditable():
            qgis.utils.iface.activeLayer().startEditing()
        

class AssetTableSelectorDialog(QDialog, asset_table_selector.Ui_SelectExistingAssetTablesDialog):
    def __init__(self, type):
        QDialog.__init__(self)
        self.setupUi(self)
        tables = rfm_library.get_regional_asset_layers(False, type)
        for table in tables:
            item = QListWidgetItem(table, self.listWidget)
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)
            
    def accept(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        tables_to_load = []
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState() == Qt.Checked:
                tables_to_load.append(self.listWidget.item(i).text())
        for table in tables_to_load:
            grouping = self.get_grouping(table)
            layer_is_present = QgsMapLayerRegistry.instance().mapLayersByName(table)
            if not layer_is_present:
                if globals.db == "postgis":
                    rfm_library.load_postgis_layer(table, grouping)
                elif globals.db == "spatialite":
                    rfm_library.load_spatialite_layer(table, grouping)
            else:
                response = QMessageBox.information(None, "Layer already loaded!", table + " is already loaded into the map.  Do you want to load it again?", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                if response == QMessageBox.Yes:
                    if globals.db == "postgis":
                        rfm_library.load_postgis_layer(table, grouping)
                    elif globals.db == "spatialite":
                        rfm_library.load_spatialite_layer(table, grouping)
        self.close()
        QApplication.restoreOverrideCursor()
        
    def get_grouping(self, tbl_name):
        if tbl_name.endswith("fmas_by_fma") or tbl_name.endswith("_fmas_complete") or tbl_name.endswith("_fmas_combined"):
            grouping = "fma"
        elif tbl_name.endswith("fmas_shs") or tbl_name.endswith("fmas_cib") or tbl_name.endswith("fmas_lrr") or tbl_name.endswith("fmas_ram"):
            grouping = "fma"
        elif tbl_name.endswith("fmas_by_priority"):
            grouping = "priority"
        elif tbl_name.endswith("fmas_by_fma_and_priority"):
            grouping = "fma, priority"
        elif tbl_name.endswith("_fmas"):
            grouping = ""
        else:
            grouping = None
        return grouping


class CreateRegionAssetsDialog(QDialog, create_region_assets.Ui_CreateRegionAssetsDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        if globals.preferred_region == "All of WA":
            sql = "SELECT region FROM regions"
            regions = []
            with globals.conn:
                csr = globals.conn.cursor()
                csr.execute(sql)
                rows = csr.fetchall()
                csr.close()
                for row in rows:
                    regions.append(row[0])
                self.cbx_regions.addItems(regions)
        else:
            self.cbx_regions.addItem(globals.preferred_region)
        
    def accept(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        region = self.cbx_regions.currentText()
        vector_types = [("polys", "MULTIPOLYGON"), ("lines", "LINESTRING"), ("points", "POINT")]
        for vector_type in vector_types:
            tbl_name = region.lower().replace(" ", "_") + "_asset_" + vector_type[0]
            if self.table_check_ok(tbl_name, region):
                sql_drop = "DROP TABLE IF EXISTS " + tbl_name
                if vector_type[0] == "polys":
                    sql_create = "CREATE TABLE " + tbl_name + \
                        " AS SELECT asset_polys.* FROM asset_polys, regions " + \
                        "WHERE region = '" + region + "' AND " + \
                        "ST_Intersects(asset_polys.geometry, regions.geometry)"
                else:
                    sql_create = "CREATE TABLE " + tbl_name + \
                        " AS SELECT * FROM asset_" + vector_type[0]

                sql_primary_key = "ALTER TABLE " + tbl_name + " ADD gid serial PRIMARY KEY"
                sql_spatial_index = "CREATE INDEX " + tbl_name + "_geom_idx ON " + tbl_name + " USING GIST (geometry);"
                rfm_library.run_nonselect_sql([sql_drop, sql_create, sql_primary_key, sql_spatial_index])
                rfm_library.update_updates_table(tbl_name)
                if globals.db == "postgis":
                    rfm_library.load_postgis_layer(tbl_name)
                elif globals.db == "spatialite":
                    rfm_library.load_spatialite_layer(tbl_name)
                rfm_library.update_regional_assets_menu(globals.update_assets_menu, True)
                rfm_library.update_regional_assets_menu(globals.prioritise_menu, True)
        self.close()
        QtGui.QApplication.restoreOverrideCursor()
        
    def table_check_ok(self, tbl_name, region):
        sql_table_check = """SELECT EXISTS (
                                   SELECT 1
                                   FROM   information_schema.tables 
                                   WHERE  table_schema = 'public'
                                   AND    table_name = '""" + tbl_name + "');"
        result = rfm_library.run_select_sql(sql_table_check)[0][0]
        if result is False:
            return True     # i.e. OK to create table with this name
        else:
            result = QtGui.QMessageBox.information(None, "Table already exists", "There is already a table " + tbl_name.upper() + \
              " in the database.  If you continue you will lose any updates which have been made to that table." + \
              "\n\nDo you want to overwrite the existing " + tbl_name.upper() + " table?", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, defaultButton=QtGui.QMessageBox.NoButton)
            if result == QtGui.QMessageBox.Yes:
                return True
            else:
                return False


class DeleteAssetsDialog(QDialog, delete_assets.Ui_DeleteAssetsDialog):
    def __init__(self, asset_layers):
        QDialog.__init__(self)
        self.setupUi(self)
        self.filter_layers(asset_layers)
        self.btn_go.clicked.connect(self.accept)
        self.btn_stop.clicked.connect(self.close)
        # following code is to enable old widgets to be retained
        self.rad_selected_features.setVisible(False)
        self.label_4.setVisible(False)
        self.rad_entire_layer.setVisible(False)
                
    def filter_layers(self, asset_layers):
        self.cbx_asset_layers.setFilters(QgsMapLayerProxyModel.HasGeometry)
        #rfmp_postgis_asset_layers = []
        excepted_list = []
        registry = QgsMapLayerRegistry.instance()
        layers = registry.mapLayers()
        for layer in layers:
            if not layers[layer].name() in asset_layers:
                excepted_list.append(layers[layer])
        self.cbx_asset_layers.setExceptedLayerList(excepted_list)
        
    def accept(self):
        #if not self.rad_selected_features.isChecked() and not self.rad_entire_layer.isChecked():
        #    QMessageBox.information(None, "Choose an option!", "To delete, you must choose to delete selected assets or the entire layer")
        #    return
        asset_layer = self.cbx_asset_layers.currentLayer()
        if asset_layer.selectedFeatureCount() == 0:
            QMessageBox.information(None, "No features selected!", "No features have been selected for deletion.  Select any features you want to delete then run this tool.")
            self.close()
            return
        #if self.rad_selected_features.isChecked():
        reply = QMessageBox.warning(None, "Asset features will be permanently deleted!", "You are about to delete " + str(asset_layer.selectedFeatureCount()) + " features from " + asset_layer.name() + ".  Do you want to continue?", buttons=QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            asset_layer.dataProvider().deleteFeatures([f.id() for f in asset_layer.selectedFeatures()])
            asset_layer.reload()
            qgis.utils.iface.mapCanvas().refreshAllLayers()
            QApplication.restoreOverrideCursor()
            QMessageBox.information(None, "Asset features deleted", str(asset_layer.selectedFeatureCount()) + " features deleted from " + asset_layer.name() + ".")
            
        #Following code is for deletion of entire layer
        """elif self.rad_entire_layer.isChecked():
            sql = "DROP TABLE " + asset_layer.name()
            reply = QMessageBox.warning(None, "Table will be completely deleted!", "You are about to delete the entire table " + asset_layer.name() + " from the database.  Do you want to continue?", buttons=QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.Yes:
                rfm_library.run_nonselect_sql([sql])
                QgsMapLayerRegistry.instance().removeMapLayers([self.cbx_asset_layers.currentLayer().id()])
            QMessageBox.information(None, "Table deleted", asset_layer.name() + " has been deleted from the database.")
        """
        self.close()

    
class EditingMainWindow(QMainWindow):
    #parent class for GroupEditorMainWindow, DetailedEditorMainWindow
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        show_db_tables(self.cbx_postgis_tables)
        self.rad_any_anom.setChecked(True)
        self.btn_add_layer.clicked.connect(self.load_db_layer)
        self.check_add_layer_enabling()
        self.cbx_postgis_tables.currentIndexChanged.connect(self.check_add_layer_enabling)
            
    def get_anomalies(self):
        if not self.rad_any_anom.isChecked():
            if self.rad_fma_anom.isChecked():
                field = "fma"
            elif self.rad_asset_class_anom.isChecked():
                field = "asset_class"
            elif self.rad_resilience_anom.isChecked():
                field = "resilience"
            if globals.db == "postgis":
                self.anomalies_sql = "SELECT gid, asset_name, fma, asset_class, resilience FROM " + self.layer.name() + " WHERE CONCAT(" + field + ", '') NOT IN (" + str(globals.expected_values[field])[1:-1] + ")"
            elif globals.db == "spatialite":
                self.anomalies_sql = "SELECT gid, asset_name, fma, asset_class, resilience FROM " + self.layer.name() + " WHERE " + field + " IS NULL OR " + field + " NOT IN (" + str(globals.expected_values[field])[1:-1] + ")"
        else:
            if globals.db == "postgis":
                self.anomalies_sql = "SELECT gid, asset_name, fma, asset_class, resilience FROM " + self.layer.name() + " WHERE CONCAT(fma, '') NOT IN (" + str(globals.expected_values['fma'])[1:-1] + ") OR CONCAT(asset_class, '') NOT IN (" + str(globals.expected_values['asset_class'])[1:-1] + ") OR CONCAT(resilience, '') NOT IN (" + str(globals.expected_values['resilience'])[1:-1] + ")"
            elif globals.db == "spatialite":
                self.anomalies_sql = "SELECT gid, asset_name, fma, asset_class, resilience FROM " + self.layer.name() + " WHERE fma IS NULL OR fma NOT IN (" + str(globals.expected_values['fma'])[1:-1] + ") OR asset_class IS NULL OR asset_class NOT IN (" + str(globals.expected_values['asset_class'])[1:-1] + ") OR resilience IS NULL OR resilience NOT IN (" + str(globals.expected_values['resilience'])[1:-1] + ")"
        anomalies = rfm_library.run_select_sql(self.anomalies_sql)
        return anomalies
        
    def load_db_layer(self):
        # Check if layer loaded
        db_table = self.cbx_postgis_tables.currentText()
        layer_if_present = QgsMapLayerRegistry.instance().mapLayersByName(db_table)
        if not layer_if_present:
            if globals.db == "postgis":
                rfm_library.load_postgis_layer(db_table)
            elif globals.db == "spatialite":
                rfm_library.load_spatialite_layer(db_table)
        layer = QgsMapLayerRegistry.instance().mapLayersByName(db_table)[0]
        qgis.utils.iface.setActiveLayer(layer)
        self.btn_add_layer.setEnabled(False)
        return layer

    def check_add_layer_enabling(self):
        layer_if_present = QgsMapLayerRegistry.instance().mapLayersByName(self.cbx_postgis_tables.currentText())
        if not layer_if_present:
            self.btn_add_layer.setEnabled(True)
            self.lbl_selection_count.setText("")
        else:
            self.btn_add_layer.setEnabled(False)
            selected_features = layer_if_present[0].selectedFeatures()
            self.lbl_selection_count.setText(str(len(selected_features)) + " feature(s) selected")

        
class GroupEditorMainWindow(EditingMainWindow, group_editor.Ui_GroupEditorMainWindow):
    def __init__(self, layer=None):
        EditingMainWindow.__init__(self)
        if qgis.utils.iface.activeLayer() is None:
            self.lbl_selection_count.setText("")
        elif self.cbx_postgis_tables.findText(qgis.utils.iface.activeLayer().name()) > -1:
            self.cbx_postgis_tables.setCurrentIndex(self.cbx_postgis_tables.findText(qgis.utils.iface.activeLayer().name()))
            selected_features = qgis.utils.iface.activeLayer().selectedFeatures()
            self.lbl_selection_count.setText(str(len(selected_features)) + " feature(s) selected")
        else:
            self.lbl_selection_count.setText("")
        self.rad_fma.toggled.connect(self.rad_button_toggled)
        self.rad_asset_class.toggled.connect(self.rad_button_toggled)
        self.rad_resilience.toggled.connect(self.rad_button_toggled)
        self.btn_case_errors.clicked.connect(self.correct_case_errors)
        self.btn_set_values.clicked.connect(self.set_values)
        self.btn_select_anomalies.clicked.connect(self.call_get_anomalies)
        self.btn_detailed_edit.clicked.connect(self.open_detailed_editor)
        
    def rad_button_toggled(self):
        self.cbx_values.clear()
        if self.rad_fma.isChecked():
            self.cbx_values.addItems(globals.expected_values["fma"])
            self.edit_field = "fma"
        elif self.rad_asset_class.isChecked():
            self.cbx_values.addItems(globals.expected_values["asset_class"])
            self.edit_field = "asset_class"
        elif self.rad_resilience.isChecked():
            self.cbx_values.addItems(globals.expected_values["resilience"])
            self.edit_field = "resilience"
    
    def call_get_anomalies(self):
        self.layer = self.load_db_layer()
        anomalies = self.get_anomalies()
        anomaly_ids = [row[0] for row in anomalies]
        self.layer.setSelectedFeatures(anomaly_ids)
        self.check_add_layer_enabling()
       
    def correct_case_errors(self):
        db_table = self.cbx_postgis_tables.currentText()
        for key, value_list in globals.expected_values.iteritems():
            for value in value_list:
                sql = "UPDATE " + db_table + " SET " + key + " = '" + value + "' WHERE REPLACE(UPPER(" + key + "), ' ', '') = '" + value.upper().replace(" ", "") + "'"
                rfm_library.run_nonselect_sql([sql])
        QMessageBox.information(None, "", "Completed correction of case errors in " + db_table)
        
    def set_values(self):
        db_table = self.cbx_postgis_tables.currentText()
        layer = self.load_db_layer()
        # Check if any features/rows selected
        selected_features = layer.selectedFeatures()
        count = layer.selectedFeatureCount()
        if count == 0:
            QMessageBox.information(None, "No selected features", "No features/rows have been selected from " + db_table + ".  To use this part of the tool you need to make a selection first.")
            self.close()
            return
        # Get gids of selection
        gids = []
        for feature in selected_features:
            gids.append(int(feature["gid"]))
        gids_string = str(gids)[1:-1]
        # Assemble sql
        sql = "UPDATE " + db_table + " SET " + self.edit_field + " = '" + self.cbx_values.currentText() + "' WHERE gid in (" + gids_string + ")"
        # Run sql
        rfm_library.run_nonselect_sql([sql])
        QMessageBox.information(None, self.edit_field + " updated", str(count) +  " records had <b>" + self.edit_field + "</b> set to '" + self.cbx_values.currentText() + "'")
        
    def open_detailed_editor(self):
        layer = self.load_db_layer()
        self.close()
        globals.detailed_editor = DetailedEditorMainWindow(layer)
        globals.detailed_editor.show()


class DetailedEditorMainWindow(EditingMainWindow, detailed_editor.Ui_DetailedEditor):
    def __init__(self, layer=None):
        EditingMainWindow.__init__(self)
        self.tbl_features.setColumnWidth(0, 80)
        self.tbl_features.setColumnWidth(1, 200)
        self.tbl_features.setColumnWidth(2, 60)
        self.tbl_features.setColumnWidth(3, 120)
        self.tbl_features.setColumnWidth(4, 90)
        self.tbl_features.setColumnWidth(5, 80)
        self.tbl_features.setColumnWidth(6, 80)
        self.tbl_features.setColumnWidth(7, 80)
        self.tbl_features.setColumnWidth(8, 80)
        self.layer = layer
        self.btn_select_anomalies.clicked.connect(self.call_get_anomalies)
        self.tbl_features.itemClicked.connect(self.item_clicked)
        self.current_hover = [-1, -1]
        self.tbl_features.cellEntered.connect(self.cellHover)
        self.btn_group_edit.clicked.connect(self.open_group_editor)
        
    def cellHover(self, row, column):
        item = self.tbl_features.item(row, column)
        old_item = self.tbl_features.item(self.current_hover[0], self.current_hover[1])
        if self.current_hover != [row,column]:
            if column == 4:
                if old_item is not None:
                    if old_item.column() == 5:
                        old_item.setBackground(QColor(220, 220, 220, 255))
            if column > 4:
                if old_item is not None:
                    if old_item.column() > 4:
                        old_item.setBackground(QColor(220, 220, 220, 255))
                    else:
                        old_item.setBackground(QColor('white'))
                item.setBackground(QColor(200, 230, 255, 255))
        self.current_hover = [row, column]
    
    def call_get_anomalies(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.layer = self.load_db_layer()
        self.tbl_features.setRowCount(0)
        anomalies = self.get_anomalies()
        i = 0
        #for feature in anomalies_iterator:
        self.tbl_features.setSortingEnabled(False)
        for row in anomalies:
            self.add_row_to_table(row)
            i += 1
        self.tbl_features.setSortingEnabled(True)
        total_count_sql = "SELECT COUNT(*) FROM " + self.layer.name()
        total_count = rfm_library.run_select_sql(total_count_sql)[0][0]
        
        if self.rad_fma_anom.isChecked():
            self.search_column = "fma"
        elif self.rad_asset_class_anom.isChecked():
            self.search_column = "asset_class"
        elif self.rad_resilience_anom.isChecked():
            self.search_column = "resilience"
        else:
            self.search_column = "one or more of fma, asset_class and resilience"
        self.lbl_selection_count.setText(str(i) + " of " + str(total_count) + " feature(s) have invalid values for " + self.search_column)
        QApplication.restoreOverrideCursor()
    
    def item_clicked(self, item):
        if item.column() > 4:
            id = int(self.tbl_features.item(item.row(), 0).text())
            if item.column() == 5:
                self.flash_btn_clicked(id)
            elif item.column() == 6:
                self.zoom_btn_clicked(id)
            elif item.column() == 7:
                self.edit_btn_clicked(id, item.row())
                item.setBackground(QColor(220, 220, 220, 255))
            elif item.column() == 8:
                self.delete_btn_clicked(id)
    
    def add_row_to_table(self, feature):
        id = feature[0]
        row_no = self.tbl_features.rowCount()
        self.tbl_features.setRowCount(row_no + 1)
        self.tbl_features.setItem(row_no, 0, QCustomTableWidgetItem(str(feature[0])))
        if feature[1] is not None:
            self.tbl_features.setItem(row_no, 1, QTableWidgetItem(str(feature[1])))
        else:
            self.tbl_features.setItem(row_no, 1, QTableWidgetItem("NULL"))
        
        # feature[2] is fma
        if feature[2] is not None:
            self.tbl_features.setItem(row_no, 2, QTableWidgetItem(str(feature[2])))
        else:
            self.tbl_features.setItem(row_no, 2, QTableWidgetItem("NULL"))
        if str(feature[2]) in globals.expected_values["fma"]:
            self.tbl_features.item(row_no, 2).setForeground(QColor(0, 150, 0, 255))
        else:
            self.tbl_features.item(row_no, 2).setForeground(QColor(200, 0, 0, 255))
        
        # feature[3] is asset_class
        if feature[3] is not None:
            self.tbl_features.setItem(row_no, 3, QTableWidgetItem(str(feature[3])))
        else:
            self.tbl_features.setItem(row_no, 3, QTableWidgetItem("NULL"))
        if str(feature[3]) in globals.expected_values["asset_class"]:
            self.tbl_features.item(row_no, 3).setForeground(QColor(0, 150, 0, 255))
        else:
            self.tbl_features.item(row_no, 3).setForeground(QColor(200, 0, 0, 255))
        
        # feature[4] is resilience
        if feature[4] is not None:
            self.tbl_features.setItem(row_no, 4, QTableWidgetItem(str(feature[4])))
        else:
            self.tbl_features.setItem(row_no, 4, QTableWidgetItem("NULL"))
        if str(feature[4]) in globals.expected_values["resilience"]:
            self.tbl_features.item(row_no, 4).setForeground(QColor(0, 150, 0, 255))
        else:
            self.tbl_features.item(row_no, 4).setForeground(QColor(200, 0, 0, 255))
        self.tbl_features.setItem(row_no, 5, QTableWidgetItem("Flash"))
        self.tbl_features.item(row_no, 5).setBackground(QColor(220, 220, 220, 255))
        self.tbl_features.item(row_no, 5).setTextAlignment(Qt.AlignCenter)
        self.tbl_features.setItem(row_no, 6, QTableWidgetItem("Zoom"))
        self.tbl_features.item(row_no, 6).setBackground(QColor(220, 220, 220, 255))
        self.tbl_features.item(row_no, 6).setTextAlignment(Qt.AlignCenter)
        self.tbl_features.setItem(row_no, 7, QTableWidgetItem("Edit"))
        self.tbl_features.item(row_no, 7).setBackground(QColor(220, 220, 220, 255))
        self.tbl_features.item(row_no, 7).setTextAlignment(Qt.AlignCenter)
        self.tbl_features.setItem(row_no, 8, QTableWidgetItem("Delete"))
        self.tbl_features.item(row_no, 8).setBackground(QColor(220, 220, 220, 255))
        self.tbl_features.item(row_no, 8).setTextAlignment(Qt.AlignCenter)

    def flash_btn_clicked(self, id):
        # Get feature (using id)
        request = QgsFeatureRequest(id)
        iterator = self.layer.getFeatures(request)
        feature = iterator.next()
        # Create highlight
        highlight = QgsHighlight(qgis.utils.iface.mapCanvas(), feature.geometry(), self.layer)

        # Set highlight symbol properties
        highlight.setColor(QColor(0, 255, 255, 255))
        highlight.setWidth(6)
        highlight.setFillColor(QColor(0, 255, 255, 255))
        
        # Display highlight and set timer to turn off display
        highlight.show()
        QTimer.singleShot(2000, lambda: self.end_flash(highlight))
        
    def end_flash(self, highlight):
        highlight.hide()
        
    def zoom_btn_clicked(self, id):
        geom_type = self.layer.geometryType()
        # Get feature (using id)
        request = QgsFeatureRequest(id)
        iterator = self.layer.getFeatures(request)
        feature = iterator.next()
        geom = feature.geometry()
        albers_extent = geom.boundingBox().buffer(1000)
        
        #transform
        canvas_crs = qgis.utils.iface.mapCanvas().mapSettings().destinationCrs()
        albers_crs = QgsCoordinateReferenceSystem()
        albers_crs.createFromProj4(albers_wa_string)
        if canvas_crs != albers_wa_string:
            crs_transformer = QgsCoordinateTransform(albers_crs, canvas_crs)
            extent = crs_transformer.transform(albers_extent)
            qgis.utils.iface.mapCanvas().setExtent(extent)
        else:
            qgis.utils.iface.mapCanvas().setExtent(albers_extent)
        qgis.utils.iface.mapCanvas().refreshAllLayers()
        self.flash_btn_clicked(id)
        
    def edit_btn_clicked(self, id, parent_row_no):
        edit_record_dialog = EditAssetDialog(self.layer, id, self, parent_row_no)
        edit_record_dialog.exec_()
        
    def delete_btn_clicked(self, id):
        request = QgsFeatureRequest(id)
        iterator = self.layer.getFeatures(request)
        feature = iterator.next()
        sql = "DELETE FROM " + self.layer.name() + " WHERE gid = " + str(feature["gid"])
        reply = QMessageBox.information(None, "Permanent deletion from database", "You are about to permanently delete this feature from the assets database.  Are you sure you want to continue?", buttons=QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.No:
            return
        rfm_library.run_nonselect_sql([sql])
        # Refresh table
        #self.call_get_anomalies()
        qgis.utils.iface.mapCanvas().refreshAllLayers()
        self.tbl_features.removeRow(self.tbl_features.currentRow())
        total_count_sql = "SELECT COUNT(*) FROM " + self.layer.name()
        total_count = rfm_library.run_select_sql(total_count_sql)[0][0]
        anom_count_sql = self.anomalies_sql.replace("gid, asset_name, fma, asset_class, resilience", "count(*)")
        anom_count = rfm_library.run_select_sql(anom_count_sql)[0][0]
        self.lbl_selection_count.setText(str(anom_count) + " of " + str(total_count) + " feature(s) have invalid values for " + self.search_column)
        QMessageBox.information(None, "Deleted", "Feature has been deleted.")
        
    def open_group_editor(self):
        layer = self.load_db_layer()
        self.close()
        globals.group_editor = GroupEditorMainWindow(layer)
        globals.group_editor.show()


class EditAssetDialog(QDialog, edit_record.Ui_EditFMAsDialog):
    def __init__(self, layer, id, parent, parent_row_no):
        QDialog.__init__(self)
        self.setupUi(self)
        self.layer = layer
        self.id = id
        self.parent = parent
        self.parent_row_no = parent_row_no
        request = QgsFeatureRequest(id)
        iterator = self.layer.getFeatures(request)
        feature = iterator.next()
        self.txt_gid.setText(str(id))
        self.txt_asset_name.setText(str(feature["asset_name"]))
        if feature["fma"] not in globals.expected_values["fma"]:
            self.cbx_fma.addItems([str(feature["fma"])])
        self.cbx_fma.addItems(globals.expected_values["fma"])
        index = self.cbx_fma.findText(str(feature["fma"]))
        self.cbx_fma.setCurrentIndex(index)

        if feature["resilience"] not in globals.expected_values["resilience"]:
            self.cbx_resilience.addItems([str(feature["resilience"])])
        self.cbx_resilience.addItems(globals.expected_values["resilience"])
        index = self.cbx_resilience.findText(str(feature["resilience"]))
        self.cbx_resilience.setCurrentIndex(index)
        
        if feature["asset_class"] not in globals.expected_values["asset_class"]:
            self.cbx_asset_class.addItems([str(feature["asset_class"])])
        self.cbx_asset_class.addItems(globals.expected_values["asset_class"])
        index = self.cbx_asset_class.findText(str(feature["asset_class"]))
        self.cbx_asset_class.setCurrentIndex(index)
        
        self.orig_asset_name = self.txt_asset_name.text()
        self.orig_fma = self.cbx_fma.currentText()
        self.orig_resilience = self.cbx_resilience.currentText()
        self.orig_asset_class = self.cbx_asset_class.currentText()
        
        self.btn_ok.clicked.connect(self.update)
        self.btn_cancel.clicked.connect(self.close)

    def update(self):
        set_clause = ""
        if self.txt_asset_name.text() != self.orig_asset_name:
            set_clause += " asset_name = '" + self.txt_asset_name.text() + "'"
        if self.cbx_fma.currentText() != self.orig_fma:
            if set_clause != "":
                set_clause += ", "
            set_clause += " fma = '" + self.cbx_fma.currentText() + "'"
        if self.cbx_resilience.currentText() != self.orig_resilience:
            if set_clause != "":
                set_clause += ", "
            set_clause += " resilience = '" + self.cbx_resilience.currentText() + "'"
        if self.cbx_asset_class.currentText() != self.orig_asset_class:
            if set_clause != "":
                set_clause += ", "
            set_clause += " asset_class = '" + self.cbx_asset_class.currentText() + "'"
        if set_clause == "":
            reply = QMessageBox.information(None, "No change", "You have not made any edits to the original data.  Do you want to change any values?", buttons=QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                self.close()
            return
        sql = "UPDATE " + self.layer.name() + " SET " + set_clause + " WHERE gid = " + self.txt_gid.text()
        #QMessageBox.information(None, "", sql)
        rfm_library.run_nonselect_sql([sql])
        for i in range(self.parent.tbl_features.rowCount()):
            if self.parent.tbl_features.item(i, 0).text() == str(self.id):
                row_to_update = i
                break
        self.update_parent_form_table(i)
        QMessageBox.information(None, "Updated", "Record with gid " + self.txt_gid.text() + " updated.")
        self.close()
        
    def update_parent_form_table(self, row_no):
        request = QgsFeatureRequest(self.id)
        iterator = self.layer.getFeatures(request)
        feature = iterator.next()
        self.parent.tbl_features.setItem(row_no, 1, QTableWidgetItem(str(feature["asset_name"])))
        self.parent.tbl_features.setItem(row_no, 2, QTableWidgetItem(str(feature["fma"])))
        if str(feature["fma"]) in globals.expected_values["fma"]:
            self.parent.tbl_features.item(row_no, 2).setForeground(QColor(0, 150, 0, 255))
        else:
            self.parent.tbl_features.item(row_no, 2).setForeground(QColor(200, 0, 0, 255))
        self.parent.tbl_features.setItem(row_no, 3, QTableWidgetItem(str(feature["asset_class"])))
        if str(feature["asset_class"]) in globals.expected_values["asset_class"]:
            self.parent.tbl_features.item(row_no, 3).setForeground(QColor(0, 150, 0, 255))
        else:
            self.parent.tbl_features.item(row_no, 3).setForeground(QColor(200, 0, 0, 255))
        self.parent.tbl_features.setItem(row_no, 4, QTableWidgetItem(str(feature["resilience"])))
        if str(feature[4]) in globals.expected_values["resilience"]:
            self.parent.tbl_features.item(row_no, 4).setForeground(QColor(0, 150, 0, 255))
        else:
            self.parent.tbl_features.item(row_no, 4).setForeground(QColor(200, 0, 0, 255))
        total_count_sql = "SELECT COUNT(*) FROM " + self.parent.layer.name()
        total_count = rfm_library.run_select_sql(total_count_sql)[0][0]
        anom_count_sql = self.parent.anomalies_sql.replace("gid, asset_name, fma, asset_class, resilience", "count(*)")
        anom_count = rfm_library.run_select_sql(anom_count_sql)[0][0]
        self.parent.lbl_selection_count.setText(str(anom_count) + " of " + str(total_count) + " feature(s) have invalid values for " + self.parent.search_column)

        
class SelectFMAGroupingDialog(QDialog, fma_grouping_selector.Ui_SelectFMAGroupingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        globals.fma_group_bys = []
        self.btn_go.clicked.connect(self.go)
        self.btn_stop.clicked.connect(self.stop)
        
    def go(self):
        if self.chk_by_type.isChecked():
            globals.fma_group_bys.append("fma")
        if self.chk_by_priority.isChecked():
            globals.fma_group_bys.append("priority")
        if self.chk_by_type_n_priority.isChecked():
            globals.fma_group_bys.append("fma, priority")
        if self.chk_combine_all.isChecked():
            globals.fma_group_bys.append("")
        self.close()
        
    def stop(self):
        globals.fma_group_bys = None
        self.close()
        
        
class SingleRegionReportDialog(QDialog, region_report.Ui_SingleRegionReportDialog):
    def __init__(self, region, region_info, region_specific_thresholds):
        QDialog.__init__(self)
        self.setupUi(self)
        self.region = region
        self.region_info = region_info
        self.region_specific_thresholds = region_specific_thresholds
        self.label.setText(region.upper().replace("_", " ") + " Report")
        self.tbl_fma_type.setRowCount(0)
        self.tbl_fma_type.setColumnWidth(1, 100)
        self.tbl_fma_type.setColumnWidth(7, 130)
        self.tbl_fma_type.setColumnWidth(8, 165)
        #self.tbl_brmz.setRowCount(0)
        #self.tbl_brmz.setColumnWidth(1, 100)
        self.fill_tables()
        self.btn_close.clicked.connect(self.close)
        self.btn_csv.clicked.connect(self.export_csv)
        self.tbl_fma_type.cellClicked.connect(self.cell_clicked_tbl_fma_type)
        ##self.tbl_brmz.cellClicked.connect(self.cell_clicked_tbl_fma_type)
        
        # Added 4-Aug-2020 to include district reporting
        districts_sql = "SELECT admin_zone FROM districts WHERE region = '" + region.lower().replace(" ", "_") + "'"
        districts = rfm_library.run_select_sql(districts_sql)
        if len(districts) < 2:
            self.cbx_districts.setVisible(False)
        else:
            district_list = ['Full Region'] + [dist[0] for dist in districts]
            self.cbx_districts.addItems(district_list)
            self.cbx_districts.currentIndexChanged.connect(rfm_library.toggle_district_report)

    def fill_tables(self):
        bold_font = QFont()
        bold_font.setBold(True)
        total_area = 0
        total_with_target = 0
        total_reached = 0
        total_burn = 0
        for fma_type in ['SHS', 'CIB', 'LRR', 'RAM']:
            # get distinct targets in report info for that fma_type - e.g. SHS: -1, 60, LRR: -1, 30, 45
            targets = self.get_distinct_targets_per_fma(fma_type)
            targets.sort()
            for target in targets:
                area = 0
                reached = 0
                #i = 0
                for info_row in self.region_info:
                    if info_row[1] == fma_type and info_row[2] == target and info_row[4] is not None:
                        area += info_row[4]
                        total_area += info_row[4]
                        if target > 0:
                            total_with_target += info_row[4]
                            reached_th = info_row[3]
                            if reached_th:
                                reached += info_row[4]
                                total_reached += info_row[4]
                if area > 0:
                    percentage = round((area - reached) * 100 / area, 1)
                else:
                    percentage = 0
                area = int(round(area, 0))
                if area > 0:
                    reached = int(round(reached, 0))
                    row_no = self.tbl_fma_type.rowCount() 
                    self.tbl_fma_type.setRowCount(row_no + 1)
                    self.tbl_fma_type.setItem(row_no, 0, QCustomTableWidgetItem(fma_type))
                    if target == -1:
                        fuel_type_desc = "with no target"
                        target = "N/A"
                        reached = "N/A"
                        percentage = "N/A"
                        burn = "N/A"
                    else:
                        fuel_type_desc = "with target " + str(target) + "%"
                        if percentage < target:
                            burn = (target - percentage) * area/100
                            total_burn += burn
                            burn = int(round(burn, 0))
                        else:
                            burn = 0
                    self.tbl_fma_type.setItem(row_no, 1, QCustomTableWidgetItem(fuel_type_desc))
                    hyperlink_style_font = QFont()
                    hyperlink_style_font.setUnderline(True)
                    self.tbl_fma_type.item(row_no, 1).setFont(hyperlink_style_font)
                    self.tbl_fma_type.item(row_no, 1).setForeground(QBrush(QColor(0, 0, 255)))
                    self.tbl_fma_type.setItem(row_no, 2, QCustomTableWidgetItem(area))
                    self.tbl_fma_type.setItem(row_no, 3, QCustomTableWidgetItem(reached))
                    self.tbl_fma_type.setItem(row_no, 4, QCustomTableWidgetItem(percentage))
                    self.tbl_fma_type.setItem(row_no, 5, QCustomTableWidgetItem(target))
                    self.tbl_fma_type.setItem(row_no, 6, QCustomTableWidgetItem(burn))
                    self.tbl_fma_type.setItem(row_no, 7, QTableWidgetItem("Show this fuel"))
                    self.tbl_fma_type.item(row_no, 7).setBackground(QColor(220, 220, 220, 255))
                    if target != "N/A" and percentage != "N/A":
                        self.tbl_fma_type.setItem(row_no, 8, QTableWidgetItem("Show overage"))
                        self.tbl_fma_type.item(row_no, 8).setBackground(QColor(220, 220, 220, 255))
                        if percentage >= target:
                            self.tbl_fma_type.item(row_no, 4).setForeground(QColor(0, 150, 0, 255))
                        else:
                            self.tbl_fma_type.item(row_no, 4).setForeground(QColor(200, 0, 0, 255))
                        
        # Add totals
        total_area = int(round(total_area, 0))
        total_reached = int(round(total_reached, 0))
        total_burn = int(round(total_burn, 0))
        total_with_target = int(round(total_with_target, 0))
        row_no = self.tbl_fma_type.rowCount() 
        self.tbl_fma_type.setRowCount(row_no + 1)
        self.tbl_fma_type.setItem(row_no, 0, QCustomTableWidgetItem("TOTALS"))
        self.tbl_fma_type.setItem(row_no, 1, QCustomTableWidgetItem("With target"))
        self.tbl_fma_type.setItem(row_no, 2, QCustomTableWidgetItem(total_with_target))
        self.tbl_fma_type.setItem(row_no, 3, QCustomTableWidgetItem(total_reached))
        self.tbl_fma_type.setItem(row_no, 4, QCustomTableWidgetItem("-"))
        self.tbl_fma_type.setItem(row_no, 5, QCustomTableWidgetItem("-"))
        self.tbl_fma_type.setItem(row_no, 6, QCustomTableWidgetItem(total_burn))
        for i in range(7):
            self.tbl_fma_type.item(row_no, i).setFont(bold_font)
        
        row_no = self.tbl_fma_type.rowCount() 
        self.tbl_fma_type.setRowCount(row_no + 1)
        self.tbl_fma_type.setItem(row_no, 0, QCustomTableWidgetItem(""))
        self.tbl_fma_type.setItem(row_no, 1, QCustomTableWidgetItem("No target"))
        self.tbl_fma_type.setItem(row_no, 2, QCustomTableWidgetItem(total_area - total_with_target))
        self.tbl_fma_type.setItem(row_no, 3, QCustomTableWidgetItem("-"))
        self.tbl_fma_type.setItem(row_no, 4, QCustomTableWidgetItem("-"))
        self.tbl_fma_type.setItem(row_no, 5, QCustomTableWidgetItem("-"))
        self.tbl_fma_type.setItem(row_no, 6, QCustomTableWidgetItem(0))
        for i in range(7):
            self.tbl_fma_type.item(row_no, i).setFont(bold_font)
            
        """# Zones table
        zones = self.get_distinct_zones()
        zones.sort()
        for zone in zones:
            targets = self.get_distinct_targets_per_zone(zone)
            targets.sort()
            for target in targets:
                area = 0
                reached = 0
                for info_row in self.region_info:
                    if info_row[1] == zone and info_row[3] == target:
                        area += info_row[5]
                        if target > 0:
                            reached_th = info_row[4]
                            if reached_th:
                                reached += info_row[5]
                if area > 0:
                    percentage = round((area - reached) * 100 / area, 1)
                else:
                    percentage = "N/A"
                area = int(round(area, 0))
                reached = int(round(reached, 0))
                row_no = self.tbl_brmz.rowCount() 
                self.tbl_brmz.setRowCount(row_no + 1)
                self.tbl_brmz.setItem(row_no, 0, QCustomTableWidgetItem(zone))
                if target == -1:
                    fuel_type_desc = "with no target"
                    target = "N/A"
                    reached = "N/A"
                    percentage = "N/A"
                    burn = "N/A"
                else:
                    fuel_type_desc = "with target " + str(target) + "%"
                    if percentage < target:
                        burn = (target - percentage) * area/100
                        total_burn += burn
                        burn = int(round(burn, 0))
                    else:
                        burn = 0
                self.tbl_brmz.setItem(row_no, 1, QCustomTableWidgetItem(fuel_type_desc))
                self.tbl_brmz.setItem(row_no, 2, QCustomTableWidgetItem(area))
                self.tbl_brmz.setItem(row_no, 3, QCustomTableWidgetItem(reached))
                self.tbl_brmz.setItem(row_no, 4, QCustomTableWidgetItem(percentage))
                self.tbl_brmz.setItem(row_no, 5, QCustomTableWidgetItem(target))
                self.tbl_brmz.setItem(row_no, 6, QCustomTableWidgetItem(burn))
                if area > 0:
                    if target != "N/A" and percentage != "N/A":
                        if (area - reached) * 100 / area > target:      # i.e. if percentage > target
                            self.tbl_brmz.item(row_no, 4).setForeground(QColor(0, 150, 0, 255))
                        else:
                            self.tbl_brmz.item(row_no, 4).setForeground(QColor(200, 0, 0, 255))
        """
        self.align_cells()
                            
    def align_cells(self):
        tbl = self.tbl_fma_type
        for row_no in range(tbl.rowCount()):
            for col_no in [0, 1]:
                tbl.item(row_no, col_no).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            for col_no in [2, 3, 6]:
                tbl.item(row_no, col_no).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for col_no in [4, 5, 7, 8]:
                try:
                    tbl.item(row_no, col_no).setTextAlignment(Qt.AlignCenter)
                except:
                    pass

    def get_distinct_targets_per_fma(self, fma_type):
        targets = []
        for row in self.region_info:
            #if row[2] == fma_type:
            #    target = row[3]
            if row[1] == fma_type:
                target = row[2]
                if target not in targets:
                    targets.append(target)
        return targets

    """def get_distinct_zones(self):
        zones = []
        for row in self.region_info:
            zone = row[1]
            if zone not in zones:
                zones.append(zone)
        return zones
    """

    """def get_distinct_targets_per_zone(self, zone):
        targets = []
        for row in self.region_info:
            if row[1] == zone:
                target = row[3]
                if target not in targets:
                    targets.append(target)
        return targets
    """
        
    def cell_clicked_tbl_fma_type(self, row, column):
        fma_type = self.tbl_fma_type.item(row, 0).text()
        target = self.tbl_fma_type.item(row, 5).text()
        if column == 1:
            if target != 'N/A':
                heading = "Veg types for " + fma_type + " where target is for " + target + "% of the vegetation to be below the threshold age:\n"
            else:
                heading = "Veg types for " + fma_type + " where no target is specified in risk framework:\n"
                target = "-1"     # Note that target is changed (for input to sql statement)            
            sql = "SELECT fuel_type FROM fuel_type_indicative_thresholds WHERE " + fma_type + "_target = " + target
            if self.region_specific_thresholds:
                sql = sql.replace('fuel_type_indicative_thresholds', self.region.replace(" ", "_") + "_default_thresholds")
            if rfm_library.table_exists(self.region.lower().replace(" ", "_") + "_spatial_thresholds"):
                sql += " UNION SELECT DISTINCT fuel_type FROM " + self.region.replace(" ", "_") + "_spatial_thresholds WHERE " + fma_type + "_target = " + target
            sql += " ORDER BY fuel_type"
            fuel_types_result = rfm_library.run_select_sql(sql)
            fuel_types_string = ""
            for row in fuel_types_result:
                fuel_types_string += "* " + row[0] + "\n"
            QMessageBox.information(None, "Threshold veg type info", heading + fuel_types_string)
        elif column == 7:
            # Prob insert code to check whether already loaded - but need to incorporate FMA/target filter
            #filter_expression = QgsExpression("fma_type = '" + fma_type + "' AND target = " + target)
            if target != 'N/A':
                title = fma_type.upper() + " (" + target + "% target) fuel"
            else:
                target = "-1"     # Note that target is changed (for input to sql statement)
                title = fma_type.upper() + " (no target) fuel"
            filter = "fma_type = '" + fma_type + "' AND target = " + target
            rfm_library.load_postgis_layer(self.region.lower().replace(" ", "_") + "_underlying_report_data", None, None, filter, title)
            
        elif column == 8:
            # Prob insert code to check whether already loaded - but need to incorporate FMA/target filter
            #filter_expression = QgsExpression("fma_type = '" + fma_type + "' AND target = " + target)
            filter = "fma_type = '" + fma_type + "' AND target = " + target + " AND yslb >= threshold_age"
            title = fma_type.upper() + " (" + target + "% target) overage"
            rfm_library.load_postgis_layer(self.region.lower().replace(" ", "_") + "_underlying_report_data", None, None, filter, title)

    def export_csv(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        #get location of this file
        rfm_plugin_folder = os.path.dirname(os.path.abspath(__file__))
        report_template = os.path.join(rfm_plugin_folder, "rfm_resources/report.csv")
        try:
            f = open(report_template, 'w')
        except:
            QMessageBox.information(None, "Report file open!", "You may have the existing report file open.  Close it and try the export again.")
            return
        #f.write("Region, Zone, FMA Type, Target, Reached t'hold, Area" + os.linesep)
        f.write("Region, FMA Type, Target, Reached t'hold, Area" + "\n")

        for row in self.region_info:
            #f.write(str(row[0])+ ", " + str(row[1])+ ", " + str(row[2])+ ", " + str(row[3]) + ", " + str(row[4])+ ", " + str(row[5])+ os.linesep)
            f.write(str(row[0])+ ", " + str(row[1])+ ", " + str(row[2])+ ", " + str(row[3]) + ", " + str(row[4])  + "\n")
        f.close()
        xl = Dispatch("Excel.Application")
        xl.Visible = True # otherwise excel is hidden

        wb = xl.Workbooks.Open(report_template)
        QApplication.restoreOverrideCursor()
        QMessageBox.information(None, "Temporary file!", "The output file is stored in \nC:/Users/your_user_name/.qgis2/python/plugins/RFMPlanner/rfm_resources/report.csv and will be overwritten next time you export a report.  If you want to keep the infomation, save it as an Excel file in a location convenient for you.")
        bring_excel_to_front()


class NamedAssetSelectorDialog(QDialog, asset_name_selector.Ui_AssetNameSelectorDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        named_assets = rfm_library.get_named_assets()
        for asset in named_assets:
            item = QListWidgetItem(asset, self.listWidget)
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)

    def accept(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        selected_assets = []
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState() == Qt.Checked:
                selected_assets.append(self.listWidget.item(i).text())
        for asset in selected_assets:
            rfm_library.create_fma_single_asset(asset)
            name_for_tables = asset.lower().replace(" ", "_")
            rfm_library.open_named_asset_report(name_for_tables)
        QApplication.restoreOverrideCursor()
        self.close()

class BRMZsReportDialog(QDialog, brmzs_report.Ui_BRMZsReportDialog):
    def __init__(self, brmz_info):
        QDialog.__init__(self)
        self.setupUi(self)
        self.regions_by_brmz = brmz_info[0]
        self.non_existent_fmas_combined = brmz_info[1]
        self.brmz_data = brmz_info[2]
        self.tbl_brmz_info.setRowCount(0)
        self.tbl_brmz_info.setColumnWidth(0, 150)
        self.tbl_brmz_info.setColumnWidth(2, 70)
        self.tbl_brmz_info.setColumnWidth(3, 70)
        self.tbl_brmz_info.setColumnWidth(4, 70)
        self.fill_table()
        self.btn_close.clicked.connect(self.close)
        self.btn_csv.clicked.connect(self.export_csv)
        
    def fill_table(self):
        bold_font = QFont()
        bold_font.setBold(True)
        for item in self.regions_by_brmz:
            zone = item[0]
            region = item[1]
            row_no = self.tbl_brmz_info.rowCount()
            self.tbl_brmz_info.setRowCount(row_no + 1)
            if row_no > 0:
                zone_above = self.tbl_brmz_info.item(row_no - 1, 0).text()
                if zone != zone_above:
                    self.tbl_brmz_info.setItem(row_no, 0, QCustomTableWidgetItem(zone_above))
                    self.tbl_brmz_info.setItem(row_no, 1, QCustomTableWidgetItem("TOTAL"))
                    data = self.extract_whole_zone_data(zone_above)
                    area = data[0]
                    area = int(round(area, 0))
                    #reached = data[1]
                    #if area == 0:
                    #    percentage = "N/A"
                    #else:
                    #    percentage = round((area - reached)*100/area, 1)
                    #    area = int(round(area, 0))
                    #    reached = int(round(reached,0))
                    self.tbl_brmz_info.setItem(row_no, 2, QCustomTableWidgetItem("ALL"))
                    self.tbl_brmz_info.setItem(row_no, 3, QCustomTableWidgetItem(area))
                    self.tbl_brmz_info.item(row_no, 0).setFont(bold_font)
                    self.tbl_brmz_info.item(row_no, 1).setFont(bold_font)
                    self.tbl_brmz_info.item(row_no, 2).setFont(bold_font)
                    self.tbl_brmz_info.item(row_no, 3).setFont(bold_font)
                    row_no += 1
                    self.tbl_brmz_info.setRowCount(row_no + 1)
            self.tbl_brmz_info.setItem(row_no, 0, QCustomTableWidgetItem(zone))
            self.tbl_brmz_info.setItem(row_no, 1, QCustomTableWidgetItem(region))
            if region in self.non_existent_fmas_combined:
                self.tbl_brmz_info.setItem(row_no, 2, QCustomTableWidgetItem("No data"))
                self.tbl_brmz_info.setItem(row_no, 3, QCustomTableWidgetItem("No data"))
                self.tbl_brmz_info.setItem(row_no, 4, QCustomTableWidgetItem("No data"))
                self.tbl_brmz_info.setItem(row_no, 5, QCustomTableWidgetItem("No data"))
                self.tbl_brmz_info.setItem(row_no, 6, QCustomTableWidgetItem("No data"))
            else:
                targets = self.get_distinct_targets_per_zone_and_region(zone, region)
                targets.sort()
                rows_added = 0
                for target in targets:
                    area = 0
                    reached = 0
                    for info_row in self.brmz_data:
                        if info_row[0] == region.lower().replace(" ", "_") and info_row[1] == zone and info_row[3] == target:
                            area += info_row[5]
                            if target > 0:
                                reached_th = info_row[4]
                                if reached_th:
                                    reached += info_row[5]
                    if area > 0:
                        percentage = str(round((area - reached) * 100 / area, 1))
                    else:
                        percentage = "N/A"
                    area = int(round(area, 0))
                    reached = int(round(reached, 0))
                    if rows_added > 0:
                        row_no = self.tbl_brmz_info.rowCount() 
                        self.tbl_brmz_info.setRowCount(row_no + 1)
                        #self.tbl_brmz_info.setItem(row_no, 0, QCustomTableWidgetItem(zone))
                    
                    rows_added += 1
                    if target == -1:
                        fuel_type_desc = "with no target"
                        target = "N/A"
                        reached = "N/A"
                        percentage = "N/A"
                    else:
                        fuel_type_desc = "with target " + str(target) + "%"
                    self.tbl_brmz_info.setItem(row_no, 0, QCustomTableWidgetItem(zone))
                    self.tbl_brmz_info.setItem(row_no, 1, QCustomTableWidgetItem(region))
                    self.tbl_brmz_info.setItem(row_no, 2, QCustomTableWidgetItem(fuel_type_desc))
                    self.tbl_brmz_info.setItem(row_no, 3, QCustomTableWidgetItem(area))
                    self.tbl_brmz_info.setItem(row_no, 4, QCustomTableWidgetItem(reached))
                    self.tbl_brmz_info.setItem(row_no, 5, QCustomTableWidgetItem(percentage))
                    self.tbl_brmz_info.setItem(row_no, 6, QCustomTableWidgetItem(target))
                    if target != "N/A" and percentage != "N/A":
                        if area > 0:
                            if (area - reached) * 100 / area > target:      # i.e. if percentage > target
                                self.tbl_brmz_info.item(row_no, 5).setForeground(QColor(0, 150, 0, 255))
                            else:
                                self.tbl_brmz_info.item(row_no, 5).setForeground(QColor(200, 0, 0, 255))

        # Add last set of zone totals (shd turn this into one or more fns also called above)
        row_no = self.tbl_brmz_info.rowCount()
        self.tbl_brmz_info.setRowCount(row_no + 1)
        #if row_no > 0:
        zone_above = self.tbl_brmz_info.item(row_no - 1, 0).text()
        #if zone != zone_above:
        self.tbl_brmz_info.setItem(row_no, 0, QCustomTableWidgetItem(zone_above))
        self.tbl_brmz_info.setItem(row_no, 1, QCustomTableWidgetItem("TOTAL"))
        data = self.extract_whole_zone_data(zone_above)
        area = data[0]
        reached = data[1]
        if area == 0:
            percentage = "N/A"
        else:
            percentage = round((area - reached)*100/area, 1)
            area = int(round(area, 0))
            reached = int(round(reached,0))
        self.tbl_brmz_info.setItem(row_no, 2, QCustomTableWidgetItem(area))
        self.tbl_brmz_info.setItem(row_no, 3, QCustomTableWidgetItem(reached))
        self.tbl_brmz_info.setItem(row_no, 4, QCustomTableWidgetItem(percentage))
        self.tbl_brmz_info.item(row_no, 0).setFont(bold_font)
        self.tbl_brmz_info.item(row_no, 1).setFont(bold_font)
        self.tbl_brmz_info.item(row_no, 2).setFont(bold_font)
        self.tbl_brmz_info.item(row_no, 3).setFont(bold_font)
        self.tbl_brmz_info.item(row_no, 4).setFont(bold_font)
        
    def get_distinct_targets_per_zone_and_region(self, zone, region):
        targets = []
        for row in self.brmz_data:
            if row[0] == region.lower().replace(" ", "_") and row[1] == zone:
                target = row[3]
                if target not in targets:
                    targets.append(target)
        return targets

    def extract_data(self, zone, region):
        region = region.lower().replace(" ", "_")
        result = None
        area = 0
        reached = 0
        for row in self.brmz_data:
            if row[0] == region and row[1] == zone:
                area += row[5]
                if row[4]:      
                    reached += row[5]
        return (area, reached)
                
    def extract_whole_zone_data(self, zone):
        total = 0
        reached = 0
        for row in self.brmz_data:
            if row[1] == zone:
                total += row[5]
                if row[4]:      
                    reached += row[5]
        return (total, reached)

    def export_csv(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        #get location of this file
        rfm_plugin_folder = os.path.dirname(os.path.abspath(__file__))
        report_template = os.path.join(rfm_plugin_folder, "rfm_resources/report.csv")
        try:
            f = open(report_template, 'w')
        except:
            QMessageBox.information(None, "Report file open!", "You may have the existing report file open.  Close it and try the export again.")
            return
        #f.write("Region, Zone, FMA Type, Target, Reached t'hold, Area" + os.linesep)
        f.write("Region, Zone, FMA Type, Target, Reached t'hold, Area" + "\n")
        
        for row in self.brmz_data:
            #f.write(str(row[0])+ ", " + str(row[1])+ ", " + str(row[2])+ ", " + str(row[3]) + ", " + str(row[4])+ ", " + str(row[5])+ os.linesep)
            f.write(str(row[0])+ ", " + str(row[1])+ ", " + str(row[2])+ ", " + str(row[3]) + ", " + str(row[4])+ ", " + str(row[5])  + "\n")
        f.close()
        xl = Dispatch("Excel.Application")
        xl.Visible = True # otherwise excel is hidden

        wb = xl.Workbooks.Open(report_template)
        QApplication.restoreOverrideCursor()
        QMessageBox.information(None, "Temporary file!", "The output file is stored in \nC:/Users/your_user_name/.qgis2/python/plugins/RFMPlanner/rfm_resources/report.csv and will be overwritten next time you export a report.  If you want to keep the infomation, save it as an Excel file in a location convenient for you.")
        bring_excel_to_front()
        
        
class IndicTholdDialog(QDialog, show_thresholds.Ui_ListThresholdsDialog):
    def __init__(self, thresholds_list, regional_defaults=False, reg_defaults_tbl_name=None, region=None):
        QDialog.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.regional_defaults = regional_defaults
        self.reg_defaults_tbl_name = reg_defaults_tbl_name
        self.region = region
        self.tbl_thresholds.setRowCount(0)
        for i in range(self.tbl_thresholds.columnCount()):
            col_name = self.tbl_thresholds.horizontalHeaderItem(i).text()
            col_name = col_name.replace(" ", "\n")
            self.tbl_thresholds.setHorizontalHeaderItem(i, QTableWidgetItem(col_name))
        self.tbl_thresholds.setColumnWidth(0, 200)
        self.tbl_thresholds.setColumnWidth(1, 80)
        self.tbl_thresholds.setColumnWidth(2, 60)
        self.tbl_thresholds.setColumnWidth(3, 60)
        self.tbl_thresholds.setColumnWidth(4, 60)
        self.tbl_thresholds.setColumnWidth(5, 100)
        self.tbl_thresholds.setColumnWidth(6, 100)
        if not regional_defaults:
            self.tbl_thresholds.setColumnCount(5)   # i.e. remove update column and its buttons
        self.fill_table(thresholds_list)
        self.btn_close.clicked.connect(self.close)
        
    def fill_table(self, thresholds_list):
        for row in thresholds_list:
            self.fill_row(row)
            
    def fill_row(self, row):
        row_no = self.tbl_thresholds.rowCount()
        self.tbl_thresholds.setRowCount(row_no + 1)
        #if row_no > 0:
        self.tbl_thresholds.setItem(row_no, 0, QTableWidgetItem(row[0]))
        self.tbl_thresholds.item(row_no, 0).setFlags(Qt.ItemIsEditable)
        self.tbl_thresholds.setItem(row_no, 1, QTableWidgetItem(str(row[1])))
        self.tbl_thresholds.item(row_no, 1).setFlags(Qt.ItemIsEditable)
        self.tbl_thresholds.setItem(row_no, 2, QCustomTableWidgetItem(row[2]))
        self.tbl_thresholds.item(row_no, 2).setFlags(Qt.ItemIsEditable)
        self.tbl_thresholds.setItem(row_no, 3, QCustomTableWidgetItem(row[3]))
        self.tbl_thresholds.item(row_no, 3).setFlags(Qt.ItemIsEditable)
        self.tbl_thresholds.setItem(row_no, 4, QCustomTableWidgetItem(row[4]))
        self.tbl_thresholds.item(row_no, 4).setFlags(Qt.ItemIsEditable)
        if self.regional_defaults:
            update_button = QPushButton("Update")
            self.tbl_thresholds.setCellWidget(row_no, 5, update_button)
            update_button.clicked.connect(lambda: self.update(row[5]))  # row[5] is pk for regional default_thresholds table
            spatial_button = QPushButton("Add")
            self.tbl_thresholds.setCellWidget(row_no, 6, spatial_button)
            spatial_button.clicked.connect(lambda: self.add_spatial(row[5]))  # row[5] is pk for regional default_thresholds table

    def update(self, pk):
        self.update_dlg = UpdateTholdDialog(self.reg_defaults_tbl_name, pk, self)
        self.update_dlg.show()
        
    def add_spatial(self, pk):
        self.add_spatial_dlg = AddSpatialDialog(self.reg_defaults_tbl_name, pk, self)
        self.add_spatial_dlg.show()
        
        
class UpdateTholdDialog(QDialog, update_threshold.Ui_UpdateThresholdDialog):
    def __init__(self, reg_defaults_tbl_name, pk, parent_dlg):
        from rfm_library import run_select_sql
        #try:
        QDialog.__init__(self)
        self.setupUi(self)
        self.reg_defaults_tbl_name = reg_defaults_tbl_name
        self.pk = str(pk)
        self.parent_dlg = parent_dlg
        self.region = self.parent_dlg.region
        self.current_info = run_select_sql("SELECT * FROM " + self.reg_defaults_tbl_name + " WHERE pk = " + self.pk)
        self.txt_fuel.setText(str(self.current_info[0][0]))
        self.txt_fuel.setEnabled(False)
        self.txt_thold_age.setText(str(self.current_info[0][1]))
        self.txt_shs_target.setText(str(self.current_info[0][2]))
        self.txt_cib_target.setText(str(self.current_info[0][3]))
        self.txt_lrr_target.setText(str(self.current_info[0][4]))
        self.textBrowser.setVisible(False)
        #except Exception as e:
        #    debug(e.msg)
        
    def accept(self):
        from rfm_library import run_nonselect_sql, update_updates_table
        fuel = self.txt_fuel.text()
        thold = self.txt_thold_age.text()
        shs_target = self.txt_shs_target.text()
        cib_target = self.txt_cib_target.text()
        lrr_target = self.txt_lrr_target.text()
        try:
            thold_int = int(thold)
            if thold_int == 0 or thold_int < -1:
                QMessageBox.information(None, "Invalid value!", "Threshold age must be -1 or a positive integer!")
                self.txt_thold_age.setText(str(self.current_info[0][2]))
                return
        except:
            QMessageBox.information(None, "Invalid value!", "Threshold age must be -1 or a positive integer!")
            self.txt_thold_age.setText(str(self.current_info[0][2]))
            return
        try:
            for target in [shs_target, cib_target, lrr_target]:
                target_int = int(target)
                if target_int < -1 or target_int == 0 or target_int > 100:
                    QMessageBox.information(None, "Invalid value!", "Target must be -1 or a positive integer up to 100!")
                    self.txt_shs_target.setText(str(self.current_info[0][2]))
                    self.txt_cib_target.setText(str(self.current_info[0][3]))
                    self.txt_lrr_target.setText(str(self.current_info[0][4]))
                    return
        except:
            QMessageBox.information(None, "Invalid value!", "Target must be -1 or a positive integer up to 100!")
            self.txt_shs_target.setText(str(self.current_info[0][2]))
            self.txt_cib_target.setText(str(self.current_info[0][3]))
            self.txt_lrr_target.setText(str(self.current_info[0][4]))
            return
        sql = "UPDATE " + self.reg_defaults_tbl_name + " SET threshold_age = " + thold + ", shs_target = " + shs_target + ", cib_target = " + cib_target + ", lrr_target = " + lrr_target + " WHERE pk = " + self.pk
        run_nonselect_sql([sql])
        update_updates_table(self.region + "_default_thresholds")
        msg = "threshold_age set to " + thold + ", shs_target set to " + shs_target + ", cib_target set to " + cib_target + ", lrr_target set to " + lrr_target
        QMessageBox.information(None, "Complete", msg)
        self.close()
        self.update_parent_dlg(fuel, thold, shs_target, cib_target, lrr_target)
        
    def update_parent_dlg(self, fuel, thold, shs_target, cib_target, lrr_target):
        row_count = self.parent_dlg.tbl_thresholds.rowCount()
        for row in range(row_count):
            if self.parent_dlg.tbl_thresholds.item(row, 0).text() == fuel:
                self.parent_dlg.tbl_thresholds.item(row, 1).setText(thold)
                self.parent_dlg.tbl_thresholds.item(row, 2).setText(shs_target)
                self.parent_dlg.tbl_thresholds.item(row, 3).setText(cib_target)
                self.parent_dlg.tbl_thresholds.item(row, 4).setText(lrr_target)


class AddSpatialDialog(UpdateTholdDialog, update_threshold.Ui_UpdateThresholdDialog):
    def __init__(self, reg_defaults_tbl_name, pk, parent_dlg):
        from rfm_library import run_select_sql
        #try:
        UpdateTholdDialog.__init__(self, reg_defaults_tbl_name, pk, parent_dlg)
        self.setupUi(self)
        self.reg_defaults_tbl_name = reg_defaults_tbl_name
        self.pk = str(pk)
        self.parent_dlg = parent_dlg
        self.region = self.parent_dlg.region
        self.current_info = run_select_sql("SELECT * FROM " + self.reg_defaults_tbl_name + " WHERE pk = " + self.pk)
        self.txt_fuel.setText(str(self.current_info[0][0]))
        self.txt_fuel.setEnabled(False)
        self.txt_thold_age.setText(str(self.current_info[0][1]))
        self.txt_shs_target.setText(str(self.current_info[0][2]))
        self.txt_cib_target.setText(str(self.current_info[0][3]))
        self.txt_lrr_target.setText(str(self.current_info[0][4]))
        #except Exception as e:
        #    debug(e.msg)
            
    def accept(self):
        from rfm_library import update_spat_var_tholds
        fuel = self.txt_fuel.text()
        thold_age = self.txt_thold_age.text()
        shs_target = self.txt_shs_target.text()
        cib_target = self.txt_cib_target.text()
        lrr_target = self.txt_lrr_target.text()
        update_spat_var_tholds(fuel, thold_age, shs_target, cib_target, lrr_target)
        self.parent_dlg.showMinimized()
        self.close()