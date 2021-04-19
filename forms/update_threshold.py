# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'update_threshold.ui'
#
# Created: Thu Jul 30 15:50:34 2020
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

class Ui_UpdateThresholdDialog(object):
    def setupUi(self, UpdateThresholdDialog):
        UpdateThresholdDialog.setObjectName(_fromUtf8("UpdateThresholdDialog"))
        UpdateThresholdDialog.resize(580, 319)
        self.buttonBox = QtGui.QDialogButtonBox(UpdateThresholdDialog)
        self.buttonBox.setGeometry(QtCore.QRect(130, 250, 231, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.txt_fuel = QtGui.QLineEdit(UpdateThresholdDialog)
        self.txt_fuel.setGeometry(QtCore.QRect(160, 30, 321, 27))
        self.txt_fuel.setObjectName(_fromUtf8("txt_fuel"))
        self.txt_thold_age = QtGui.QLineEdit(UpdateThresholdDialog)
        self.txt_thold_age.setGeometry(QtCore.QRect(160, 70, 113, 27))
        self.txt_thold_age.setObjectName(_fromUtf8("txt_thold_age"))
        self.txt_shs_target = QtGui.QLineEdit(UpdateThresholdDialog)
        self.txt_shs_target.setGeometry(QtCore.QRect(160, 110, 113, 27))
        self.txt_shs_target.setObjectName(_fromUtf8("txt_shs_target"))
        self.label = QtGui.QLabel(UpdateThresholdDialog)
        self.label.setGeometry(QtCore.QRect(40, 30, 70, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_3 = QtGui.QLabel(UpdateThresholdDialog)
        self.label_3.setGeometry(QtCore.QRect(40, 110, 101, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(UpdateThresholdDialog)
        self.label_4.setGeometry(QtCore.QRect(40, 70, 111, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.txt_cib_target = QtGui.QLineEdit(UpdateThresholdDialog)
        self.txt_cib_target.setGeometry(QtCore.QRect(160, 150, 113, 27))
        self.txt_cib_target.setObjectName(_fromUtf8("txt_cib_target"))
        self.label_5 = QtGui.QLabel(UpdateThresholdDialog)
        self.label_5.setGeometry(QtCore.QRect(40, 150, 91, 21))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.txt_lrr_target = QtGui.QLineEdit(UpdateThresholdDialog)
        self.txt_lrr_target.setGeometry(QtCore.QRect(160, 190, 113, 27))
        self.txt_lrr_target.setObjectName(_fromUtf8("txt_lrr_target"))
        self.label_6 = QtGui.QLabel(UpdateThresholdDialog)
        self.label_6.setGeometry(QtCore.QRect(40, 190, 91, 21))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.textBrowser = QtGui.QTextBrowser(UpdateThresholdDialog)
        self.textBrowser.setGeometry(QtCore.QRect(310, 100, 231, 121))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))

        self.retranslateUi(UpdateThresholdDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), UpdateThresholdDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UpdateThresholdDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UpdateThresholdDialog)

    def retranslateUi(self, UpdateThresholdDialog):
        UpdateThresholdDialog.setWindowTitle(_translate("UpdateThresholdDialog", "Dialog", None))
        self.label.setText(_translate("UpdateThresholdDialog", "fuel_type", None))
        self.label_3.setText(_translate("UpdateThresholdDialog", "SHS target", None))
        self.label_4.setText(_translate("UpdateThresholdDialog", "threshold_age", None))
        self.label_5.setText(_translate("UpdateThresholdDialog", "CIB target", None))
        self.label_6.setText(_translate("UpdateThresholdDialog", "LRR target", None))
        self.textBrowser.setHtml(_translate("UpdateThresholdDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Change threshold_age and/or </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">one or more targets.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Then click OK to start using </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">QGIS to create a polygon</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">with these attributes.</span></p></body></html>", None))

