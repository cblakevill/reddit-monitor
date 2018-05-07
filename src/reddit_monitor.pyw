import sys
from PyQt5.QtWidgets import QApplication
from config_manager import ConfigManager
from gui import GUI
from updater import Updater

if __name__ == '__main__':
    app = QApplication(sys.argv)
    config_man = ConfigManager("properties.json")
    updater = Updater(config_man)
    g = GUI(config_man, updater)
    updater.start()
    g.show()
    sys.exit(app.exec_())
