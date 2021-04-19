# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_record.ui'
#
# Created: Mon Mar 25 05:38:30 2019
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

class Ui_EditFMAsDialog(object):
    def setupUi(self, EditFMAsDialog):
        EditFMAsDialog.setObjectName(_fromUtf8("EditFMAsDialog"))
        EditFMAsDialog.resize(569, 363)
        self.label = QtGui.QLabel(EditFMAsDialog)
        self.label.setGeometry(QtCore.QRect(80, 40, 70, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.txt_gid = QtGui.QLineEdit(EditFMAsDialog)
        self.txt_gid.setGeometry(QtCore.QRect(190, 40, 113, 27))
        self.txt_gid.setReadOnly(True)
        self.txt_gid.setObjectName(_fromUtf8("txt_gid"))
        self.label_2 = QtGui.QLabel(EditFMAsDialog)
        self.label_2.setGeometry(QtCore.QRect(80, 130, 70, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.cbx_fma = QtGui.QComboBox(EditFMAsDialog)
        self.cbx_fma.setGeometry(QtCore.QRect(190, 130, 211, 27))
        self.cbx_fma.setObjectName(_fromUtf8("cbx_fma"))
        self.label_3 = QtGui.QLabel(EditFMAsDialog)
        self.label_3.setGeometry(QtCore.QRect(80, 80, 101, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.txt_asset_name = QtGui.QLineEdit(EditFMAsDialog)
        self.txt_asset_name.setGeometry(QtCore.QRect(190, 80, 211, 27))
        self.txt_asset_name.setObjectName(_fromUtf8("txt_asset_name"))
        self.cbx_asset_class = QtGui.QComboBox(EditFMAsDialog)
        self.cbx_asset_class.setGeometry(QtCore.QRect(190, 180, 211, 27))
        self.cbx_asset_class.setObjectName(_fromUtf8("cbx_asset_class"))
        self.label_4 = QtGui.QLabel(EditFMAsDialog)
        self.label_4.setGeometry(QtCore.QRect(80, 180, 101, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(EditFMAsDialog)
        self.label_5.setGeometry(QtCore.QRect(80, 230, 101, 21))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.cbx_resilience = QtGui.QComboBox(EditFMAsDialog)
        self.cbx_resilience.setGeometry(QtCore.QRect(190, 230, 211, 27))
        self.cbx_resilience.setObjectName(_fromUtf8("cbx_resilience"))
        self.btn_ok = QtGui.QPushButton(EditFMAsDialog)
        self.btn_ok.setGeometry(QtCore.QRect(110, 300, 112, 34))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_ok.setFont(font)
        self.btn_ok.setDefault(True)
        self.btn_ok.setObjectName(_fromUtf8("btn_ok"))
        self.btn_cancel = QtGui.QPushButton(EditFMAsDialog)
        self.btn_cancel.setGeometry(QtCore.QRect(290, 300, 112, 34))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_cancel.setFont(font)
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))

        self.retranslateUi(EditFMAsDialog)
        QtCore.QMetaObject.connectSlotsByName(EditFMAsDialog)

    def retranslateUi(self, EditFMAsDialog):
        EditFMAsDialog.setWindowTitle(_translate("EditFMAsDialog", "Dialog", None))
        self.label.setText(_translate("EditFMAsDialog", "ID (gid)", None))
        self.label_2.setText(_translate("EditFMAsDialog", "fma", None))
        self.label_3.setText(_translate("EditFMAsDialog", "asset_name", None))
        self.label_4.setText(_translate("EditFMAsDialog", "asset_class", None))
        self.label_5.setText(_translate("EditFMAsDialog", "resilience", None))
        self.btn_ok.setText(_translate("EditFMAsDialog", "OK", None))
        self.btn_cancel.setText(_translate("EditFMAsDialog", "Cancel", None))

