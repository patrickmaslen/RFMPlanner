# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'group_editor.ui'
#
# Created: Fri Mar 29 11:30:07 2019
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_EditingAssistantMainWindow(object):
    def setupUi(self, EditingAssistantMainWindow):
        EditingAssistantMainWindow.setObjectName(_fromUtf8("EditingAssistantMainWindow"))
        EditingAssistantMainWindow.resize(800, 861)
        self.centralwidget = QtGui.QWidget(EditingAssistantMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(45, 615, 216, 131))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.rad_fma = QtGui.QRadioButton(self.groupBox)
        self.rad_fma.setGeometry(QtCore.QRect(50, 30, 82, 21))
        self.rad_fma.setObjectName(_fromUtf8("rad_fma"))
        self.rad_asset_class = QtGui.QRadioButton(self.groupBox)
        self.rad_asset_class.setGeometry(QtCore.QRect(50, 60, 131, 21))
        self.rad_asset_class.setObjectName(_fromUtf8("rad_asset_class"))
        self.rad_resilience = QtGui.QRadioButton(self.groupBox)
        self.rad_resilience.setGeometry(QtCore.QRect(50, 90, 111, 21))
        self.rad_resilience.setObjectName(_fromUtf8("rad_resilience"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(255, 5, 331, 26))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(335, 175, 281, 41))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.cbx_postgis_tables = QtGui.QComboBox(self.centralwidget)
        self.cbx_postgis_tables.setGeometry(QtCore.QRect(185, 55, 361, 31))
        self.cbx_postgis_tables.setObjectName(_fromUtf8("cbx_postgis_tables"))
        self.btn_detailed_edit = QtGui.QPushButton(self.centralwidget)
        self.btn_detailed_edit.setGeometry(QtCore.QRect(150, 760, 291, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_detailed_edit.setFont(font)
        self.btn_detailed_edit.setObjectName(_fromUtf8("btn_detailed_edit"))
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(55, 585, 671, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.groupBox_3 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(35, 315, 351, 141))
        self.groupBox_3.setTitle(_fromUtf8(""))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.rad_fma_anom = QtGui.QRadioButton(self.groupBox_3)
        self.rad_fma_anom.setGeometry(QtCore.QRect(50, 10, 82, 21))
        self.rad_fma_anom.setObjectName(_fromUtf8("rad_fma_anom"))
        self.rad_asset_class_anom = QtGui.QRadioButton(self.groupBox_3)
        self.rad_asset_class_anom.setGeometry(QtCore.QRect(50, 40, 131, 21))
        self.rad_asset_class_anom.setObjectName(_fromUtf8("rad_asset_class_anom"))
        self.rad_resilience_anom = QtGui.QRadioButton(self.groupBox_3)
        self.rad_resilience_anom.setGeometry(QtCore.QRect(50, 70, 121, 21))
        self.rad_resilience_anom.setObjectName(_fromUtf8("rad_resilience_anom"))
        self.rad_any_anom = QtGui.QRadioButton(self.groupBox_3)
        self.rad_any_anom.setGeometry(QtCore.QRect(50, 100, 161, 21))
        self.rad_any_anom.setObjectName(_fromUtf8("rad_any_anom"))
        self.btn_select_anomalies = QtGui.QPushButton(self.groupBox_3)
        self.btn_select_anomalies.setGeometry(QtCore.QRect(260, 100, 66, 31))
        self.btn_select_anomalies.setObjectName(_fromUtf8("btn_select_anomalies"))
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(15, 285, 431, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.btn_case_errors = QtGui.QPushButton(self.centralwidget)
        self.btn_case_errors.setGeometry(QtCore.QRect(185, 165, 131, 61))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_case_errors.setFont(font)
        self.btn_case_errors.setObjectName(_fromUtf8("btn_case_errors"))
        self.lbl_selection_count = QtGui.QLabel(self.centralwidget)
        self.lbl_selection_count.setGeometry(QtCore.QRect(95, 475, 221, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_selection_count.setFont(font)
        self.lbl_selection_count.setObjectName(_fromUtf8("lbl_selection_count"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 60, 171, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.groupBox_2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(275, 625, 381, 121))
        self.groupBox_2.setTitle(_fromUtf8(""))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.btn_set_values = QtGui.QPushButton(self.groupBox_2)
        self.btn_set_values.setGeometry(QtCore.QRect(280, 80, 66, 31))
        self.btn_set_values.setObjectName(_fromUtf8("btn_set_values"))
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(25, 10, 241, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cbx_values = QtGui.QComboBox(self.groupBox_2)
        self.cbx_values.setGeometry(QtCore.QRect(210, 40, 141, 31))
        self.cbx_values.setObjectName(_fromUtf8("cbx_values"))
        self.label_7 = QtGui.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(15, 535, 431, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.btn_add_layer = QtGui.QPushButton(self.centralwidget)
        self.btn_add_layer.setEnabled(False)
        self.btn_add_layer.setGeometry(QtCore.QRect(245, 105, 231, 31))
        self.btn_add_layer.setObjectName(_fromUtf8("btn_add_layer"))
        EditingAssistantMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(EditingAssistantMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        EditingAssistantMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(EditingAssistantMainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        EditingAssistantMainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(EditingAssistantMainWindow)
        QtCore.QMetaObject.connectSlotsByName(EditingAssistantMainWindow)

    def retranslateUi(self, EditingAssistantMainWindow):
        EditingAssistantMainWindow.setWindowTitle(_translate("EditingAssistantMainWindow", "Group Editing", None))
        self.groupBox.setTitle(_translate("EditingAssistantMainWindow", "Column for editing", None))
        self.rad_fma.setText(_translate("EditingAssistantMainWindow", "fma", None))
        self.rad_asset_class.setText(_translate("EditingAssistantMainWindow", "asset_class", None))
        self.rad_resilience.setText(_translate("EditingAssistantMainWindow", "resilience", None))
        self.label_2.setText(_translate("EditingAssistantMainWindow", "RFM Editing Assistant", None))
        self.label_4.setText(_translate("EditingAssistantMainWindow", "Removes excess spaces and ensures \n"
"correct upper/lower case", None))
        self.btn_detailed_edit.setText(_translate("EditingAssistantMainWindow", "Go to Detailed Editing", None))
        self.label_5.setText(_translate("EditingAssistantMainWindow", "Update selected features from map or rows from attribute table:", None))
        self.rad_fma_anom.setText(_translate("EditingAssistantMainWindow", "fma", None))
        self.rad_asset_class_anom.setText(_translate("EditingAssistantMainWindow", "asset_class", None))
        self.rad_resilience_anom.setText(_translate("EditingAssistantMainWindow", "resilience", None))
        self.rad_any_anom.setText(_translate("EditingAssistantMainWindow", "any of the above", None))
        self.btn_select_anomalies.setText(_translate("EditingAssistantMainWindow", "OK", None))
        self.label_6.setText(_translate("EditingAssistantMainWindow", "Select rows with invalid values for:", None))
        self.btn_case_errors.setText(_translate("EditingAssistantMainWindow", "Fix case and\n"
"space errors", None))
        self.lbl_selection_count.setText(_translate("EditingAssistantMainWindow", "selected feature(s)", None))
        self.label.setText(_translate("EditingAssistantMainWindow", "Database layer", None))
        self.btn_set_values.setText(_translate("EditingAssistantMainWindow", "OK", None))
        self.label_3.setText(_translate("EditingAssistantMainWindow", "Set value for selected rows to:", None))
        self.label_7.setText(_translate("EditingAssistantMainWindow", "Group Edit:", None))
        self.btn_add_layer.setText(_translate("EditingAssistantMainWindow", "Add database layer to map", None))

