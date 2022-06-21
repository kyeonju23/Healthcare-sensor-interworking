from ctypes.wintypes import RGB
from operator import index
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pyqtgraph as pg

import sys, json, time


form_class = uic.loadUiType("page.ui")[0]

class MainWindow(QtWidgets.QMainWindow,form_class):
    def __init__(self,*args, **kwargs) :
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.move(0, -1)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.pushButton_e.clicked.connect(QtWidgets.qApp.quit)
        self.pushButton_s.clicked.connect(self.button)
        self.pushButton_save.clicked.connect(self.savebutton)

        self.x_pleth = list(range(300))
        self.y_pleth = [0 for _ in range(300)]
        pen_pleth = pg.mkPen(color=(255, 255, 0))

        self.x_ecg = list(range(300))
        self.y_ecg = [0 for _ in range(300)]
        pen_ecg = pg.mkPen(color=(0, 255, 0))

        self.graphWidget_ECG.getPlotItem().hideAxis('bottom')
        self.graphWidget_ECG.getPlotItem().hideAxis('left')

        self.graphWidget_Pleth.getPlotItem().hideAxis('bottom')
        self.graphWidget_Pleth.getPlotItem().hideAxis('left')

        self.graphWidget_Pleth.setYRange(-10, 10, padding=0)
        self.graphWidget_ECG.setYRange(-40, 40, padding=0)

        self.ecg_data = self.graphWidget_ECG.plot(self.x_ecg,self.y_ecg,pen=pen_ecg)
        self.pleth_data = self.graphWidget_Pleth.plot(self.x_pleth,self.y_pleth,pen=pen_pleth)

        self.show()

    click = 0
    def button(self):
        if self.click == 0:
            self.pushButton_s.setText("STOP")

            self.timer1 = QTimer()
            self.timer1.setInterval(1000)
            self.timer1.timeout.connect(self.update_estimations_data)
            self.timer1.start()

            self.timer2 = QTimer()
            self.timer2.setInterval(10)
            self.timer2.timeout.connect(self.update_pleth_data)
            self.timer2.start()

            self.timer3 = QTimer()
            self.timer3.setInterval(3)
            self.timer3.timeout.connect(self.update_ecg_data)
            self.timer3.start()

            self.click = 1

        else :
            self.pushButton_s.setText("START")
            self.click = 0
            self.timer1.stop()
            self.timer2.stop()
            self.timer3.stop()

    save = 0
    timer4 = QTimer()
    def savebutton(self):
        if self.save == 0:
            self.pushButton_save.setText("END")
            self.fileName = time.strftime('%y%m%d_%H%M%S')

            self.timer4.setInterval(1000)
            self.timer4.timeout.connect(self.save_f)
            self.timer4.start()

            self.save += 1

        else :
            self.pushButton_save.setText("SAVE")
            self.save -= 1
            self.timer4.stop()

    def save_f(self):
        with open ('./save/ECGDATA/'+'ECG_'+self.fileName+'.csv', 'a') as f: 
            with open('waveform_ecg.json', 'r') as file:
                ECG_DATA = json.load(file)['waveform_ecg']
            f.write(str(ECG_DATA)+'\n')
        
        with open ('./save/PlethDATA/'+'Pleth_'+self.fileName+'.csv', 'a') as f:
            with open('waveform_pleth.json', 'r') as file:
                Pleth_DATA = json.load(file)['waveform_pleth']
            f.write(str(Pleth_DATA)+'\n')

        with open ('./save/ESTDATA/'+'EST_'+self.fileName+'.csv', 'a') as f:
            with open('Estimations.json', 'r') as file:
                EST_DATA = json.load(file)
            f.write(str(EST_DATA)+'\n')


    def update_estimations_data(self):
        with open('Estimations.json', 'r') as file:
            data = json.load(file)

        self.label_hr.setText(str(data['HR']))
        self.label_spo2.setText(str(data['SpO2']))
        self.label_nibp_h.setText(str(data['NIBP_H']))
        self.label_nibp_L.setText(str(data['NIBP_L']))
        self.label_nibp_m.setText(str(data['NIBP_M']))
        self.label_t2.setText(str(data['T']))

    index_pleth = 0
    def update_pleth_data(self):
        try:
            with open('waveform_pleth.json', 'r') as file:
                dataList = json.load(file)['waveform_pleth']
        except:
            return

        self.x_pleth = self.x_pleth[1:]
        self.x_pleth.append(self.x_pleth[-1] + 1)
        self.y_pleth = self.y_pleth[1:]
        self.y_pleth.append(dataList[self.index_pleth]) 
        pen_pleth = pg.mkPen(color=(255, 255, 0))

        self.index_pleth += 1

        if self.index_pleth == 100:
            self.index_pleth = 0

        self.pleth_data.setData(self.x_pleth, self.y_pleth, pen=pen_pleth)

    index_ecg = 0
    def update_ecg_data(self):
        try:
            with open('waveform_ecg.json', 'r') as file:
                dataList = json.load(file)['waveform_ecg']
        except:
            return

        self.x_ecg = self.x_ecg[1:]
        self.x_ecg.append(self.x_ecg[-1] + 1)
        self.y_ecg = self.y_ecg[1:]
        self.y_ecg.append(dataList[self.index_ecg])
        pen_ecg = pg.mkPen(color=(0, 255, 0))

        self.index_ecg += 1

        if self.index_ecg == 300:
            self.index_ecg = 0

        self.ecg_data.setData(self.x_ecg,self.y_ecg,pen=pen_ecg)

if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()