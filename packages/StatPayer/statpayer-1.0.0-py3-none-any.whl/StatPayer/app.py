from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

import traceback

import engine

class FileSaveWidget(QWidget):
    def __init__(self, parent=None):
        super(FileSaveWidget, self).__init__(parent)

        self.filedialog = QFileDialog()
        self.button_save = QPushButton('Save')
        self.button_save.clicked.connect(self.save_file)

        layout = QGridLayout()
        layout.addWidget(self.button_save)

        self.setLayout(layout)

    def save_file(self):
        fn = self.filedialog.getSaveFileName(filter='*.xlsx')
        self.write_file(fn[0])

    def write_file(self, fn):
        print('UNIMPLEMENTED')

class StatPaySaveWidget(FileSaveWidget):
    def __init__(self, loader, parent=None):
        super(StatPaySaveWidget, self).__init__(parent)

        self.loader = loader

    def write_file(self, fn):
        engine.write_timesheet(fn, self.loader.data['raw'])

class FileSelectionWidget(QWidget):
    def __init__(self, parent=None, file_loading_lambda=lambda fn: None):
        super(FileSelectionWidget, self).__init__(parent)

        self.file_loader = file_loading_lambda
        
        self.filedialog = QFileDialog()
        self.button_load = QPushButton('Load')
        self.button_load.clicked.connect(self.open_file)

        layout = QGridLayout()
        l0 = QVBoxLayout()
        l0.addWidget(self.button_load)
        layout.addLayout(l0, 0, 0)
        layout.setColumnStretch(0,1)
        
        self.setLayout(layout)

        self.fn = []
        self.data = {}
        self.callbacks = []
        
    def callback(self):
        for i in self.callbacks:
            i(self)

    def load_file(self, fn):
        try:
            self.fn = fn
            self.data['raw'] = self.file_loader(self.fn)
            self.callback()
        except:
            traceback.print_exc()

    def open_file(self):
        try:
            fns = self.filedialog.getOpenFileNames()[0]
        except Exception as e:
            traceback.print_exc()
        if(len(fns) > 0):
            self.load_file(fns[0])
            


class main_window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Stat pay
        stat_filesel = FileSelectionWidget(file_loading_lambda=lambda fn: engine.generate_statsheet(engine.read_timesheet(fn)))
        stat_filesave = StatPaySaveWidget(stat_filesel)
        stat_table = QTableWidget()

        def update_table(table_df, qtable):
            qtable.clearContents()
            qtable.clear()
            qtable.setColumnCount(0)

            N = 0
            M = 0
            for i in table_df:
                M=0
                qtable.insertColumn(N)
                qtable.setHorizontalHeaderItem(N, QTableWidgetItem(str(i)))
                for j in table_df[i]:
                    if(N==0):
                        qtable.insertRow(M)
                    it = QTableWidgetItem(str(j))
                    qtable.setItem(M, N, it)
                    M += 1
                N+=1

            qtable.setRowCount(M)
            qtable.setColumnCount(N)
        
        stat_filesel.callbacks += [ lambda s: update_table(s.data['raw'], stat_table) ]

        layout = QVBoxLayout()
        layout.addWidget(stat_table)
        layout.addWidget(stat_filesel)
        layout.addWidget(stat_filesave)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

if __name__=='__main__':
    app = QApplication([])
    window = main_window()
    window.show()
    app.exec()
