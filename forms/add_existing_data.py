# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_existing_data.ui'
#
# Created: Thu Feb 28 10:34:29 2019
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

class Ui_AddAssetsDialog(object):
    def setupUi(self, AddAssetsDialog):
        AddAssetsDialog.setObjectName(_fromUtf8("AddAssetsDialog"))
        AddAssetsDialog.resize(960, 526)
        font = QtGui.QFont()
        font.setPointSize(11)
        AddAssetsDialog.setFont(font)
        self.buttonBox = QtGui.QDialogButtonBox(AddAssetsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(310, 450, 156, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.cbx_map_layers = QgsMapLayerComboBox(AddAssetsDialog)
        self.cbx_map_layers.setGeometry(QtCore.QRect(214, 45, 246, 27))
        self.cbx_map_layers.setObjectName(_fromUtf8("cbx_map_layers"))
        self.label = QtGui.QLabel(AddAssetsDialog)
        self.label.setGeometry(QtCore.QRect(45, 45, 161, 26))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(AddAssetsDialog)
        self.label_2.setGeometry(QtCore.QRect(45, 100, 161, 26))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.cbx_postgis_tables = QtGui.QComboBox(AddAssetsDialog)
        self.cbx_postgis_tables.setGeometry(QtCore.QRect(215, 101, 246, 26))
        self.cbx_postgis_tables.setObjectName(_fromUtf8("cbx_postgis_tables"))
        self.groupBox = QtGui.QGroupBox(AddAssetsDialog)
        self.groupBox.setGeometry(QtCore.QRect(35, 150, 771, 261))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(30, 40, 681, 41))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cbx_asset_name_field = QgsFieldComboBox(self.groupBox)
        self.cbx_asset_name_field.setGeometry(QtCore.QRect(320, 100, 160, 27))
        self.cbx_asset_name_field.setObjectName(_fromUtf8("cbx_asset_name_field"))
        self.cbx_asset_fma_field = QgsFieldComboBox(self.groupBox)
        self.cbx_asset_fma_field.setGeometry(QtCore.QRect(320, 180, 160, 27))
        self.cbx_asset_fma_field.setObjectName(_fromUtf8("cbx_asset_fma_field"))
        self.cbx_asset_resilience_field = QgsFieldComboBox(self.groupBox)
        self.cbx_asset_resilience_field.setGeometry(QtCore.QRect(320, 220, 160, 27))
        self.cbx_asset_resilience_field.setObjectName(_fromUtf8("cbx_asset_resilience_field"))
        self.cbx_asset_class_field = QgsFieldComboBox(self.groupBox)
        self.cbx_asset_class_field.setGeometry(QtCore.QRect(320, 140, 160, 27))
        self.cbx_asset_class_field.setObjectName(_fromUtf8("cbx_asset_class_field"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(170, 105, 126, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(175, 145, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(175, 185, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(175, 225, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(AddAssetsDialog)
        self.label_8.setGeometry(QtCore.QRect(480, 30, 446, 51))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(AddAssetsDialog)
        self.label_9.setGeometry(QtCore.QRect(480, 90, 461, 51))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_9.setFont(font)
        self.label_9.setWordWrap(True)
        self.label_9.setObjectName(_fromUtf8("label_9"))

        self.retranslateUi(AddAssetsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AddAssetsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddAssetsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddAssetsDialog)

    def retranslateUi(self, AddAssetsDialog):
        AddAssetsDialog.setWindowTitle(_translate("AddAssetsDialog", "Add existing assets data", None))
        self.label.setText(_translate("AddAssetsDialog", "Layer to copy:", None))
        self.label_2.setText(_translate("AddAssetsDialog", "Append to:", None))
        self.groupBox.setTitle(_translate("AddAssetsDialog", "Field Matching", None))
        self.label_3.setText(_translate("AddAssetsDialog", "Select the field from the copy layer which corresponds to the assets database field.  Note that it must be a text field.\n"
"If there is no such field, leave blank:", None))
        self.label_4.setText(_translate("AddAssetsDialog", "asset_name", None))
        self.label_5.setText(_translate("AddAssetsDialog", "asset_class", None))
        self.label_6.setText(_translate("AddAssetsDialog", "fma", None))
        self.label_7.setText(_translate("AddAssetsDialog", "resilience", None))
        self.label_8.setText(_translate("AddAssetsDialog", "<html><head/><body><p>Select the map layer whose data is to be copied and appended to RFMA data.</p></body></html>", None))
        self.label_9.setText(_translate("AddAssetsDialog", "<html><head/><body><p>Select the RFMA layer to which the data will be appended.</p></body></html>", None))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
