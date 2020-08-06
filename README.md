# pyqt5demo

```
非常方便好用的左界面 + 右控制台形式。
python代码中任意print 控制台日志，自动显示在右边控制台中，方便知道点击按钮背后实时发生了什么。
因为做了sys.std 重定向，不需要大幅修改现有代码来实际操作控制台控件,就能达到代码中的任意print和控制台日志自动显示在控制台的效果。
sys.std重定向很重要，就算当前在pyqt客户端类中可以直接操作textEdit控件，更多的被导入的第三方包和模块，对ui控件一无所知，
那些包里面不可能去直接操作ui控件。

由于这个客户端实现了标准输出和错误输出以及异常钩子重写，实现了所有信息显示在右边控制台，所以十分方便程序调试。根本不需要看客户端生成的文件日志。
这个demo可以作为左界面右控制台布局的万能通用pyqt5客户端基类。

实现了客户端重启后加载上一次的值。

```

## 可以运行python脚本和python代码

![Image text](https://i.niupic.com/images/2020/07/28/8sML.png)


## 翻译

![Image text](https://i.niupic.com/images/2020/07/29/8sYi.png)


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
import re
import subprocess
import sys
import time
import threading
from configobj import ConfigObj

from qtui import Ui_MainWindow
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtBoundSignal, QThread
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QLineEdit, QTextEdit, QPlainTextEdit

from nb_log import LoggerMixinDefaultWithFileHandler
from nb_log.monkey_print import reverse_patch_print
import nb_log
from translate_util.translate_tool import translate_other2cn, translate_other2en

reverse_patch_print()
nb_log.nb_log_config_default.DEFAULUT_USE_COLOR_HANDLER = False


def my_excepthook(exc_type, exc_value, tb):
    """
    异常重定向到print，print重定向到控制台，一切信息逃不出控制台。
    :param exc_type:
    :param exc_value:
    :param tb:
    :return:
    """
    msg = ' Traceback (most recent call last):\n'
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        name = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        msg += '   File "%.500s", line %d, in %.500s\n' % (filename, lineno, name)
        tb = tb.tb_next

    msg += ' %s: %s\n' % (exc_type.__name__, exc_value)
    print(msg)


class WindowsClient(QMainWindow, LoggerMixinDefaultWithFileHandler):
    """
    左界面右控制台的，通用客户端基类，重点是吃力了控制台，不带其他逻辑。
    """

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        # 除了控制台以外，在文件中也会记录日志。
        self.file_logger = nb_log.get_logger(f'{self.__class__.__name__}_file', is_add_stream_handler=False,
                                             log_filename=f'{self.__class__.__name__}_file.log', log_path='./')

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

        self.config_ini = ConfigObj("qt_box_values.ini", encoding='UTF8')

        sys.excepthook = my_excepthook  # 错误重定向到print，print重定向到qt界面的控制台，使永远不会发生出错导致闪退。

        self.__init_std()
        self.custom_init()
        self.set_button_click_event()
        self.set_default_value()

        self._init_all_input_box_value()

    def custom_init(self):
        pass

    def set_button_click_event(self):
        pass

    def set_default_value(self):
        pass

    def __init_std(self):
        sys.stdout.write = self._write
        sys.stderr.write = self._write
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
            sys.stdout.write = lambda info: self.file_logger.debug(info)
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
        self.file_logger.debug(info)

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

    def _save_all_input_box_value(self):
        # 客户端退出前保存所有输入框的值到ini文件，使下次重启时候默认加载上一次的值。
        for k, v in self.ui.__dict__.items():
            if k == 'textEdit':  # textEdit这个使代表右边那个黑框控制台，把这个排除在外
                continue
            if isinstance(v, QLineEdit):
                self.config_ini['qt_input_box_valus'][k] = v.text()
            if isinstance(v, (QTextEdit, QPlainTextEdit)):
                self.config_ini['qt_input_box_valus'][k] = v.toPlainText()
            self.config_ini.write()

    def _init_all_input_box_value(self):
        """
        初始化界面的值为上一次客户端关闭之前的值
        :return:
        """
        for k, v in self.ui.__dict__.items():
            try:
                print(f'控件的名字 {k},  控件对象 {v}')
                if isinstance(v, QLineEdit):
                    v.setText(self.config_ini['qt_input_box_valus'][k])
                if isinstance(v, (QTextEdit, QPlainTextEdit)):
                    v.setPlainText(self.config_ini['qt_input_box_valus'][k])
                print(f"成功设置 【{k}】 -- 【{self.config_ini['qt_input_box_valus'][k]}】")
            except KeyError as e:
                print(e)

    def closeEvent(self, event):
        self._save_all_input_box_value()
        reply = QtWidgets.QMessageBox.question(self, '警告', '\n你确认要退出吗？',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class CustomQthread(QThread):
    def __init__(self, parent=None, target=None, args=(), kwargs={}):  # noqa
        super(CustomQthread, self).__init__(parent)
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):
        """Method representing the thread's activity.

        You may override this method in a subclass. The standard run() method
        invokes the callable object passed to the object's constructor as the
        target argument, if any, with sequential and keyword arguments taken
        from the args and kwargs arguments, respectively.

        """
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs


def run_fun_in_new_thread(f, args=()):
    threading.Thread(target=f, args=args).start()


class CustomWindowsClient(WindowsClient, ):

    def set_button_click_event(self):
        self.ui.pushButton.clicked.connect(lambda: run_fun_in_new_thread(self.test_button_fun))
        # self.ui.pushButton.clicked.connect(self.test_button_fun)
        self.ui.pushButton_5.clicked.connect(lambda: run_fun_in_new_thread(self.exec_python_code))  # 运行py代码
        self.ui.pushButton_6.clicked.connect(lambda: run_fun_in_new_thread(self.exec_python_script))  # 运行py脚本

        # 翻译
        self.ui.pushButton_7.clicked.connect(lambda: run_fun_in_new_thread(self.translate_words, args=('baidu',)))
        self.ui.pushButton_8.clicked.connect(lambda: run_fun_in_new_thread(self.translate_words, args=('google',)))
        self.ui.pushButton_9.clicked.connect(lambda: run_fun_in_new_thread(self.translate_words, args=('youdao',)))
        self.ui.pushButton_10.clicked.connect(lambda: run_fun_in_new_thread(self.translate_words, args=('iciba',)))
        self.ui.pushButton_11.clicked.connect(lambda: run_fun_in_new_thread(self.translate_words, args=('all',)))

    def set_default_value(self):
        self.ui.plainTextEdit.setPlainText("""# 可以在这里面写代码。

import time

for xxxx in range(10):
    time.sleep(1)
    print(xxxx)
print('脚本运行完成')""")
        # QLineEdit.setText()
        self.ui.lineEdit.setText(r'F:\coding2\ydfhome\tests\test1.py')
        # self.ui.lineEdit.setText(r'F:\Users\ydf\Desktop\oschina\ydfhome\tests\test1.py')
        self.ui.lineEdit_2.setText(r'F:\coding2\ydfhome')
        # self.ui.plainTextEdit_2.setPlainText("""燕子去了，有再来的时候；杨柳枯了，有再青的时候；桃花谢了，有再开的时候。但是，聪明的你告诉我，我们的日子为什么一去不复返呢？——是有人偷了他们罢：那是谁？又藏在何处呢？是他们自己逃走了罢：现在又到了哪里呢？""")

    def test_button_fun(self):
        for i in range(1, 10):
            self.logger.debug(i)
            self.logger.info(i)
            self.logger.error(i)
            self.logger.warning(i)
            self.logger.critical(i)
            print(i)
            time.sleep(2)
        1 / 0  # 故意错误

    def exec_python_code(self):
        code = self.ui.plainTextEdit.toPlainText()
        msg = f'读取到的要执行的代码是: \n\n - - - - - - - - - - - - - - -   \n {code}  \n - - - - - - - - - - - - - - -  \n\n'
        # self.logger.debug(msg)
        print(msg)
        exec(code)

    def exec_python_script(self):
        # QLineEdit.text()
        script_path = self.ui.lineEdit.text().replace('\\', '/')
        python_path = str(self.ui.lineEdit_2.text()).replace('\\', '/')
        print(script_path)
        print(python_path)
        cmd_str = f'''set PYTHONPATH=%PYTHONPATH%;{python_path} & python {script_path}'''
        print(cmd_str)
        pi = subprocess.Popen(cmd_str.encode('utf8').decode('gbk'), shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, bufsize=1)
        # out, err = pi.communicate()
        # print(out)
        # print(err)
        # for line in err.splitlines():
        #     print(line.decode('utf8'))
        # for line in out.splitlines():
        #     print(line.decode('utf8'))
        empty_line_num = 0
        for line in iter(pi.stdout.readline, "b"):
            # print(line)
            time.sleep(0.1)
            if line != b'':
                empty_line_num = 0
            else:
                empty_line_num += 1
            if empty_line_num > 100:
                break
            try:
                line_str = line.decode('gbk')
            except UnicodeDecodeError:
                try:
                    line_str = line.decode('utf8')
                except UnicodeDecodeError:
                    line_str = line.decode('gb2312')
            if line_str:
                print(line_str)

    def translate_words(self, translate_platx):  # 此函数是演示pyqt按钮传参的典范。
        to_be_translate_words = self.ui.plainTextEdit_2.toPlainText()
        to_be_translate_words_is_cn = False
        for ch in to_be_translate_words:
            if u'\u4e00' <= ch <= u'\u9fff':
                to_be_translate_words_is_cn = True
                break
        """
        for plat in ['google', 'baidu', 'iciba', 'youdao']:
        print(f'{plat}:{translate_other2en(content, plat)}')
        """
        if translate_platx == 'all':
            translate_plat_list = ['baidu', 'google', 'youdao', 'iciba']
        else:
            translate_plat_list = [translate_platx]
        for translate_plat in translate_plat_list:
            # print(f'使用 {translate_plat} 翻译 \n\n {to_be_translate_words} \n\n ')
            print(f'使用 {translate_plat} 翻译中 。。。。。 ')
            t_start = time.time()
            if to_be_translate_words_is_cn:
                result = translate_other2en(to_be_translate_words, platform=translate_plat)
            else:
                result = translate_other2cn(to_be_translate_words, platform=translate_plat)
            print(
                f'翻译耗时 {time.time() - t_start} 秒 ，结果：\n\n {result} \n\n  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n')
            self.ui.plainTextEdit_3.setPlainText(result or '')

    def show(self):
        # ui.tab_5.hide()  不行
        # ui.tab_5.setVisible(False)  #不行
        # self.ui.tabWidget.tabBar().hide()  # 隐藏标签栏

        # 设置icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo1.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.setFixedSize(self.width(), self.height())  # 设置窗口不允许拉伸

        super().show()


if __name__ == '__main__':
    """
    参数 含义
    -F 指定打包后只生成一个exe格式的文件
    -D 创建一个目录，包含exe文件，但会依赖很多文件（默认选项）
    -c 使用控制台，无界面(默认)
    -w 使用窗口，无控制台
    -p 添加搜索路径，让其找到对应的库。
    --icon 改变生成程序的icon图标(图片必须是icon格式的，可以在线转换)

    pyuic5 -o qtui.py qtui.ui
    --add-data "F:\coding2\ydfhome\pyqt项目\pyqt5demo\logo1.ico;logo1.ico"
    pyinstaller -F -w -i logo1.ico -p F:\minicondadir\Miniconda2\envs\py36\Lib\site-packages --nowindowed  qt_app.py
    """
    # F:\Users\ydf\Desktop\oschina\ydfhome\tests\test1.py
    # from qdarkstyle import load_stylesheet_pyqt5

    myapp = QApplication(sys.argv)
    # myapp.setStyleSheet(load_stylesheet_pyqt5())
    client = CustomWindowsClient()
    client.show()
    sys.exit(myapp.exec_())

```