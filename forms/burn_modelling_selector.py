# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'burn_modelling_selector.ui'
#
# Created: Thu May 06 16:21:17 2021
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

class Ui_BurnModellingSelectorDialog(object):
    def setupUi(self, BurnModellingSelectorDialog):
        BurnModellingSelectorDialog.setObjectName(_fromUtf8("BurnModellingSelectorDialog"))
        BurnModellingSelectorDialog.resize(545, 712)
        self.mMapLayerComboBox = QgsMapLayerComboBox(BurnModellingSelectorDialog)
        self.mMapLayerComboBox.setGeometry(QtCore.QRect(190, 40, 291, 27))
        self.mMapLayerComboBox.setObjectName(_fromUtf8("mMapLayerComboBox"))
        self.mFieldComboBox = QgsFieldComboBox(BurnModellingSelectorDialog)
        self.mFieldComboBox.setGeometry(QtCore.QRect(199, 280, 251, 27))
        self.mFieldComboBox.setObjectName(_fromUtf8("mFieldComboBox"))
        self.groupBox = QtGui.QGroupBox(BurnModellingSelectorDialog)
        self.groupBox.setGeometry(QtCore.QRect(180, 90, 311, 121))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.rad_map_selection = QtGui.QRadioButton(self.groupBox)
        self.rad_map_selection.setGeometry(QtCore.QRect(30, 60, 261, 25))
        self.rad_map_selection.setObjectName(_fromUtf8("rad_map_selection"))
        self.rad_all_polys = QtGui.QRadioButton(self.groupBox)
        self.rad_all_polys.setGeometry(QtCore.QRect(30, 30, 171, 25))
        self.rad_all_polys.setChecked(True)
        self.rad_all_polys.setObjectName(_fromUtf8("rad_all_polys"))
        self.rad_list_selection = QtGui.QRadioButton(self.groupBox)
        self.rad_list_selection.setGeometry(QtCore.QRect(30, 90, 261, 25))
        self.rad_list_selection.setObjectName(_fromUtf8("rad_list_selection"))
        self.label = QtGui.QLabel(BurnModellingSelectorDialog)
        self.label.setGeometry(QtCore.QRect(30, 40, 151, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(BurnModellingSelectorDialog)
        self.label_2.setGeometry(QtCore.QRect(200, 250, 281, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.tableWidget = QtGui.QTableWidget(BurnModellingSelectorDialog)
        self.tableWidget.setEnabled(False)
        self.tableWidget.setGeometry(QtCore.QRect(200, 330, 256, 281))
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.label_3 = QtGui.QLabel(BurnModellingSelectorDialog)
        self.label_3.setGeometry(QtCore.QRect(30, 250, 151, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.btn_process = QtGui.QPushButton(BurnModellingSelectorDialog)
        self.btn_process.setGeometry(QtCore.QRect(200, 640, 112, 34))
        self.btn_process.setObjectName(_fromUtf8("btn_process"))
        self.btn_cancel = QtGui.QPushButton(BurnModellingSelectorDialog)
        self.btn_cancel.setGeometry(QtCore.QRect(340, 640, 112, 34))
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.label_4 = QtGui.QLabel(BurnModellingSelectorDialog)
        self.label_4.setGeometry(QtCore.QRect(20, 360, 161, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(BurnModellingSelectorDialog)
        self.label_5.setGeometry(QtCore.QRect(20, 390, 161, 21))
        self.label_5.setObjectName(_fromUtf8("label_5"))

        self.retranslateUi(BurnModellingSelectorDialog)
        QtCore.QObject.connect(self.btn_cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), BurnModellingSelectorDialog.close)
        QtCore.QObject.connect(self.btn_process, QtCore.SIGNAL(_fromUtf8("clicked()")), BurnModellingSelectorDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(BurnModellingSelectorDialog)

    def retranslateUi(self, BurnModellingSelectorDialog):
        BurnModellingSelectorDialog.setWindowTitle(_translate("BurnModellingSelectorDialog", "Dialog", None))
        self.groupBox.setTitle(_translate("BurnModellingSelectorDialog", "Burn Cell Selection", None))
        self.rad_map_selection.setText(_translate("BurnModellingSelectorDialog", "Use selected burn cells on map", None))
        self.rad_all_polys.setText(_translate("BurnModellingSelectorDialog", "Use all burn cells", None))
        self.rad_list_selection.setText(_translate("BurnModellingSelectorDialog", "Select burn cells from list below", None))
        self.label.setText(_translate("BurnModellingSelectorDialog", "Burn Cells Layer", None))
        self.label_2.setText(_translate("BurnModellingSelectorDialog", "Attribute holding name or identifier", None))
        self.label_3.setText(_translate("BurnModellingSelectorDialog", "Identifier field", None))
        self.btn_process.setText(_translate("BurnModellingSelectorDialog", "Process", None))
        self.btn_cancel.setText(_translate("BurnModellingSelectorDialog", "Cancel", None))
        self.label_4.setText(_translate("BurnModellingSelectorDialog", "Use Ctrl key to select", None))
        self.label_5.setText(_translate("BurnModellingSelectorDialog", "multiple features", None))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
