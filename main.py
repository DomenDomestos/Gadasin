import sys
from PyQt5 import QtWidgets, uic
import socket
import threading
import time

def conv(data1):
    return data1.encode('utf-8')
def deconv(data1):
    return data1.decode('utf-8')

sock = socket.socket()
sock.connect(('localhost', 8888))
sock.send(b'' + conv("Connect"))
data = sock.recv(1024)
print(deconv(data))

DATAS=[]

def conv_datas_into_h_a_z(N):
    sock.send(b'' + conv("get day "+str(N)))
    ddd=""
    while (True):
        data = sock.recv(4096)
        exits=False
        if (len(data)<4096):
            exits=True
        data = deconv(data)
        ddd = ddd + data
        if (exits==True):
            break
    s1 = ddd.split(' ')
    s1 = s1[2:]
    znach = []
    hours = []
    anoms = []
    count1 = 0
    for i in s1:
        i = i[1:-1]
        i = i.split('-')
        hours.append(int(count1))
        znach.append(float(i[0]))
        anoms.append(float(i[1]))
        count1 += 1
    return hours, znach, anoms

STOPPER=True
Day=[]
def refresh():
    sock.send(b'' + conv("get now"))
    data = sock.recv(1024)
    data = deconv(data)
    global Day
    Day=data.split(' ')
    Day=Day[1:]
    for i in range(len(Day)):
        Day[i]=Day[i][1:-1]

    if STOPPER==False:
        thread = threading.Timer(1, refresh)
        thread.start()



class Window(QtWidgets.QMainWindow):

    def __init__(self):

        super(Window, self).__init__()

        self.ui = uic.loadUi('authorizationwindow.ui', self)
        self.ui.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.ok.clicked.connect(self.Login)
        self.ui.registration.clicked.connect(self.Registration)

    def Login(self):

        #запрос серверу о логине и пароле
        #если логин и пароль правильный, то статус успешно
        sock.send(b'' + conv("LOGIN "+self.ui.login.text()+" "+self.ui.password.text()))
        data = sock.recv(1024)
        data=deconv(data)

        if (int(data)==1):
            QtWidgets.QMessageBox.information(self, 'Статус', 'Успешно!')
            self.MainWindow()
        else:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

        # if (self.ui.login.text() == '111' and self.ui.password.text() == '222'):
        #       QtWidgets.QMessageBox.information(self, 'Статус','Успешно!')
        #       self.MainWindow()
        #
        # else:
        #      QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def Registration(self):

        self.ui = uic.loadUi('registrationwindow.ui', self)
        self.ui.addpassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.newregistration.clicked.connect(self.addUser)
        self.ui.relogin.clicked.connect(self.ReLogin)
        # newemail = self.addemail.text()

    def ReLogin(self):

        self.ui = uic.loadUi('authorizationwindow.ui', self)
        self.ui.password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.ui.ok.clicked.connect(self.Login)
        self.ui.registration.clicked.connect(self.Registration)


    def addUser(self):

        # если соединение с сервером установлено, то
        # запрос передачи данных серверу newlogin = rLOGIN
        # запрос передачи данных серверу newpassword = rPASSWORD
        # запрос передачи данных серверу newemail = rEMAIL

        l=self.addlogin.text()
        p=self.addpassword.text()
        sock.send(b'' + conv("REGISTER " + l + " " + p))
        data = sock.recv(1024)
        data = deconv(data)

        if (int(data) == 1):
            QtWidgets.QMessageBox.information(self,'Статус','Вы зарегистрировались!')


        #else:
        #      QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Соединение с сервером не установлено!')


    def MainWindow(self):


        self.ui = uic.loadUi('mainwindow.ui', self)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.GraphWidget, 0, 0)


        self.ui.setsensorperiod.clicked.connect(self.SetSensorPeriod)
        self.ui.diagnostic.clicked.connect(self.StartDiagnistic)
        self.ui.setsampling.clicked.connect(self.Sampling)

        sock.send(b'' + conv("get allday"))
        data = sock.recv(4096)
        data = deconv(data)
        global DATAS
        DATAS = data.split(' ')
        DATAS=DATAS[:-1]
        Da=[]
        for i in range(len(DATAS)):
            Da.append(str(i)+"|   "+DATAS[i])

        #получить часы, значения и аномалии нулевой записи
        h, z, a = conv_datas_into_h_a_z(0)
        # print(data)
        # если соединение с сервером установлено, то
        # DATA получить данные с сервера о температуре установленного периода
        # тут должен быть файл-таблица с аномальными данными!
        # data = open('text.txt')
        self.adataview.addItems(Da)
        self.ui.adataview.itemClicked.connect(self.click_to_item)
        #надо написать алгоритм считывания с файла (часы,температура) для plot
        self.plot(h,z)

        # else:
        #      QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Соединение с сервером не установлено!')
    def click_to_item(self, item):
        s=item.text().split('|')
        s=s[0]
        h, z, a = conv_datas_into_h_a_z(int(s))
        self.plot(h, z)

    def SetSensorPeriod(self):

        # если соединение с сервером установлено, то

        # data = open('text.txt')

        start = self.startperiod.date().toString("yyyy-MM-dd")
        end = self.endperiod.date().toString("yyyy-MM-dd")

        alltimes=[]
        startu=-1
        endu=-1
        for i in DATAS:
            alltimes.append(i.split(' ')[:1][0])
        bark=0
        for i in alltimes:
            # print(str(start)+" "+str(i))
            if (str(start)==str(i)):
                startu=bark
            if (str(end)==str(i)):
                endu=bark
                break
            bark+=1

        # print(alltimes)
        # print(str(start))
        # print(startu)


        if self.ui.setsensorperiod.clicked.connect:

            # надо написать алгоритм считывания с файла определенного периода с start до end

            H=[]
            Z=[]
            A=[]
            z1=-1
            if (startu!=-1):
                if (endu==-1):
                    z1=len(DATAS)-startu
                else:
                    z1=endu-startu
            cou=0
            for i in range(z1):
                # print(i)
                h, z, a = conv_datas_into_h_a_z(i)
                for j in range(len(h)):
                    H.append(cou)
                    Z.append(z[j])
                    A.append(a[j])
                    cou+=1


            # print(Z)
            # self.adataview.clear()
            # self.adataview.addItems(data)

            # надо написать алгоритм считывания с файла (часы,температура) для plot
            self.plot(H, Z)

            # QtWidgets.QMessageBox.information(self, 'Статус','Новый период установлен!')


        # else:
        #      QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Соединение с сервером не установлено!')

    def refresh2(self):
        global Day
        H = []
        Z = []
        A = []
        cou = 0
        for i in Day:
            i = i.split('-')
            H.append(cou)
            cou += 1
            Z.append(float(i[0]))
            A.append(float(i[1]))
        self.plot(H, Z)
        if STOPPER == False:
            thread1 = threading.Timer(1, self.refresh2)
            thread1.start()
            print("1")


    def Sampling(self):

        global STOPPER
        if STOPPER==True:
            STOPPER=False
        else:
            STOPPER=True
        refresh()



        self.refresh2()
        # sampling = self.sampling.text()
        # data = open('text.txt')

        # надо написать алгоритм считывания с файла заданной дискретизацией


        # if self.ui.setsampling.clicked.connect:
        #
        #
        #     self.adataview.clear()
        #     self.adataview.addItems(data)
        #
        #     QtWidgets.QMessageBox.information(self, 'Статус', 'Новый интервал считывания установлен!')


    def StartDiagnistic(self):

        self.adataview.clear()
        # если соединение с сервером установлено, то
        # тут должен быть файл с информации о диагностике!

        # data = open('Diagnostic.txt',encoding='utf-8')
        data=''
        sock.send(b'' + conv("CONFIG"))
        data = sock.recv(1024)
        data = deconv(data).split('\n')

        self.adataview.clear()
        self.adataview.addItems(data)

        QtWidgets.QMessageBox.information(self, 'Статус', 'Новый данные получены!')
        # else:
        #      QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Соединение с сервером не установлено!')

    def plot(self, hour, temperature):
        self.GraphWidget.clear()
        self.GraphWidget.plot(hour, temperature)

if __name__ == '__main__':

    import sys
    # connect = Connect()
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()



    sys.exit(app.exec_())
