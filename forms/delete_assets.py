# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'delete_assets.ui'
#
# Created: Tue Apr 30 05:16:05 2019
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

class Ui_DeleteAssetsDialog(object):
    def setupUi(self, DeleteAssetsDialog):
        DeleteAssetsDialog.setObjectName(_fromUtf8("DeleteAssetsDialog"))
        DeleteAssetsDialog.resize(505, 384)
        self.cbx_asset_layers = QgsMapLayerComboBox(DeleteAssetsDialog)
        self.cbx_asset_layers.setGeometry(QtCore.QRect(90, 180, 271, 27))
        self.cbx_asset_layers.setObjectName(_fromUtf8("cbx_asset_layers"))
        self.label = QtGui.QLabel(DeleteAssetsDialog)
        self.label.setGeometry(QtCore.QRect(40, 20, 431, 111))
        self.label.setObjectName(_fromUtf8("label"))
        self.btn_stop = QtGui.QPushButton(DeleteAssetsDialog)
        self.btn_stop.setGeometry(QtCore.QRect(260, 240, 75, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_stop.setFont(font)
        self.btn_stop.setObjectName(_fromUtf8("btn_stop"))
        self.btn_go = QtGui.QPushButton(DeleteAssetsDialog)
        self.btn_go.setGeometry(QtCore.QRect(140, 240, 75, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_go.setFont(font)
        self.btn_go.setObjectName(_fromUtf8("btn_go"))
        self.label_4 = QtGui.QLabel(DeleteAssetsDialog)
        self.label_4.setGeometry(QtCore.QRect(10, 320, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.rad_selected_features = QtGui.QRadioButton(DeleteAssetsDialog)
        self.rad_selected_features.setGeometry(QtCore.QRect(0, 300, 301, 25))
        self.rad_selected_features.setObjectName(_fromUtf8("rad_selected_features"))
        self.rad_entire_layer = QtGui.QRadioButton(DeleteAssetsDialog)
        self.rad_entire_layer.setGeometry(QtCore.QRect(10, 340, 301, 25))
        self.rad_entire_layer.setObjectName(_fromUtf8("rad_entire_layer"))
        self.label_2 = QtGui.QLabel(DeleteAssetsDialog)
        self.label_2.setGeometry(QtCore.QRect(90, 140, 281, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(DeleteAssetsDialog)
        QtCore.QMetaObject.connectSlotsByName(DeleteAssetsDialog)

    def retranslateUi(self, DeleteAssetsDialog):
        DeleteAssetsDialog.setWindowTitle(_translate("DeleteAssetsDialog", "Delete Assets", None))
        self.label.setText(_translate("DeleteAssetsDialog", "This tool helps safely delete assets from the database.\n"
"The relevant assets layer must be loaded in the map\n"
" and the asset(s) you want to delete should be selected.", None))
        self.btn_stop.setText(_translate("DeleteAssetsDialog", "Cancel", None))
        self.btn_go.setText(_translate("DeleteAssetsDialog", "OK", None))
        self.label_4.setText(_translate("DeleteAssetsDialog", "OR", None))
        self.rad_selected_features.setText(_translate("DeleteAssetsDialog", "Delete selected asset(s) from:", None))
        self.rad_entire_layer.setText(_translate("DeleteAssetsDialog", "Delete entire layer:", None))
        self.label_2.setText(_translate("DeleteAssetsDialog", "Delete selected asset(s) from:", None))

from qgis.gui import QgsMapLayerComboBox
