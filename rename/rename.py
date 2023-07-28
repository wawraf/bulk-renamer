# -*- coding: utf-8 -*-
# rename/rename.py

"""This module provides the Renamer class to rename multiple files."""

import time
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal


class Renamer(QObject):
    # Define custom signals
    progressed = pyqtSignal(int)
    renamedFile = pyqtSignal(Path)
    finished = pyqtSignal()

    def __init__(self, files: tuple, prefix: str):
        super().__init__()
        self._files = files
        self._prefix = prefix

    def rename(self):
        for fileNumber, file in enumerate(self._files, 1):
            new_file = file.parent.joinpath(
                f"{self._prefix}_{str(fileNumber)}{file.suffix}"
            )
            file.rename(new_file)
            time.sleep(0.5)  # Comment this line to rename files faster.
            self.progressed.emit(fileNumber)
            self.renamedFile.emit(new_file)
        self.progressed.emit(0)  # Reset the progress
        self.finished.emit()
