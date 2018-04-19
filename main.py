if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from pictograph.pictograph import MainWindow

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()

    sys.exit(app.exec_())