import os
from threading import Event, Thread
from queue import Empty, Queue

from PyQt6.QtCore import pyqtSignal, QObject, QSettings

from .download import Download


class DownloadThread(Thread):
    def __init__(self, queue):
        super().__init__()

        self.queue = queue
        self.daemon = True
        self._stop_event = Event()

    def run(self):
        while not self._stop_event.is_set():
            self._run()

    def _run(self):
        try:
            download = self.queue.get(block=True, timeout=5)
            download.download()
        except Empty:
            return

    def stop(self):
        self._stop_event.set()


class DownloadManager(QObject):
    DEFAULT_HOME_DIRECTORY = os.path.expanduser("~/Downloads/Multi-DL/")
    DEFAULT_TEMP_DIRECTORY = os.path.expanduser("~/Downloads/Multi-DL/.temp")
    DEFAULT_THREAD_COUNT = 5

    download_added_signal = pyqtSignal(Download)

    def __init__(self):
        super().__init__()

        # Settings information
        self.thread_count = DownloadManager.DEFAULT_THREAD_COUNT
        self.home_directory = DownloadManager.DEFAULT_HOME_DIRECTORY
        self.temp_directory = DownloadManager.DEFAULT_TEMP_DIRECTORY

        # Download list and queue
        self.downloads = []
        self.queue = Queue()

        # Worker threads
        self.threads = []
        for _ in range(self.thread_count):
            thread = DownloadThread(self.queue)
            thread.start()
            self.threads.append(thread)

    def add_download(self, url, title=None):
        download = Download(url, title)
        download.home_directory = self.home_directory
        download.temp_directory = self.temp_directory

        self.downloads.append(download)
        self.queue.put(download)
        self.download_added_signal.emit(download)

    def get_settings(self):
        settings = QSettings()
        settings.setValue("threads", self.thread_count)
        settings.setValue("download_directory", self.home_directory)
        settings.setValue("temp_directory", self.temp_directory)
        return settings

    def update_settings(self, settings):
        thread_count = settings.value(
            "threads", DownloadManager.DEFAULT_THREAD_COUNT, type=int
        )
        home_directory = settings.value("download_directory", "", type=str)
        temp_directory = settings.value("temp_directory", "", type=str)

        self._set_thread_count(thread_count)
        if home_directory:
            self.home_directory = os.path.expanduser(home_directory)
        if temp_directory:
            self.temp_directory = os.path.expanduser(temp_directory)

    def _set_thread_count(self, thread_count):
        if thread_count > self.thread_count:
            d = thread_count - self.thread_count
            for _ in range(d):
                thread = DownloadThread(self.queue)
                thread.start()
                self.threads.append(thread)
            self.thread_count = thread_count
        elif thread_count < self.thread_count:
            d = self.thread_count - thread_count
            stop_threads = self.threads[:d]
            for thread in stop_threads:
                thread.stop()
            self.threads = self.threads[d:]
            self.thread_count = thread_count
