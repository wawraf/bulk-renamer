# -*- coding: utf-8 -*-
# rename/views.py

"""This module provides the Renamer main window."""

from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtCore import QThread

from pathlib import Path
from collections import deque

from .ui.window import Ui_Window
from .rename import Renamer


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self._files = deque()
        self._filesCount = len(self._files)
        self.ui = Ui_Window()
        self.ui.setupUi(self)
        self._setup()
        self._connect_signals_slots()

    def _setup(self):
        self.ui.prefixEdit.setEnabled(False)
        self.ui.renameFilesButton.setEnabled(False)
        self.ui.loadFilesButton.setFocus(True)

    def _check_prefix(self):
        self.ui.renameFilesButton.setEnabled(bool(self.ui.prefixEdit.text()))

    def _connect_signals_slots(self):
        self.ui.loadFilesButton.clicked.connect(self.load_files)
        self.ui.renameFilesButton.clicked.connect(self.rename_files)
        self.ui.prefixEdit.textChanged.connect(self._check_prefix)

    def load_files(self):
        self.ui.dstFilesList.clear()

        if self.ui.dirEdit.text():
            init_dir = self.ui.dirEdit.text()
        else:
            init_dir = str(Path.home())
        files, _filter = QFileDialog.getOpenFileNames(self, "Choose files to rename", init_dir)

        if len(files) > 0:
            self.ui.prefixEdit.setEnabled(True)
            self.ui.prefixEdit.setFocus(True)

            src_dir_name = str(Path(files[0]).parent)
            self.ui.dirEdit.setText(src_dir_name)
            for file in files:
                self._files.append(Path(file))
                self.ui.srcFilesList.addItem(file)
            self._filesCount = len(self._files)

    def rename_files(self):
        self._run_renamer_thread()

    def _run_renamer_thread(self):
        """Create, setup and run worker thread"""

        prefix = self.ui.prefixEdit.text()
        self._thread = QThread()
        self._renamer = Renamer(tuple(self._files), prefix)
        self._renamer.moveToThread(self._thread)

        # Renaming (target function)
        self._thread.started.connect(self._renamer.rename)
        # Update when renamedFile or progressed signal is emitted
        self._renamer.renamedFile.connect(self._update_state)
        self._renamer.progressed.connect(self._update_progress_bar)
        # Clean
        self._renamer.finished.connect(self._thread.quit)
        self._renamer.finished.connect(self._renamer.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        # Start worker
        self._thread.start()

    def _update_state(self, new_file: Path):
        self._files.popleft()
        self.ui.srcFilesList.takeItem(0)
        self.ui.dstFilesList.addItem(str(new_file))

    def _update_progress_bar(self, file_number: int):
        current_progress = 100 * file_number/self._filesCount
        self.ui.progressBar.setValue(current_progress)
