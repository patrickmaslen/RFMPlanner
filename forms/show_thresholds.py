# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'show_thresholds.ui'
#
# Created: Thu Aug 06 12:32:04 2020
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

class Ui_ListThresholdsDialog(object):
    def setupUi(self, ListThresholdsDialog):
        ListThresholdsDialog.setObjectName(_fromUtf8("ListThresholdsDialog"))
        ListThresholdsDialog.resize(944, 741)
        self.lbl_title = QtGui.QLabel(ListThresholdsDialog)
        self.lbl_title.setGeometry(QtCore.QRect(90, 40, 721, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_title.setObjectName(_fromUtf8("lbl_title"))
        self.btn_close = QtGui.QPushButton(ListThresholdsDialog)
        self.btn_close.setGeometry(QtCore.QRect(380, 680, 112, 34))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_close.setFont(font)
        self.btn_close.setDefault(True)
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.tbl_thresholds = QtGui.QTableWidget(ListThresholdsDialog)
        self.tbl_thresholds.setGeometry(QtCore.QRect(70, 110, 801, 501))
        self.tbl_thresholds.setColumnCount(7)
        self.tbl_thresholds.setObjectName(_fromUtf8("tbl_thresholds"))
        self.tbl_thresholds.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tbl_thresholds.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_thresholds.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_thresholds.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_thresholds.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_thresholds.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_thresholds.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_thresholds.setHorizontalHeaderItem(6, item)
        self.label = QtGui.QLabel(ListThresholdsDialog)
        self.label.setGeometry(QtCore.QRect(100, 630, 711, 21))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(ListThresholdsDialog)
        QtCore.QMetaObject.connectSlotsByName(ListThresholdsDialog)

    def retranslateUi(self, ListThresholdsDialog):
        ListThresholdsDialog.setWindowTitle(_translate("ListThresholdsDialog", "Thresholds and Targets", None))
        self.lbl_title.setText(_translate("ListThresholdsDialog", "Indicative fuel age thresholds", None))
        self.btn_close.setText(_translate("ListThresholdsDialog", "Close", None))
        self.tbl_thresholds.setSortingEnabled(True)
        item = self.tbl_thresholds.horizontalHeaderItem(0)
        item.setText(_translate("ListThresholdsDialog", "Fuel type", None))
        item = self.tbl_thresholds.horizontalHeaderItem(1)
        item.setText(_translate("ListThresholdsDialog", "Threshold age", None))
        item = self.tbl_thresholds.horizontalHeaderItem(2)
        item.setText(_translate("ListThresholdsDialog", "SHS Target", None))
        item = self.tbl_thresholds.horizontalHeaderItem(3)
        item.setText(_translate("ListThresholdsDialog", "CIB Target", None))
        item = self.tbl_thresholds.horizontalHeaderItem(4)
        item.setText(_translate("ListThresholdsDialog", "LRR Target", None))
        item = self.tbl_thresholds.horizontalHeaderItem(5)
        item.setText(_translate("ListThresholdsDialog", "Update", None))
        item = self.tbl_thresholds.horizontalHeaderItem(6)
        item.setText(_translate("ListThresholdsDialog", "+Exception (spatial)", None))
        self.label.setText(_translate("ListThresholdsDialog", "Values of -1 indicate there is no threshold age / target set for that fuel type / FMA combination", None))

