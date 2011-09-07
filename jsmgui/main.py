# coding=utf-8
#---------------------------------------------------------------------------
# Copyright 2011 utahta
#---------------------------------------------------------------------------
import sys
from PyQt4 import QtGui, QtCore
import jsm
import re
import datetime
import time

class SearchBrandThread(QtCore.QThread):
    """銘柄検索スレッド
    裏で実行。。。
    """
    def __init__(self):
        super(SearchBrandThread, self).__init__()
        self.result_set = []
    
    def __del__(self):
        self.wait()
    
    def search(self, terms):
        self.terms = terms
        self.start()
        
    def run(self):
        q = jsm.Quotes()
        try:
            self.result_set = q.search(self.terms)
        except:
            self.result_set = []
        self.emit(QtCore.SIGNAL('searchEnd()'))

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
        self.setWindowTitle(u'銘柄検索')
        
        self.progress = QtGui.QProgressDialog(self)
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
        self.connect(self.thread, QtCore.SIGNAL('searchEnd()'),
                     self.on_search_end)
        self.ok.clicked.connect(self.on_ok)
        
    def on_search(self):
        terms = unicode(self.terms.text()).encode('utf8')
        if not terms:
            QtGui.QMessageBox().warning(self, u'警告', u'コードまたは企業名を入力してください')
            return
        self.result_set.clear()
        self.progress.show()
        self.thread.search(terms) # 裏で実行
    
    def on_search_end(self):
        self.progress.hide()
        self.result_set.clear()
        for res in self.thread.result_set:
            self.result_set.addItem(u'%s %s' % (res.ccode, res.name.decode('utf8')))
            
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
    """銘柄コード入力欄パーツ
    """
    def __init__(self):
        super(CCodeWidget, self).__init__()
        self.search_brand = SearchBrandDialog(self)
        self.setup_ui()
        self.setup_event()
        
    def setup_ui(self):
        self.line_edit = QtGui.QLineEdit()
        self.line_edit.setFixedWidth(80)
        self.button = QtGui.QPushButton(u'銘柄検索')
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        
    def setup_event(self):
        self.button.clicked.connect(self.on_show_search)
        
    def on_show_search(self):
        self.search_brand.show()

class SelectRangeWidget(QtGui.QWidget):
    """レンジ選択パーツ
    デイリー、ウィークリー、マンスリー
    """
    def __init__(self):
        super(SelectRangeWidget, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.combo = QtGui.QComboBox(self)
        self.combo.addItem(u'デイリー')
        self.combo.addItem(u'週間')
        self.combo.addItem(u'月間')
        self.combo.setSizeAdjustPolicy(self.combo.AdjustToContents)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.combo)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def get_range(self):
        text = self.combo.currentText()
        if text == u'デイリー':
            return jsm.DAILY
        elif text == u'週間':
            return jsm.WEEKLY
        elif text == u'月間':
            return jsm.MONTHLY
        return jsm.DAILY

class CalendarDialog(QtGui.QDialog):
    def __init__(self, date=None):
        super(CalendarDialog, self).__init__()
        self._date = date
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        self.calendar = QtGui.QCalendarWidget()
        if isinstance(self._date, datetime.date):
            self.calendar.setSelectedDate(QtCore.QDate(self._date.year, self._date.month, self._date.day))
        today = datetime.date.today()
        self.calendar.setMaximumDate(QtCore.QDate(today.year, today.month, today.day))

        self.ok = QtGui.QPushButton(u'決定')
        self.cancel = QtGui.QPushButton(u'キャンセル')
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.calendar)
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.ok)
        hbox.addWidget(self.cancel)
        layout.addLayout(hbox)
        
        self.setLayout(layout)
        self.setWindowTitle(u'日付')
        
class DateWidget(QtGui.QWidget):
        def __init__(self, date):
            super(DateWidget, self).__init__()
            self.date = date
            self.setup_ui()
            self.setup_event()
            
        def setup_ui(self):
            self.label = QtGui.QLabel(self.date.strftime('%Y-%m-%d'))
            self.button = QtGui.QPushButton(u'日付')
            self.calendar = CalendarDialog(self.date)
            
            layout = QtGui.QHBoxLayout()
            layout.addWidget(self.label)
            layout.addWidget(self.button)
            layout.addStretch()
            
            self.setLayout(layout)
            
        def setup_event(self):
            self.calendar.ok.clicked.connect(self._on_calendar_clicked)
            self.calendar.cancel.clicked.connect(self.calendar.close)
            self.button.clicked.connect(self._on_show_calendar)
            
        def _on_show_calendar(self):
            self.calendar.show()
            
        def _on_calendar_clicked(self):
            self.date = self.calendar.calendar.selectedDate().toPyDate()
            self.label.setText(self.date.strftime('%Y-%m-%d'))
            self.calendar.close()
                        
class StartDateWidget(DateWidget):
    """開始日時パーツ"""
    def __init__(self):
        super(StartDateWidget, self).__init__(datetime.date.fromtimestamp(time.time() - 2592000))

class EndDateWidget(DateWidget):
    """終了日時パーツ"""
    def __init__(self):
        super(EndDateWidget, self).__init__(datetime.date.today())
        
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

class PriceTab(QtGui.QWidget):
    """株価取得タブ
    """
    def __init__(self):
        super(PriceTab, self).__init__()
        self.thread = SavePriceThread()
        self.setup_ui()
        self.setup_event()
        
    def setup_ui(self):
        self.ccode = CCodeWidget()
        self.range = SelectRangeWidget()
        self.start_date = StartDateWidget()
        self.end_date = EndDateWidget()
        self.save_price = SavePriceWidget()
        
        layout = QtGui.QVBoxLayout()
        
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel(u'銘柄'), 0, 0)
        grid.addWidget(self.ccode, 0, 1)
        grid.addWidget(QtGui.QLabel(u'対象'), 1, 0)
        grid.addWidget(self.range, 1, 1)
        grid.addWidget(QtGui.QLabel(u'開始'), 2, 0)
        grid.addWidget(self.start_date, 2, 1)
        grid.addWidget(QtGui.QLabel(u'終了'), 3, 0)
        grid.addWidget(self.end_date, 3, 1)
        grid.setSpacing(0)
        layout.addLayout(grid)
        layout.addWidget(self.save_price)
        
        self.setLayout(layout)
        
        self.progress = QtGui.QProgressDialog(self)
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
            QtGui.QMessageBox().warning(self, u'警告', u'銘柄コードを入力してください')
            return
        if not re.match('\d\d\d\d', ccode):
            QtGui.QMessageBox().warning(self, u'警告', u'銘柄コードは4桁の数字です')
            return
        range = self.range.get_range()
        start_date = self.start_date.date
        end_date = self.end_date.date
        q = jsm.Quotes()
        try:
            result = q.search(ccode)
        except:
            QtGui.QMessageBox().critical(self, u'エラー', u'不明なエラーが発生しました')
            return
        if not result:
            QtGui.QMessageBox().warning(self, u'警告', u'不明な銘柄コードです')
            return
        default_name = '%s%s_%s_%s.csv' % (ccode, ('d', 'w', 'm')[range], start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
        path = QtGui.QFileDialog().getSaveFileName(self, u'保存先', default_name)
        if path:
            self.thread.save(path, ccode, range, start_date, end_date)
            self.progress.show()
    
    def on_saved(self):
        self.progress.hide()
        
class TabWindow(QtGui.QTabWidget):
    def __init__(self):
        super(TabWindow, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.addTab(PriceTab(), u'株価')

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setCentralWidget(TabWindow())
        self.setWindowTitle(u'jsm')

class Application(QtGui.QApplication):
    def __init__(self):
        super(Application, self).__init__(sys.argv)
        self.win = MainWindow()
        self.win.show()

if __name__ == '__main__':
    Application().exec_()
