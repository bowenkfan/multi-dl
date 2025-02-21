import os
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import pyqtSignal, QObject

from .download import Download

class DownloadManager(QObject):
    DEFAULT_HOME_DIRECTORY = os.path.expanduser('~/Downloads/Multi-DL/')
    DEFAULT_TEMP_DIRECTORY = os.path.expanduser('~/Downloads/Multi-DL/.temp')

    download_added_signal = pyqtSignal(Download)

    def __init__(self):
        super().__init__()

        # Download list and executor
        self.downloads = []
        self.futures = []
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Configuration information
        self.home_directory = DownloadManager.DEFAULT_HOME_DIRECTORY
        self.temp_directory = DownloadManager.DEFAULT_TEMP_DIRECTORY

    def add_download(self, url, title=None):
        download = Download(url, title)
        future = self.executor.submit(download.download)
        self.downloads.append(download)
        self.futures.append(future)
        self.download_added_signal.emit(download)
