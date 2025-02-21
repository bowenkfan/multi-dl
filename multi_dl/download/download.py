import os
from enum import Enum

import yt_dlp
from PyQt6.QtCore import pyqtSignal, QObject

class Status(Enum):
    IDLE = 0
    DOWNLOADING = 1
    PAUSED = 2
    COMPLETED = 3
    FAILED = -1

class Download(QObject):
    # Default values
    DEFAULT_HOME_DIRECTORY = os.path.expanduser('~/Downloads/Multi-DL/')
    DEFAULT_TEMP_DIRECTORY = os.path.expanduser('~/Downloads/Multi-DL/.temp')
    DEFAULT_OUTTMPL = '%(title)s.%(ext)s'

    # PyQt update signal
    info_updated_signal = pyqtSignal(tuple)

    def __init__(self, url, title=None):
        super().__init__()

        # General information
        self.url = url
        self.title = title

        # Directory information
        self.home_directory = Download.DEFAULT_HOME_DIRECTORY
        self.temp_directory = Download.DEFAULT_TEMP_DIRECTORY

        # Status information
        self.status = Status.IDLE

    def download(self):
        self._set_status(Status.DOWNLOADING)
        try:
            self._download()
        except Exception as e:
            print('Unhandled exception:', e)
            self._set_status(Status.FAILED)
            return
        self._set_status(Status.COMPLETED)

    def _download(self):
        # Create home and temp directory if not exist
        os.makedirs(self.home_directory, exist_ok=True)
        os.makedirs(self.temp_directory, exist_ok=True)

        # Generate options and start download
        options = self._yt_dlp_options()
        with yt_dlp.YoutubeDL(options) as yt_dlp_download:
            yt_dlp_download.download([self.url])

    def _yt_dlp_options(self):
        # Generate home and temp paths
        paths = {}
        paths['home'] = self.home_directory
        paths['temp'] = self.temp_directory

        # Generate yt_dlp options
        options = {}
        options['paths'] = paths
        options['outtmpl'] = f'{self.title}.%(ext)s' if self.title else Download.DEFAULT_OUTTMPL
        options['progress_hooks'] = [self._progress_hook]
        options['quiet'] = True
        options['noprogress'] = True
        
        return options

    def _progress_hook(self, d):
        total_size = d.get('total_bytes')
        downloaded_size = d.get('downloaded_bytes')
        if total_size is None or downloaded_size is None:
            return
        progress = int(downloaded_size / total_size * 100)
        self.info_updated_signal.emit(('Progress', progress))
            
    def _set_status(self, status):
        self.status = status
        self.info_updated_signal.emit(('Status', status.name))

    def __str__(self):
        return self.title or self.url
