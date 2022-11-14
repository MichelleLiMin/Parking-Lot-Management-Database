import sys
import psycopg2

from config import config
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QComboBox, QVBoxLayout, QGridLayout, QDialog, QWidget, \
    QPushButton, QApplication, QMainWindow,   QMessageBox, QLabel, QLineEdit,QDateTimeEdit
from PyQt5.QtCore import QDateTime


# to be continued
# add ticket price

class DBManager():
    def __init__(self):
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        self.conn = psycopg2.connect(**params)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS parking_spots(id BIGSERIAL NOT NULL PRIMARY KEY,l_plate VARCHAR(15) NOT NULL,spot_type INT,p_date TIMESTAMP,p_hour INT, p_bill INT,ticket_status INT);")
        print("CREATE TABLE parking_spots")
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS free_spots(id INT NOT NULL PRIMARY KEY,pLot_compact INT,pLot_large INT,pLot_electric INT,pLot_motorbike INT,pLot_handicapped INT);")
        print('CREATE TABLE free_spots')

        self.c.execute("SELECT * FROM free_spots WHERE id = 1")
        self.msg = self.c.fetchone()

        if not self.msg:
            print("not msg-------", self.msg)

            self.pLot_compact, self.pLot_large,  self.pLot_electric,  self.pLot_motorbike,  self.pLot_handicapped = [
                50, 20, 10, 15, 10]
            self.c.execute(
                f"INSERT INTO free_spots(id, pLot_compact,pLot_large,pLot_electric,pLot_motorbike,pLot_handicapped) VALUES (1, {self.pLot_compact}, {self.pLot_large}, {self.pLot_electric}, {self.pLot_motorbike}, {self.pLot_handicapped})")
            print("Insert data")
            self.conn.commit()

        self.c.execute("SELECT * FROM free_spots WHERE id = 1")

        self.data = self.c.fetchone()
        print("fetch data-------", self.data)

        self.pLot_compact, self.pLot_large,  self.pLot_electric,  self.pLot_motorbike,  self.pLot_handicapped = [
            self.data[1], self.data[2], self.data[3], self.data[4], self.data[5]]
        self.s_typeList = [self.pLot_compact, self.pLot_large,
                           self.pLot_electric, self.pLot_motorbike, self.pLot_handicapped]

        self.pLot_free = self.pLot_compact + self.pLot_large + \
            self.pLot_electric + self.pLot_motorbike + self.pLot_handicapped

        self.spot_key = ["pLot_compact", "pLot_large",
                         "pLot_electric", "pLot_motorbike", "pLot_handicapped"]

        self.pBill_compact, self.pBill_large,  self.pBill_electric,  self.pBill_motorbike,  self.pBill_handicapped = [
            1, 2, 2, 1, 0]
        print("Tables created successfully........")

    def parkVehicle(self, l_plate, spot_type, p_date, p_hour, p_bill, ticket_status, pLot_update):
        try:
            print("start inserting data")
            self.c.execute("INSERT INTO parking_spots(l_plate,spot_type ,p_date ,p_hour, p_bill ,ticket_status) VALUES ( %s,%s, %s,%s, %s, %s)",
                           (l_plate, spot_type, p_date.dateTime().toString(), p_hour, p_bill, ticket_status))
            self.c.execute(
                f"INSERT INTO free_spots(id, pLot_compact,pLot_large,pLot_electric,pLot_motorbike,pLot_handicapped) VALUES (1, {self.pLot_compact}, {self.pLot_large}, {self.pLot_electric}, {self.pLot_motorbike}, {self.pLot_handicapped}) On CONFLICT (id) DO UPDATE SET {self.spot_key[spot_type]} =" + str(pLot_update))
            print("data inserted")
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(
                QMessageBox(), 'Successful', 'Vehicle is parked successfully.')
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error',
                                'Could not park the vehicle.')
        # except Exception as ex:
        #     print(ex)

    def searchVehicle(self, id):

        self.c.execute("SELECT * from parking_spots WHERE id="+str(id))
        self.sdata = self.c.fetchone()
        print("data selected")
        if not self.sdata:
            QMessageBox.warning(
                QMessageBox(), 'Error', 'Could not find any vehicle with ticket no '+str(id) + ", Are you sure you parked the car here?")
            return None
        self.list = []
        for i in range(0, 7):
            print(self.list)
            self.list.append(self.sdata[i])
        self.c.close()
        self.conn.close()
        ticketStatus(self.list)

    def removeVehicle(self, id):

        self.c.execute("SELECT * from parking_spots WHERE id="+str(id))

        self.rdata = self.c.fetchone()

        if not self.rdata:
            QMessageBox.warning(
                QMessageBox(), 'Error', 'Could not remove the vehicle with ticket no '+str(id) + ", Are you sure you parked the car here?")
            return None
        else:
            lPlate = self.rdata[1]
            sType = self.rdata[2]
            self.c.execute(
                f"SELECT {self.spot_key[sType]} FROM free_spots WHERE id=1")
            self.rLot = self.c.fetchone()
            lot_num = self.rLot[sType]
            self.c.execute("DELETE from parking_spots WHERE id="+str(id))
            self.c.execute(
                f"INSERT INTO free_spots(id, pLot_compact,pLot_large,pLot_electric,pLot_motorbike,pLot_handicapped) VALUES (1, {self.pLot_compact}, {self.pLot_large}, {self.pLot_electric}, {self.pLot_motorbike}, {self.pLot_handicapped}) On CONFLICT (id) DO UPDATE SET {self.spot_key[sType]} =" + str(lot_num+1))
            print("database free_spots updated")

            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(
                QMessageBox(), 'Successful', f'Vehicle {lPlate} is removed, Thanks for parking here.')

    def parking_bill(self):
        pass


class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.userNameLabel = QLabel("Username")
        self.PassWprdLabel = QLabel("Password")
        self.userName = QLineEdit(self)
        self.passWord = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QGridLayout(self)
        layout.addWidget(self.userNameLabel, 1, 1)
        layout.addWidget(self.PassWprdLabel, 2, 1)
        layout.addWidget(self.userName, 1, 2)
        layout.addWidget(self.passWord, 2, 2)
        layout.addWidget(self.buttonLogin, 3, 1, 1, 2)

        self.setWindowTitle("Login")

    def handleLogin(self):
        if (self.userName.text() == '' and
                self.passWord.text() == ''):
            self.accept()
        else:
            QMessageBox.warning(
                self, 'Error', 'Bad user or password')


def ticketStatus(list):

    id = list[0]
    l_plate = list[1]

    if list[2] == 0:
        spot_type = "COMPACT"
    elif list[2] == 1:
        spot_type = "LARGE"
    elif list[2] == 2:
        spot_type = "ELECTRIC"
    elif list[2] == 3:
        spot_type = "MOTORBIKE"
    elif list[2] == 4:
        spot_type = "HANDICAPPED"

    p_date = list[3]
    p_hours = list[4]

    if list[5] == 0:
        p_bill = "1 €/h"
    elif list[5] == 1:
        p_bill = "2 €/h"
    elif list[5] == 2:
        p_bill = "2 €/h"
    elif list[5] == 3:
        p_bill = "1 €/h"
    elif list[5] == 4:
        p_bill = "Free"

    if list[6] == 0:
        ticket_status = "ACTIVE"
    elif list[6] == 1:
        ticket_status = "PAID"
    elif list[6] == 2:
        ticket_status = "LOST"

    table = QTableWidget()
    table.setWindowTitle("Vehicle Details")
    table.setRowCount(7)
    table.setColumnCount(2)

    table.setItem(0, 0, QTableWidgetItem("Ticket No."))
    table.setItem(0, 1, QTableWidgetItem(str(id)))
    table.setItem(1, 0, QTableWidgetItem("License Plate"))
    table.setItem(1, 1, QTableWidgetItem(l_plate))
    table.setItem(2, 0, QTableWidgetItem("Spot Type"))
    table.setItem(2, 1, QTableWidgetItem(str(spot_type)))
    table.setItem(3, 0, QTableWidgetItem("Parking Date"))
    table.setItem(3, 1, QTableWidgetItem(str(p_date)))
    table.setItem(4, 0, QTableWidgetItem("Parking Hours"))
    table.setItem(4, 1, QTableWidgetItem(str(p_hours)))
    table.setItem(5, 0, QTableWidgetItem("Parking Bill"))
    table.setItem(5, 1, QTableWidgetItem(str(p_bill)))
    table.setItem(6, 0, QTableWidgetItem("Ticket Status"))
    table.setItem(6, 1, QTableWidgetItem(str(ticket_status)))

    table.horizontalHeader().setStretchLastSection(True)
    table.show()
    dialog = QDialog()
    dialog.setWindowTitle("Ticket Status")
    dialog.resize(500, 300)
    dialog.setLayout(QVBoxLayout())
    dialog.layout().addWidget(table)
    dialog.exec()
    print("Ticket Status")


class ParkVehicle(QDialog, DBManager):

    def __init__(self):
        super().__init__()

        self.btnCancel = QPushButton("Cancel", self)
        self.btnReset = QPushButton("Reset", self)
        self.btnPark = QPushButton("Park", self)

        self.btnCancel.setFixedHeight(30)
        self.btnReset.setFixedHeight(30)
        self.btnPark.setFixedHeight(30)

        self.l_plateInput = QLineEdit(self)

        self.p_date = QDateTimeEdit(QDateTime.currentDateTime())
        self.p_hourInput = QLineEdit(self)

        self.s_typeCombo = QComboBox(self)
        self.s_typeCombo.addItem("COMPACT", ["1 €/h"])
        self.s_typeCombo.addItem("LARGE", ["2 €/h"])
        self.s_typeCombo.addItem("ELECTRIC", ["2 €/h"])
        self.s_typeCombo.addItem("MOTORBIKE", ["1 €/h"])
        self.s_typeCombo.addItem("HANDICAPPED", ["Free"])
        self.p_billCombo = QComboBox(self)

        self.s_typeCombo.currentIndexChanged.connect(self.updateP_billCombo)
        self.updateP_billCombo(self.s_typeCombo.currentIndex())

        self.t_statusCombo = QComboBox(self)
        self.t_statusCombo.addItem("ACTIVE")
        self.t_statusCombo.addItem("PAID")
        self.t_statusCombo.addItem("LOST")

        # self.ticketLabel = QLabel("ID")
        self.l_plateLabel = QLabel("License Plate")
        self.s_typeLabel = QLabel("Spot Type")
        self.p_dateLabel = QLabel("Parking Date")
        self.p_hourLabel = QLabel("Parking Hours")
        self.p_billLabel = QLabel("Parking Bill")
        self.t_statusLabel = QLabel("Ticket Status")

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.l_plateLabel, 1, 1)
        self.grid.addWidget(self.s_typeLabel, 2, 1)
        self.grid.addWidget(self.p_dateLabel, 3, 1)
        self.grid.addWidget(self.p_hourLabel, 4, 1)
        self.grid.addWidget(self.p_billLabel, 5, 1)
        self.grid.addWidget(self.t_statusLabel, 6, 1)

        self.grid.addWidget(self.l_plateInput, 1, 2)
        self.grid.addWidget(self.s_typeCombo, 2, 2)
        self.grid.addWidget(self.p_date, 3, 2)
        self.p_date.setReadOnly(True)
        self.grid.addWidget(self.p_hourInput, 4, 2)
        self.grid.addWidget(self.p_billCombo, 5, 2)
        self.grid.addWidget(self.t_statusCombo, 6, 2)

        self.grid.addWidget(self.btnReset, 9, 1)
        self.grid.addWidget(self.btnCancel, 9, 3)
        self.grid.addWidget(self.btnPark, 9, 2)

        self.btnPark.clicked.connect(self.parkVehicle2)
        self.btnCancel.clicked.connect(self.close)
        self.btnReset.clicked.connect(self.reset)

        self.setLayout(self.grid)
        self.setWindowTitle("Park vehicle Details")
        self.resize(500, 300)

    def updateP_billCombo(self, index):
        self.p_billCombo.clear()
        p_bills = self.s_typeCombo.itemData(index)
        if p_bills:
            self.p_billCombo.addItems(p_bills)

    def close(self):
        self.close()

    def reset(self):
        self.p_hourInput.setText("")
        self.l_plateInput.setText("")

    def parkVehicle2(self):
        self.l_plate = self.l_plateInput.text()
        self.spot_type = self.s_typeCombo.currentIndex()
        self.p_date = self.p_date
        try:
            self.p_hour = int(self.p_hourInput.text())
        except Exception:
            QMessageBox.information(QMessageBox(), 'Error',
                                    'Parking hour is wrong, please enter an interger.')

        self.p_bill = self.p_billCombo.currentIndex()
        self.ticket_status = self.t_statusCombo.currentIndex()

        for i in range(0, 5):
            if self.spot_type == i and self.s_typeList[i] > 0:
                self.s_typeList[i] -= 1

                self.dbhelper = DBManager()
                self.dbhelper.parkVehicle(self.l_plate, self.spot_type, self.p_date,
                                          self.p_hour, self.p_bill, self.ticket_status, self.s_typeList[i])
            elif self.spot_type == i:
                QMessageBox.information(QMessageBox(), 'Error',
                                        (f"We have {self.pLot_compact} spots available. I am sorry"))


class Window(QMainWindow, DBManager):
    def __init__(self):
        super().__init__()
        # 2 removeVehicle panel
        self.ticketForDelete = 0
        self.vboxDelete = QVBoxLayout()
        self.ticketRemove = QLabel("Enter the ticket no of the vehicle")
        self.editFieldDelete = QLineEdit()
        self.btnSearchDelete = QPushButton("Search", self)

        self.btnSearchDelete.clicked.connect(self.removeVehicle)
        self.vboxDelete.addWidget(self.ticketRemove)
        self.vboxDelete.addWidget(self.editFieldDelete)
        self.vboxDelete.addWidget(self.btnSearchDelete)
        self.dialogDelete = QDialog()
        self.dialogDelete.setWindowTitle("Remove Vehicle")
        self.dialogDelete.setLayout(self.vboxDelete)

        # 3 ticketStatus panel
        self.ticketToBeSearched = 0
        self.vboxSearch = QVBoxLayout()
        self.ticketSearch = QLabel("Enter the ticket no of the vehicle")
        self.editField = QLineEdit()
        self.btnSearch = QPushButton("Search", self)
        self.btnSearch.clicked.connect(self.ticketStatus)
        self.vboxSearch.addWidget(self.ticketSearch)
        self.vboxSearch.addWidget(self.editField)
        self.vboxSearch.addWidget(self.btnSearch)
        self.dialogSearch = QDialog()
        self.dialogSearch.setWindowTitle("Enter ticket No")
        self.dialogSearch.setLayout(self.vboxSearch)

        # 0 Vehicle Database Management System window panel
        # Using a GridLayout to allow the widget to be resized
        layout = QGridLayout()
        self.total_spot = DBManager()
        self.btnpLot_compactDisplay = QPushButton("Compact Spot", self)
        self.btnpLot_largeDisplay = QPushButton("Large Spot", self)
        self.btnpLot_electricDisplay = QPushButton("Electric Spot", self)
        self.btnpLot_motorbikeDisplay = QPushButton("Motobike Spot", self)
        self.btnpLot_handicappedDisplay = QPushButton("Handicappe Spot", self)
        self.btnpLot_freeDisplay = QLabel(str(self.total_spot.pLot_free), self)
        self.btnParkVehicle = QPushButton("Park Vehicle", self)
        self.btnTicketStatusDetails = QPushButton("Ticket Status", self)
        self.btnRemoveVehicle = QPushButton("Remove Vehicle", self)

        self.btnpLot_compactDisplayFont = self.btnpLot_compactDisplay.font()
        self.btnpLot_compactDisplayFont.setPointSize(13)
        self.btnpLot_compactDisplay.setFont(self.btnpLot_compactDisplayFont)
        self.btnpLot_compactDisplay.clicked.connect(self.freeSpotDisplay)
        layout.addWidget(self.btnpLot_compactDisplay, 0, 0, 1, 1)

        self.btnpLot_largeDisplayFont = self.btnpLot_largeDisplay.font()
        self.btnpLot_largeDisplayFont.setPointSize(13)
        self.btnpLot_largeDisplay.setFont(self.btnpLot_largeDisplayFont)
        self.btnpLot_largeDisplay.clicked.connect(self.freeSpotDisplay)
        layout.addWidget(self.btnpLot_largeDisplay, 1, 0, 1, 1)

        self.btnpLot_electricDisplayFont = self.btnpLot_electricDisplay.font()
        self.btnpLot_electricDisplayFont.setPointSize(13)
        self.btnpLot_electricDisplay.setFont(self.btnpLot_electricDisplayFont)
        self.btnpLot_electricDisplay.clicked.connect(self.freeSpotDisplay)
        layout.addWidget(self.btnpLot_electricDisplay, 2, 0, 1, 1)

        self.btnpLot_motorbikeDisplayFont = self.btnpLot_motorbikeDisplay.font()
        self.btnpLot_motorbikeDisplayFont.setPointSize(13)
        self.btnpLot_motorbikeDisplay.setFont(self.btnpLot_motorbikeDisplayFont)
        self.btnpLot_motorbikeDisplay.clicked.connect(self.freeSpotDisplay)
        layout.addWidget(self.btnpLot_motorbikeDisplay, 3, 0, 1, 1)

        self.btnpLot_handicappedDisplayFont = self.btnpLot_handicappedDisplay.font()
        self.btnpLot_handicappedDisplayFont.setPointSize(13)
        self.btnpLot_handicappedDisplay.setFont(
            self.btnpLot_handicappedDisplayFont)
        self.btnpLot_handicappedDisplay.clicked.connect(self.freeSpotDisplay)
        layout.addWidget(self.btnpLot_handicappedDisplay, 4, 0, 1, 1)

        self.btnpLot_freeDisplayFont = self.btnpLot_freeDisplay.font()
        self.btnpLot_freeDisplayFont.setPointSize(103)
        self.btnpLot_freeDisplay.setFont(self.btnpLot_freeDisplayFont)
        layout.addWidget(self.btnpLot_freeDisplay, 0, 1, 4, 1)

        # 1 ParkVehicle btn
        self.btnParkVehicleFont = self.btnParkVehicle.font()
        self.btnParkVehicleFont.setPointSize(13)
        self.btnParkVehicle.setFont(self.btnParkVehicleFont)
        self.btnParkVehicle.clicked.connect(self.parkVehicle)
        print("window - .clicked.connect(self.parkVehicle)")
        layout.addWidget(self.btnParkVehicle, 5, 0, 1, 1)

        # 2 RemoveVehicle btn
        self.btnRemoveVehicleFont = self.btnParkVehicle.font()
        self.btnRemoveVehicleFont.setPointSize(13)
        self.btnRemoveVehicle.setFont(self.btnRemoveVehicleFont)

        self.btnRemoveVehicle.clicked.connect(self.showRemovedDialog)
        print("window - .clicked.connect(self.showRemovedDialog)")
        layout.addWidget(self.btnRemoveVehicle, 5, 1, 1, 1)

        # 3 TicketStatusDetails btn
        self.btnTicketStatusDetailsFont = self.btnParkVehicle.font()
        self.btnTicketStatusDetailsFont.setPointSize(13)
        self.btnTicketStatusDetails.setFont(self.btnTicketStatusDetailsFont)
        self.btnTicketStatusDetails.clicked.connect(self.ticketStatusDialog)
        print("window- .clicked.connect(self.ticketStatusDialog)")
        layout.addWidget(self.btnTicketStatusDetails, 6, 0, 1, 2)

        # window panel
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.setFixedSize(400, 280)
        self.setWindowTitle("Vehicle Database Management System")

    def freeSpotDisplay(self):
        source = self.sender()
        self.vehicleType = ParkVehicle()

        if source.text() == 'Compact Spot':
            pLot_free = self.vehicleType.pLot_compact
            print("pLot_compact", pLot_free)
        elif source.text() == 'Large Spot':
            pLot_free = self.vehicleType.pLot_large
            print("pLot_large", pLot_free)

        elif source.text() == 'Electric Spot':
            pLot_free = self.vehicleType.pLot_electric
            print("pLot_electric", pLot_free)

        elif source.text() == 'Motobike Spot':
            pLot_free = self.vehicleType.pLot_motorbike
            print("pLot_motorbike", pLot_free)

        elif source.text() == 'Handicappe Spot':
            pLot_free = self.vehicleType.pLot_handicapped
            print("pLot_handicapped", pLot_free)

        self.btnpLot_freeDisplay.setText(str(pLot_free))
        print(pLot_free)

    def parkVehicle(self):
        enterVehicle = ParkVehicle()
        print("window - ParkVehicle()")
        enterVehicle.exec()

    def ticketStatusDialog(self):
        print("window - ticketStatusDialog()")
        self.dialogSearch.exec()

    def showRemovedDialog(self):
        self.dialogDelete.exec()

    def ticketStatus(self):
        if self.editField.text() == "":
            QMessageBox.warning(
                QMessageBox(), 'Error', 'You must give the Ticket number to show the results for.')
            return None
        ticketStatus = DBManager()
        ticketStatus.searchVehicle(int(self.editField.text()))
        print("window - ticketStatus()-DBManager()")

    def removeVehicle(self):
        print("inside removeVehicle funstion in window")
        if self.editFieldDelete.text() == "":
            QMessageBox.warning(
                QMessageBox(), 'Error', 'You must give the ticket number to show the results for.')
            return None
        removeVehicle = DBManager()
        print("start deleting")
        removeVehicle.removeVehicle(int(self.editFieldDelete.text()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()

    if login.exec_() == QDialog.Accepted:
        window = Window()
        window.show()
    sys.exit(app.exec_())
