# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fma_grouping_selector.ui'
#
# Created: Tue Mar 12 16:10:50 2019
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

class Ui_SelectFMAGroupingDialog(object):
    def setupUi(self, SelectFMAGroupingDialog):
        SelectFMAGroupingDialog.setObjectName(_fromUtf8("SelectFMAGroupingDialog"))
        SelectFMAGroupingDialog.resize(524, 312)
        SelectFMAGroupingDialog.setModal(True)
        self.label = QtGui.QLabel(SelectFMAGroupingDialog)
        self.label.setGeometry(QtCore.QRect(40, 30, 401, 51))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.chk_by_type = QtGui.QCheckBox(SelectFMAGroupingDialog)
        self.chk_by_type.setGeometry(QtCore.QRect(80, 85, 321, 25))
        self.chk_by_type.setObjectName(_fromUtf8("chk_by_type"))
        self.chk_by_priority = QtGui.QCheckBox(SelectFMAGroupingDialog)
        self.chk_by_priority.setGeometry(QtCore.QRect(80, 115, 261, 25))
        self.chk_by_priority.setObjectName(_fromUtf8("chk_by_priority"))
        self.chk_by_type_n_priority = QtGui.QCheckBox(SelectFMAGroupingDialog)
        self.chk_by_type_n_priority.setGeometry(QtCore.QRect(80, 145, 401, 25))
        self.chk_by_type_n_priority.setObjectName(_fromUtf8("chk_by_type_n_priority"))
        self.chk_combine_all = QtGui.QCheckBox(SelectFMAGroupingDialog)
        self.chk_combine_all.setGeometry(QtCore.QRect(80, 175, 361, 25))
        self.chk_combine_all.setObjectName(_fromUtf8("chk_combine_all"))
        self.btn_go = QtGui.QPushButton(SelectFMAGroupingDialog)
        self.btn_go.setGeometry(QtCore.QRect(90, 240, 75, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_go.setFont(font)
        self.btn_go.setObjectName(_fromUtf8("btn_go"))
        self.btn_stop = QtGui.QPushButton(SelectFMAGroupingDialog)
        self.btn_stop.setGeometry(QtCore.QRect(200, 240, 75, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_stop.setFont(font)
        self.btn_stop.setObjectName(_fromUtf8("btn_stop"))

        self.retranslateUi(SelectFMAGroupingDialog)
        QtCore.QMetaObject.connectSlotsByName(SelectFMAGroupingDialog)

    def retranslateUi(self, SelectFMAGroupingDialog):
        SelectFMAGroupingDialog.setWindowTitle(_translate("SelectFMAGroupingDialog", "FMA Grouping", None))
        self.label.setText(_translate("SelectFMAGroupingDialog", "Select FMA layer(s) to create:", None))
        self.chk_by_type.setText(_translate("SelectFMAGroupingDialog", "Categorised by FMA Type only", None))
        self.chk_by_priority.setText(_translate("SelectFMAGroupingDialog", "Categorised by Priority only", None))
        self.chk_by_type_n_priority.setText(_translate("SelectFMAGroupingDialog", "Categorised by both FMA Type and Priority", None))
        self.chk_combine_all.setText(_translate("SelectFMAGroupingDialog", "Combine all (i.e. not split into categories)", None))
        self.btn_go.setText(_translate("SelectFMAGroupingDialog", "OK", None))
        self.btn_stop.setText(_translate("SelectFMAGroupingDialog", "Cancel", None))

