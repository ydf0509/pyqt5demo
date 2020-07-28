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


