# coding=utf-8
#---------------------------------------------------------------------------
# Copyright 2011 utahta
#---------------------------------------------------------------------------
import sys
from PyQt4 import QtGui, QtCore
import jsm
import re

class SearchBrandThread(QtCore.QThread):
    """銘柄検索スレッド
    裏で実行。。。
    """
    def __init__(self):
        super(SearchBrandThread, self).__init__()
    
    def __del__(self):
        self.wait()
    
    def search(self, terms):
        self.terms = terms
        self.start()
        
    def run(self):
        q = jsm.Quotes()
        try:
            result_set = q.search(self.terms)
        except:
            result_set = []
        self.emit(QtCore.SIGNAL('searchEnd'), result_set)

class SearchBrandDialog(QtGui.QDialog):
    """銘柄検索ダイアログ
    """
    def __init__(self, parent):
        super(SearchBrandDialog, self).__init__()
        self.parent = parent
        self.thread = SearchBrandThread()
        self.setModal(True)
        self.setup_ui()
        self.setup_event()
                
    def setup_ui(self):
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(QtGui.QLabel(u'コードまたは企業名を入力'))
        layout.addLayout(self.get_search_layout())
        layout.addLayout(self.get_result_set_layout())
        layout.addLayout(self.get_ok_layout())
        self.setLayout(layout)
        
        self.progress = QtGui.QProgressDialog(self, QtCore.Qt.CustomizeWindowHint)
        self.progress.setLabelText(u'取得中...')
        self.progress.setModal(True)
        self.progress.setRange(0, 0)
        self.progress.setCancelButton(None)        
        
    def get_search_layout(self):
        self.terms = QtGui.QLineEdit()
        self.search = QtGui.QPushButton(u'検索')
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.terms)
        layout.addWidget(self.search)
        return layout
    
    def get_result_set_layout(self):
        self.result_set = QtGui.QListWidget()
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.result_set)
        return layout
        
    def get_ok_layout(self):
        self.ok = QtGui.QPushButton(u'決定')
        self.cancel = QtGui.QPushButton(u'キャンセル')
        
        layout = QtGui.QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.ok)
        layout.addWidget(self.cancel)
        return layout
            
    def setup_event(self):
        self.search.clicked.connect(self.on_search)
        self.cancel.clicked.connect(self.close)
        self.connect(self.thread, QtCore.SIGNAL('searchEnd'),
                     self.on_search_end)
        self.ok.clicked.connect(self.on_ok)
        
    def on_search(self):
        terms = self.terms.text()
        if not terms:
            QtGui.QMessageBox().warning(self, u'警告', u'コードまたは企業名を入力してください')
            return
        self.result_set.clear()
        self.progress.show()
        self.thread.search(terms) # 裏で実行
    
    def on_search_end(self, result_set):
        self.progress.hide()
        self.result_set.clear()
        for res in result_set:
            self.result_set.addItem(u'%s %s' % (res.ccode, res.name))
            
    def on_ok(self):
        items = self.result_set.selectedItems()
        if not items:
            self.close()
            return
        item = items[0]
        m = re.match('(\d\d\d\d) ', item.text())
        if m:
            self.parent.line_edit.setText(m.group(1))
        self.close()

class CCodeWidget(QtGui.QWidget):
    """証券コード入力欄パーツ
    """
    def __init__(self):
        super(CCodeWidget, self).__init__()
        self.search_brand = SearchBrandDialog(self)
        self.setup_ui()
        self.setup_event()
        
    def setup_ui(self):
        self.label = QtGui.QLabel(u'証券コード')
        self.line_edit = QtGui.QLineEdit()
        self.button = QtGui.QPushButton(u'銘柄検索')
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        
    def setup_event(self):
        self.button.clicked.connect(self.on_show_search)
        
    def on_show_search(self):
        self.search_brand.show()

class SavePriceWidget(QtGui.QWidget):
    """保存ボタンパーツ
    """
    def __init__(self):
        super(SavePriceWidget, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.button = QtGui.QPushButton(u'保存')
        
        layout = QtGui.QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.button)
        
        self.setLayout(layout)        

class SavePriceThread(QtCore.QThread):
    def __init__(self):
        super(SavePriceThread, self).__init__()
    
    def save(self, path, ccode, range, start_date=None, end_date=None, all=False):
        self.path = path
        self.ccode = ccode
        self.range = range
        self.start_date = start_date
        self.end_date = end_date
        self.all = all
        self.start()
        
    def run(self):
        c = jsm.QuotesCsv()
        c.save_historical_prices(self.path, self.ccode, self.range, self.start_date, self.end_date, self.all)
        self.emit(QtCore.SIGNAL('saved'))

class PriceWidget(QtGui.QWidget):
    """株価取得タブ
    """
    def __init__(self):
        super(PriceWidget, self).__init__()
        self.thread = SavePriceThread()
        self.setup_ui()
        self.setup_event()
        
    def setup_ui(self):
        self.ccode = CCodeWidget()
        self.save_price = SavePriceWidget()
        
        layout = QtGui.QVBoxLayout()        
        layout.addWidget(self.ccode)
        layout.addWidget(self.save_price)
        
        self.setLayout(layout)
        
        self.progress = QtGui.QProgressDialog(self, QtCore.Qt.CustomizeWindowHint)
        self.progress.setLabelText(u'保存中...')
        self.progress.setModal(True)
        self.progress.setRange(0, 0)
        self.progress.setCancelButton(None)
        
    def setup_event(self):
        self.save_price.button.clicked.connect(self.on_save)
        self.connect(self.thread, QtCore.SIGNAL('saved'),
                     self.on_saved)
        
    def on_save(self):
        ccode = self.ccode.line_edit.text()
        if not ccode:
            QtGui.QMessageBox().warning(self, u'警告', u'証券コードを入力してください')
            return
        if not re.match('\d\d\d\d', ccode):
            QtGui.QMessageBox().warning(self, u'警告', u'証券コードを入力してください')
            return
        q = jsm.Quotes()
        try:
            result = q.search(ccode)
        except:
            QtGui.QMessageBox().critical(self, u'エラー', u'不明なエラーが発生しました')
            return
        if not result:
            QtGui.QMessageBox().warning(self, u'警告', u'不明な証券コードです')
            return
        path = QtGui.QFileDialog().getSaveFileName(self, u'保存先', '%s.csv' % ccode)
        self.thread.save(path, ccode, jsm.DAILY)
        self.progress.show()
    
    def on_saved(self):
        self.progress.hide()
        
class TabWindow(QtGui.QTabWidget):
    def __init__(self):
        super(TabWindow, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.addTab(PriceWidget(), u'株価')

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setCentralWidget(TabWindow())
        self.setWindowTitle(u'jsm GUI')
        self.resize(350, 300)

class Application(QtGui.QApplication):
    def __init__(self):
        super(Application, self).__init__(sys.argv)
        self.win = MainWindow()
        self.win.show()

if __name__ == '__main__':
    Application().exec_()