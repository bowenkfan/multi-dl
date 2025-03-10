import csv
import json

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHeaderView,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from multi_dl.download import DownloadManager
from .settings import SettingsWindow


class MultiDLWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.manager = DownloadManager()
        self.manager.download_added_signal.connect(self.on_download_added)

        # Window setup
        self.setWindowTitle("Multi-DL")
        self.resize(600, 400)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Menu bar and menus
        menu_bar = self.menuBar()

        settings_menu = menu_bar.addMenu("Settings")

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

        file_menu = menu_bar.addMenu("File")

        create_batch_csv_action = QAction("Download from CSV File", self)
        create_batch_csv_action.triggered.connect(self.create_batch_downloads_csv)
        file_menu.addAction(create_batch_csv_action)

        create_batch_json_action = QAction("Download from JSON File", self)
        create_batch_json_action.triggered.connect(self.create_batch_downloads_json)
        file_menu.addAction(create_batch_json_action)

        create_batch_jsonl_action = QAction("Download from JSONL File", self)
        create_batch_jsonl_action.triggered.connect(self.create_batch_downloads_jsonl)
        file_menu.addAction(create_batch_jsonl_action)

        # URL input and download button
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL")
        download_button = QPushButton("Download")
        download_button.clicked.connect(self.handle_add_download)
        self.url_input.returnPressed.connect(download_button.click)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(download_button)
        main_layout.addLayout(url_layout)

        # Table widget and table header settings
        self.header = ["Title", "Status", "Speed", "ETA"]
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.header))
        self.table.setHorizontalHeaderLabels(self.header)
        main_layout.addWidget(self.table)

        # Header resizing
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(1, 110)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)

    def open_settings(self):
        settings_window = SettingsWindow(self.manager, self)
        if settings_window.exec() == QDialog.DialogCode.Accepted:
            settings_window.save_settings()

    def create_batch_downloads_csv(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
        if not filename:
            return  # cancelled

        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            info_list = [{"url": row["url"], "title": row["title"]} for row in reader]

        for info in info_list:
            url = info["url"]
            title = info["title"]
            self.manager.add_download(url, title)

    def create_batch_downloads_json(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select JSON File", "", "JSON Files (*.json)"
        )
        if not filename:
            return  # cancelled

        with open(filename, "r", encoding="utf-8") as f:
            info_list = json.load(f)

        for info in info_list:
            url = info["url"]
            title = info["title"]
            self.manager.add_download(url, title)

    def create_batch_downloads_jsonl(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select JSONL File", "", "JSONL Files (*.jsonl)"
        )
        if not filename:
            return  # cancelled

        with open(filename, "r", encoding="utf-8") as f:
            info_list = [json.loads(line) for line in f]

        for info in info_list:
            url = info["url"]
            title = info["title"]
            self.manager.add_download(url, title)

    def on_download_added(self, download):
        row = self.table.rowCount()
        self.table.insertRow(row)

        column_to_text = {"Title": str(download), "Status": download.status.name}
        for i, column_header in enumerate(self.header):
            text = column_to_text.get(column_header, "")
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, i, item)

        download.info_updated_signal.connect(
            lambda info, r=row: self.on_info_updated(r, info)
        )

    def on_info_updated(self, row, info):
        key, value = info

        if key == "Progress":
            col = self.header.index("Status")
            status_item = self.table.item(row, col)
            progress_bar = self.table.cellWidget(row, col)
            if not progress_bar:
                status_item.setText("")
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                self.table.setCellWidget(row, col, progress_bar)
            progress_bar.setValue(value)
            return

        # Set item text to value for key != 'Progress'
        col = self.header.index(key)
        item = self.table.item(row, col)
        item.setText(value)

        if key == "Status" and value in ["FINISHED", "ERROR"]:
            progress_bar = self.table.cellWidget(row, col)
            if progress_bar:
                self.table.removeCellWidget(row, col)
            item.setForeground(QColor("green" if value == "FINISHED" else "red"))
            self.table.item(row, self.header.index("Speed")).setText("")
            self.table.item(row, self.header.index("ETA")).setText("")

    def handle_add_download(self):
        url = self.url_input.text().strip()
        if url:
            self.manager.add_download(url)
            self.url_input.clear()
