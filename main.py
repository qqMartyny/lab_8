from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, \
    QMessageBox, QHeaderView
import sys

import psycopg2


class TabbedTableApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(360, 250, 1330, 615)

        self.setWindowTitle("Schedule")

        self.connect_to_db()

        self.init_ui()

        self.create_subjects()
        self.create_teachers()
        self.create_week()

    def init_ui(self):
        self.tab_widget = QTabWidget()

        self.tab_subject = QWidget()
        self.tab_teacher = QWidget()
        self.tab_schedule = QWidget()

        # Добавляем табы

        self.tab_widget.addTab(self.tab_subject, "Предметы")
        self.tab_widget.addTab(self.tab_teacher, "Преподаватели")
        self.tab_widget.addTab(self.tab_schedule, "Расписание")

        # Предметы
        self.table_subject = QTableWidget()
        self.layout_subject = QVBoxLayout()
        self.layout_subject.addWidget(self.table_subject)
        self.tab_subject.setLayout(self.layout_subject)

        # Учителя
        self.table_teacher = QTableWidget()
        self.layout_teacher = QVBoxLayout()
        self.layout_teacher.addWidget(self.table_teacher)
        self.tab_teacher.setLayout(self.layout_teacher)

        # Расписание
        self.tab_days = QTabWidget()
        self.layout3 = QVBoxLayout()
        self.layout3.addWidget(self.tab_days)
        self.tab_schedule.setLayout(self.layout3)

        # Компановка
        button_update = QPushButton("update")
        button_update.clicked.connect(self.update_button)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tab_widget)
        self.layout.addWidget(button_update)
        self.setLayout(self.layout)

    def connect_to_db(self):
        self.conn = psycopg2.connect(database="laba_8",
                                     user="postgres",
                                     password="bed8w7",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    def create_subjects(self):
        self.cursor.execute("select * from subject order by id;")
        data = self.cursor.fetchall()

        rows = len(data)
        cols = 2

        self.table_subject.setRowCount(rows + 1)
        self.table_subject.setColumnCount(cols + 2)

        for row in range(rows):
            for col in range(cols):
                item = QTableWidgetItem(f"{data[row][col]}")
                self.table_subject.setItem(row, col, item)
            else:
                button_edit = QPushButton("edit")
                button_delete = QPushButton("delete")

                button_edit.clicked.connect(self.edit_subject)
                button_delete.clicked.connect(self.delete_subject)

                self.table_subject.setCellWidget(row, cols, button_edit)
                self.table_subject.setCellWidget(row, cols + 1, button_delete)

        button_add_row = QPushButton("add_row")
        button_add_row.clicked.connect(self.add_subject)
        self.table_subject.setCellWidget(rows, cols, button_add_row)

        # Настраиваю вывод
        header_labels_1 = ["id", "Название", "", ""]
        self.table_subject.setHorizontalHeaderLabels(header_labels_1)
        self.table_subject.verticalHeader().setVisible(False)
        header = self.table_subject.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStyleSheet("QHeaderView::section { border: 1px solid black; }")

    def create_teachers(self):
        self.cursor.execute("select * from teacher order by id;")
        data = self.cursor.fetchall()

        rows = len(data)
        cols = 3

        self.table_teacher.setRowCount(rows + 1)
        self.table_teacher.setColumnCount(cols + 2)

        for row in range(rows):
            for col in range(cols):
                item = QTableWidgetItem(f"{data[row][col]}")
                self.table_teacher.setItem(row, col, item)
            else:
                button_edit = QPushButton("edit")
                button_delete = QPushButton("delete")
                button_edit.clicked.connect(self.edit_teacher)
                button_delete.clicked.connect(self.delete_teacher)

                self.table_teacher.setCellWidget(row, cols, button_edit)
                self.table_teacher.setCellWidget(row, cols + 1, button_delete)

        button_add_row = QPushButton("add_row")
        button_add_row.clicked.connect(self.add_teacher)
        self.table_teacher.setCellWidget(rows, cols, button_add_row)

        # Настраиваю вывод
        header_labels_1 = ["id", "Имя", "id предмета", "", ""]
        self.table_teacher.setHorizontalHeaderLabels(header_labels_1)
        self.table_teacher.verticalHeader().setVisible(False)
        header = self.table_teacher.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStyleSheet("QHeaderView::section { border: 1px solid black; }")

    def create_week(self):
        weekday_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

        for i in weekday_names:
            day = QWidget()
            day.layout = QVBoxLayout(day)
            day.layout.addWidget(self.create_days_table(i))
            day.setLayout(day.layout)
            self.tab_days.addTab(day, i)

    def create_days_table(self, day):
        self.cursor.execute(f"select * from timetable t where t.day='{day}' order by id;")
        data = self.cursor.fetchall()
        data_old = []
        rows = len(data)
        cols = 6

        table = QTableWidget()

        table.setRowCount(rows + 1)
        table.setColumnCount(cols + 2)

        for row in range(rows):
            for col in range(cols):
                item = QTableWidgetItem(f"{data[row][col]}")
                table.setItem(row, col, item)
                if col == 0:
                    data_old.append(data[row][col])
            else:
                button_edit = QPushButton("edit")
                button_delete = QPushButton("delete")

                button_edit.clicked.connect(lambda _, table=table, data_old=data_old: self.edit_week(table, data_old))
                button_delete.clicked.connect(
                    lambda _, table=table, data_old=data_old: self.delete_week(table, data_old))

                table.setCellWidget(row, cols, button_edit)
                table.setCellWidget(row, cols + 1, button_delete)

        button_add = QPushButton("add_row")
        button_add.clicked.connect(lambda _, table=table, data_old=data_old: self.week_add(table, data_old))
        table.setCellWidget(rows, cols, button_add)

        # Настраиваю вывод
        header_labels_1 = ["id", "День", "id преподавателя", "Вид", "Кабинет", "Время", "", ""]
        table.setHorizontalHeaderLabels(header_labels_1)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStyleSheet("QHeaderView::section { border: 1px solid black; }")

        return table

    def identification(self, table):
        button = self.sender()
        row = table.indexAt(button.pos()).row()
        col = table.columnCount()
        data = [row]
        for i in range(col - 2):
            text = table.item(row, i).text()
            data.append(text)

        return data

    def days_clear(self):
        for i in range(6):
            self.tab_days.removeTab(0)
        self.create_week()

    def delete_subject(self):
        try:
            data = self.identification(self.table_subject)
            print(data)
            self.cursor.execute(f"delete from subject where id={data[1]};")
        except:
            QMessageBox.information(self, "Error", f"Не удалось удалить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.table_subject.clear()
        self.create_subjects()

    def edit_subject(self):
        try:
            data = self.identification(self.table_subject)
            self.cursor.execute(
                f"select * from subject where id=(SELECT id FROM subject ORDER BY id LIMIT 1 OFFSET {data[0]});")
            data_s = self.cursor.fetchall()

            self.cursor.execute(
                f"select * from teacher where fk_id_subject={data_s[0][0]};")
            data_t = self.cursor.fetchall()
            data_tt = []
            for i in range(len(data_t)):
                self.cursor.execute(
                    f"select * from timetable where fk_id_teacher={data_t[i][0]};")
                data_teacher = self.cursor.fetchall()
                data_tt += data_teacher
            self.cursor.execute(f"delete from subject where id={data_s[0][0]};")
            self.cursor.execute(f"insert into subject values({data[1]}, '{data[2]}');")
            for i in range(len(data_t)):
                self.cursor.execute(f"insert into teacher values ({data_t[i][0]}, '{data_t[i][1]}', {data[1]});")
            for j in range(len(data_tt)):
                self.cursor.execute(
                    f"insert into timetable values({data_tt[j][0]}, '{data_tt[j][1]}', {data_tt[j][2]}, '{data_tt[j][3]}', '{data_tt[j][4]}', '{data_tt[j][5]}');")

        except:
            QMessageBox.information(self, "Error", f"Не удалось обновить запись!", QMessageBox.Ok)
        self.conn.commit()

    def add_subject(self):
        try:
            data = self.identification(self.table_subject)
            self.cursor.execute(f"insert into subject values({data[1]}, '{data[2]}');")
        except:
            QMessageBox.information(self, "Error", f"Не удалось добавить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.table_subject.clear()
        self.create_subjects()

    def delete_teacher(self):
        try:
            data = self.identification(self.table_teacher)
            self.cursor.execute(f"delete from teacher where id={data[1]};")
        except:
            QMessageBox.information(self, "Error", f"Не удалось удалить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.table_teacher.clear()
        self.create_teachers()

    def edit_teacher(self):
        try:
            data = self.identification(self.table_teacher)
            self.cursor.execute(
                f"select * from teacher where id=(SELECT id FROM teacher ORDER BY id LIMIT 1 OFFSET {data[0]});")
            data_t = self.cursor.fetchall()
            self.cursor.execute(
                f"select * from timetable where fk_id_teacher={data_t[0][0]};")
            data_tt = self.cursor.fetchall()
            self.cursor.execute(
                f"delete from teacher where id={data_t[0][0]};")
            self.cursor.execute(f"insert into teacher values({data[1]}, '{data[2]}', {data[3]});")

            for i in range(len(data_tt)):
                self.cursor.execute(
                    f"insert into timetable values({data_tt[i][0]}, '{data_tt[i][1]}', {data[1]}, '{data_tt[i][3]}', '{data_tt[i][4]}', '{data_tt[i][5]}');")

        except:
            QMessageBox.information(self, "Error", f"Не удалось обновить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.table_teacher.clear()
        self.create_teachers()

    def add_teacher(self):
        try:
            data = self.identification(self.table_teacher)
            self.cursor.execute(f"insert into teacher values({data[1]}, '{data[2]}', {data[3]});")
        except:
            QMessageBox.information(self, "Error", f"Не удалось добавить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.table_teacher.clear()
        self.create_teachers()

    def delete_week(self, table, data_old):
        try:
            data = self.identification(table)
            self.cursor.execute(f"delete from timetable where id={data[1]};")
        except:
            QMessageBox.information(self, "Error", f"Не удалось удалить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.days_clear()

    def edit_week(self, table, data_old):
        try:
            data = self.identification(table)
            data_now = []
            button = self.sender()
            row = table.rowCount()
            for i in range(row - 1):
                text = int(table.item(i, 0).text())
                data_now.append(text)
            for i in range(len(data_old)):
                if data_now[i] != data_old[i]:
                    self.cursor.execute(f"delete from timetable where id={data_old[i]};")
                else:
                    self.cursor.execute(f"delete from timetable where id={data[1]};")
            self.cursor.execute(
                f"insert into timetable values({data[1]}, '{data[2]}', {data[3]}, '{data[4]}', '{data[5]}', '{data[6]}');")

        except:
            QMessageBox.information(self, "Error", f"Не удалось обновить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.days_clear()

    def week_add(self, table, data_old):
        try:
            data = self.identification(table)
            self.cursor.execute(
                f"insert into timetable values({data[1]}, '{data[2]}', {data[3]}, '{data[4]}', '{data[5]}', '{data[6]}');")
        except:
            QMessageBox.information(self, "Error", f"Не удалось добавить запись!", QMessageBox.Ok)
        self.conn.commit()
        self.days_clear()

    def update_button(self):
        self.days_clear()
        self.table_teacher.clear()
        self.table_subject.clear()
        self.create_subjects()
        self.create_teachers()


app = QApplication(sys.argv)
window = TabbedTableApp()
window.show()
sys.exit(app.exec_())
