# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'region_report.ui'
#
# Created: Tue Aug 04 11:07:16 2020
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

class Ui_SingleRegionReportDialog(object):
    def setupUi(self, SingleRegionReportDialog):
        SingleRegionReportDialog.setObjectName(_fromUtf8("SingleRegionReportDialog"))
        SingleRegionReportDialog.resize(1217, 569)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SingleRegionReportDialog.sizePolicy().hasHeightForWidth())
        SingleRegionReportDialog.setSizePolicy(sizePolicy)
        SingleRegionReportDialog.setMinimumSize(QtCore.QSize(808, 0))
        SingleRegionReportDialog.setModal(False)
        self.label = QtGui.QLabel(SingleRegionReportDialog)
        self.label.setGeometry(QtCore.QRect(135, 25, 641, 26))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.tbl_fma_type = QtGui.QTableWidget(SingleRegionReportDialog)
        self.tbl_fma_type.setGeometry(QtCore.QRect(55, 95, 1111, 351))
        self.tbl_fma_type.setColumnCount(9)
        self.tbl_fma_type.setObjectName(_fromUtf8("tbl_fma_type"))
        self.tbl_fma_type.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_fma_type.setHorizontalHeaderItem(8, item)
        self.tbl_fma_type.horizontalHeader().setDefaultSectionSize(85)
        self.btn_close = QtGui.QPushButton(SingleRegionReportDialog)
        self.btn_close.setGeometry(QtCore.QRect(455, 490, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_close.setFont(font)
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.btn_csv = QtGui.QPushButton(SingleRegionReportDialog)
        self.btn_csv.setGeometry(QtCore.QRect(580, 490, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_csv.setFont(font)
        self.btn_csv.setObjectName(_fromUtf8("btn_csv"))
        self.cbx_districts = QtGui.QComboBox(SingleRegionReportDialog)
        self.cbx_districts.setGeometry(QtCore.QRect(140, 60, 211, 27))
        self.cbx_districts.setObjectName(_fromUtf8("cbx_districts"))

        self.retranslateUi(SingleRegionReportDialog)
        QtCore.QMetaObject.connectSlotsByName(SingleRegionReportDialog)

    def retranslateUi(self, SingleRegionReportDialog):
        SingleRegionReportDialog.setWindowTitle(_translate("SingleRegionReportDialog", "Region Report", None))
        self.label.setText(_translate("SingleRegionReportDialog", "Region Report", None))
        item = self.tbl_fma_type.horizontalHeaderItem(0)
        item.setText(_translate("SingleRegionReportDialog", "FMA type", None))
        item = self.tbl_fma_type.horizontalHeaderItem(1)
        item.setText(_translate("SingleRegionReportDialog", "Fuel types", None))
        item = self.tbl_fma_type.horizontalHeaderItem(2)
        item.setText(_translate("SingleRegionReportDialog", "Area (ha)", None))
        item = self.tbl_fma_type.horizontalHeaderItem(3)
        item.setText(_translate("SingleRegionReportDialog", "Area >= t\'hold", None))
        item = self.tbl_fma_type.horizontalHeaderItem(4)
        item.setText(_translate("SingleRegionReportDialog", "% below t\'hold", None))
        item = self.tbl_fma_type.horizontalHeaderItem(5)
        item.setText(_translate("SingleRegionReportDialog", "Target", None))
        item = self.tbl_fma_type.horizontalHeaderItem(6)
        item.setText(_translate("SingleRegionReportDialog", "Burn needed", None))
        item = self.tbl_fma_type.horizontalHeaderItem(7)
        item.setText(_translate("SingleRegionReportDialog", "Show all fuel", None))
        item = self.tbl_fma_type.horizontalHeaderItem(8)
        item.setText(_translate("SingleRegionReportDialog", "Show overage fuel", None))
        self.btn_close.setText(_translate("SingleRegionReportDialog", "Close", None))
        self.btn_csv.setText(_translate("SingleRegionReportDialog", "Export csv", None))

