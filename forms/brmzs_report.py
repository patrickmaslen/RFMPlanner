# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'brmzs_report.ui'
#
# Created: Mon Jun 10 05:19:12 2019
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

class Ui_BRMZsReportDialog(object):
    def setupUi(self, BRMZsReportDialog):
        BRMZsReportDialog.setObjectName(_fromUtf8("BRMZsReportDialog"))
        BRMZsReportDialog.resize(821, 613)
        self.label = QtGui.QLabel(BRMZsReportDialog)
        self.label.setGeometry(QtCore.QRect(135, 15, 236, 26))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.tbl_brmz_info = QtGui.QTableWidget(BRMZsReportDialog)
        self.tbl_brmz_info.setGeometry(QtCore.QRect(25, 50, 771, 501))
        self.tbl_brmz_info.setColumnCount(7)
        self.tbl_brmz_info.setObjectName(_fromUtf8("tbl_brmz_info"))
        self.tbl_brmz_info.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tbl_brmz_info.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_brmz_info.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_brmz_info.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_brmz_info.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_brmz_info.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_brmz_info.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_brmz_info.setHorizontalHeaderItem(6, item)
        self.tbl_brmz_info.horizontalHeader().setDefaultSectionSize(105)
        self.btn_close = QtGui.QPushButton(BRMZsReportDialog)
        self.btn_close.setGeometry(QtCore.QRect(250, 580, 75, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_close.setFont(font)
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.btn_csv = QtGui.QPushButton(BRMZsReportDialog)
        self.btn_csv.setGeometry(QtCore.QRect(370, 580, 116, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_csv.setFont(font)
        self.btn_csv.setObjectName(_fromUtf8("btn_csv"))

        self.retranslateUi(BRMZsReportDialog)
        QtCore.QMetaObject.connectSlotsByName(BRMZsReportDialog)

    def retranslateUi(self, BRMZsReportDialog):
        BRMZsReportDialog.setWindowTitle(_translate("BRMZsReportDialog", "BRMZs Report", None))
        self.label.setText(_translate("BRMZsReportDialog", "Bushfire Risk Zones Report", None))
        item = self.tbl_brmz_info.horizontalHeaderItem(0)
        item.setText(_translate("BRMZsReportDialog", "Zone", None))
        item = self.tbl_brmz_info.horizontalHeaderItem(1)
        item.setText(_translate("BRMZsReportDialog", "Region", None))
        item = self.tbl_brmz_info.horizontalHeaderItem(2)
        item.setText(_translate("BRMZsReportDialog", "Fuel types", None))
        item = self.tbl_brmz_info.horizontalHeaderItem(3)
        item.setText(_translate("BRMZsReportDialog", "Total FMA ha", None))
        item = self.tbl_brmz_info.horizontalHeaderItem(4)
        item.setText(_translate("BRMZsReportDialog", "Area > t\'hold", None))
        item = self.tbl_brmz_info.horizontalHeaderItem(5)
        item.setText(_translate("BRMZsReportDialog", "% below t\'hold", None))
        item = self.tbl_brmz_info.horizontalHeaderItem(6)
        item.setText(_translate("BRMZsReportDialog", "Target", None))
        self.btn_close.setText(_translate("BRMZsReportDialog", "Close", None))
        self.btn_csv.setText(_translate("BRMZsReportDialog", "Export csv", None))

