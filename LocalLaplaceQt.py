from PyQt5 import QtGui, QtCore, QtWidgets, QtSql
import datetime
import sys
import ctypes

import LocalLaplaceOpenCVQtUi
from LocalLaplaceImageConverter import LocalLaplaceImageConverter
from ImageQualityEvaluator import ImageQualityEvaluator


class MainWindow(QtWidgets.QMainWindow, LocalLaplaceOpenCVQtUi.Ui_LocalLaplaceOpenCVQtClass):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.DIALMAX = 400
        self.DIALMIN = 0
        self.DIALINITVALUE = 500
        self.LCDINITVALUE = 1.0
        self.LCDDIGITSCOUNT = 5
        self.DIALLCDREL = 100
        self.SETTINGSFILE = "LocalLaplaceOpenCVQt.ini"
        self.DBNAME = "LocalLaplaceOpenCVQt2.db3"
        self.kSigmaR = 0.8
        self.kAlpha = 0.2
        self.kBeta = 0.5
        self.inputFileName = ""
        self.ostatnioOtwieraneMax = 4
        self.ostatnioOtwieraneActions = []
        self.pixmapObrazWejsciowy = QtGui.QPixmap()
        self.pixmapObrazWyjsciowy = QtGui.QPixmap()
        self.sliderScale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.skalaObrazuWejsciowego = 100
        self.LPLevels = 0
        self.timer = QtCore.QElapsedTimer()
        self.timertotal = QtCore.QElapsedTimer()
        self.db = QtSql.QSqlDatabase()
        self.dbOpenOk = False
        self.setWindowIcon(QtGui.QIcon('LocalLaplaceOpenCVQtPy.ico'))
        self.setupUi(self)
        self.groupScale.setLayout(self.create_slider_skalowanie())
        self.sliderScale.valueChanged.connect(self.slider_scale_value_changed)
        self.actionOtworz.triggered.connect(self.otworz_plik_wejsciowy)
        self.actionZapiszSesje.triggered.connect(self.action_zapisz_sesje_triggered)
        self.wowe = None
        self.actionWyjscie.triggered.connect(self.show_wyjscie)
        self.wwy = None
        self.quality_results = {'BRISQUE': None, 'MSE': None, 'PSNR': None, 'SSIM': None, 'GMSD': None}
        # self.quality_maps = {'MSE': None, 'PSNR': None, 'SSIM': None, 'GMSD': None}
        self.dialAlpha.setNotchesVisible(True)
        self.dialAlpha.setMaximum(self.DIALMAX)
        self.dialAlpha.setMinimum(self.DIALMIN)
        self.dialAlpha.setValue(self.DIALINITVALUE)
        self.lcdNumberAlpha.display(self.LCDINITVALUE)
        self.lcdNumberAlpha.setNumDigits(self.LCDDIGITSCOUNT)
        self.dialAlpha.valueChanged.connect(self.wyswietl_lcd_alpha)
        self.dialBeta.setNotchesVisible(True)
        self.dialBeta.setMaximum(self.DIALMAX)
        self.dialBeta.setMinimum(self.DIALMIN)
        self.dialBeta.setValue(self.DIALINITVALUE)
        self.lcdNumberBeta.display(self.LCDINITVALUE)
        self.lcdNumberBeta.setNumDigits(self.LCDDIGITSCOUNT)
        self.dialBeta.valueChanged.connect(self.wyswietl_lcd_beta)
        self.dialSigmaR.setNotchesVisible(True)
        self.dialSigmaR.setMaximum(self.DIALMAX)
        self.dialSigmaR.setMinimum(self.DIALMIN)
        self.dialSigmaR.setValue(self.DIALINITVALUE)
        self.lcdNumberSigmaR.display(self.LCDINITVALUE)
        self.lcdNumberSigmaR.setNumDigits(self.LCDDIGITSCOUNT)
        self.dialSigmaR.valueChanged.connect(self.wyswietl_lcd_sigmar)
        self.pushButtonDefault.clicked.connect(self.push_button_default_clicked)
        self.pushButtonApply.clicked.connect(self.push_button_apply_clicked)
        self.InitOstatnioOtwierane()
        self.InitDB()

    def create_slider_skalowanie(self):
        self.sliderScale.setRange(1, 4)
        self.sliderScale.setSingleStep(1)
        self.sliderScale.setValue(4)
        label1 = QtWidgets.QLabel("25%")
        label2 = QtWidgets.QLabel("50%")
        label3 = QtWidgets.QLabel("75%")
        label4 = QtWidgets.QLabel("100%")
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.sliderScale, 0, 0, 1, 4)
        layout.addWidget(label1, 1, 0, 1, 1)
        layout.addWidget(label2, 1, 1, 1, 1)
        layout.addWidget(label3, 1, 2, 1, 1)
        layout.addWidget(label4, 1, 3, 1, 1)
        return layout

    def wyswietl_lcd_alpha(self):
        floatval = float(float(self.dialAlpha.value()) / self.DIALLCDREL)
        self.lcdNumberAlpha.display(floatval)
        self.kAlpha = floatval

    def wyswietl_lcd_beta(self):
        floatval = float(float(self.dialBeta.value()) / self.DIALLCDREL)
        self.lcdNumberBeta.display(floatval)
        self.kBeta = floatval

    def wyswietl_lcd_sigmar(self):
        floatval = float(float(self.dialSigmaR.value()) / self.DIALLCDREL)
        self.lcdNumberSigmaR.display(floatval)
        self.kSigmaR = floatval

    def slider_scale_value_changed(self):
        self.skalaObrazuWejsciowego = self.sliderScale.value() * 25

    def push_button_default_clicked(self):
        settings = QtCore.QSettings(self.SETTINGSFILE, QtCore.QSettings.IniFormat)
        self.setControls(settings)

    def image_converter_info_received(self, value: int):
        QtCore.qDebug("Hello z " + str(QtCore.QThread.currentThread()) + " Value " + str(value))
        self.logArea.appendPlainText("LPLevel: " + str(value) + "\t" + str(self.timer.elapsed()) + " ms")
        self.timer.restart()
        self.logArea.repaint()
        QtWidgets.QApplication.processEvents()

    def image_converter_start_info_received(self, value: int):
        self.LPLevels = value
        self.logArea.appendPlainText("Number of LP_Level: " + str(value))
        self.logArea.repaint()
        QtWidgets.QApplication.processEvents()

    def push_button_apply_clicked(self):
        if self.inputFileName:
            self.labelObrazWyjsciowy.repaint()
            self.labelObrazWyjsciowy.clear()
            self.logArea.appendPlainText("_____ Session starts  _____")
            self.logArea.repaint()
            self.timer.start()
            self.timertotal.start()
            ic = LocalLaplaceImageConverter(self.kAlpha, self.kBeta, self.kSigmaR, self.inputFileName,
                                            self.skalaObrazuWejsciowego)
            ic.sendInfoFromConverter.connect(self.image_converter_info_received, QtCore.Qt.DirectConnection)
            ic.sendStartInfoFromConverter.connect(self.image_converter_start_info_received, QtCore.Qt.DirectConnection)
            ic.start()
            ic.LocalLaplaceImageProcessor()
            ic.quit()
            self.pixmapObrazWyjsciowy = QtGui.QPixmap("output.png")
            pixmap = self.pixmapObrazWyjsciowy.scaled(self.labelObrazWyjsciowy.size(), QtCore.Qt.KeepAspectRatio)
            self.labelObrazWyjsciowy.setPixmap(pixmap)
            self.logArea.appendPlainText("Total time: " + str(self.timertotal.elapsed()) + " ms")
            self.generateImageQualityStats()

    def generateImageQualityStats(self):
        if self.comboBoxImageQuality.currentIndex() > 0:
            iqe = ImageQualityEvaluator("models/brisque_model_live.yml", "models/brisque_range_live.yml",
                                        self.inputFileName, "output.png", self.skalaObrazuWejsciowego)
            self.quality_results = iqe.generateResults(self.comboBoxImageQuality.currentIndex())

            for key in self.quality_results.keys():
                if self.quality_results[key] is not None and key == 'BRISQUE':

                    self.labelWartoscBrisque.setText(str(self.quality_results[key]))
                if self.quality_results[key] is not None and key == 'MSE':

                    self.labelWartoscMSE.setText(str(self.quality_results[key]))

                if self.quality_results[key] is not None and key == 'PSNR':

                    self.labelWartoscPSNR.setText(str(self.quality_results[key]))

                if self.quality_results[key] is not None and key == 'SSIM':

                    self.labelWartoscSSIM.setText(str(self.quality_results[key]))

                if self.quality_results[key] is not None and key == 'GMSD':

                    self.labelWartoscGMSD.setText(str(self.quality_results[key]))

    def setControls(self, settings: QtCore.QSettings):
        self.kAlpha = float(settings.value('Alpha'))
        self.dialAlpha.setValue(int(self.kAlpha * float(self.DIALLCDREL)))
        self.kBeta = float(settings.value('Beta'))
        self.dialBeta.setValue(int(self.kBeta * float(self.DIALLCDREL)))
        self.kSigmaR = float(settings.value('SigmaR'))
        self.dialSigmaR.setValue(int(self.kSigmaR * float(self.DIALLCDREL)))

    def resizeEvent(self, event):
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def OpenRecentFile(self):
        action = self.sender()
        if action:
            self.inputFileName = action.data()
            self.openFile(action.data())

    def updateMenus(self, size, ostatnioOtwieranePaths: []):
        self.menuOstatnioOtwietane.actions().clear()
        self.menuOstatnioOtwietane.clear()
        self.ostatnioOtwieraneActions.clear()
        for i in range(0, size, 1):
            oOAction = QtWidgets.QAction(self.menuOstatnioOtwietane)
            oOAction.setVisible(False)
            oOAction.triggered.connect(self.OpenRecentFile)
            strippedName = QtCore.QFileInfo(ostatnioOtwieranePaths[i]).fileName()
            oOAction.setText(strippedName)
            oOAction.setData(ostatnioOtwieranePaths[i])
            oOAction.setVisible(True)
            self.ostatnioOtwieraneActions.append(oOAction)
            self.menuOstatnioOtwietane.addAction(self.ostatnioOtwieraneActions[i])
        self.menuOstatnioOtwietane.update()
        if size == 0:
            self.menuOstatnioOtwietane.menuAction().setVisible(False)

    def updateSettings(self, filePath):
        settings = QtCore.QSettings(self.SETTINGSFILE, QtCore.QSettings.IniFormat)
        ostatnioOtwieranePaths = settings.value('ostatnioOtwierane', [], str)
        ostatnioOtwieranePaths = list(filter(lambda a: a != filePath, ostatnioOtwieranePaths))
        ostatnioOtwieranePaths.insert(0, filePath)
        while len(ostatnioOtwieranePaths) > self.ostatnioOtwieraneMax:
            del ostatnioOtwieranePaths[-1]
        settings.setValue('ostatnioOtwierane', ostatnioOtwieranePaths)
        self.updateMenus(len(ostatnioOtwieranePaths), ostatnioOtwieranePaths)
        if not self.menuOstatnioOtwietane.menuAction().isVisible():
            self.menuOstatnioOtwietane.menuAction().setVisible(True)

    def openFile(self, fileName):
        pixmap = QtGui.QPixmap(fileName)
        pixmap = pixmap.scaled(self.labelObrazWejsciowy.size(), QtCore.Qt.KeepAspectRatio)
        self.labelObrazWejsciowy.setPixmap(pixmap)

        self.inputFileName = fileName
        self.updateSettings(fileName)

    def otworz_plik_wejsciowy(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setWindowTitle("Select input file")
        dlg.setDirectory('.\\')
        dlg.setNameFilters(["Jpg (*.jpg)", "Png (*.png)", "Bmp (*.bmp)", "All files (*)"])
        filenames = None
        if dlg.exec_():
            filenames = dlg.selectedFiles()
        if filenames:
            self.openFile(filenames[0])
        else:
            self.inputFileName = ""

    def InitOstatnioOtwierane(self):
        settings = QtCore.QSettings(self.SETTINGSFILE, QtCore.QSettings.IniFormat)
        ostatnioOtwieranePaths = settings.value("ostatnioOtwierane", [], str)
        itEnd = 0
        if len(ostatnioOtwieranePaths) <= self.ostatnioOtwieraneMax:
            itEnd = len(ostatnioOtwieranePaths)
        else:
            itEnd = self.ostatnioOtwieraneMax
        self.updateMenus(itEnd, ostatnioOtwieranePaths)

    def show_wyjscie(self):
        quit_msg = "Do you want to quit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Quit', quit_msg, QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            sys.exit(0)

    def action_zapisz_sesje_triggered(self):
        res = QtWidgets.QMessageBox.question(self, 'Zapis aktualnej sesji', 'Czy zapisać aktualną sesję?',
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if res == QtWidgets.QMessageBox.Yes and self.labelObrazWyjsciowy.pixmap is not None:
            opis = QtWidgets.QInputDialog.getMultiLineText(self, 'Opis aktualnej sesji',
                                                           'Wprowadź opis aktualnej sesji')
            inByteArray = QtCore.QByteArray()
            inBuffer = QtCore.QBuffer(inByteArray)
            inBuffer.open(QtCore.QIODevice.WriteOnly)

            self.labelObrazWyjsciowy.pixmap().save(inBuffer, 'png')

            inByteArrayMSE = QtCore.QByteArray()
            if self.quality_results['MSE'] is not None:
                inBufferMSE = QtCore.QBuffer(inByteArrayMSE)
                inBufferMSE.open(QtCore.QIODevice.WriteOnly)


            inByteArrayPSNR = QtCore.QByteArray()
            if self.quality_results['PSNR'] is not None:
                inBufferPSNR = QtCore.QBuffer(inByteArrayPSNR)
                inBufferPSNR.open(QtCore.QIODevice.WriteOnly)


            inByteArraySSIM = QtCore.QByteArray()
            if self.quality_results['SSIM'] is not None:
                inBufferSSIM = QtCore.QBuffer(inByteArraySSIM)
                inBufferSSIM.open(QtCore.QIODevice.WriteOnly)


            inByteArrayGMSD = QtCore.QByteArray()
            if self.quality_results['GMSD'] is not None:
                inBufferGMSD = QtCore.QBuffer(inByteArrayGMSD)
                inBufferGMSD.open(QtCore.QIODevice.WriteOnly)


            now_time = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

            query = QtSql.QSqlQuery(self.db)
            query.prepare("INSERT INTO Sesje (opis, timestamp, Alpha , Beta, SigmaR, skala, brisque, mse, psnr, ssim,"
                          " gmsd, plikWejsciowy, LPLevels, obrazWyjsciowy) "
                          "VALUES (:opis, :timestamp, :Alpha, :Beta, :SigmaR, :skala, :brisque, :mse, :psnr, :ssim,"
                          ":gmsd,"" :plikWejsciowy, :LPLevels, :obrazWyjsciowy)")
            query.bindValue(":opis", opis[0])
            query.bindValue(":timestamp", now_time)
            query.bindValue(":Alpha", self.kAlpha)
            query.bindValue(":Beta", self.kBeta)
            query.bindValue(":SigmaR", self.kSigmaR)
            query.bindValue(":skala", str(self.skalaObrazuWejsciowego))
            query.bindValue(":brisque", str(self.quality_results['BRISQUE']))
            query.bindValue(":mse", str(self.quality_results['MSE']))
            query.bindValue(":psnr", str(self.quality_results['PSNR']))
            query.bindValue(":ssim", str(self.quality_results['SSIM']))
            query.bindValue(":gmsd", str(self.quality_results['GMSD']))
            query.bindValue(":plikWejsciowy", self.inputFileName)
            query.bindValue(":LPLevels", self.LPLevels)
            query.bindValue(":obrazWyjsciowy", inByteArray)
            # if self.quality_results['MSE'] is not None:
            #     query.bindValue(":msemap", inByteArrayMSE)
            # if self.quality_results['PSNR'] is not None:
            #     query.bindValue(":psnrmap", inByteArrayPSNR)
            # if self.quality_results['SSIM'] is not None:
            #     query.bindValue(":ssimmap", inByteArraySSIM)
            # if self.quality_results['GMSD'] is not None:
            #     query.bindValue(":gmsdmap", inByteArrayGMSD)
            if query.exec_() is None:
                QtCore.qDebug("Error : Save data to session:\n" + query.lastError())
            else:
                QtCore.qDebug("Sucess : Save data to session\n")

    def InitDB(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.DBNAME)
        if not self.db.open():
            QtCore.qDebug("Error: DB Connection Error")
        else:
            QtCore.qDebug("DB: Connection OK")
            self.dbOpenOk = True
            query = QtSql.QSqlQuery(self.db)
            query.exec("CREATE TABLE IF NOT EXISTS Sesje ( SesjaID integer primary key, opis TEXT,timestamp TEXT,"
                       " Alpha REAL, Beta REAL, SigmaR REAL, skala TEXT, brisque TEXT, mse TEXT, psnr TEXT, ssim TEXT,"
                       " gmsd TEXT, plikWejsciowy TEXT,LPLevels INTEGER, obrazWyjsciowy BLOB)")


def main():
    myappid = 'KSSoft.LocalLaplace.LocalLaplaceImageConverter.1'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QtWidgets.QApplication(sys.argv)
    locale = QtCore.QLocale.system().name()
    qt_translator = QtCore.QTranslator()
    if qt_translator.load("qt_"+locale):
        app.installTranslator(qt_translator)
    form = MainWindow()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
