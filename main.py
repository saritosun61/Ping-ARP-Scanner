from PyQt5.QtWidgets import *
from scanner import *
import sys
import socket
import requests
import subprocess
import os
from PyQt5.QtCore import QThread, pyqtSignal
import psutil

class PingScan(QThread):
    update_ping_label = pyqtSignal(str)
    update_ping_progressbar = pyqtSignal(int)
    update_ping_listwidget = pyqtSignal(str)
    def __init__(self,ip):
        super().__init__()
        self.ip = ip
    def run(self):
        for i in range(1,255):
            if os.system(f"ping -n 1 {self.ip}{str(i)}"):
                #self.ui.listWidget_ip.addItem()
                self.update_ping_listwidget.emit(self.ip+str(i))
            #self.ui.label_taranan_IP.setText()
            self.update_ping_label.emit(self.ip+str(i))
            #self.ui.progressBar_ip.setValue()
            self.update_ping_progressbar.emit(int((i/255)*100))
class ArpScan(QThread):
    update_arp_label = pyqtSignal(str)
    update_arp_progressbar = pyqtSignal(int)
    update_arp_listwidget = pyqtSignal(str)    
    def __init__(self,ip):
        super().__init__()
        self.ip = ip
    def run(self):
        for i in range(1,256):
            a = os.popen(f"arp -a {self.ip}{str(i)}").read().splitlines()
            if len(a)>=3:
                a = a[3].split(" ")[2]
                #self.ui.listWidget_ip.addItem()
                self.update_arp_listwidget.emit(a)
            #self.ui.label_taranan_IP.setText()
            self.update_arp_label.emit(self.ip + str(i))
            #self.ui.progressBar_ip.setText()
            self.update_arp_progressbar.emit(int((i/255)*100))
class PortScan(QThread):
    update_port_label = pyqtSignal(str)
    update_port_progressbar = pyqtSignal(int)
    update_port_listwidget = pyqtSignal(str)
    def __init__(self,ip,a,b):
        super().__init__()
        self.ip = ip
        self.a = a
        self.b = b
    def run(self):
        for i in range(self.a,self.b+1):
            soket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            #self.ui.label_taranan_Port.setText()
            self.update_port_label.emit(str(i))
            #self.ui.progressBar_port.setValue()
            self.update_port_progressbar.emit(int(((i-self.a)/(self.b-self.a))*100))
            if soket.connect_ex((self.ip,i)) == 0:
                servis = socket.getservbyport(i)
                #self.ui.listWidget_acik_port.addItem()
                self.update_port_listwidget.emit(str(i)+"   "+str(servis))
            soket.close()


class Scanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_cikis.clicked.connect(self.cikis)
        self.mevcut_network()
        self.ui.listWidget_network.currentTextChanged.connect(lambda: self.ui.label_secilen_network.setText(str(self.ui.listWidget_network.currentItem().text())))
        self.ui.pushButton_ping.clicked.connect(self.ping_taramasi)
        self.ui.pushButton_arp.clicked.connect(self.arp_taramasi)
        self.ui.pushButton_port.clicked.connect(self.port_taramasi)
        self.ui.listWidget_ip.currentTextChanged.connect(lambda: self.ui.label_taranacak_IP.setText(str(self.ui.listWidget_ip.currentItem().text())))
        self.prosesler()
    def prosesler(self):
        proses = psutil.process_iter()
        self.ui.tableWidget_proses.clear()
        self.ui.tableWidget_proses.setRowCount(500)
        self.ui.tableWidget_proses.setColumnCount(3)
        self.ui.tableWidget_proses.setHorizontalHeaderLabels(("PID","PROSES","DURUM"))
        for i,j in enumerate(proses):
            self.ui.tableWidget_proses.setItem(i,0,QTableWidgetItem(str(j.pid)))
            self.ui.tableWidget_proses.setItem(i,1,QTableWidgetItem(str(j.name())))
            self.ui.tableWidget_proses.setItem(i,2,QTableWidgetItem(str(j.status())))



    def port_taramasi(self):
        ip = self.ui.label_taranacak_IP.text()
        a = self.ui.spinBox_a.value()
        b = self.ui.spinBox_b.value()
        self.port_thread = PortScan(ip,a,b)
        self.port_thread.update_port_label.connect(self._update_port_label)
        self.port_thread.update_port_listwidget.connect(self._update_port_listwidget)
        self.port_thread.update_port_progressbar.connect(self._update_port_progressbar)
        self.port_thread.start()
    def _update_port_progressbar(self,sayi):
        self.ui.progressBar_port.setValue(sayi)
    def _update_port_listwidget(self,text):
        self.ui.listWidget_acik_port.addItem(text)
    def _update_port_label(self,text):
        self.ui.label_taranan_Port.setText(text)

    def arp_taramasi(self):
        ip = ".".join(self.ui.label_secilen_network.text().split(".")[0:3]) + "."
        self.ip_arp_thread = ArpScan(ip)
        self.ip_arp_thread.update_arp_label.connect(self._update_arp_label)
        self.ip_arp_thread.update_arp_listwidget.connect(self._update_arp_listwidget)
        self.ip_arp_thread.update_arp_progressbar.connect(self._update_arp_progressbar)
        self.ip_arp_thread.start()
    def _update_arp_label(self,text):
        self.ui.label_taranan_IP.setText(text)
    def _update_arp_listwidget(self,text):
        self.ui.listWidget_ip.addItem(text)
    def _update_arp_progressbar(self,number):
        self.ui.progressBar_ip.setValue(number)

    
    def ping_taramasi(self):
        ip = ".".join(self.ui.label_secilen_network.text().split(".")[0:3]) + "."
        self.ip_ping_thread = PingScan(ip)
        self.ip_ping_thread.update_ping_label.connect(self._update_ping_label)
        self.ip_ping_thread.update_ping_listwidget.connect(self._update_ping_listwidget)
        self.ip_ping_thread.update_ping_progressbar.connect(self._update_ping_progressbar)
        self.ip_ping_thread.start()
    def _update_ping_label(self,text):
        self.ui.label_taranan_IP.setText(text)
    def _update_ping_listwidget(self,text):
        self.ui.listWidget_ip.addItem(text)
    def _update_ping_progressbar(self,number):
        self.ui.progressBar_ip.setValue(number)
    
    def mevcut_network(self):
        self.ui.label_lokal_ip.setText(str(socket.gethostbyname(socket.gethostname())))
        try:
            self.ui.label_global_ip.setText(requests.get("https://api.ipify.org").text)
        except:
            QErrorMessage(self).showMessage("İnternet bağlantınızı kontrol ediniz!")
            self.ui.label_global_ip.setText("Bağlantı yok!")
       
        process = subprocess.Popen('arp -a | findstr "Interface:"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode('utf-8').splitlines()
        l = []
        for i in output:
            l.append(i.split(" ")[1])
        self.ui.listWidget_network.addItems(l)
        self.ui.listWidget_network.setCurrentRow(0)





    def cikis(self):
        pencere.close()
        uygulama.quit()
        sys.exit()


if __name__ == "__main__":
    uygulama = QApplication(sys.argv)
    pencere = Scanner()
    pencere.show()
    sys.exit(uygulama.exec_())