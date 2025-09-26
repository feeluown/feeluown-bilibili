import os
import importlib

# 新版 FeelUOwn 会在启动的时候，设置这个环境变量
qt_moduel_name = os.getenv('FEELUOWN_QT_API', 'PyQt5')

if qt_moduel_name != 'PyQt5':
    qt_moduel_name = 'PyQt6'

QtCore = importlib.import_module(qt_moduel_name + ".QtCore", package=qt_moduel_name)
QtGui = importlib.import_module(qt_moduel_name + ".QtGui", package=qt_moduel_name)
QtWidgets = importlib.import_module(qt_moduel_name + ".QtWidgets", package=qt_moduel_name)

QLineEdit = QtWidgets.QLineEdit
QLabel = QtWidgets.QLabel
QPushButton = QtWidgets.QPushButton
QDialog = QtWidgets.QDialog
QVBoxLayout = QtWidgets.QVBoxLayout
QFileDialog = QtWidgets.QFileDialog
QMessageBox = QtWidgets.QMessageBox
QInputDialog = QtWidgets.QInputDialog
QFrame = QtWidgets.QFrame
QTabWidget = QtWidgets.QTabWidget
QWidget = QtWidgets.QWidget

pyqtSignal = QtCore.pyqtSignal
QThread = QtCore.QThread
QCloseEvent = QtGui.QCloseEvent

if qt_moduel_name == 'PyQt5':
    RichText = QtCore.Qt.RichText
    Password = QLineEdit.Password
    QAction = QtWidgets.QAction
    TextSelectableByMouse = QtCore.Qt.TextSelectableByMouse
    ActionsContextMenu = QtCore.Qt.ActionsContextMenu
    Dialog = QtCore.Qt.Dialog
    TextBrowserInteraction = QtCore.Qt.TextBrowserInteraction
else:
    RichText = QtCore.Qt.TextFormat.RichText
    Password = QLineEdit.EchoMode.Password
    QAction = QtGui.QAction
    TextSelectableByMouse = QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
    ActionsContextMenu = QtCore.Qt.ContextMenuPolicy.ActionsContextMenu
    Dialog = QtCore.Qt.WindowType.Dialog
    TextBrowserInteraction = QtCore.Qt.TextInteractionFlag.TextBrowserInteraction

