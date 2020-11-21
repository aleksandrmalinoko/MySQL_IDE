import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QTableWidget
from PyQt5.uic.properties import QtCore

from ui import Ui_MainWindow
import mysql.connector


class CurrencyConv(QtWidgets.QMainWindow):
    def __init__(self):
        super(CurrencyConv, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.loadTableButton.clicked.connect(self.converter)
        self.ui.editTableButton.clicked.connect(self.enable_edit)
        self.ui.dbTable.itemChanged.connect(self.on_change)
        self.cnx = mysql.connector.connect(host="localhost",
                                      user='admin',
                                      password='pass',
                                      db="Lab_1_schema")
        self.header_labels = []
        self.edit_table_rules = False
        self.table_list()

    def on_change(self, item):
        table_item = item
        self.change_db(table_item.row(), table_item.column())

    def change_db(self, row, column):
        query = f"UPDATE {str(self.ui.listTables.currentText())}" \
                f" SET {self.header_labels[column]}=" \
                f"'{self.ui.dbTable.item(row, column).text()}'" \
                f"WHERE "
        column_count = len(self.header_labels)
        for i in range(0, column_count):
            if i != column:
                query = f"{query} {self.header_labels[i]} = '{self.ui.dbTable.item(row, i).text()}'"
                if i != column_count - 1:
                    query = f"{query} AND"
                else:
                    query = f"{query};"
        cursor = self.cnx.cursor()
        cursor.execute(query, )
        self.cnx.commit()
        cursor.close()

    def table_list(self):
        # Этап заполнения списка таблиц
        cursor = self.cnx.cursor()
        query = ("SHOW TABLES;")
        cursor.execute(query, )
        for record in cursor:
            self.ui.listTables.addItem(record[0])
        cursor.close()

    def enable_edit(self):
        if not self.edit_table_rules:
            self.ui.dbTable.setEditTriggers(QTableWidget.DoubleClicked)
            self.ui.editTableButton.setText("Сохранить изменения")
            self.edit_table_rules = True
        else:
            self.ui.dbTable.setEditTriggers(QTableWidget.NoEditTriggers)
            self.ui.editTableButton.setText("Редактировать таблицу")
            self.edit_table_rules = False

    def converter(self):
        # Именуем колонки
        cursor = self.cnx.cursor()
        query = (f"SHOW COLUMNS FROM {str(self.ui.listTables.currentText())};")
        cursor.execute(query, )
        rows = cursor.fetchall()
        for row in rows:
            self.header_labels.append(row[0])
        cursor.close()
        # Этап заполнения таблицы
        cursor = self.cnx.cursor()
        query = (f"SELECT * FROM {str(self.ui.listTables.currentText())};")
        cursor.execute(query,)
        rows = cursor.fetchall()
        self.ui.dbTable.blockSignals(True)
        self.ui.dbTable.setColumnCount(0)
        self.ui.dbTable.setRowCount(0)
        self.ui.dbTable.setColumnCount(len(rows[0]))
        self.ui.addRowTable.setColumnCount(len(rows[0]))
        self.ui.dbTable.setHorizontalHeaderLabels(self.header_labels)
        # self.ui.addRowTable.horizontalHeader().setMaximumSize(QtCore.QSize(16777215, 0))
        # self.ui.dbTable.horizontalHeaderItem(0).
        for record in rows:
            row_position = self.ui.dbTable.rowCount()
            self.ui.dbTable.insertRow(row_position)
            for item_idx in range(len(record)):
                self.ui.dbTable.setItem(row_position, item_idx, QTableWidgetItem(str(record[item_idx])))
        self.ui.dbTable.blockSignals(False)
        cursor.close()
        # self.ui.dbTable.setEnabled(False)
        self.ui.dbTable.setEditTriggers(QTableWidget.NoEditTriggers)
        #self.cnx.close()



app = QtWidgets.QApplication([])
application = CurrencyConv()
application.show()

sys.exit(app.exec())
