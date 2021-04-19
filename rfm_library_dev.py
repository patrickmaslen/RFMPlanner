##################################################
### CONTENTS
###  CREATION OF FMA POLYGONS
###  VEG AGE THRESHOLD AND TARGET CUSTOMISATION AND CALCULATION
###  UTILITIES


import ConfigParser, datetime, ogr2ogr, os
from shutil import copyfile

from PyQt4.QtCore import QSettings, Qt, QVariant
from PyQt4.QtGui import QAction, QApplication, QCursor, QFont, QHeaderView, QMenu, QMessageBox, QTableWidgetItem
from PyQt4 import QtSql
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsDataSourceURI, QgsFeature, QgsField, \
    QgsGeometry, QgsMapLayerRegistry, QgsPoint, QgsProject, QgsVectorFileWriter, QgsVectorLayer
from qgis.gui import *
import qgis.utils
import processing
import psycopg2
from pyspatialite import dbapi2 as sqlite3
import globals
import rfm_planner_dialogs
import sql_clauses
import time
import getpass
import subprocess

iface = qgis.utils.iface
albers_wa_string = 'proj4: +proj=aea +lat_1=-17.5 +lat_2=-31.5 +lat_0=0 +lon_0=121 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
rfm_resources_dir = os.path.join(os.path.dirname(__file__), "rfm_resources")

def initialise_settings(rfmplanner):
    # Called by rfm_planner.rfm_menu.aboutToShow, get_regional_asset_layers, get_regions
    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
    if not globals.settings_initialised:
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__),'config.cfg'))
        globals.prioritisation_on = config.getboolean('settings_menu', 'prioritisation')
        globals.db = config.get('settings_menu', 'db')
        if not globals.dev and not globals.uat:
            globals.rfmp_db = config.get('general', 'prod_db')
            globals.rfmp_host = config.get('general', 'prod_host')
            globals.rfmp_port = config.get('general', 'prod_port')
        else:
            if globals.uat:
                globals.rfmp_db = config.get('general', 'uat_db')
            elif globals.dev:
                globals.rfmp_db = config.get('general', 'dev_db')
            globals.rfmp_host = config.get('general', 'uat_host')
            globals.rfmp_port = config.get('general', 'uat_port')
        globals.rfmp_user = config.get('general', 'rfmp_user')
        globals.rfmp_pw = config.get('general', 'rfmp_pw')
        globals.connection_string = "dbname=" + globals.rfmp_db + " host=" + globals.rfmp_host +  " port=" + globals.rfmp_port + " user=" + globals.rfmp_user + " password=" + globals.rfmp_pw
        globals.spatialite_db = os.path.join(os.path.dirname(__file__),config.get('general', 'spatialite_db'))
        # Connect to db
        if globals.db == 'postgis':
            globals.conn = psycopg2.connect(globals.connection_string)
        elif globals.db == 'spatialite':
            globals.conn = sqlite3.connect(globals.spatialite_db)
        globals.preferred_region = config.get('preferred_region', 'preferred_region')
        globals.ogr2ogr_path = '"' + os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'rfm_resources', 'ogr2ogr.exe')) + '"'
        
        # Check if user is administrator
        globals.administrator = find_if_admin()
        if globals.administrator:
            rfmplanner.import_new_fuel_age_action = QAction("Import new fuel age data", rfmplanner.iface.mainWindow())
            rfmplanner.import_new_fuel_type_action = QAction("Import new fuel type data", rfmplanner.iface.mainWindow())
            #rfmplanner.data_admin_menu.addAction(rfmplanner.import_new_fuel_age_action)
            #rfmplanner.data_admin_menu.addAction(rfmplanner.import_new_fuel_type_action)
            rfmplanner.import_new_fuel_age_action.triggered.connect(import_new_fuel_age)
            rfmplanner.import_new_fuel_type_action.triggered.connect(import_new_fuel_type)
        globals.settings_initialised = True
        
        update_regional_assets_menu(globals.update_assets_menu, True)
        update_regional_assets_menu(globals.prioritise_menu, True)
        update_preferred_region_menu(globals.preferred_region_menu)
        
        # Check for new data - commented out as most relevant data is in a gdb, less conducive to mod date checks.
        #tables_to_check = dict(config.items('data_locations'))
        #check_for_new_data(tables_to_check)
    QApplication.restoreOverrideCursor()
    
def find_if_admin():
    # Detects if this user has data admin privileges
    # Called by __init__
    username = getpass.getuser().lower()
    sql = "SELECT COUNT(*) FROM administrators WHERE username = '" + username + "'"
    result = run_select_sql(sql)[0][0]
    if result == 0:
        return False
    elif result == 1:
        return True
    
def append_assets():
    # Appends new assets to existing asset tables - not directly but by doing a couple of checks then calling rfm_planner_dialogs.AddExistingAssetsDialog()
    # Called by rfm_planner.append_assets_action.triggered
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    # Check whether any non-RFMP layers loaded
    non_rfmp_layers = []
    registry = QgsMapLayerRegistry.instance()
    layers = registry.mapLayers()
    for layer in layers:
        if not layers[layer].source().startswith("dbname='" + globals.rfmp_db + "'"):
            non_rfmp_layers.append(layers[layer])
    if len(non_rfmp_layers) == 0:
        QMessageBox.information(None, "Add layer to map!", "To copy a layer into the database, it needs to be added to the map first.")
        QApplication.restoreOverrideCursor()
        return
    # Check that at least one RFMP layer has been created
    tables = get_regional_asset_layers(True)
    if len(tables) == 0:
        QMessageBox.information(None, "No RFM tables yet!", "Before copying a layer into the database, the appropriate asset table must be created in the database.  In the RFM Planning menu, use 'Set up asset layers'.")
        QApplication.restoreOverrideCursor()
        return
    add_existing_data_form = rfm_planner_dialogs.AddExistingAssetsDialog()
    QApplication.restoreOverrideCursor()
    add_existing_data_form.exec_()
    
def update_regional_assets_menu(update_assets_menu, pref_rgn_only):
    # POPULATES AND SORTS (PREFERRED REGION FIRST THEN OTHER REGIONS IN ALPHABETICAL ORDER) DIALOGUES LISTING ASSET/FMA LAYERS
    # update_assets_menu is either globals.update_assets_menu or globals.prioritise_menu
    # pref_rgn_only is Boolean
    # Called by initialise_settings, change_preferred_region,  rfm_planner_dialogs.CreateRegionAssetsDialog.accept
    update_assets_menu.clear()
    load_regional_assets_action = {}
    regional_asset_layers = get_regional_asset_layers(pref_rgn_only)
    for i in range(len(regional_asset_layers)):
        load_regional_assets_action[i] = QAction(regional_asset_layers[i], qgis.utils.iface.mainWindow())
        update_assets_menu.addAction(load_regional_assets_action[i])
        
def update_preferred_region_menu(preferred_region_menu):
    # ENSURES PREFERRED REGION IS SHOWN IN BOLD IN THE 'PREFERRED REGION' MENU
    # Called by initialise_settings, change_preferred_region
    preferred_region_menu.clear()
    preferred_region_action = {}
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__),'config.cfg'))
    preferred_region = config.get('preferred_region', 'preferred_region')
    preferred_region_font = QFont()
    preferred_region_font.setBold(True)
    regions = ["All of WA"] + get_regions()
    for i in range(len(regions)):
        preferred_region_action[i] = QAction(regions[i], qgis.utils.iface.mainWindow())
        if regions[i] == preferred_region:
            preferred_region_action[i].setFont(preferred_region_font)
        preferred_region_menu.addAction(preferred_region_action[i])

def change_preferred_region(q):  # q is an instance of QAction
    # Called by rfm_planner.initGui (when preferred_region_menu.triggered)
    #config file used to store preferred region between QGIS sessions; globals used during operation.
    config_file = os.path.join(os.path.dirname(__file__),'config.cfg')
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config.set('preferred_region', 'preferred_region', q.text())
    with open(config_file, 'wb') as configfile:
        config.write(configfile)
    update_preferred_region_menu(globals.preferred_region_menu)
    globals.preferred_region = q.text()
    update_regional_assets_menu(globals.update_assets_menu, True)
    update_regional_assets_menu(globals.prioritise_menu, True)

def get_regional_asset_layers(pref_rgn_only, type="asset"):
    # Returns list of asset layers for region (or whole of WA)
    # pref_rgn_only is Boolean
    # type is one of 'asset', 'fma' or 'draft fma'
    # Called by append_assets, update_regional_assets_menu, rfm_planner_dialogs.show_postgis_tables, rfm_planner_dialogs.AssetTableSelectorDialog.__init__
    if not globals.settings_initialised:
        initialise_settings()
    if globals.db == "postgis":
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    elif globals.db == "spatialite":
        sql = "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    rows = run_select_sql(sql)
    tables = []
    if type == "asset":
        for row in rows:
            for vector_type in ["polys", "lines", "points"]:
                if row[0].endswith("_asset_" + vector_type):
                    tables.append(row[0])
    elif type == "fma":
        for row in rows:
            if "_fmas" in row[0]:
                tables.append(row[0])
    elif type == "draft fma":
        for row in rows:
            if "_fma_seed" in row[0]:
                tables.append(row[0])
    if globals.preferred_region == "All of WA":
        return sorted(tables)
    else:
        tables.sort()
        reordered_tables = []
        for table in tables:
            if table.lower().startswith(globals.preferred_region.lower().replace(" ", "_")):
                reordered_tables.append(table)
        for table in reordered_tables:
            tables.remove(table)
        if not pref_rgn_only:
            reordered_tables += tables
        return reordered_tables
    
def get_regions():
    # RETURNS LIST OF ALL DBCA REGIONS
    # Called by update_preferred_region_menu
    if not globals.settings_initialised:
        initialise_settings()
    sql = "SELECT region FROM regions"
    rows = run_select_sql(sql)
    regions = []
    for row in rows:
        regions.append(row[0])
    return regions    

def set_editor_widgets(vlayer):
    # Called by load_postgis_layer (only for asset layers - sets editor widgets in QGIS)
    fields = vlayer.fields()
    relevant_field_indices = {"fma": -1, "resilience": -1, "asset_class": -1}
    for field_name in relevant_field_indices:
        relevant_field_indices[field_name] = fields.indexFromName(field_name)
    for field in relevant_field_indices:
        value_dict = {}
        if field in relevant_field_indices:
            for val in globals.expected_values[field]:
                value_dict[val] = val
        vlayer.editFormConfig().setWidgetType(relevant_field_indices[field], "ValueMap")
        vlayer.editFormConfig().setWidgetConfig(relevant_field_indices[field], value_dict)

"""def check_for_new_data(tables):
    # Called by initialise_settings
    try:
        for table, path in tables.items():
            update_needed = False
            #get mod date
            mod_date_unix = os.path.getmtime(path)
            mod_date = datetime.datetime.fromtimestamp(mod_date_unix).strftime('%Y-%m-%d %H:%M')
            #get table date
            table_date_info = run_select_sql("SELECT last_update FROM table_updates WHERE table_name = '" + table + "'")
            if len(table_date_info) == 0:
                update_needed = True
            else:
                table_date = table_date_info[0][0]
                if mod_date > table_date:
                    update_needed = True
            if update_needed:
                import_table(table, path)
    except:
        pass
"""

def import_table(table, path):
    # Called by check_for_new_data
    try:
        QMessageBox.information(None, "Table update required", "New data has been found for " + \
                            table + ".  It will take a few moments to update this.")
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        #write to db (overwriting existing table) and projecting to WA Albers
        ogr2ogr.main([ "",
            "-overwrite",
            "-f", "PostgreSQL",
            "PG:" + globals.connection_string,
            "-lco", "GEOMETRY_NAME=geometry",
            "-nlt", "MULTIPOLYGON", 
            "-nln", table, 
            "-t_srs", albers_wa_string,
            path
            ])
        QMessageBox.information(None, "Great success!", "Table imported")
        #update updates table
        update_updates_table(table)
        QApplication.restoreOverrideCursor()
    except Exception as e:
        QMessageBox.information(None, "Problem importing table", "There was a problem importing " + table + ".  Take a screenshot of this message and contact GIS Apps in OIM\n\n" + str(e))
    finally:
        QApplication.restoreOverrideCursor()

def open_group_editing_assistant(start_layer=None):
    # Called by check_fma_correctly_filled (subject to MsgBox), check_asset_class_and_resilience_correctly_filled (subject to MsgBox), rfm_planner.initGui
    globals.group_editor = rfm_planner_dialogs.GroupEditorMainWindow()
    if start_layer:
        globals.group_editor.cbx_postgis_tables.setCurrentIndex(globals.group_editor.cbx_postgis_tables.findText(start_layer))
    globals.group_editor.show()

def open_detailed_editing_assistant(start_layer=None):
    # Called by open_group_editing_assistant
    globals.detailed_editing_assistant = rfm_planner_dialogs.DetailedEditorMainWindow()
    if start_layer:
        globals.detailed_editing_assistant.cbx_postgis_tables.setCurrentIndex(globals.detailed_editing_assistant.cbx_postgis_tables.findText(start_layer))
    globals.detailed_editing_assistant.show()

def manage_prioritise_assets(q):  # q is an instance of QAction
    # Called by fma_planner.prioritise_menu.triggered
    postgis_table = q.text()
    # Check whether any rows in postgis_table
    sql = "SELECT COUNT(*) FROM " + postgis_table
    if run_select_sql(sql)[0][0] == 0:
        QMessageBox.information(None, "No data!", postgis_table + " is empty so there are no assets to prioritise for this layer.")
        return
    if check_asset_class_and_resilience_correctly_filled(postgis_table) == "stop":
        return
    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
    sql_list = []
    for asset_class in globals.asset_class_priorities:
        class_priority = globals.asset_class_priorities[asset_class]
        for resil in globals.expected_values["resilience"]:
            reg_priority = globals.regional_priority_grid[class_priority][resil]
            sql = "UPDATE " + postgis_table + " SET priority = " + str(reg_priority) + " WHERE asset_class = '" + asset_class + "' AND resilience = '" + resil + "'"
            sql_list.append(sql)
            run_nonselect_sql(sql_list)
    QApplication.restoreOverrideCursor()
    QMessageBox.information(None, "", postgis_table + " prioritisation complete")


#############################################################
###  CREATION OF FMA POLYGONS
#############################################################

def create_fmas(warn_if_exists=True):
    # Controls the generation of FMAs
    # Called by rfm_planner.generate_fma_action.triggered, show_indicative_thresholds (if FMAs have not yet been calculated)
    if globals.db == "spatialite":
        QApplication.restoreOverrideCursor()
        QMessageBox.information(None, "Not available in local db", "Calculation of FMAs is not available from the local spatialite database.")
        return
    start = datetime.datetime.now().strftime("%H:%M:%S")
    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
    region_to_buffer = get_region_to_buffer()
    if region_to_buffer is None:
        QMessageBox.information(None, "No asset layers!", "You need to create at least one asset layer.  Go to the RFM Planning menu > Set up asset layers.")
        QApplication.restoreOverrideCursor()
        return
    elif region_to_buffer == "cancelled":
        QApplication.restoreOverrideCursor()
        return
    else:
        if table_exists(region_to_buffer + "_fmas_complete") and warn_if_exists:
            reply = QMessageBox.information(None, "FMAs already calculated!", region_to_buffer + "_fmas_complete already exists in the database.  Are you sure you want to overwrite it?  (This could take up to 2 hrs).", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                QApplication.restoreOverrideCursor()
                return
        # Following line commented out but can be re-included if different fma_group_bys required (e.g.group by fma and piority)
        #get_fma_tables_to_create()
        #globals.fma_group_bys = ["fma"]
        
        # Following lines commented out but can be re-included if different fma_group_bys required (e.g.group by fma and piority)
        #if globals.fma_group_bys is None:
        #    return
        #elif globals.fma_group_bys == []:
        #    QMessageBox.information(None, "No selection made", "No FMA grouping was selected.")
        #    return
        #else:
        fcs_to_buffer = get_fcs_to_buffer(region_to_buffer)     # e.g. warren_asset_polys
        # Get relevant fma types (i.e. which of SHS, CIB, LRR appear in the assets fcs)
        fma_types_in_fcs = []
        for fc in fcs_to_buffer:
            if not check_fma_correctly_filled(fc):
                QApplication.restoreOverrideCursor()
                return
        for fc in fcs_to_buffer:
            sql = "SELECT DISTINCT fma FROM " + fc + " WHERE fma IS NOT NULL"
            fma_types_in_fc = run_select_sql(sql)
            for type in fma_types_in_fc:
                if type[0] not in fma_types_in_fcs:
                    fma_types_in_fcs.append(type[0])
        
        #debug_msg_box('some test code starts 353')
        #if not region_to_buffer in globals.forest_regions:
        #    if 'LRR' in fma_types_in_fcs:
        #        create_interim(current_fma, lower_priority_fmas)
        #return
            #    erase LRR_polys from interim_copy of region_fma_seed
            #    insert LRR_polys into interim_copy of region_fma_seed
        #remove 'LRR' from fma_types_in_fcs

        intersect_layers_info = []  # Will be filled with lists of 3 items each: region_to_buffer (text), fma_type (text) and intersect_layer (text - name of temp_intersect_tbl_name returned by calculate_buffers - e.g. ["warren", "CIB", "warren_intersects_cib"])
        for fma_type in fma_types_in_fcs:
            intersect_layer = calculate_buffers(region_to_buffer, fma_type, fcs_to_buffer)
            if intersect_layer != "failed":
                intersect_layers_info.append([region_to_buffer, fma_type, intersect_layer])
            else:
                return

        # At this point we have e.g. warren_intersects_cib and warren_intersects_shs; takes < 5 sec
        QApplication.restoreOverrideCursor()
        return
        drop_list = []  # Will be filled with list of interim PostGIS tables which can be dropped after completion
        for intersect_layer_info in intersect_layers_info:
            region = intersect_layer_info[0]
            fma_type = intersect_layer_info[1].lower()
            intersect_layer = intersect_layer_info[2]
            fma_layer_name = region + "_fmas_" + fma_type    # e.g. warren_fmas_cib
            iface.mainWindow().statusBar().showMessage("creating " + fma_layer_name)
            drop_sql = "DROP TABLE IF EXISTS " + fma_layer_name + "; DROP INDEX IF EXISTS " + fma_layer_name + "_spatial_idx;"
            drop_list.append(drop_sql)
            drop_intersect_sql = "DROP TABLE IF EXISTS " + intersect_layer
            drop_list.append(drop_intersect_sql)
            if globals.prioritisation_on:
                create_sql = "CREATE TABLE " + fma_layer_name + "(fma text, name text, priority integer, geometry geometry(MultiPolygon, 900914));"
                insert_sql = "INSERT INTO " + fma_layer_name + " SELECT '" + fma_type.upper() + "', name, priority, ST_Multi((ST_Dump(ST_Union(geometry))).geom) FROM " + intersect_layer + " GROUP BY priority;"
            else:
                create_sql = "CREATE TABLE " + fma_layer_name + "(fma text, name text, geometry geometry(MultiPolygon, 900914));"
                insert_sql = "INSERT INTO " + fma_layer_name + " SELECT '" + fma_type.upper() + "', name, ST_Multi((ST_Dump(ST_Union(geometry))).geom) FROM " + intersect_layer + " GROUP BY name;"
            index_sql = "CREATE INDEX " + fma_layer_name + "_spatial_idx ON " + fma_layer_name + " USING GIST (geometry);"
            name_index_sql = "CREATE INDEX " + fma_layer_name + "_name_idx ON " + fma_layer_name + " USING BTREE (name);"
            make_valid_sql = "UPDATE " + fma_layer_name + " SET geometry = ST_CollectionExtract(ST_MakeValid(geometry), 3) WHERE NOT ST_IsValid(geometry);"
            run_nonselect_sql([drop_sql, create_sql, index_sql, insert_sql, make_valid_sql, "ANALYZE " + fma_layer_name])
        # Takes about 5 sec to get here; at this point we have e.g. warren_fmas_cib and warren_fmas_shs
        combined_fmas = combine_fmas_non_overlapping(region, fma_types_in_fcs)      # returns name of combined_fmas layer e.g. warren_fmas_combined
        complete_fmas(region_to_buffer)
        #run_nonselect_sql(drop_list)
        QApplication.restoreOverrideCursor()
        #now = datetime.datetime.now().strftime("%H:%M:%S")
        #debug_msg_box("started " + start + "\nfinished " + now)

def get_fcs_to_buffer(region):
    # Called by create_fmas
    if globals.db == "postgis":
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
    elif globals.db == "spatialite":
        sql = "SELECT name FROM sqlite_master WHERE type = 'table';"
    rows = run_select_sql(sql)
    fcs = []
    for row in rows:
        for vector_type in ["polys", "lines", "points"]:
            if row[0] == region + "_asset_" + vector_type:
                fcs.append(row[0])
    return fcs

"""def get_fma_tables_to_create():
    table_selector = rfm_planner_dialogs.SelectFMAGroupingDialog()
    QApplication.restoreOverrideCursor()
    table_selector.exec_()
"""

def get_region_to_buffer():
    #get set of regions for which there are asset layers
    # Called by create_fmas
    if globals.db == "postgis":
        sql = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_asset_%' AND table_schema='public' AND table_type='BASE TABLE';"
    elif globals.db == "spatialite":
        sql = "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%_asset_%' AND name NOT LIKE 'sqlite_%';"
    results = run_select_sql(sql)
    regions_with_assets = []
    for item in results:
        region_name = item[0][:item[0].find("_asset_")]
        if region_name not in regions_with_assets:
            regions_with_assets.append(str(region_name))
    if len(regions_with_assets) == 0:
        return None
    elif globals.preferred_region == "All of WA":
        if len(regions_with_assets) == 1:
            return regions_with_assets[0]
        else:
            rgn_selector_msg = QMessageBox(QMessageBox.Information, "Select region", "Choose which region to buffer.")
            for rgn in regions_with_assets:
                rgn_selector_msg.addButton(rgn, QMessageBox.AcceptRole)
            cancel = rgn_selector_msg.addButton(QMessageBox.Cancel)
            rgn_selector_msg.exec_()
            if rgn_selector_msg.clickedButton() == cancel:
                return "cancelled"
            else:
                return rgn_selector_msg.clickedButton().text()
    else:
        if globals.preferred_region.lower().replace(" ", "_") in regions_with_assets:
            return globals.preferred_region.lower().replace(" ", "_")
        else:
            return None

def check_fma_correctly_filled(fc):
    # Called by create_fmas
    sql = "SELECT * FROM " + fc + " WHERE fma NOT IN ('SHS', 'CIB', 'LRR', 'RAM') OR fma IS NULL"
    results = run_select_sql(sql)
    if len(results) == 0:
        return True
    else:
        reply = QMessageBox.warning(None, "Invalid FMA(s)!", 
            "There are " + str(len(results)) + " invalid values for FMA in " + fc + \
            ".  The buffer can only be performed when every row in the attribute table" \
            " has one of the following values in the FMA column: SHS, CIB, LRR, RAM.\n\nWould you like to open the Editing Assistant to work on this?", QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            open_group_editing_assistant(fc)
        return False

def check_asset_class_and_resilience_correctly_filled(fc):
    # Called by manage_prioritise_assets
    count_sql = "SELECT COUNT(*) FROM " + fc
    count = run_select_sql(count_sql)[0][0]
    asset_classes_string = str(globals.expected_values["asset_class"])[1:-1]
    resiliences_string = str(globals.expected_values["resilience"])[1:-1]
    sql = "SELECT * FROM " + fc + " WHERE asset_class NOT IN (" + asset_classes_string + ") OR asset_class IS NULL OR resilience NOT IN (" + resiliences_string + ") OR resilience IS NULL"
    results = run_select_sql(sql)
    if len(results) > 0:
        reply = QMessageBox.warning(None, "Invalid Data!", 
            "There are " + str(len(results)) + " rows in " + fc + " with invalid values for asset_class and/or resilience.  Priorities can only be calculated for " + str(count - len(results)) + " of the " + str(count) + " rows.\n\nWould you like to open the Editing Assistant to work on this?", QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            open_group_editing_assistant(fc)
            return "stop"
        elif reply == QMessageBox.No:
            return None
        elif reply == QMessageBox.Cancel:
            return "stop"

def calculate_buffers(region_to_buffer, fma_type, fcs_to_buffer):
    # Calculates a set of buffers for the region and the specified fma_type, based on the asset points, lines and polys
    # Called by create_fmas (once for each fma type)
    try:
        # Set up intersects table e.g. warren_intersects_lrr
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        temp_intersect_tbl_name = region_to_buffer + "_intersects_" + fma_type      # e.g. warren_intersects_lrr
        iface.mainWindow().statusBar().showMessage("calculating buffers for " + temp_intersect_tbl_name) 
        drop_sql = "DROP TABLE IF EXISTS " + temp_intersect_tbl_name
        if globals.prioritisation_on:
            create_sql = "CREATE TABLE " + temp_intersect_tbl_name + " (name text, priority integer, geometry geometry(MultiPolygon, 900914))"
        else:
            create_sql = "CREATE TABLE " + temp_intersect_tbl_name + " (name text, geometry geometry(MultiPolygon, 900914))"
        spatial_index_sql = "CREATE INDEX " + temp_intersect_tbl_name + "_idx ON " + temp_intersect_tbl_name + " USING GIST (geometry);"
        name_index_sql = "CREATE INDEX " + temp_intersect_tbl_name + "_name_idx ON " + temp_intersect_tbl_name + " USING BTREE (name);"
        run_nonselect_sql([drop_sql, create_sql, spatial_index_sql])
        #get buffers
        sql = "SELECT DISTINCT buffer FROM vw_fma_buffers WHERE fma_code = '" + fma_type + "' ORDER BY buffer DESC"
        buffer_distances = run_select_sql(sql)      # e.g. [(None,), (-1,), (5000,), (1000,), (500,)] NB -1 indicates Southwestern regions
        drop_list = []
        for buffer_distance in buffer_distances:
            if buffer_distance[0] is not None:
                temp_buffer_tbl_name = region_to_buffer + "_buffers_" + fma_type + "_" + str(buffer_distance[0])        # e.g. warren_buffers_lrr_5000
                drop_sql = "DROP TABLE IF EXISTS " + temp_buffer_tbl_name
                if globals.prioritisation_on:
                    create_sql = "CREATE TABLE " + temp_buffer_tbl_name + " (name text, priority integer, geometry geometry(MultiPolygon, 900914))"
                else:
                    create_sql = "CREATE TABLE " + temp_buffer_tbl_name + " (name text, geometry geometry(MultiPolygon, 900914))"
                spatial_index_sql = "CREATE INDEX " + temp_buffer_tbl_name + "_idx ON " + temp_buffer_tbl_name + " USING GIST (geometry);"
                name_index_sql = "CREATE INDEX " + temp_buffer_tbl_name + "_name_idx ON " + temp_buffer_tbl_name + " USING BTREE (name);"
                run_nonselect_sql([drop_sql, create_sql, spatial_index_sql])
                drop_list.append(drop_sql)
                for fc in fcs_to_buffer:
                    if globals.prioritisation_on:
                        insert_sql = "INSERT INTO " + temp_buffer_tbl_name + " SELECT priority, ST_Multi((ST_Dump(ST_Union(ST_Buffer(geometry, " + str(buffer_distance[0]) + ")))).geom) FROM " + fc + " WHERE fma = '" + fma_type + "' GROUP BY priority"
                    else:
                        insert_sql = "INSERT INTO " + temp_buffer_tbl_name + " SELECT asset_name, ST_Multi((ST_Dump(ST_Union(ST_Buffer(geometry, " + str(buffer_distance[0]) + ")))).geom) FROM " + fc + " WHERE fma = '" + fma_type + "' GROUP BY asset_name"
                    run_nonselect_sql([insert_sql])
                make_valid_sql = "UPDATE " + temp_buffer_tbl_name + " SET geometry = ST_MakeValid(geometry) WHERE NOT ST_isValid(geometry);"
                analyze_sql = "ANALYZE " + temp_buffer_tbl_name
                run_nonselect_sql(["ALTER TABLE " + temp_buffer_tbl_name + " ADD COLUMN id SERIAL PRIMARY KEY;", make_valid_sql, analyze_sql])
                
                calculate_intersects(region_to_buffer, fma_type, str(buffer_distance[0]), temp_buffer_tbl_name, temp_intersect_tbl_name)
        run_nonselect_sql(["ALTER TABLE " + temp_intersect_tbl_name + " ADD COLUMN id SERIAL PRIMARY KEY;"])
        if globals.prioritisation_on:
            handle_overlapping_intersects(temp_intersect_tbl_name)
        #iface.mainWindow().statusBar().showMessage("calculate_buffers")
        #run_nonselect_sql(drop_list)
        iface.mainWindow().statusBar().showMessage("calculate_buffers done")
        QApplication.restoreOverrideCursor()
        return temp_intersect_tbl_name
    except Exception as e:
        QApplication.restoreOverrideCursor()
        QMessageBox.information(None, "Failed to create buffers", 
                                "There was a problem with creating the buffers.  Contact GIS Apps in OIM.\n\n" + str(e))
        return "failed"
    
def calculate_intersects(region_to_buffer, fma_type, buffer_distance, temp_buffer_tbl_name, temp_intersect_tbl_name):
    # Called by calculate_buffers (once for each buffer distance per fma type)
    try:
        iface.mainWindow().statusBar().showMessage("calculating intersects for " + temp_buffer_tbl_name)     # e.g. warren_intersects_lrr
        # Intersect with buffer_extents_mvw
        buffer_extents = region_to_buffer + "_buffer_extents_mvw"
        insert_sql = sql_clauses.calculate_intersects()
        if not globals.prioritisation_on:
            insert_sql = insert_sql.replace("priority, ", "")
        insert_sql = insert_sql.replace("temp_intersect_tbl_name", temp_intersect_tbl_name)
        insert_sql = insert_sql.replace("temp_buffer_tbl_name", temp_buffer_tbl_name)
        insert_sql = insert_sql.replace("buffer_extents", buffer_extents)
        insert_sql = insert_sql.replace("fma_type", fma_type)
        insert_sql = insert_sql.replace("buffer_distance", buffer_distance)
        make_valid_sql = "UPDATE " + temp_intersect_tbl_name + " SET geometry = ST_Multi(ST_CollectionExtract(ST_MakeValid(geometry), 3)) WHERE NOT ST_isValid(geometry);"
        run_nonselect_sql([insert_sql, make_valid_sql, "ANALYZE " + temp_intersect_tbl_name])
        #debug_msg_box(temp_intersect_tbl_name + " updated for " + fma_type + ' and ' +  buffer_distance)
    except Exception as e:
        QApplication.restoreOverrideCursor()
        QMessageBox.information(None, "Failed to calculate intersects", 
                                "There was a problem with calculating the intersects.  Contact GIS Apps in OIM.\n\n" + str(e))

def handle_overlapping_intersects(temp_intersect_tbl_name):
    priority_sequence = [-1, None, "NULL", 5, 4, 3, 2, 1]
    rows = run_select_sql(sql_clauses.find_overlapping_intersects().replace("mytable", temp_intersect_tbl_name))
    # each row consists of [a.id, b.id, a.priority, b.priority]
    for row in rows:
        if priority_sequence.index(row[2]) <= priority_sequence.index(row[3]):
            sql = "UPDATE " + temp_intersect_tbl_name + " SET geometry = ST_Multi(ST_Difference(geometry, (SELECT geometry FROM " + temp_intersect_tbl_name + " WHERE id = " + str(row[1]) + "))) WHERE id = " + str(row[0])
            run_nonselect_sql([sql])
        else:
            sql = "UPDATE " + temp_intersect_tbl_name + " SET geometry = ST_Multi(ST_Difference(geometry, (SELECT geometry FROM " + temp_intersect_tbl_name + " WHERE id = " + str(row[0]) + "))) WHERE id = " + str(row[1])
            run_nonselect_sql([sql])

def combine_fmas_non_overlapping(region, fma_types_in_fcs):
    # Called by create_fmas
    iface.mainWindow().statusBar().showMessage("combine_fmas_non_overlapping") 
    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
    fma_seed = region + "_fma_seed"     # Originally referred to PG table containing Glen Daniel's RAM + LRR FMAs; these tables were updated to show all dept land as 'RAM' in non-forest regions, and as 'LRR in forest regions. These seeds are used as starting point to generate full FMAs.
    latest_layer = ""   # Stores name of latest PG layer created by create_interim
    drop = False    # Tracks if a PG table needs dropping
    if "LRR" in fma_types_in_fcs:
        latest_layer = create_interim(region + "_fmas_lrr", fma_seed)
        drop = True
    if "CIB" in fma_types_in_fcs:
        if latest_layer == "":
            latest_layer = create_interim(region + "_fmas_cib", fma_seed)
        else:
            old_layer = latest_layer
            latest_layer = create_interim(region + "_fmas_cib", latest_layer)
            if drop:
                run_nonselect_sql(["DROP TABLE IF EXISTS " + old_layer])
            drop = True
    if "SHS" in fma_types_in_fcs:
        if latest_layer == "":
            latest_layer = create_interim(region + "_fmas_shs", fma_seed)
        else:
            old_layer = latest_layer
            latest_layer = create_interim(region + "_fmas_shs", latest_layer)
            if drop:
                run_nonselect_sql(["DROP TABLE IF EXISTS " + old_layer])
    run_nonselect_sql(["DROP TABLE IF EXISTS " + region + "_fmas_combined"])
    run_nonselect_sql(["ALTER TABLE " + latest_layer + " RENAME TO " + region + "_fmas_combined"])
    iface.mainWindow().statusBar().showMessage("loading " + region + "_fmas_combined") 
    QApplication.restoreOverrideCursor()
    iface.mainWindow().statusBar().showMessage("")
    return region + "_fmas_combined"

def create_interim(current_fma, lower_priority_fmas):
    # Called by combine_fmas_non_overlapping
    tbl_name = "interim_" + current_fma
    iface.mainWindow().statusBar().showMessage("creating " + tbl_name)
    if globals.prioritisation_on:
        sql = sql_clauses.calculate_interim_fmas_combined()     # This SQL creates a layer based on input 2 but with input1 area erased from it and replaced by features from input1
    else:
        sql = sql_clauses.calculate_interim_fmas_combined_no_prioritisn()
    sql = sql.replace("table_name", tbl_name)
    sql = sql.replace("input1", current_fma)
    sql = sql.replace("input2", lower_priority_fmas)
    run_nonselect_sql([sql, "ANALYZE " + tbl_name])
    return tbl_name

def complete_fmas(region):
    # Called by create_fmas
    iface.mainWindow().statusBar().showMessage("completing fmas")
    sql = sql_clauses.create_fmas_complete()
    if not globals.prioritisation_on:
        sql = sql.replace(", priority", "")
    sql = sql.replace("region", region)
    #run_nonselect_sql([sql, "DROP TABLE IF EXISTS " + region + "_fmas_combined;"])
    run_nonselect_sql([sql])
    iface.mainWindow().statusBar().showMessage("")
    if globals.prioritisation_on:
        load_postgis_layer(region + "_fmas_complete", "fma, priority")
    else:
        load_postgis_layer(region + "_fmas_complete", "fma")


##########################################################################
###  VEG AGE THRESHOLD AND TARGET CUSTOMISATION AND CALCULATION
##########################################################################

def calculate_indic_tholds():   #Can prob be deleted
    # Called by rfm_planner.indic_thold_action.triggered, rfm_planner.show_indicative_thresholds (if not yet calculated), calculate_defin_tholds (if no region-specific thods)
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    if globals.preferred_region == "All of WA":
        QMessageBox.information(None, "Specify region!", "This tool will only work when 'Preferred Region' is set to a single region, not 'All of WA'.")
        QApplication.restoreOverrideCursor()
        return
    region = globals.preferred_region.lower().replace(" ", "_")
    fmas_tbl_name = region + "_fmas_complete"
    if not table_exists(fmas_tbl_name):
        QMessageBox.information(None, "Create FMA Polygons!", "This tool will only work once you have created the FMA polygons (RFM Planning menu > Calculate > Create FMA Polygons)")
        QApplication.restoreOverrideCursor()
        return
    indic_thold_tbl_name = region + "_with_indic_thold"
    if table_exists(indic_thold_tbl_name):
        reply = QMessageBox.question(None, "Indicative threshold polys already calculated!", indic_thold_tbl_name + " already exists.  Are you sure you want to overwrite it?  (this will take several minutes)", QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.No:
            QApplication.restoreOverrideCursor()
            return
    sql_create = sql_clauses.create_threshold_table().replace("region", region)
    run_nonselect_sql([sql_create])
    for code in ["shs", "cib", "lrr"]:
        sql = sql_clauses.threshold_calculation_code()
        sql = sql.replace("region", region)
        sql = sql.replace("code", code)
        sql = sql.replace("CODE", code.upper())
        run_nonselect_sql([sql])
    sql_last_part = sql_clauses.threshold_calculation_last_part().replace("region", region)
    run_nonselect_sql([sql_last_part])
    load_postgis_layer(region + "_past_indic_thold", None, "id")    # Loads a view showing only those areas PAST (or equal to) the threshold age
    QApplication.restoreOverrideCursor()

def update_reg_default_tholds():
    # ENABLES USER TO CREATE AND/OR OPEN FOR EDITING A TABLE TO SET DEFAULT VEG AGE THRESHOLDS FOR THEIR REGION
    # check if reg table exists
    # get current region in south_west format
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    if globals.preferred_region == "All of WA":
        QMessageBox.information(None, "Specify region!", "This tool will only work when 'Preferred Region' is set to a single region, not 'All of WA'.")
        QApplication.restoreOverrideCursor()
        return
    region = globals.preferred_region.lower().replace(" ", "_")
    reg_defaults_tbl_name = region + "_default_thresholds"
    if not table_exists(reg_defaults_tbl_name):
        reply = QMessageBox.question(None, "Create table?", "There is not yet a table in the database for " + globals.preferred_region + " default thresholds.  Click 'Yes' to create a new table for your region copied from the statewide defaults then open for editing.", QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            create_table_sql = "CREATE TABLE " + reg_defaults_tbl_name + " AS TABLE fuel_type_indicative_thresholds;"
            pk_sql = "ALTER TABLE " + reg_defaults_tbl_name + " ADD COLUMN pk SERIAL PRIMARY KEY;"
            trigger_sql = """CREATE TRIGGER trig_region_def_th_update 
            AFTER INSERT OR UPDATE OR DELETE ON region_default_thresholds 
            FOR EACH STATEMENT
            EXECUTE PROCEDURE update_table_updates();""".replace('region', region)
            
            create_lookup_sql = sql_clauses.create_region_fuel_fma_thold_target_lookup().replace('region', region)
            #update_updates_table(region + "_default_thresholds ")
            run_nonselect_sql([create_table_sql, pk_sql, trigger_sql, create_lookup_sql])
        elif reply == QMessageBox.No:
            QApplication.restoreOverrideCursor()
            return
    
    # Open and allow edits
    thresholds_list = run_select_sql("SELECT * FROM " + reg_defaults_tbl_name + " ORDER BY pk")
    qgis.utils.iface.indic_thresholds_report = rfm_planner_dialogs.IndicTholdDialog(thresholds_list, True, reg_defaults_tbl_name, region)
    qgis.utils.iface.indic_thresholds_report.lbl_title.setText(globals.preferred_region + " Default Fuel Age Thresholds")
    qgis.utils.iface.indic_thresholds_report.show()
    QApplication.restoreOverrideCursor()

def update_spat_var_tholds(fuel_type, thold_age, shs_target, cib_target, lrr_target):
    # check if regional spatially varying thresholds table exists
    # get current region in south_west format
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    if globals.preferred_region == "All of WA":
        QMessageBox.information(None, "Specify region!", "This tool will only work when 'Preferred Region' is set to a single region, not 'All of WA'.")
        QApplication.restoreOverrideCursor()
        return
    region = globals.preferred_region.lower().replace(" ", "_")
    reg_sp_tholds_tbl_name = region + "_spatial_thresholds"
    if not table_exists(reg_sp_tholds_tbl_name):
        check_threshold_domains()
        reply = QMessageBox.question(None, "Create table?", "There is not yet a table in the database for " + globals.preferred_region + " spatially varying thresholds.  Click 'Yes' to create a new empty table.  It will be created then added to the QGIS map canvas, where it can be edited using QGIS tools.", QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            create_sql = "CREATE TABLE " + reg_sp_tholds_tbl_name + " AS TABLE fuel_type_indicative_thresholds WITH NO DATA;"
            pk_sql = "ALTER TABLE " + reg_sp_tholds_tbl_name + " ADD COLUMN pk SERIAL PRIMARY KEY;"
            geom_sql = "ALTER TABLE " + reg_sp_tholds_tbl_name + " ADD COLUMN geometry geometry(MultiPolygon,900914);"
            spat_index_sql = "CREATE INDEX idx_" + reg_sp_tholds_tbl_name + "_geom ON " + reg_sp_tholds_tbl_name + " USING GIST(geometry);"
            fuel_index_sql = "CREATE INDEX idx_" + reg_sp_tholds_tbl_name + "_fuel ON " + reg_sp_tholds_tbl_name + "(fuel_type)";
            trigger_sql = """CREATE TRIGGER trig_region_sp_th_update 
            AFTER INSERT OR UPDATE OR DELETE ON region_spatial_thresholds 
            FOR EACH STATEMENT
            EXECUTE PROCEDURE update_table_updates();""".replace('region', region)
            domain_sql = "ALTER TABLE " + reg_sp_tholds_tbl_name + " ALTER COLUMN fuel_type SET DATA TYPE d_fuel_types, ALTER COLUMN threshold_age SET DATA TYPE d_thold_ages, ALTER COLUMN shs_target SET DATA TYPE d_targets, ALTER COLUMN cib_target SET DATA TYPE d_targets, ALTER COLUMN lrr_target SET DATA TYPE d_targets"
            create_lookup_sql = sql_clauses.create_region_fuel_fma_thold_target_spatial_lookup().replace('region', region)
            update_updates_table(region + "_spatial_thresholds")
            run_nonselect_sql([create_sql, pk_sql, geom_sql, spat_index_sql, fuel_index_sql, trigger_sql, domain_sql, create_lookup_sql])
        elif reply == QMessageBox.No:
            QApplication.restoreOverrideCursor()
            return
    thresholds_lyr = call_load_postgis_layer(None, reg_sp_tholds_tbl_name)
    thresholds_lyr.setDefaultValueExpression(0, "'" + fuel_type + "'")
    thresholds_lyr.setDefaultValueExpression(1, thold_age)
    thresholds_lyr.setDefaultValueExpression(2, shs_target)
    thresholds_lyr.setDefaultValueExpression(3, cib_target)
    thresholds_lyr.setDefaultValueExpression(4, lrr_target)
    #set_edit_widgets(thresholds_lyr)
    QApplication.restoreOverrideCursor()

def show_spatial_thresholds():
    # Called by menu item "Add spatial thresholds layer to map"
    #get region
    region = globals.preferred_region.lower().replace(" ", "_")
    if region == "all_of_wa":
        QMessageBox.information(None, "Choose region", "This tool is not designed to work when the preferred region is set to 'All of WA'.  Choose a region then retry.")
        return
    #check if table exists
    if not table_exists(region + "_spatial_thresholds"):
        QMessageBox.information(None, "Table does not exist", "Spatially varying thresholds for this region have not been created.  Go to RFM Planner menu > Data Admin > Fuel thresholds/targets > Update regional fuel thresholds to create spatial thresholds.")
        return
    #add to map
    layer = load_postgis_layer(region + "_spatial_thresholds")
    layer.triggerRepaint()

def check_threshold_domains():
    # Creates domains for new spatially varying thrsholds table
    # Called by update_spat_var_tholds
    sql = "SELECT * FROM pg_type WHERE typname = 'd_fma_types'"
    if len(run_select_sql(sql)) == 0:
        run_nonselect_sql([sql_clauses.create_fma_domain()])
    sql = "SELECT * FROM pg_type WHERE typname = 'd_fuel_types'"
    if len(run_select_sql(sql)) == 0:
        run_nonselect_sql([sql_clauses.create_fuel_domain()])
    sql = "SELECT * FROM pg_type WHERE typname = 'd_thold_ages'"
    if len(run_select_sql(sql)) == 0:
        run_nonselect_sql([sql_clauses.create_threshold_ages_domain()])
    sql = "SELECT * FROM pg_type WHERE typname = 'd_targets'"
    if len(run_select_sql(sql)) == 0:
        run_nonselect_sql([sql_clauses.create_targets_domain()])
        
def set_edit_widgets(layer, fuel):    
    # In future could be revised to be a useful utility function
    field = 'fuel_type'
    field_index = layer.fieldNameIndex(field)
    layer.setEditorWidgetV2(field_index, 'ValueMap')
    values = create_value_map(field)
    layer.setEditorWidgetV2Config(field_index, values)
    for field in ['threshold_age', 'shs_target', 'cib_target', 'lrr_target']:
        field_index = layer.fieldNameIndex(field)
        layer.setEditorWidgetV2(field_index, 'Range')
        value_range = globals.value_ranges[field]
        layer.setEditorWidgetV2Config(field_index, value_range)
    
def create_value_map(field):
    domain = globals.domains[field]
    value_map = {}
    for item in domain:
        value_map[item] = item
    return value_map

def calculate_defin_tholds():   # Can prob be deleted
    # Called by rfm_planner.defin_thold_action.triggered, rfm_planner.show_indicative_thresholds (if not yet calculated)
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    if globals.preferred_region == "All of WA":
        QMessageBox.information(None, "Specify region!", "This tool will only work when 'Preferred Region' is set to a single region, not 'All of WA'.")
        QApplication.restoreOverrideCursor()
        return
    region = globals.preferred_region.lower().replace(" ", "_")
    fmas_tbl_name = region + "_fmas_complete"
    if not table_exists(fmas_tbl_name):
        QMessageBox.information(None, "Create FMA Polygons!", "This tool will only work once you have created the FMA polygons (RFM Planning menu > Calculate > Create FMA Polygons)")
        QApplication.restoreOverrideCursor()
        return
    # If no region-specific tholds, use indicative tholds
    thold_tbl_name = region + "_with_thold"
    default_tholds_tbl_name = region + "_default_thresholds"
    spatial_tholds_tbl_name = region + "_spatial_thresholds"
    default_tholds_exist = table_exists(default_tholds_tbl_name)
    spatial_tholds_exist = table_exists(spatial_tholds_tbl_name)
    if not default_tholds_exist and not spatial_tholds_exist:
        #debug_msg_box("didn't find regional thold tables")
        calculate_indic_tholds()
        QApplication.restoreOverrideCursor()
        return
    
    # Otherwise continue
    thold_tbl_name = region + "_with_thold"
    proceed = check_threshold_table_dates(region)
    if not proceed:
        debug_msg_box("Thresholds will not be calculated until all relevant tables are up to date.")
    else:
        if table_exists(thold_tbl_name):
            reply = QMessageBox.question(None, "Threshold polys already calculated!", thold_tbl_name + " already exists.  Are you sure you want to overwrite it?  (this may take half an hour or so).", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                QApplication.restoreOverrideCursor()
                return
        sql_create = sql_clauses.create_definitive_threshold_table().replace("region", region)
        run_nonselect_sql([sql_create])
        for code in ["shs", "cib", "lrr"]:
            sql = sql_clauses.threshold_calculation_definitive()
            sql = sql.replace("region", region)
            sql = sql.replace("code", code)
            sql = sql.replace("CODE", code.upper())
            run_nonselect_sql([sql])
        load_postgis_layer(region + "_past_thold", None, "id")    # Loads a view showing only those areas PAST (or equal to) the threshold age
    QApplication.restoreOverrideCursor()
    
def check_fma_table_dates(region):
    # checks that region_fmas_complete postdates last update to region_asset_points, _lines and _polys
    # returns Boolean (True if OK)
    ok = False
    fmas_complete_tbl_name = region + "_fmas_complete"
    asset_points_tbl_name = region + "_asset_points"
    asset_lines_tbl_name = region + "_asset_lines"
    asset_polys_tbl_name = region + "_asset_polys"
    fmas_complete_mod_date = get_mod_date(fmas_complete_tbl_name)
    asset_points_mod_date = get_mod_date(asset_points_tbl_name)
    asset_lines_mod_date = get_mod_date(asset_lines_tbl_name)
    asset_polys_mod_date = get_mod_date(asset_polys_tbl_name)
    if fmas_complete_mod_date > max([asset_points_mod_date, asset_lines_mod_date, asset_polys_mod_date]):
        ok = True
    return ok

def check_fuel_type_age_table_dates(region):
    # checks that region_fuel_type_age postdates last update to region_fuel_type and region_fuel_age
    # returns Boolean (True if OK)
    ok = False
    fuel_type_age_tbl_name = region + "_fuel_type_age"
    fuel_type_tbl_name = region + "_fuel_type"
    fuel_age_tbl_name = region + "_fuel_age"
    fuel_type_age_mod_date = get_mod_date(fuel_type_age_tbl_name)
    fuel_type_mod_date = get_mod_date(fuel_type_tbl_name)
    fuel_age_mod_date = get_mod_date(fuel_age_tbl_name)
    if fuel_type_age_mod_date > max([fuel_type_mod_date, fuel_age_mod_date]):
        ok = True
    return ok
    
def check_underlying_report_data_dates(region):
    # Checks that region_underlying_report_data postdates all input datasets
    ok = False
    #fma_dates_ok = check_fma_table_dates(region)
    #if not fma_dates_ok:
    #    return ok
    #fuel_type_age_dates_ok = check_fuel_type_age_table_dates(region)
    #if not fuel_type_age_dates_ok:
    #    return ok

    underlying_report_data_tbl_name = region + "_underlying_report_data"
    default_thresholds_tbl_name = region + "_default_thresholds"
    spatial_thresholds_tbl_name = region + "_spatial_thresholds"
    fmas_complete_tbl_name = region + "_fmas_complete"
    fuel_type_age_tbl_name = region + "_fuel_type_age"
    underlying_report_data_mod_date = get_mod_date(underlying_report_data_tbl_name)
    default_thresholds_mod_date = get_mod_date(default_thresholds_tbl_name)
    spatial_thresholds_mod_date = get_mod_date(spatial_thresholds_tbl_name)
    fmas_complete_mod_date = get_mod_date(fmas_complete_tbl_name)
    fuel_type_age_mod_date = get_mod_date(fuel_type_age_tbl_name)
    if underlying_report_data_mod_date > max([default_thresholds_mod_date, spatial_thresholds_mod_date, fmas_complete_mod_date, fuel_type_age_mod_date]):
        ok = True
    return ok

def check_threshold_table_dates(region):    # Can prob be deleted
    # Checks whether sequence of tables re thresholds/targets is correct; if not prompts user to re-calculate relevant tables
    # Called by calculate_defin_tholds, get_report_data
    thold_tbl_name = region + "_with_thold"
    default_tholds_tbl_name = region + "_default_thresholds"
    spatial_tholds_tbl_name = region + "_spatial_thresholds"
    default_tholds_exist = table_exists(default_tholds_tbl_name)
    spatial_tholds_exist = table_exists(spatial_tholds_tbl_name)
    ## if no default thresholds and no spatial thresholds for region, proceed as normal
    #if not default_tholds_exist and not spatial_tholds_exist:
    #    #debug_msg_box("didn't find regional thold tables")
    #    return True
    #else:
    # check whether tables exist in db and if so what their mod dates are
    thold_tbl_mod_date = get_mod_date(thold_tbl_name)   #None
    default_tholds_mod_date = get_mod_date(default_tholds_tbl_name)
    spatial_tholds_mod_date = get_mod_date(spatial_tholds_tbl_name) # None
    # if default_tholds_tbl_name exists or spatial_tholds_mod_date exists then check whether region_no_target and 3 x region_fuel_type_age_with_thold_code exist, and if so, mod date
    mod_dates = {}
    mod_dates[region + "_no_target"] = get_mod_date(region + "_no_target")
    mod_dates[region + "_fuel_type_age_with_thold"] = get_mod_date(region + "_fuel_type_age_with_thold")
    mod_dates[region + "_fuel_type_age_with_thold_shs"] = get_mod_date(region + "_fuel_type_age_with_thold_shs")
    mod_dates[region + "_fuel_type_age_with_thold_cib"] = get_mod_date(region + "_fuel_type_age_with_thold_cib")
    mod_dates[region + "_fuel_type_age_with_thold_lrr"] = get_mod_date(region + "_fuel_type_age_with_thold_lrr")
    #debug_msg_box(mod_dates)
    tables_to_create = []
    for table in mod_dates:
        if mod_dates[table] is None or mod_dates[table] < default_tholds_mod_date or mod_dates[table] < spatial_tholds_mod_date:
            tables_to_create.append(str(table))
    if len(tables_to_create) > 0:
        reply = QMessageBox.question(None, "Regional tables must be calculated!", "The following tables need to be calculated in order to continue: " + str(tables_to_create)[1:-1] + ".  Do you wish to continue?  (This may take half an hour or so).", QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            create_tables(region, tables_to_create, default_tholds_exist, spatial_tholds_exist)
            return True
        else:
            return False
    else:
        return True
            
def create_tables(region, tables_to_create, default_tholds_exist, spatial_tholds_exist):
    # Called by check_threshold_table_dates
    for table in tables_to_create:
        if table == region + "_no_target":
            sql = sql_clauses.create_region_no_target().replace("region", region)
            run_nonselect_sql([sql])
        elif table == region + "_fuel_type_age_with_thold":
            sql = sql_clauses.create_region_fuel_type_age_with_thold().replace("region", region)
            run_nonselect_sql([sql])
            # fill by clipping to region bdry then update according to region_default_tholds
            #debug_msg_box("filling region_fuel_type_age_with_thold")
            sql = sql_clauses.fill_region_fuel_type_age_with_thold().replace("xregionx", region)
            sql = sql.replace("zregionz", region.upper().replace("_", " "))
            run_nonselect_sql([sql])

    for table in tables_to_create:    
        for code in ['shs', 'cib', 'lrr']:
            if table == region + "_fuel_type_age_with_thold_" + code:
                if table_exists(region + "_default_thresholds"):
                    sql = sql_clauses.create_region_fuel_type_age_with_thold_code()
                    sql = sql.replace("region", region).replace("code", code)
                    run_nonselect_sql([sql])
                    sql = sql_clauses.fill_region_fuel_type_age_with_thold_code()
                    #debug_msg_box("filling region_fuel_type_age_with_thold_code")
                    sql = sql.replace("region", region)
                    sql = sql.replace("code", code)
                    sql = sql.replace("CODE", code.upper())
                    run_nonselect_sql([sql])

def delete_assets():
    # Called by rfm_planner.delete_assets_action.triggered
    registry = QgsMapLayerRegistry.instance()
    layers = registry.mapLayers()
    asset_layers = []
    for layer in layers:
        if globals.preferred_region in [None, "All of WA"]:
            if globals.db == "postgis":
                if (layers[layer].source().startswith("dbname='" + globals.rfmp_db + "'") and ("asset_points" in layers[layer].name() or "asset_lines" in layers[layer].name() or "asset_polys" in layers[layer].name())): 
                    asset_layers.append(layers[layer])
            elif globals.db == "spatialite":
                if (layers[layer].source().startswith("dbname='" + globals.spatialite_db + "'") and ("asset_points" in layers[layer].name() or "asset_lines" in layers[layer].name() or "asset_polys" in layers[layer].name())): 
                    asset_layers.append(layers[layer])
        else:
            if globals.db == "postgis":
                if (layers[layer].source().startswith("dbname='" + globals.rfmp_db + "'") and layers[layer].name().startswith(globals.preferred_region.lower().replace(" ", "_")) and ("asset_points" in layers[layer].name() or "asset_lines" in layers[layer].name() or "asset_polys" in layers[layer].name())): 
                    asset_layers.append(layers[layer].name())
            elif globals.db == "spatialite":
                if (layers[layer].source().startswith("dbname='" + globals.spatialite_db + "'") and layers[layer].name().startswith(globals.preferred_region.lower().replace(" ", "_")) and ("asset_points" in layers[layer].name() or "asset_lines" in layers[layer].name() or "asset_polys" in layers[layer].name())): 
                    asset_layers.append(layers[layer].name())
    if len(asset_layers) == 0:
        QMessageBox.information(None, "No asset layers!", "You need to add the relevant asset layer to the map.")
        return
    
    delete_assets_form = rfm_planner_dialogs.DeleteAssetsDialog(asset_layers)
    delete_assets_form.exec_()

def open_report(type):
    # type is one of 'preferred_region', 'all_regions', 'brmzs'
    # Called by rfm_planner.report_preferred_region_action.triggered
    if type == "preferred_region":
        region_info = get_region_info()
        region = globals.preferred_region.lower().replace(" ", "_")
        if table_exists(region + "_default_thresholds"):
            region_specific_thresholds = True
        else:
            region_specific_thresholds = False
        if region_info is not None:
            qgis.utils.iface.single_region_report = rfm_planner_dialogs.SingleRegionReportDialog(globals.preferred_region, region_info, region_specific_thresholds)
            tbl_widget = qgis.utils.iface.single_region_report.tbl_fma_type
            header = tbl_widget.horizontalHeader()
            for i in range(7):
                header.setResizeMode(i, QHeaderView.ResizeToContents)
            qgis.utils.iface.single_region_report.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
            qgis.utils.iface.single_region_report.setWindowState(Qt.WindowActive)
            qgis.utils.iface.single_region_report.show()
            qgis.utils.iface.single_region_report.activateWindow()
    elif type == "all_regions":
        debug_msg_box(type + " report not yet implemented")
    elif type == "brmzs":
        debug_msg_box(type + " report not yet implemented")
    #    brmz_info = get_brmz_info()
    #    if brmz_info is not None:
    #        qgis.utils.iface.brmz_report = rfm_planner_dialogs.BRMZsReportDialog(brmz_info)
    #        qgis.utils.iface.brmz_report.show()
    
def toggle_district_report(index):
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    if index == 0:
        region_info = get_region_info()
        qgis.utils.iface.single_region_report.region_info = region_info
        qgis.utils.iface.single_region_report.tbl_fma_type.setRowCount(0)
        qgis.utils.iface.single_region_report.fill_tables()
    else:
        region = globals.preferred_region.lower().replace(" ", "_")
        district_upper = qgis.utils.iface.single_region_report.cbx_districts.currentText()
        district = district_upper.lower().replace(" ", "_")
        if not table_exists(region + "_underlying_report_data_" + district):
            sql_create_dist_table = sql_clauses.create_region_name_underlying_report_data_district_name().replace('district_name', district_upper).replace('region_name', region)
            sql_create_dist_view = sql_clauses.create_regional_summary_report_data_district().replace('district', district).replace('region_name', region)
            run_nonselect_sql([sql_create_dist_table, sql_create_dist_view])
        retrieve_data_sql = "SELECT * FROM " + region + "_summary_report_data_" + district
        district_info = run_select_sql(retrieve_data_sql)
        qgis.utils.iface.single_region_report.region_info = district_info
        qgis.utils.iface.single_region_report.tbl_fma_type.setRowCount(0)
        qgis.utils.iface.single_region_report.fill_tables()
    QApplication.restoreOverrideCursor()

def list_indicative_fuel_thresholds():
    thresholds_list = run_select_sql("SELECT * FROM fuel_type_indicative_thresholds")
    qgis.utils.iface.indic_thresholds_report = rfm_planner_dialogs.IndicTholdDialog(thresholds_list)
    qgis.utils.iface.indic_thresholds_report.show()

def get_region_info(region=None):
    # Called by open_report
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    if globals.preferred_region == "All of WA":
        QMessageBox.information(None, "Specify region!", "This tool will only work when 'Preferred Region' is set to a single region, not 'All of WA'.")
        QApplication.restoreOverrideCursor()
        return
    if region == None:
        region = globals.preferred_region.lower().replace(" ", "_")
    underlying_report_data_table = region + "_underlying_report_data"
    if table_exists(region + "_default_thresholds") or table_exists(region + "_spatial_thresholds"):
        region_specific_thresholds = True
    else:
        region_specific_thresholds = False

    # Check fmas_complete is present and up to date
    tbl_name = region + "_fmas_complete"
    if not table_exists(tbl_name) or not check_fma_table_dates(region):
        if not table_exists(tbl_name):
            msg = "This tool will only work once you have created the FMA polygons.  Do you want to do this now?  It may take 15 min or so."
        if not check_fma_table_dates(region):
            msg = "There is new data in the database. You need to update the FMA polygons before the report can be calculated.  Do you want to do this now?  It may take 15 min or so."
        reply = QMessageBox.question(None, "Create FMA Polygons!", msg, QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.No:
            QApplication.restoreOverrideCursor()
            return
        else:
            create_fmas(False) # False switches off a repeat of the warning just given
        
    # Check fuel_type_age is present and up to date
    tbl_name = region + "_fuel_type_age"
    if not table_exists(tbl_name) or not check_fuel_type_age_table_dates(region):
        msg = "There is new data in the database. You need to update the fuel_type_age polygons before the report can be calculated.  Do you want to do this now?  It may take 15 min or so."
        reply = QMessageBox.question(None, "Create fuel_type_age Polygons!", msg, QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.No:
            QApplication.restoreOverrideCursor()
            return
        else:
            sql = sql_clauses.fill_region_fuel_type_age().replace('region', region)
            run_nonselect_sql([sql])
            
    # If report data for this region already exists, check date sequencing OK and suggest using this existing data
    final_rows = None
    if table_exists(region + "_underlying_report_data"):
        mod_date_underlying_report_data = get_mod_date(region + "_underlying_report_data")
        mod_date_fuel_type_age = get_mod_date(region + "_fuel_type_age")
        mod_date_fmas_complete = get_mod_date(region + "_fmas_complete")
        mod_date_thresholds = None
        if region_specific_thresholds:
            mod_date_thresholds = max([get_mod_date(region + "_default_thresholds"), get_mod_date(region + "_spatial_thresholds")])
        if mod_date_underlying_report_data > max([mod_date_fuel_type_age, mod_date_fmas_complete, mod_date_thresholds]):
            if not table_exists(region + "_summary_report_data"):
                sql = """CREATE VIEW region_summary_report_data AS
                        SELECT 'region' AS xxx , fma_type, target, CASE WHEN yslb >= threshold_age THEN TRUE ELSE FALSE END AS reached_th, SUM(ST_Area(geometry))/10000 AS area_ha
                        FROM region_underlying_report_data
                        GROUP BY xxx, fma_type, target, reached_th;""".replace('region', region).replace('xxx', 'region')
                run_nonselect_sql([sql])
            retrieve_data_sql = "SELECT * FROM region_summary_report_data".replace("region", region)
            final_rows = run_select_sql(retrieve_data_sql)
    if final_rows == None:
        final_rows = create_report_data(region, region_specific_thresholds)
    QApplication.restoreOverrideCursor()
    return final_rows
    
def get_report_data_OLD(region):
    # Called by get_region_info, get_brmz_info
    tbl_name = region + "_summary_report_data"
    #if table_exists(tbl_name):
    #    QApplication.restoreOverrideCursor()
    #    reply = QMessageBox.question(None, "Summary report data already exists!", "Summary report data has already been stored for " + #region.upper().replace("_", " ") + ".  Do you want to use the stored data? (Much quicker than re-calculating)", QMessageBox.Yes|QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #        #sql = "SELECT region, zone, fma, target, reached_th, area FROM " + tbl_name
    #        sql = "SELECT region, fma, target, reached_th, area FROM " + tbl_name
    #        final_rows = run_select_sql(sql)
    #        return final_rows
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    fma_rows = []
    # Get total fma areas
    sql_regional_areas_by_fma = sql_clauses.regional_areas_by_fma().replace("region", region)
    regional_areas_by_fma = run_select_sql(sql_regional_areas_by_fma)
    for ra in regional_areas_by_fma:
        fma_type = ra[0]
        fma_area = ra[1]
        fma_rows.append([fma_type, fma_area])
    if table_exists(region + "_fuel_type_age_with_thold"):
        proceed = check_threshold_table_dates(region)
        if not proceed:
            debug_msg_box("Report can not be created until all relevant tables are up to date.")
            QApplication.restoreOverrideCursor()
            return
        sql_region_thold_details = sql_clauses.regional_areas_with_defin_thold_details().replace("region", region)
        region_specific = True
    else:
        sql_region_thold_details = sql_clauses.regional_areas_with_indic_thold_details().replace("region", region)
        region_specific = False
    region_thold_rows = run_select_sql(sql_region_thold_details)
    #debug_msg_box(region_thold_rows)
    non_th_rows = []    # This will store info for areas in fmas where veg type has no target / threshold
    for fma_row in fma_rows:
        fma_type = fma_row[0]
        area = fma_row[1]
        for th_row in region_thold_rows:
            th_fma = th_row[0]
            sub_area = th_row[3]
            if th_fma == fma_type:
                area -= sub_area
        if area > 0:
            non_th_rows.append((fma_type, -1, 'NULL', area))
    combined_rows = region_thold_rows + non_th_rows
    #create table to store data
    run_nonselect_sql([sql_clauses.create_regional_summary_report_data().replace("region_name", region)])
    region_name = region.upper().replace("_", " ")
    for row in combined_rows:
        run_nonselect_sql(["INSERT INTO " + tbl_name + "(region, fma, target, reached_th, area) VALUES ('" + region + "', '" + row[0] + "', " + str(row[1]) + ", " + str(row[2]) + ", " + str(row[3]) + ");"])
    sql = "SELECT region, fma, target, reached_th, area FROM " + tbl_name
    final_rows = run_select_sql(sql)
    QApplication.restoreOverrideCursor()
    return (region_specific, final_rows)

def create_report_data(region, region_specific_thresholds):
    # Called by get_region_info, get_brmz_info
    QMessageBox.information(None, "Calculating report", "The system needs to do some complex calculations which may take several minutes, especially if you have spatially varying fuel age thresholds / targets.")
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    tbl_name = region + "_summary_report_data"
    districts_sql = "SELECT admin_zone FROM districts WHERE region = '" + region + "'"
    districts_list = [item[0].lower().replace(" ", "_") for item in run_select_sql(districts_sql)]
    for district in districts_list:
        sql = "DROP TABLE IF EXISTS " + region + "_underlying_report_data_" + district + " CASCADE"
        run_nonselect_sql([sql])
    fma_rows = []
    sql_assemble_report_data_spatial_tholds_part_2_list = []
    sql_assemble_report_data_spatial_tholds_part_3_list = []
    sql_assemble_report_data_spatial_tholds_part_4_list = []
    # Get total fma areas
    sql_regional_areas_by_fma = sql_clauses.regional_areas_by_fma().replace("region", region)
    regional_areas_by_fma = run_select_sql(sql_regional_areas_by_fma)
    for ra in regional_areas_by_fma:
        fma_type = ra[0]
        fma_area = ra[1]
        fma_rows.append([fma_type, fma_area])
    if region_specific_thresholds:
        if table_exists(region + '_spatial_thresholds'):
            sql_get_fuel_type = 'SELECT fuel_type FROM ' + region + '_spatial_thresholds'
            fuel_types_w_spatial_tholds_string = ""
            fuel_types_w_spatial_tholds_list = []
            fuel_types_w_spatial_tholds = run_select_sql(sql_get_fuel_type)
            if len(fuel_types_w_spatial_tholds) > 0:
                for ft in fuel_types_w_spatial_tholds:
                    fuel_types_w_spatial_tholds_string += "'" + ft[0] + "',"
                    fuel_types_w_spatial_tholds_list.append(ft[0])
                fuel_types_w_spatial_tholds_string = fuel_types_w_spatial_tholds_string[:-1]
                sql_assemble_report_data = sql_clauses.assemble_report_data_spatial_tholds_part_1().replace('region', region).replace('xxx', 'region').replace('fuel_types_w_spatial_tholds', fuel_types_w_spatial_tholds_string)
                
                for ft in fuel_types_w_spatial_tholds_list:
                    # insert data for areas where no spatial, first for fuel_type_age polys w no intersection w spatial, then for those that do
                    sql_assemble_report_data_spatial_tholds_part_2 = sql_clauses.assemble_report_data_spatial_tholds_part_2().replace('region', region).replace('xxx', 'region').replace('fuel_type_w_spatial_thold', ft)
                    sql_assemble_report_data_spatial_tholds_part_2_list.append(sql_assemble_report_data_spatial_tholds_part_2)
                    sql_assemble_report_data_spatial_tholds_part_3 = sql_clauses.assemble_report_data_spatial_tholds_part_3().replace('region', region).replace('xxx', 'region').replace('fuel_type_w_spatial_thold', ft)
                    sql_assemble_report_data_spatial_tholds_part_3_list.append(sql_assemble_report_data_spatial_tholds_part_3)
                    #insert data for areas where spatial
                    sql_assemble_report_data_spatial_tholds_part_4 = sql_clauses.assemble_report_data_spatial_tholds_part_4().replace('region', region).replace('xxx', 'region').replace('fuel_type_w_spatial_thold', ft)
                    sql_assemble_report_data_spatial_tholds_part_4_list.append(sql_assemble_report_data_spatial_tholds_part_4)
            else:   #May occur if table created but no rows created
                sql_assemble_report_data = sql_clauses.assemble_report_data().replace('region', region).replace('xxx', 'region')
        else:
            sql_assemble_report_data = sql_clauses.assemble_report_data().replace('region', region).replace('xxx', 'region')
    else:
        sql_assemble_report_data = sql_clauses.assemble_report_data().replace('region_fuel_fma_thold_target_lookup', 'default_fuel_fma_thold_target_lookup').replace("region", region).replace('xxx', 'region')
    run_nonselect_sql([sql_assemble_report_data])
    run_nonselect_sql(sql_assemble_report_data_spatial_tholds_part_2_list)
    run_nonselect_sql(sql_assemble_report_data_spatial_tholds_part_3_list)
    run_nonselect_sql(sql_assemble_report_data_spatial_tholds_part_4_list)
    retrieve_data_sql = "SELECT * FROM region_summary_report_data".replace("region", region)
    summary_report_data_rows = run_select_sql(retrieve_data_sql)
    QApplication.restoreOverrideCursor()
    return summary_report_data_rows

def get_brmz_info():
    # Called by open_report
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    #list of regions per brmz
    #list of regions with no fmas_combined
    #data for all regions with fmas_combined
    sql = "SELECT * FROM regions_by_brmz"
    regions_by_brmz = run_select_sql(sql)
    brmzs = sorted(list(set([item[0] for item in regions_by_brmz])))
    all_regions = set([item[1] for item in regions_by_brmz])
    brmz_data = []
    # Get list of regions for which fmas_combined table has not been created in db
    non_existent_fmas_combined = []
    for region in all_regions:
        if not table_exists(region.lower().replace(" ", "_") + "_fmas_combined"):
            non_existent_fmas_combined.append(region)
        else:
            brmz_data += create_report_data(region.lower().replace(" ", "_"))
    QApplication.restoreOverrideCursor()
    return (regions_by_brmz, non_existent_fmas_combined, brmz_data)

#def import_new_fuel_age():
#    QMessageBox.information(None, "", "import_new_fuel_age")
    
def import_new_fuel_type():
    QMessageBox.information(None, "", "import_new_fuel_type not yet implemented")

########################################
###  UTILITIES (alphabetical order)
########################################

def call_load_postgis_layer(q, name=None):  # q is an instance of QAction
    # Called by rfm_planner.update_assets_submenu.triggered
    if name is None and q is not None:
        name = q.text()
    # Check whether layer already loaded - if not load it, if it is, set it as active layer.
    layer_if_present = QgsMapLayerRegistry.instance().mapLayersByName(name)
    if not layer_if_present:
        load_postgis_layer(name)
    else:
        qgis.utils.iface.setActiveLayer(layer_if_present[0])
    layer = qgis.utils.iface.activeLayer()
    layer.startEditing()
    qgis.utils.iface.actionAddFeature().trigger()
    return layer

def debug_msg_box(message, heading=""):
    # easy method allowing user to debug without worrying about data types and headings (headings are optional)
    QMessageBox.information(None, str(heading), str(message))

def get_mod_date(table):
    mod_date = None
    try:
        if table_exists(table):
            sql = "SELECT last_update FROM table_updates WHERE table_name = '" + table + "'"
            mod_date = run_select_sql(sql)[0][0]
    except:
        pass
    return mod_date

def get_region_dict():
    region_dict = {}
    regions = run_select_sql("SELECT region FROM regions;")
    for region in regions:
        region_dict[region[0].lower().replace(" ", "_")] = region[0]
    return region_dict

def load_postgis_layer(tbl_name, fma_grouping=None, key_column="", filter=None, title=None):
    # Called by numerous functions from rfm_library, rfm_planner_dialogs and rfm_planner
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    uri = QgsDataSourceURI()
    uri.setConnection(globals.rfmp_host, globals.rfmp_port, globals.rfmp_db, globals.rfmp_user, globals.rfmp_pw)
    schema = 'public'
    geom_column = 'geometry' 
    uri.setDataSource(schema, tbl_name, geom_column, "", key_column)
    if title is None:
        lyr_name = tbl_name
    else:
        lyr_name = title
    try:
        s = QSettings()
        old_validation = s.value( "/Projections/defaultBehaviour" )
        s.setValue( "/Projections/defaultBehaviour", "useGlobal" )
        vlayer = QgsVectorLayer(uri.uri(), lyr_name, 'postgres')
        vlayer.setCrs(QgsCoordinateReferenceSystem(albers_wa_string))
        vlayer.setSubsetString(filter)
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        s.setValue( "/Projections/defaultBehaviour", old_validation)
        style_layer(tbl_name, vlayer, fma_grouping)
        return vlayer   # Added May 2020 for work with spatially varying thresholds
    except Exception as e:
        QMessageBox.information(None, "", e.message)

def load_spatialite_layer(tbl_name, fma_grouping=None):
    try:
        s = QSettings()
        old_validation = s.value( "/Projections/defaultBehaviour" )
        s.setValue( "/Projections/defaultBehaviour", "useGlobal" )
        uri = "dbname='" + globals.spatialite_db + "' table='" + tbl_name + "' (geometry) sql="
        vlayer = QgsVectorLayer(uri, tbl_name, 'spatialite')
        vlayer.setCrs(QgsCoordinateReferenceSystem(albers_wa_string))
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        s.setValue( "/Projections/defaultBehaviour", old_validation)
        style_layer(tbl_name, vlayer, fma_grouping)
    except Exception as e:
        QMessageBox.information(None, "", e.message)

def run_nonselect_sql(sql_list):
    # General help function to run 'non-select' SQL in the PostGIS db
    if globals.conn is None:
        QMessageBox.information(None, "", "globals.conn is None")
        globals.conn = psycopg2.connect(globals.connection_string)
    try:
        with globals.conn:
            csr = globals.conn.cursor()
            for sql in sql_list:
                if sql is not None and sql != "":
                    csr.execute(sql)
            csr.close()
    except psycopg2.InterfaceError, e:
        QMessageBox.information(None, "", "connection timed out, reconnecting")
        globals.conn = psycopg2.connect(globals.connection_string)
        run_nonselect_sql(sql)

def run_select_sql(sql):
    # General help function to run SELECT queries in the PostGIS db
    if globals.conn is None:
        QMessageBox.information(None, "", "globals.conn is None")
        globals.conn = psycopg2.connect(globals.connection_string)
    #if globals.db == "postgis":
    try:
        with globals.conn:
            csr = globals.conn.cursor()
            csr.execute(sql)
            rows = csr.fetchall()
            csr.close()
        return rows
    except psycopg2.InterfaceError, e:
        QMessageBox.information(None, "", "connection timed out, reconnecting")
        globals.conn = psycopg2.connect(globals.connection_string)
        rows = run_select_sql(sql)
        return rows
    #elif globals.db == "spatialite":

def style_layer(tbl_name, vlayer, fma_grouping):
    if os.path.isfile(os.path.join(rfm_resources_dir, tbl_name + ".qml")):
        vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, tbl_name + ".qml"))
    elif vlayer.source().startswith("dbname='" + globals.rfmp_db + "'") or vlayer.source().startswith("dbname='" + globals.spatialite_db + "'"):
        if vlayer.name().endswith("_fuel_type"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fuel_type.qml"))
        elif vlayer.name().endswith("_spatial_thresholds"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "spatial_thresholds.qml"))
        elif vlayer.name().endswith("_asset_points"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "_asset_points.qml"))
        elif vlayer.name().endswith("_asset_lines"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "_asset_lines.qml"))
        elif vlayer.name().endswith("_asset_polys"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "_asset_polys.qml"))
        elif vlayer.name().endswith("fuel_age"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fuel_age.qml"))
        elif vlayer.name().endswith("fuel_type_past_indicative_threshold") or vlayer.name().endswith("fuel_type_past_threshold"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fuel_age_past_threshold.qml"))
        elif vlayer.name().endswith("_past_indic_thold") or vlayer.name().endswith("_past_thold"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fuel_age_past_threshold.qml"))
        elif tbl_name.endswith("_with_indic_thold") or tbl_name.endswith("_with_thold") or tbl_name.endswith("_underlying_report_data"):
            if vlayer.name().endswith("% target) fuel"):
                vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fuel_age_cf_fma_thold.qml"))
            elif vlayer.name().endswith("(no target) fuel"):
                vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "non-target_fuel.qml"))
            elif vlayer.name().endswith(" target) overage"):
                vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "overage_fuel_cf_fma_thold.qml"))
            elif vlayer.name().endswith("overage_veg"):
                vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fuel_age_past_threshold.qml"))
        elif vlayer.name().endswith("_fma_seed"):
            vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fmas_type_grouping.qml"))
        elif fma_grouping is not None:
            if fma_grouping == "":
                vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fmas_no_grouping.qml"))
            elif fma_grouping == "fma":
                if vlayer.name().endswith("_fmas_complete") or vlayer.name().endswith("_fmas_combined"):
                    if globals.prioritisation_on:
                        vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fmas_type_and_priority_grouping.qml"))
                    else:
                        vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fmas_type_grouping.qml"))
                elif vlayer.name().endswith("_fmas_shs"):
                    vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fma_shs.qml"))
                elif vlayer.name().endswith("_fmas_cib"):
                    vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fma_cib.qml"))
                elif vlayer.name().endswith("_fmas_lrr"):
                    vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fma_lrr.qml"))
                elif vlayer.name().endswith("_fmas_ram"):
                    vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fma_ram.qml"))
            elif fma_grouping == "priority":
                vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fmas_priority_grouping.qml"))
            elif fma_grouping == "fma, priority":
                vlayer.loadNamedStyle(os.path.join(rfm_resources_dir, "fmas_type_and_priority_grouping.qml"))
        # Set editor widgets
        if vlayer.name().endswith("_asset_points") or vlayer.name().endswith("_asset_lines") or vlayer.name().endswith("_asset_polys"):
            set_editor_widgets(vlayer)
    QApplication.restoreOverrideCursor()

def table_exists(tbl_name):
    # General helper to find if table exists in PostGIS / spatialite db
    if globals.db == "postgis":
        sql = "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '" + tbl_name + "') OR EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'public' AND viewname = '" + tbl_name + "');"
    elif globals.db == "spatialite":
        sql = "SELECT EXISTS (SELECT 1 FROM sqlite_master WHERE name = '" + tbl_name + "' AND type IN ('table', 'view'))"
    return run_select_sql(sql)[0][0]

def update_updates_table(tbl_name, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")):
    # Called by import_table. rfm_planner_dialogs.accept
    #sql = "SELECT COUNT(*) FROM table_updates WHERE table_name = '" + tbl_name + "'"
    #count = run_select_sql(sql)[0][0]
    #if count == 0:
    #    sql = "INSERT INTO table_updates VALUES('" + tbl_name + "', '" + date + "')"
    #elif count > 0:
    #    sql = "UPDATE table_updates SET last_update = '" + date + "' WHERE table_name = '" + tbl_name + "'"
    #else:
    #    QMessageBox.information(None, "", "funny count")
    delete_sql = "DELETE FROM table_updates WHERE table_name = '" + tbl_name + "';"
    insert_sql = "INSERT INTO table_updates VALUES('" + tbl_name + "', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');"
    run_nonselect_sql([delete_sql, insert_sql])




######################################
### TESTING
######################################
def import_new_fuel_age():
    #Not likely to be implemented unless ogr2ogr can be made to work with PG 12 (UAT; PROD is PG10)
    debug_msg_box("Not yet implemented")
    return
    if globals.db != "postgis":
        QMessageBox.information(None, "Not available in spatialite!", "This can only done when you are using the central PostGIS database.")
        return
    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
    sql = "DELETE FROM fuel_age;"
    run_nonselect_sql([sql])
    globals.ogr2ogr_path = "C:/OSGeo4W64/bin/ogr2ogr.exe"
    for layer_name in ["CPT_FIRE_FUEL_AGE_SW_UCLP"]:  #, "CPT_FIRE_FUEL_AGE_NF"]:
        ogr2ogr_parameters = [globals.ogr2ogr_path,
                '-update',
                '-append',
                '-f', 'PostgreSQL',
                'PG:' + globals.connection_string,
                '-nlt', 'MULTIPOLYGON', 
                '-nln', 'fuel_age', 
                '-t_srs', '"' + albers_wa_string + '"',
                '-fieldmap', '-1,-1,0,-1,-1,-1,-1,-1',
                'C:/Users/patrickm/Desktop/RFMP_scratch/Pat.shp']
        # Call ogr2ogr.exe, with DETACHED_PROCESS flag so that console does not appear
        DETACHED_PROCESS = 0x00000008
        #subprocess.check_call(ogr2ogr_parameters)   #, creationflags=DETACHED_PROCESS)
        with open('C:/Temp/test.txt', 'w') as f:
            process = subprocess.Popen(ogr2ogr_parameters,
                         stdout=f, 
                         stderr=f)
            stdout, stderr = process.communicate()
            stdout, stderr
    
        
    update_updates_table("fuel_age")
    QApplication.restoreOverrideCursor()
    return
                    
    region_dict = get_region_dict()
    for region in region_dict:
        if region in ['swan', 'wheatbelt']:
            # region_fuel_age
            delete_sql = """DELETE FROM """ + region + """_fuel_age;"""
            insert_sql = """INSERT INTO """ + region + """_fuel_age (SELECT yslb, 
                            CASE WHEN ST_Within(fa.geometry, r.geometry) THEN ST_Multi(fa.geometry)
                            ELSE ST_Multi(ST_Intersection(fa.geometry, r.geometry)) END
                            FROM fuel_age_bkp fa JOIN regions r ON ST_Intersects(fa.geometry, r.geometry)
                            WHERE region = '""" + region_dict[region] + """');"""
            run_nonselect_sql([delete_sql, insert_sql, "COMMIT;"])
            update_updates_table(region + "_fuel_age")
            
            #region_fuel_type_age
            delete_sql = """DELETE FROM """ + region + """_fuel_type_age;"""
            insert_sql = """INSERT INTO """ + region + """_fuel_type_age (fuel_type, yslb, geometry) 
                            (SELECT fuel_type, yslb, 
                            CASE WHEN ST_Within(fa.geometry, ft.geometry) THEN fa.geometry
                            WHEN ST_Contains(fa.geometry, ft.geometry) THEN ft.geometry
                            ELSE ST_Intersection(fa.geometry, ft.geometry) END
                            FROM """ + region + """_fuel_age fa JOIN """ + region + """_fuel_type ft ON ST_Intersects(fa.geometry, ft.geometry));"""
            update_sql = """UPDATE """ + region + """_fuel_type_age SET area = ST_Area(geometry)/10000"""
            run_nonselect_sql([delete_sql, insert_sql, update_sql, "COMMIT;"])
            update_updates_table(region + "_fuel_type_age")
    QApplication.restoreOverrideCursor()