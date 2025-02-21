import csv
import json

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QInputDialog,
    QProgressBar,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

from multi_dl.download import DownloadManager

class MultiDLWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.manager = DownloadManager()
        self.manager.download_added_signal.connect(self.on_download_added)

        # Window setup
        self.setWindowTitle('Multi-DL')
        self.resize(600, 400)

        # Menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        # Action: create single download
        create_download_action = QAction('Download from URL', self)
        create_download_action.triggered.connect(self.create_download)
        file_menu.addAction(create_download_action)

        # Action: create batch from csv file
        create_batch_csv_action = QAction('Download from CSV File', self)
        create_batch_csv_action.triggered.connect(self.create_batch_downloads_csv)
        file_menu.addAction(create_batch_csv_action)

        # Action: create batch from json file
        create_batch_json_action = QAction('Download from JSON File', self)
        create_batch_json_action.triggered.connect(self.create_batch_downloads_json)
        file_menu.addAction(create_batch_json_action)

        # Main widget and layout
        main_widget = QWidget()
        box_layout = QVBoxLayout()
        main_widget.setLayout(box_layout)
        self.setCentralWidget(main_widget)

        # Table widget and table header settings
        self.header = ['Title', 'Status']
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.header))
        self.table.setHorizontalHeaderLabels(self.header)
        box_layout.addWidget(self.table)

        # Header resizing
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        
        self.table.setColumnWidth(1, 110)

    def on_download_added(self, download):
        row = self.table.rowCount()
        self.table.insertRow(row)

        column_to_text = {'Title': str(download), 'Status': download.status.name}
        for i, column_header in enumerate(self.header):
            text = column_to_text.get(column_header, '')
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, i, item)

        download.info_updated_signal.connect(lambda info, r=row: self.info_updated_signal(r, info))

    def info_updated_signal(self, row, info):
        key, value = info
        col = self.header.index('Status' if key == 'Progress' else key)
        item = self.table.item(row, col)

        if key == 'Progress':
            progress_bar = self.table.cellWidget(row, col)
            if not progress_bar:
                item.setText('')
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                self.table.setCellWidget(row, col, progress_bar)
            progress_bar.setValue(value)

        elif key == 'Status':
            progress_bar = self.table.cellWidget(row, col)
            if progress_bar:
                self.table.removeCellWidget(row, col)
            item.setText(value)

        else:
            item.setText(value)

    def create_download(self):
        url, _ = QInputDialog.getText(self, 'Create Download', 'Enter URL:')
        url = url.strip()
        if not url:
            return  # no URL
        self.manager.add_download(url)

    def create_batch_downloads_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if not filename:
            return # cancelled
        
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            info_list = [{'url': row['url'], 'title': row['title']} for row in reader]
            
        for info in info_list:
            url = info['url']
            title = info['title']  
            self.manager.add_download(url, title)

    def create_batch_downloads_json(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select JSON File', '', 'JSON Files (*.json)')
        if not filename:
            return # cancelled

        with open(filename, 'r', encoding='utf-8') as f:
            info_list = json.load(f)
        
        for info in info_list:
            url = info['url']
            title = info['title']
            self.manager.add_download(url, title)
