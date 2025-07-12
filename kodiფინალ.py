import sys
import sqlite3
# საჭირო ბიბლიოთეკების იმპორ\ტი m  
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog
)
# PyQt5-ის დიაგრამების კომპონენტები
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QPieSeries
# ვალიდატორები, რომ ველებში მხოლოდ სწორი ტიპის მონაცემი ჩაიწეროს (რიცხვი)
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt

#
# კლასი პასუხისმგებელია ბაზასთან დაკავშირებულ ყველა ოპერაციაზე
class DatabaseManager:
    # კონსტრუქტორი: კლასის შექმნისას ავტომატურად ეშვება
    def __init__(self):
        ## ვუერთდებით data.db ფაილს, თუ არ არსებობს თავად შექმნის მას
        self.conn = sqlite3.connect("data.db")
        self.cursor = self.conn.cursor()
        # ვამოწმებთრომ ბაზაში ცხრილი არსებობს
        self.setup_database()

    # ქმნის cars ცხრილს თუ ის ჯერ არ არსებობს
    def setup_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cars (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                brand TEXT NOT NULL,
                                year INTEGER NOT NULL,
                                color TEXT NOT NULL,
                                transmission TEXT NOT NULL,
                                price REAL NOT NULL)''')
        # ვინახავთ ცვლილებებს ბაზაში
        self.conn.commit()

    # ამატებს ახალ მანქანას ბაზაში
    def add_car(self, brand, year, color, transmission, price):
        self.cursor.execute("INSERT INTO cars (brand, year, color, transmission, price) VALUES (?, ?, ?, ?, ?)",
                            (brand, year, color, transmission, price))
        self.conn.commit()

    # მოაქვს ყველა მანქანის სია ბაზიდან
    def get_all_cars(self):
        self.cursor.execute("SELECT * FROM cars")
        return self.cursor.fetchall()

    # ანახლებს არსებული მანქანის მონაცემებს ID-ის მიხედვით
    def update_car(self, car_id, brand, year, color, transmission, price):
        self.cursor.execute("UPDATE cars SET brand=?, year=?, color=?, transmission=?, price=? WHERE id=?",
                            (brand, year, color, transmission, price, car_id))
        self.conn.commit()

    # შლის მანქანას ბაზიდან IDის მიხედვით
    def delete_car(self, car_id):
        self.cursor.execute("DELETE FROM cars WHERE id=?", (car_id,))
        self.conn.commit()


# ეს კლასი ქმნის ახალ ფანჯარას Dialog და მასზე აჩვენებს დიაგრამებს
class BrandStatsDialog(QDialog):
    def __init__(self, cars): # კონსტრუქტორი იღებს მანქანების სიას
        super().__init__()
        self.setWindowTitle("მანქანების სტატისტიკა")

        layout = QVBoxLayout()

        # დიაგრამა 1 რამდენი მანქანაა თითოეული ბრენდის
        count_chart = QChart()
        count_series = QBarSeries() 
        brand_count = {} 
        for car in cars:
            brand = car[1] 
            brand_count[brand] = brand_count.get(brand, 0) + 1 

        count_bar_set = QBarSet("მანქანების რაოდენობა")
        categories = list(brand_count.keys())
        for brand in categories:
            count_bar_set << brand_count[brand] 
        count_series.append(count_bar_set)

        count_chart.addSeries(count_series)
        count_chart.setTitle("მანქანების რაოდენობა ბრენდის მიხედვით")
        count_axis = QBarCategoryAxis()
        count_axis.append(categories)
        count_chart.createDefaultAxes()
        count_chart.setAxisX(count_axis, count_series)
        count_chart_view = QChartView(count_chart) # ვქმნით დიაგრამის საჩვენებელ ვიჯეტს
        layout.addWidget(count_chart_view) # ვამატებთ ფანჯარაში

        # დიაგრამა 2: საშუალო ფასი ბრენდების მიხედვით
        price_chart = QChart()
        price_series = QBarSeries()
        brand_total_price = {}
        for car in cars:
            brand, price = car[1], car[5]
            if brand in brand_total_price:
                brand_total_price[brand].append(price)
            else:
                brand_total_price[brand] = [price]

        avg_price_bar_set = QBarSet("საშუალო ფასი")
        for brand in categories:
            prices = brand_total_price[brand]
            avg_price = sum(prices) / len(prices) # ვითვლით საშუალო არითმეტიკულს
            avg_price_bar_set << avg_price
        price_series.append(avg_price_bar_set)

        price_chart.addSeries(price_series)
        price_chart.setTitle("საშუალო ფასი ბრენდის მიხედვით")
        price_axis = QBarCategoryAxis()
        price_axis.append(categories)
        price_chart.createDefaultAxes()
        price_chart.setAxisX(price_axis, price_series)
        price_chart_view = QChartView(price_chart)
        layout.addWidget(price_chart_view)

        # დიაგრამა 3: მანქანების რაოდენობა ფერების მიხედვით (წრიული დიაგრამა)
        color_chart = QChart()
        color_series = QPieSeries() # წრიული დიაგრამის სერია
        color_count = {} # ფერების დასათვლელი ლექსიკონი
        for car in cars:
            color = car[3]
            color_count[color] = color_count.get(color, 0) + 1

        for color, count in color_count.items():
            color_series.append(f"{color} ({count})", count) # ვამატებთ "ნაჭერს" დიაგრამას

        color_chart.addSeries(color_series)
        color_chart.setTitle("მანქანების რაოდენობა ფერის მიხედვით")
        color_chart_view = QChartView(color_chart)
        layout.addWidget(color_chart_view)

        self.setLayout(layout)


# --- პროგრამის მთავარი ფანჯრის კლასი ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("მანქანების მარაგის მართვა")
        self.db = DatabaseManager() # ვქმნით ბაზის მენეჯერის ობიექტს
        self.selected_car_id = None # ცვლადი არჩეული მანქანის ID-ის შესანახად
        self.setup_ui() # ვქმნით ინტერფეისის ელემენტებს
        self.load_data() # ვიტვირთავთ მონაცემებს ცხრილში

    # ეს ფუნქცია ქმნის და აწყობს ყველა ვიზუალურ ელემენტს (ღილაკებს, ველებს, ცხრილს)
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout() # მთავარი განლაგება (ჰორიზონტალური)
        form_layout = QVBoxLayout() # ფორმის ველების განლაგება (ვერტიკალური)

        
        self.brand_input = QLineEdit()
        self.year_input = QLineEdit()
        self.year_input.setValidator(QIntValidator()) # მხოლოდ მთელი რიცხვი
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator()) # ნებისმიერი რიცხვი

        #ჩამოსაშლელი მენიუების შექმნა
        self.color_input = QComboBox()
        self.color_input.addItems(["Black", "White", "Silver", "Red", "Blue"])
        self.transmission_input = QComboBox()
        self.transmission_input.addItems(["Automatic", "Manual"])

        #ველებზე სახელების დამატება
        form_layout.addWidget(QLabel("ბრენდი"))
        form_layout.addWidget(self.brand_input)
        form_layout.addWidget(QLabel("წელი"))
        form_layout.addWidget(self.year_input)
        #დანარენი ველები
        form_layout.addWidget(QLabel("ფასი"))
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(QLabel("ფერი"))
        form_layout.addWidget(self.color_input)
        form_layout.addWidget(QLabel("გადაცემათა კოლოფი"))
        form_layout.addWidget(self.transmission_input)


        #ღილაკბის შექმნ
        add_btn = QPushButton("დამატება")
        update_btn = QPushButton("განახლება")
        delete_btn = QPushButton("წაშლა")
        clear_btn = QPushButton("ფორმის გასუფთავება")
        stats_btn = QPushButton("სტატისტიკის ჩვენება")

        #ღილაკებზე ფუნქციების მიბმა
        add_btn.clicked.connect(self.add_car)
        update_btn.clicked.connect(self.update_car)
        delete_btn.clicked.connect(self.delete_car)
        clear_btn.clicked.connect(self.clear_form)
        stats_btn.clicked.connect(self.show_stats)

        # ყველა ღილაკის დამატება ფორმის განლაგებაში
        for btn in [add_btn, update_btn, delete_btn, clear_btn, stats_btn]:
            form_layout.addWidget(btn)

        #ცხრილის შექმნა
        self.table = QTableWidget()
        self.table.setColumnCount(6) # 6 სვეტი
        self.table.setHorizontalHeaderLabels(["ID", "ბრენდი", "წელი", "ფერი", "კოლოფი", "ფასი"])
        self.table.cellClicked.connect(self.fill_form_from_table)

        # საბოლოო განლაგება
        main_layout.addLayout(form_layout, 1) # მარცხნივ ფორმა 1/3
        main_layout.addWidget(self.table, 2)   # მარჯვნივ ცხრილი 2/3 
        central_widget.setLayout(main_layout)

    # ფუნქცია რომელიც ბაზიდან იღებს მონაცემებს და ავსებს ცხრილს
    def load_data(self):
        self.table.setRowCount(0) # ჯერ ვასუფთავებთ ცხრილს
        cars = self.db.get_all_cars() # ვიღებთ ყველა მანქანას
        for row_idx, row_data in enumerate(cars):
            self.table.insertRow(row_idx) # ვამატებთ ახალ რიგს
            for col_idx, value in enumerate(row_data):
                # ვავსებთ უჯრებს მონაცემებით
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    # დამატება ღილაკის ფუნქცია
    def add_car(self):
        # ვიღებთ მონაცემებს ველებიდან და ვამატებთ ბაზაში
        self.db.add_car(
            self.brand_input.text(),
            int(self.year_input.text()),
            self.color_input.currentText(),
            self.transmission_input.currentText(),
            float(self.price_input.text())
        )
        self.clear_form() # ვასუფთავებთ ფორმას
        self.load_data()  # ვანახლებთ ცხრილს

    # განახლება ღილაკის ფუნქცია
    def update_car(self):
        if self.selected_car_id is None: # ვამოწმებთ, არის თუ არა მანქანა არჩეული
            return
        # ვანახლებთ არჩეული მანქანის მონაცემებს
        self.db.update_car(
            self.selected_car_id,
            self.brand_input.text(),
            int(self.year_input.text()),
            self.color_input.currentText(),
            self.transmission_input.currentText(),
            float(self.price_input.text())
        )
        self.clear_form()
        self.load_data()

    # წაშლა ღილაკის ფუნქცია
    def delete_car(self):
        if self.selected_car_id is None:
            return
        # ვეკითხებით მომხმარებელს ნამდვილად სურს თუ არა წაშლა
        reply = QMessageBox.question(self, "წაშლის დადასტურება", "დარწმუნებული ხარ რომ გსურს ჩანაწერის წაშლა?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes: # თუ დაგვეთანხმა
            self.db.delete_car(self.selected_car_id)
            self.clear_form()
            self.load_data()

    # ასუფთავებს ყველა შეყვანის ველს
    def clear_form(self):
        self.selected_car_id = None
        self.brand_input.clear()
        self.year_input.clear()
        self.price_input.clear()
        self.color_input.setCurrentIndex(0)
        self.transmission_input.setCurrentIndex(0)

    # ცხრილში რიგზე დაჭერისას ავსებს ფორმას ამ რიგის მონაცემებით
    def fill_form_from_table(self, row, column):
        self.selected_car_id = int(self.table.item(row, 0).text())
        self.brand_input.setText(self.table.item(row, 1).text())
        self.year_input.setText(self.table.item(row, 2).text())
        self.color_input.setCurrentText(self.table.item(row, 3).text())
        self.transmission_input.setCurrentText(self.table.item(row, 4).text())
        self.price_input.setText(self.table.item(row, 5).text())

    # "სტატისტიკა" ღილაკის ფუნქცია
    def show_stats(self):
        cars = self.db.get_all_cars() # ვიღებთ ყველა მანქანას
        dialog = BrandStatsDialog(cars) # ვქმნით სტატისტიკის ფანჯარას
        dialog.exec_() # ვაჩვენებთ ფანჯარას


# --- პროგრამის გაშვების წერტილი ---
if __name__ == '__main__':
    app = QApplication(sys.argv) # ვქმნით აპლიკაციას
    window = MainWindow() # ვქმნით მთავარ ფანჯარას
    window.show() # ვაჩვენებთ ფანჯარას
    sys.exit(app.exec_()) # ვიწყებთ აპლიკაციის ციკლს