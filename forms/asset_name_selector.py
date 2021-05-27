# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'asset_name_selector.ui'
#
# Created: Mon Apr 19 13:57:05 2021
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

class Ui_AssetNameSelectorDialog(object):
    def setupUi(self, AssetNameSelectorDialog):
        AssetNameSelectorDialog.setObjectName(_fromUtf8("AssetNameSelectorDialog"))
        AssetNameSelectorDialog.resize(512, 532)
        self.buttonBox = QtGui.QDialogButtonBox(AssetNameSelectorDialog)
        self.buttonBox.setGeometry(QtCore.QRect(150, 480, 156, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.listWidget = QtGui.QListWidget(AssetNameSelectorDialog)
        self.listWidget.setGeometry(QtCore.QRect(80, 90, 321, 361))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.label = QtGui.QLabel(AssetNameSelectorDialog)
        self.label.setGeometry(QtCore.QRect(20, 30, 461, 51))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(AssetNameSelectorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AssetNameSelectorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AssetNameSelectorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AssetNameSelectorDialog)

    def retranslateUi(self, AssetNameSelectorDialog):
        AssetNameSelectorDialog.setWindowTitle(_translate("AssetNameSelectorDialog", "Asset layer selector", None))
        self.listWidget.setSortingEnabled(False)
        self.label.setText(_translate("AssetNameSelectorDialog", "Select asset names(s) to show report for:", None))

