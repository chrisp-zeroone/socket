from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget
from maya import cmds, OpenMayaUI

from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance

import export_x


def main():
    mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QWidget)

    win = MainWindow(mayaMainWindow)
    win.show()
    return win
    # TODO make dockable?
    # win.show(dockable=True)


class CpListWid(QtWidgets.QWidget):
    def __init__(self):
        self.client = export_x.Client()
        QtWidgets.QWidget.__init__(self)

        top_frame = QtWidgets.QFrame(self)
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_frame.setFrameShadow(QtWidgets.QFrame.Raised)

        vb_lay = QtWidgets.QVBoxLayout()
        top_lay = QtWidgets.QVBoxLayout(top_frame)

        hb_lay = QtWidgets.QHBoxLayout()
        con_lay = QtWidgets.QHBoxLayout()
        str_lay = QtWidgets.QHBoxLayout()

        self.add_butt = QtWidgets.QPushButton('Add', self)
        self.rem_butt = QtWidgets.QPushButton('Rem', self)
        self.sin_butt = QtWidgets.QPushButton('Send', self)
        self.str_butt = QtWidgets.QCheckBox('Stream', self)
        self.list_wid = QtWidgets.QListWidget(self)

        self.butt_b = QtWidgets.QDialogButtonBox()
        self.butt_b.setOrientation(QtCore.Qt.Horizontal)
        self.butt_b.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.dis_butt = self.butt_b.addButton('Disconnect', QtWidgets.QDialogButtonBox.ActionRole)
        self.con_butt = self.butt_b.addButton('Connect', QtWidgets.QDialogButtonBox.ActionRole)

        self.list_wid.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        hb_lay.addWidget(self.add_butt)
        hb_lay.addWidget(self.rem_butt)

        top_lay.addWidget(self.list_wid)
        top_lay.addLayout(hb_lay)

        # con_lay.addWidget(self.con_butt)
        # con_lay.addWidget(self.dis_butt)

        str_lay.addWidget(self.sin_butt)
        str_lay.addWidget(self.str_butt)

        vb_lay.addWidget(top_frame)
        vb_lay.addLayout(str_lay)
        # vb_lay.addLayout(con_lay)
        vb_lay.addWidget(self.butt_b)
        self.setLayout(vb_lay)

        self.con_butt.pressed.connect(self.client.connect)
        self.dis_butt.pressed.connect(self.client.disconnect)
        self.add_butt.pressed.connect(self.add_items)
        self.rem_butt.pressed.connect(self.rem_items)
        self.sin_butt.pressed.connect(self.client.send_values)
        self.str_butt.stateChanged.connect(self.do_auto_send)

    def do_auto_send(self, state):
        if state == QtCore.Qt.Checked:
            self.client.auto_send()
        else:
            self.client.del_exp()

    def add_items(self):
        sel_items = cmds.ls(sl=True)
        self.list_wid.addItems(sel_items)
        for item in sel_items:
            self.client.add_item(item)

    def rem_items(self):
        for item in cmds.ls(sl=True):
            self.list_wid.takeItem(self.client.items.index(item))
            self.client.rem_item(item)

class MainWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    NAME = 'Export_X'

    def __init__(self, parent):
        self.deleteInstances()
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setObjectName(self.NAME)
        self.setGeometry(100, 100, 750, 550)
        self.setWindowFlags(QtCore.Qt.Window)

        self.widget = CpListWid()
        self.setCentralWidget(self.widget)

        self.widget.butt_b.rejected.connect(self.close)

    def closeEvent(self, *args):
        self.deleteInstances()
        QtWidgets.QMainWindow.close(self)

    def dockCloseEventTriggered(self):
        self.deleteInstances()

    # Delete any instances of this class
    def deleteInstances(self):
        mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QMainWindow) # Important that it's QMainWindow, and not QWidget/QDialog

        # Go through main window's children to find any previous instances
        for obj in mayaMainWindow.children():
            if type( obj ) == MayaQDockWidget and (obj.widget().objectName() == self.__class__.NAME): # Compare object names
                print 'Deleting instance {0}'.format(obj)
                mayaMainWindow.removeDockWidget(obj) # This will remove from right-click menu, but won't actually delete it! ( still under mainWindow.children() )
                # Delete it for good
                obj.setParent(None)
                obj.deleteLater()

# class MyDockableButton(MayaQWidgetDockableMixin, QtWidgets.QPushButton):
#     def __init__(self, parent=None):
#         super(MyDockableButton, self).__init__(parent=parent)
#         self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred )
#         self.setText('Push Me')

