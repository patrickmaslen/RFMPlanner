# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_region_assets.ui'
#
# Created: Mon Feb 25 05:34:54 2019
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

class Ui_CreateRegionAssetsDialog(object):
    def setupUi(self, CreatePolyAssetsDialog):
        CreatePolyAssetsDialog.setObjectName(_fromUtf8("CreatePolyAssetsDialog"))
        CreatePolyAssetsDialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(CreatePolyAssetsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(120, 200, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.cbx_regions = QtGui.QComboBox(CreatePolyAssetsDialog)
        self.cbx_regions.setGeometry(QtCore.QRect(130, 100, 141, 22))
        self.cbx_regions.setObjectName(_fromUtf8("cbx_regions"))
        self.label = QtGui.QLabel(CreatePolyAssetsDialog)
        self.label.setGeometry(QtCore.QRect(60, 35, 321, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(CreatePolyAssetsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CreatePolyAssetsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CreatePolyAssetsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CreatePolyAssetsDialog)

    def retranslateUi(self, CreatePolyAssetsDialog):
        CreatePolyAssetsDialog.setWindowTitle(_translate("CreatePolyAssetsDialog", "Create asset layers", None))
        self.label.setText(_translate("CreatePolyAssetsDialog", "Create asset layers for region:", None))

