import sys
from PyQt5.QtWidgets import QApplication
from data_manager import DataManager
from gui import MainWindow


def main():
    app = QApplication(sys.argv)
    data_manager = DataManager()
    window = MainWindow(data_manager)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
