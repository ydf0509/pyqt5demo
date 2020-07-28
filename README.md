# pyqt5demo

```
非常方便好用的左界面 + 右控制台形式。

python代码中任意print 控制台日志，自动显示在右边控制台中，方便知道点击按钮背后实时发生了什么。

因为做了sys.std 重定向，不需要大幅修改现有代码来实际操作控制台控件,就能达到代码中的任意print和控制台日志自动显示在控制台的效果。

这个demo可以作为左界面右控制台布局的万能通用pyqt5客户端基类。

```

## 可以运行python脚本和python代码

![Image text](https://i.niupic.com/images/2020/07/28/8sML.png)


## 翻译

![Image text](http://www.kupan123.com/upload/1595908539x-1404755401.png)


## 文件介绍

```
qtui.ui是用qtdesigner布局的。
qtui.py是使用 pyuic5 -o qtui.py qtui.ui 生成的。

qt_app.py是手写的。

WindowsClient是只实现了控制台的 客户端基类，因为这种左界面 又控制台的布局形式太有必要了。

CustomWindowsClient是继承自WindowsClient的，主要是实现了

1）运行python脚本或者运行python代码

2）使用4个平台的翻译，能够中英文自动识别，需要翻译成什么。

```


## 带控制台的客户端基类的实现。

```python

class WindowsClient(QMainWindow, ):
    """
    左界面右控制台的，通用客户端基类，重点是吃力了控制台，不带其他逻辑。
    """

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)

        """
               # 这个用组合的形式，来访问控件。

               网上有的是用继承方式，让WindowsClient同时也继承Ui_MainWindow，那么这两行

               self.ui = Ui_MainWindow()  
               self.ui.setupUi(self)

               就成了一行，变成 self.setupUi(self) 然后用self.pushButtonxx 来访问控件。
               现在方式self.ui.pushButtonxx来访问控件，这种pycahrm自动补全范围更小，使用更清晰。

        """
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._now_is_stop_print = False
        self._len_textEdit = 0

        self.ui.pushButton_3.clicked.connect(self._stop_or_start_print)
        self.ui.pushButton_4.clicked.connect(self._clear_text_edit)

        self.__init_std()
        self.custom_init()
        self.set_button_click_event()
        self.set_default_value()

    def custom_init(self):
        pass

    def set_button_click_event(self):
        pass

    def set_default_value(self):
        pass

    def __init_std(self):
        sys.stdout.write = self._write
        # sys.stderr.write = self._write
        print('重定向了print到textEdit ,这个print应该显示在右边黑框。')

    def _stop_or_start_print(self):
        if self._now_is_stop_print is False:
            self._now_is_stop_print = True
            self.ui.pushButton_3.setText('暂停控制台打印')
            self.ui.pushButton_3.setStyleSheet('''
            
            color: rgb(255, 255, 255);
            font: 9pt "楷体";
            background-color: rgb(255, 8, 61);
                        ''')
            sys.stdout.write = self._pause_write
        else:
            self._now_is_stop_print = False
            self.ui.pushButton_3.setText('控制台打印中')
            self.ui.pushButton_3.setStyleSheet('''
            background-color: rgb(0, 173, 0);
            color: rgb(255, 255, 255);
            font: 9pt "楷体";
            ''')
            sys.stdout.write = self._write

    def _write(self, info):
        """
        这个是关键，普通print是如何自动显示在右边界面的黑框的。
          https://blog.csdn.net/LaoYuanPython/article/details/105317746
          :return:
        """
        # self.ui.textEdit.insertPlainText(info)
        # if len(self.ui.textEdit.toPlainText()) > 50000:
        #     self.textEdit.setPlainText('')
        self._len_textEdit += len(info)
        if self._len_textEdit > 50000:
            self.ui.textEdit.setText(' ')
            self._len_textEdit = 0
        cursor = self.ui.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(info)
        self.ui.textEdit.setTextCursor(cursor)
        self.ui.textEdit.ensureCursorVisible()
        QtWidgets.qApp.processEvents(
            QtCore.QEventLoop.ExcludeUserInputEvents | QtCore.QEventLoop.ExcludeSocketNotifiers)

    @staticmethod
    def _do_away_with_color(info: str):
        info = info.replace('\033[0;34m', '').replace('\033[0;30;44m', '')
        info = re.sub(r"\033\[0;.{1,7}m", '', info)
        info = info.replace('\033[0m', '')
        return info

    def _clear_text_edit(self):
        """
        清除控制台信息
        :return:
        """
        self.ui.textEdit.setText(' ')
        self._len_textEdit = 0

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, '警告', '\n你确认要退出吗？',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

```