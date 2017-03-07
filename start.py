#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication
from gui import Windows

"""
This file starts the program
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Windows.MainWindow()
    sys.exit(app.exec_())


