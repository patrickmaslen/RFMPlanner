# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RFMPlanner
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
import ConfigParser
from shutil import copyfile
from PyQt4.QtCore import QSettings, Qt, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QApplication, QCursor, QIcon, QMenu, QMessageBox
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
import rfm_planner_dialogs 
import rfm_library
import sql_clauses
import os.path
import psycopg2
from pyspatialite import dbapi2 as sqlite3
import globals

class RFMPlanner:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RFMPlanner_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RFM Planner')
        self.toolbar = self.iface.addToolBar(u'RFMPlanner')
        self.toolbar.setObjectName(u'RFMPlanner')
        self.settings_initialised = False

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RFMPlanner', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = RFMPlannerDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action
    
    def rfm_add_submenu(self, submenu):
        if self.rfm_menu != None:
            self.rfm_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("RFM", submenu.menuAction())

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        """icon_path = ':/plugins/RFMPlanner/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Open RFM Dialogue'),
            callback=self.run,
            parent=self.iface.mainWindow())
        """
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__),'config.cfg'))
        metadata = ConfigParser.ConfigParser()
        metadata.read(os.path.join(os.path.dirname(__file__),'metadata.txt'))
        name = metadata.get('general', 'name')
        version = metadata.get('general', 'version')
        if name.lower().endswith('dev') or version.lower().endswith('dev'):
            globals.dev = True
        elif name.lower().endswith('uat') or version.lower().endswith('uat'):
            globals.uat = True
        menu_title = "RFM Planning"
        if globals.dev:
            menu_title += " DEV"
        elif globals.uat:
            menu_title += " UAT"
        
        # Following two lines make RFM Tools accessible from a top-level menu
        self.rfm_menu = QMenu(menu_title)
        if globals.dev:
            self.rfm_menu.setStyleSheet("QMenu{background-color: red;}")
        elif globals.uat:
            self.rfm_menu.setStyleSheet("QMenu{background-color: orange;}")
        elif globals.test:
            self.rfm_menu.setStyleSheet("QMenu{background-color: blue;}")
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.rfm_menu)
        self.rfm_menu.aboutToShow.connect(lambda: rfm_library.initialise_settings(self))

        # Submenus
        self.preferred_region_menu = QMenu("Preferred Region")
        self.rfm_add_submenu(self.preferred_region_menu)
        globals.preferred_region_menu = self.preferred_region_menu
        
        self.add_layers_menu = QMenu("Add layers to map")
        self.rfm_menu.addMenu(self.add_layers_menu)
        
        self.add_asset_layers_action = QAction("Asset layers", self.iface.mainWindow())
        self.add_asset_layers_action.triggered.connect(lambda: self.add_existing_rfmp_layers("asset"))
        self.add_layers_menu.addAction(self.add_asset_layers_action)
        
        self.add_existing_fma_layers_menu = QMenu("Existing FMA layers")
        self.add_layers_menu.addMenu(self.add_existing_fma_layers_menu)
        
        self.add_calculated_fma_layers_action = QAction("Calculated FMA layers", self.iface.mainWindow())
        self.add_calculated_fma_layers_action.triggered.connect(lambda: self.add_existing_rfmp_layers("fma"))
        self.add_existing_fma_layers_menu.addAction(self.add_calculated_fma_layers_action)
        
        self.add_draft_fma_layers_action = QAction("Draft FMA layers", self.iface.mainWindow())
        self.add_draft_fma_layers_action.triggered.connect(lambda: self.add_existing_rfmp_layers("draft fma"))
        self.add_existing_fma_layers_menu.addAction(self.add_draft_fma_layers_action)
        
        self.show_risk_zone_action = QAction("Bushfire risk zone", self.iface.mainWindow())
        self.show_risk_zone_action.triggered.connect(self.add_brz_layer)
        self.add_layers_menu.addAction(self.show_risk_zone_action)
        
        self.fuel_type_menu = QMenu("Fuel type layers")
        self.add_layers_menu.addMenu(self.fuel_type_menu)
        
        self.fuel_age_menu = QMenu("Fuel age layers")
        self.add_layers_menu.addMenu(self.fuel_age_menu)
        #fuel age (my region)
        self.add_regional_fuel_age_action = QAction("My region", self.iface.mainWindow())
        self.add_regional_fuel_age_action.triggered.connect(self.add_regional_fuel_age)
        self.fuel_age_menu.addAction(self.add_regional_fuel_age_action)
        #fuel age (WA)
        self.add_statewide_fuel_age_action = QAction("Statewide", self.iface.mainWindow())
        self.add_statewide_fuel_age_action.triggered.connect(self.add_statewide_fuel_age)
        self.fuel_age_menu.addAction(self.add_statewide_fuel_age_action)
        #post-threshold (preferred region level only)
        self.past_threshold_action = QAction("Fuel age past threshold", self.iface.mainWindow())
        self.past_threshold_action.triggered.connect(self.show_veg_past_threshold)
        self.fuel_age_menu.addAction(self.past_threshold_action)
        
        self.show_spatial_thresholds_action = QAction("Spatial thresholds", self.iface.mainWindow())
        self.show_spatial_thresholds_action.triggered.connect(rfm_library.show_spatial_thresholds)
        self.add_layers_menu.addAction(self.show_spatial_thresholds_action)
        
        self.dept_land_menu = QMenu("Dept managed land")
        self.add_layers_menu.addMenu(self.dept_land_menu)
        
        self.show_dept_land_detail_action = QAction("Detail", self.iface.mainWindow())
        self.show_dept_land_detail_action.triggered.connect(lambda: rfm_library.show_dept_land("detail"))
        self.dept_land_menu.addAction(self.show_dept_land_detail_action)
        
        self.show_dept_land_bundaries_action = QAction("Boundaries", self.iface.mainWindow())
        self.show_dept_land_bundaries_action.triggered.connect(lambda: rfm_library.show_dept_land("boundaries"))
        self.dept_land_menu.addAction(self.show_dept_land_bundaries_action)        
        
        self.update_assets_menu = QMenu("Add/edit asset data")
        
        self.append_assets_action = QAction("Copy/paste from layer", self.iface.mainWindow())
        self.update_assets_menu.addAction(self.append_assets_action)
        
        self.update_assets_submenu = QMenu("Digitise assets")
        self.update_assets_menu.addMenu(self.update_assets_submenu)
        globals.update_assets_menu = self.update_assets_submenu     # This is correct
        self.rfm_add_submenu(self.update_assets_menu)
        
        self.editing_assistants_submenu = QMenu("Editing assistants")
        self.update_assets_menu.addMenu(self.editing_assistants_submenu)
        
        self.group_assistant_action = QAction("Group editing", self.iface.mainWindow())
        self.editing_assistants_submenu.addAction(self.group_assistant_action)
        
        self.detailed_assistant_action = QAction("Detailed editing", self.iface.mainWindow())
        self.editing_assistants_submenu.addAction(self.detailed_assistant_action)
        
        self.delete_assets_action = QAction("Delete assets", self.iface.mainWindow())
        self.update_assets_menu.addAction(self.delete_assets_action)
        self.delete_assets_action.triggered.connect(rfm_library.delete_assets)

        self.calculate_menu = QMenu("Calculate")
        #self.rfm_menu.addMenu(self.calculate_menu)
        
        #self.prioritise_menu = QMenu("Regional asset priorities")
        #self.calculate_menu.addMenu(self.prioritise_menu)
        #globals.prioritise_menu = self.prioritise_menu     # This is correct

        self.generate_fma_action = QAction("Create FMA polygons", self.iface.mainWindow())
        self.generate_fma_action.triggered.connect(rfm_library.create_fmas)
        #self.calculate_menu.addAction(self.generate_fma_action)
        self.rfm_menu.addAction(self.generate_fma_action)
        
        #self.indic_thold_action = QAction("Fuel age thresholds (indicative)", self.iface.mainWindow())
        #self.indic_thold_action.triggered.connect(rfm_library.calculate_indic_tholds)
        #self.calculate_menu.addAction(self.indic_thold_action)
        
        #self.defin_thold_action = QAction("Fuel age thresholds", self.iface.mainWindow())
        #self.defin_thold_action.triggered.connect(rfm_library.calculate_defin_tholds)
        #self.calculate_menu.addAction(self.defin_thold_action)
        
        # REPORTS
        self.reports_menu = QMenu("Reports")
        self.rfm_add_submenu(self.reports_menu)
        self.report_preferred_region_action = QAction("My region", self.iface.mainWindow())
        self.report_all_regions_action = QAction("All regions", self.iface.mainWindow())
        self.report_brmzs_action = QAction("Bushfire zones", self.iface.mainWindow())
        self.reports_menu.addAction(self.report_preferred_region_action)
        self.reports_menu.addAction(self.report_all_regions_action)
        self.reports_menu.addAction(self.report_brmzs_action)
        self.report_preferred_region_action.triggered.connect(lambda: rfm_library.open_report("preferred_region"))
        self.report_all_regions_action.triggered.connect(lambda: rfm_library.open_report("all_regions"))
        self.report_brmzs_action.triggered.connect(lambda: rfm_library.open_report("brmzs"))

        # Actions
        self.setup_assets_action = QAction("Initialise Region Assets", self.iface.mainWindow())
        self.setup_assets_action.triggered.connect(self.initialise_region_assets)
        #self.setup_assets_menu.addAction(self.setup_assets_action)

        self.show_region_fuel_type_action = QAction("Fuel type (my region)", self.iface.mainWindow())
        #self.show_region_fuel_type_action.triggered.connect(lambda: self.add_fuel_type_layer("region_fuel_type"))
        self.show_region_fuel_type_action.triggered.connect(lambda: self.add_fuel_type_layer("region_fuel_type_all"))
        self.fuel_type_menu.addAction(self.show_region_fuel_type_action)

        self.show_fuel_type_action = QAction("Fuel type (all)", self.iface.mainWindow())
        #self.show_fuel_type_action.triggered.connect(lambda: self.add_fuel_type_layer("fuel_type_boundaries"))
        #self.show_fuel_type_action.triggered.connect(lambda: self.add_fuel_type_layer("fuel_types_non_dept_land"))
        self.show_fuel_type_action.triggered.connect(lambda: self.add_fuel_type_layer("fuel_type_all_wa"))
        self.fuel_type_menu.addAction(self.show_fuel_type_action)
        
        """self.show_fuel_type_dept_action = QAction("Fuel type (dept land)", self.iface.mainWindow())
        #self.show_fuel_type_dept_action.triggered.connect(lambda: rfm_library.load_postgis_layer("fuel_type_boundaries"))
        self.show_fuel_type_dept_action.triggered.connect(lambda: self.add_fuel_type_layer("fuel_type_boundaries"))
        self.fuel_type_menu.addAction(self.show_fuel_type_dept_action)
        
        self.show_fuel_type_non_dept_action = QAction("Fuel type (non-dept land)", self.iface.mainWindow())
        #self.show_fuel_type_non_dept_action.triggered.connect(lambda: rfm_library.load_postgis_layer("fuel_types_non_dept_land"))
        self.show_fuel_type_non_dept_action.triggered.connect(lambda: self.add_fuel_type_layer("fuel_types_non_dept_land"))
        self.fuel_type_menu.addAction(self.show_fuel_type_non_dept_action)
        """
        self.about_action = QAction("About", self.iface.mainWindow())
        self.about_action.triggered.connect(self.show_about_info)
        self.rfm_menu.addAction(self.about_action)
        
        self.settings_menu = QMenu("Settings")
        self.rfm_add_submenu(self.settings_menu)

        globals.prioritisation_on = config.getboolean('settings_menu', 'prioritisation')
        globals.db = config.get('settings_menu', 'db')
        if globals.prioritisation_on:
            self.prioritisation_action = QAction("Prioritisation [On]", self.iface.mainWindow())
        else:
            self.prioritisation_action = QAction("Prioritisation [Off]", self.iface.mainWindow())
        self.db_action = QAction("Database [" + globals.db + "]", self.iface.mainWindow())
        self.settings_menu.addAction(self.prioritisation_action)
        self.settings_menu.addAction(self.db_action)
        self.prioritisation_action.triggered.connect(self.switch_prioritisation)
        self.db_action.triggered.connect(self.switch_db)
        
        # DATA ADMIN
        self.data_admin_menu = QMenu("Data Admin")
        self.rfm_add_submenu(self.data_admin_menu)
        self.update_thresholds_menu = QMenu("Fuel thresholds / targets", self.iface.mainWindow())
        self.data_admin_menu.addMenu(self.update_thresholds_menu)
        
        self.show_indicative_tholds_action = QAction("Show statewide default fuel thresholds", self.iface.mainWindow())
        self.update_thresholds_menu.addAction(self.show_indicative_tholds_action)
        self.show_indicative_tholds_action.triggered.connect(rfm_library.list_indicative_fuel_thresholds)
        
        self.update_regional_default_thresholds_action = QAction("Update regional fuel thresholds", self.iface.mainWindow())
        #self.update_spat_var_thresholds_action = QAction("Update spatially varying thresholds", self.iface.mainWindow())
        self.update_thresholds_menu.addAction(self.update_regional_default_thresholds_action)
        #self.update_thresholds_menu.addAction(self.update_spat_var_thresholds_action)
        self.update_regional_default_thresholds_action.triggered.connect(rfm_library.update_reg_default_tholds)
        #self.update_spat_var_thresholds_action.triggered.connect(rfm_library.update_spat_var_tholds)
        self.show_spatial_thresholds_action2 = QAction("Add spatial thresholds layer to map", self.iface.mainWindow())
        self.show_spatial_thresholds_action2.triggered.connect(rfm_library.show_spatial_thresholds)
        self.update_thresholds_menu.addAction(self.show_spatial_thresholds_action2)

        ## Create actions for update_assets_submenu
        self.update_assets_submenu.triggered[QAction].connect(rfm_library.call_load_postgis_layer)  # returns menu's QAction which was triggered
        self.append_assets_action.triggered.connect(rfm_library.append_assets)
        self.group_assistant_action.triggered.connect(rfm_library.open_group_editing_assistant)
        self.detailed_assistant_action.triggered.connect(rfm_library.open_detailed_editing_assistant)
        #self.prioritise_menu.triggered[QAction].connect(rfm_library.manage_prioritise_assets)  # returns menu's QAction which was triggered
        self.preferred_region_menu.triggered[QAction].connect(rfm_library.change_preferred_region)  # returns menu's QAction which was triggered

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&RFM Planner'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def initialise_region_assets(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        poly_assets_form = rfm_planner_dialogs.CreateRegionAssetsDialog()
        QApplication.restoreOverrideCursor()
        poly_assets_form.exec_()

    def add_existing_rfmp_layers(self, type):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        if type == "asset":
            if globals.db == "postgis":
                sql = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_asset_%' AND table_schema='public' AND table_type='BASE TABLE';"
            elif globals.db == "spatialite":
                sql ="SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%_asset_%'"
        elif type == "fma":
            if globals.db == "postgis":
                sql = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_fmas%' AND table_schema='public' AND table_type='BASE TABLE';"
            elif globals.db == "spatialite":
                sql = "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%_fmas%'"
        elif type == "draft fma":
            if globals.db == "postgis":
                sql = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_fma_seed%' AND table_schema='public' AND table_type='BASE TABLE';"
            elif globals.db == "spatialite":
                sql = "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%_fma_seed%"
        results = rfm_library.run_select_sql(sql)
        if len(results) == 0:
            QMessageBox.information(None, "No asset layers!", "There are no " + type + " layers in the database yet.")
            QApplication.restoreOverrideCursor()
            return
        add_layers_form = rfm_planner_dialogs.AssetTableSelectorDialog(type)
        add_layers_form.label.setText("Select " + type + " layer(s) to add to map")
        add_layers_form.setWindowTitle(type.upper() + " LAYER SELECTOR")
        QApplication.restoreOverrideCursor()
        add_layers_form.exec_()

    def add_brz_layer(self):
        if globals.db == "postgis":
            rfm_library.load_postgis_layer("bushfire_risk_zones")
        elif globals.db == "spatialite":
            rfm_library.load_spatialite_layer("bushfire_risk_zones")

    def add_fuel_type_layer(self, layer_name):    #"fuel_types_non_dept_land")
        #if layer_name == "region_fuel_type":
        if layer_name in ["region_fuel_type_all", "fuel_type_all_wa"]:
            region = globals.preferred_region.lower().replace(" ", "_")
            if region == "all_of_wa":
                QMessageBox.information(None, "Select single region", "This tool is not designed to run when the region is set to 'All of WA'.")
                return
            layer_name = layer_name.replace("region", region)
        if globals.db == "postgis":
            rfm_library.load_postgis_layer(layer_name)
        elif globals.db == "spatialite":
            QMessageBox.information(None, "Not available in local db", "Fuel type layers are not available from the local spatialite database.  You may be able to access a fuel type layer from the Corporate Data menu.")

    def show_veg_past_threshold(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        region = globals.preferred_region.lower().replace(" ", "_")
        if region == "all_of_wa":
            QMessageBox.information(None, "Select single region", "This tool is not designed to run when the region is set to 'All of WA'.")
            return
        if globals.db == "spatialite":
            QApplication.restoreOverrideCursor()
            QMessageBox.information(None, "Not available in local db", "Calculation of overage vegetation areas is not available from the local spatialite database.")
            return
        # Check fmas have been calculated; if not offer to calculate 
        fma_tbl_name = region + "_fmas_complete"
        if not rfm_library.table_exists(fma_tbl_name):
            reply = QMessageBox.question(None, "FMAs not yet calculated!", "FMAs have not yet been calculated.  This must be done before overage vegetation areas can be calculated.  Do you want to calculate FMAs now?  (this will take some time, maybe an hour)", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                QApplication.restoreOverrideCursor()
                return
            else:
                rfm_library.create_fmas()
                QApplication.restoreOverrideCursor()
                return
        # If fmas in place, check underlying_report_data have been calculated (this is the source of the overage veg layer);
        # if not offer to calculate
        #overage_veg_view_name = region + "_past_indic_thold"
        overage_veg_table_name = region + "_underlying_report_data"
        dates_ok = False
        if rfm_library.table_exists(overage_veg_table_name):
            dates_ok = rfm_library.check_underlying_report_data_dates(region)
        if (not rfm_library.table_exists(overage_veg_table_name)) or not dates_ok:
            reply = QMessageBox.question(None, "Overage veg areas not yet calculated!", "Overage veg areas have not yet been calculated.  This must be done before they can be displayed in the map.  Do you want to calculate them now?  (this will take several minutes)", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                QApplication.restoreOverrideCursor()
                return
            else:
                if rfm_library.table_exists(region + "_default_thresholds") or  rfm_library.table_exists(region + "_spatial_thresholds"):
                    region_specific_thresholds = True
                else:
                    region_specific_thresholds = False
                    
                """if region_specific_thresholds:
                    sql_assemble_report_data = sql_clauses.assemble_report_data().replace("region", region).replace('xxx', 'region')
                else:
                    sql_assemble_report_data = sql_clauses.assemble_report_data().replace('region_fuel_fma_thold_target_lookup', 'default_fuel_fma_thold_target_lookup').replace("region", region).replace('xxx', 'region')
                rfm_library.run_nonselect_sql([sql_assemble_report_data])
                """
                rfm_library.create_report_data(region, region_specific_thresholds)

        QApplication.restoreOverrideCursor()
        filter = "yslb >= threshold_age"
        layer = rfm_library.load_postgis_layer(region + "_underlying_report_data", None, "id", filter, "overage_veg")
        
    def show_definitive_thresholds(self):
        QMessageBox.information(None, "", "No definitive thresholds have been specified yet")
        
    def add_regional_fuel_age(self):
        if globals.db == "postgis":
            rfm_library.load_postgis_layer(globals.preferred_region.lower().replace(" ", "_") + "_fuel_age", key_column="ogc_fid")
        else:
            QMessageBox.information(None, "Not available in local db", "Fuel age layers are not available from the local spatialite database.  You may be able to access a fuel age layer from the Corporate Data menu.")
        
    def add_statewide_fuel_age(self):
        if globals.db == "postgis":        
            rfm_library.load_postgis_layer("fuel_age")
        else:
            QMessageBox.information(None, "Not available in local db", "Fuel age layers are not available from the local spatialite database.  You may be able to access a fuel age layer from the Corporate Data menu.")

    def show_about_info(self):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__),'metadata.txt'))
        name = config.get('general', 'name')
        version = config.get('general', 'version')
        release_date = config.get('general', 'release_date')
        QMessageBox.information(None, name, "Version:\t" + version + "\nRelease date:\t" + release_date)

    def switch_prioritisation(self):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__),'config.cfg'))
        prioritisation_on = config.getboolean('settings_menu', 'prioritisation')
        if prioritisation_on:   # == "True":
            response = QMessageBox.information(None, "Switch regional prioritisation on/off", "Regional prioritisation is switched on.  Do you want to switch it off?", buttons=QMessageBox.Yes|QMessageBox.No)
            if response == QMessageBox.Yes:
                config.set('settings_menu', 'prioritisation', 'False')
                with open(os.path.join(os.path.dirname(__file__),'config.cfg'), 'wb') as configfile:
                    config.write(configfile)
                globals.prioritisation_on = False
                self.prioritisation_action.setText("Prioritisation [Off]")
        #elif prioritisation_on == "False":
        else:
            response = QMessageBox.information(None, "Switch regional prioritisation on/off", "Regional prioritisation is switched off.  Do you want to switch it on?", buttons=QMessageBox.Yes|QMessageBox.No)
            if response == QMessageBox.Yes:
                config.set('settings_menu', 'prioritisation', 'True')
                with open(os.path.join(os.path.dirname(__file__),'config.cfg'), 'wb') as configfile:
                    config.write(configfile)
                globals.prioritisation_on = True
                self.prioritisation_action.setText("Prioritisation [On]")

    def switch_db(self):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__),'config.cfg'))
        db = config.get('settings_menu', 'db')
        if db == 'postgis':
            response = QMessageBox.information(None, 'Switch database', 'The current database is a statewide Postgis db on the Kensington server.  Do you want to switch to a local database?  You will be able to add assets to the local database but most other features of the tool will be unavailable, and the assets will not be on the main Postgis database.', buttons=QMessageBox.Yes|QMessageBox.No)
            if response == QMessageBox.Yes:
                config.set('settings_menu', 'db', 'spatialite')
                with open(os.path.join(os.path.dirname(__file__),'config.cfg'), 'wb') as configfile:
                    config.write(configfile)
                globals.db = 'spatialite'
                globals.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__),globals.spatialite_db))
                self.db_action.setText("Database [" + globals.db + "]")
        elif db == 'spatialite':
            response = QMessageBox.information(None, 'Switch database', 'The database is a local (on this computer) spatialite db.  Do you want to switch to the central Postgis database?', buttons=QMessageBox.Yes|QMessageBox.No)
            if response == QMessageBox.Yes:
                config.set('settings_menu', 'db', 'postgis')
                with open(os.path.join(os.path.dirname(__file__),'config.cfg'), 'wb') as configfile:
                    config.write(configfile)
                globals.db = 'postgis'
                globals.conn = psycopg2.connect(globals.connection_string)
                self.db_action.setText("Database [" + globals.db + "]")
