from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout
)

class SettingsWindow(QDialog):
    def __init__(self, manager, parent=None):
        super().__init__(parent)

        self.manager = manager
        self.setWindowTitle('Preferences')
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Number of threads
        threads_layout = QHBoxLayout()

        threads_label = QLabel('Thread Count:')

        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimum(1)
        self.threads_spin.setMaximum(100)
        self.threads_spin.setFixedWidth(50)
        self.threads_spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        threads_layout.addWidget(threads_label)
        threads_layout.addWidget(self.threads_spin)
        main_layout.addLayout(threads_layout)

        # Download directory
        download_directory_layout = QHBoxLayout()

        download_directory_label = QLabel('Download Directory:')
        self.download_directory_edit = QLineEdit()
        self.download_directory_edit.setMinimumWidth(200)

        download_directory_layout.addWidget(download_directory_label)
        download_directory_layout.addWidget(self.download_directory_edit, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(download_directory_layout)

        # Temp directory
        temp_directory_layout = QHBoxLayout()

        temp_directory_label = QLabel('Download Directory:')
        self.temp_directory_edit = QLineEdit()
        self.temp_directory_edit.setMinimumWidth(200)

        temp_directory_layout.addWidget(temp_directory_label)
        temp_directory_layout.addWidget(self.temp_directory_edit, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(temp_directory_layout)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        # Load current settings
        self.load_settings()

    def load_settings(self):
        settings = self.manager.get_settings()
        self.threads_spin.setValue(settings.value('threads', 5, type=int))
        self.download_directory_edit.setText(settings.value('download_directory', '', type=str))
        self.temp_directory_edit.setText(settings.value('temp_directory', '', type=str))

    def save_settings(self):
        settings = QSettings()
        settings.setValue('threads', self.threads_spin.value())
        settings.setValue('download_directory', self.download_directory_edit.text())
        settings.setValue('temp_directory', self.temp_directory_edit.text())
        self.manager.update_settings(settings)