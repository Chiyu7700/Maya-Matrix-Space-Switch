from PySide6 import QtWidgets
from shiboken6 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import SS_Core


#get maya main window so the ui stays on top of it
def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


class SpaceSwitchUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Maya Matrix Space Switch")
        self.setMinimumWidth(320)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        space_label = QtWidgets.QLabel("Target Spaces:")
        main_layout.addWidget(space_label)

        self.space_list = QtWidgets.QListWidget()
        self.space_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        main_layout.addWidget(self.space_list)

        space_btn_layout = QtWidgets.QHBoxLayout()
        self.add_space_btn = QtWidgets.QPushButton("Add Selected")
        self.remove_space_btn = QtWidgets.QPushButton("Remove")

        space_btn_layout.addWidget(self.add_space_btn)
        space_btn_layout.addWidget(self.remove_space_btn)
        main_layout.addLayout(space_btn_layout)

        ctrl_label = QtWidgets.QLabel("Control to Drive:")
        main_layout.addWidget(ctrl_label)

        ctrl_layout = QtWidgets.QHBoxLayout()
        self.ctrl_field = QtWidgets.QLineEdit()
        self.ctrl_field.setPlaceholderText("Select the control...")
        self.ctrl_field.setReadOnly(True)

        self.set_ctrl_btn = QtWidgets.QPushButton("<<")
        self.set_ctrl_btn.setToolTip("Set from active selection")
        self.set_ctrl_btn.setFixedWidth(40)

        ctrl_layout.addWidget(self.ctrl_field)
        ctrl_layout.addWidget(self.set_ctrl_btn)
        main_layout.addLayout(ctrl_layout)

        main_layout.addSpacing(10)

        self.build_btn = QtWidgets.QPushButton("Build Space Switch")
        self.build_btn.setMinimumHeight(35)
        main_layout.addWidget(self.build_btn)

        main_layout.addSpacing(10)

        switch_label = QtWidgets.QLabel("Switch Space:")
        main_layout.addWidget(switch_label)

        switch_layout = QtWidgets.QHBoxLayout()
        self.space_combo = QtWidgets.QComboBox()
        self.key_check = QtWidgets.QCheckBox("Key")
        self.key_check.setToolTip("Key the switch on the current frame")
        self.switch_btn = QtWidgets.QPushButton("Switch")

        switch_layout.addWidget(self.space_combo, 1)
        switch_layout.addWidget(self.key_check)
        switch_layout.addWidget(self.switch_btn)
        main_layout.addLayout(switch_layout)

    def connect_signals(self):
        self.add_space_btn.clicked.connect(self.add_spaces)
        self.remove_space_btn.clicked.connect(self.remove_spaces)
        self.set_ctrl_btn.clicked.connect(self.set_ctrl)
        self.build_btn.clicked.connect(self.build)
        self.switch_btn.clicked.connect(self.switch_space)

    def get_spaces(self):
        return [self.space_list.item(i).text() for i in range(self.space_list.count())]

    #add selected objects to the list, skip ones already in there
    def add_spaces(self):
        current = self.get_spaces()
        for obj in cmds.ls(selection=True, transforms=True):
            if obj not in current:
                self.space_list.addItem(obj)

    def remove_spaces(self):
        for item in self.space_list.selectedItems():
            self.space_list.takeItem(self.space_list.row(item))

    def set_ctrl(self):
        sel = cmds.ls(selection=True, transforms=True)
        if not sel:
            cmds.warning("Select a control first")
            return
        self.ctrl_field.setText(sel[0])
        self.refresh_switch_spaces()

    def build(self):
        spaces = self.get_spaces()
        ctrl = self.ctrl_field.text()

        if not spaces or not ctrl:
            cmds.warning("Need at least one space and a control")
            return
        if ctrl in spaces:
            cmds.warning("The control can't be one of its own spaces")
            return
        if cmds.attributeQuery("space", node=ctrl, exists=True):
            cmds.warning(f"{ctrl} already has a space attribute")
            return

        SS_Core.build_space_switch(spaces, ctrl)
        print(f"Built space switch on {ctrl}")
        self.refresh_switch_spaces()

    #fill the dropdown with the spaces from the ctrl's enum
    def refresh_switch_spaces(self):
        self.space_combo.clear()
        ctrl = self.ctrl_field.text()
        if not cmds.objExists(ctrl) or not cmds.attributeQuery("space", node=ctrl, exists=True):
            return

        enum_names = cmds.attributeQuery("space", node=ctrl, listEnum=True)[0]
        self.space_combo.addItems(enum_names.split(":"))
        self.space_combo.setCurrentIndex(cmds.getAttr(ctrl + ".space"))

    def switch_space(self):
        ctrl = self.ctrl_field.text()
        if self.space_combo.count() == 0 or not cmds.objExists(ctrl):
            cmds.warning("Build a space switch on the control first")
            return

        SS_Core.match_switch(ctrl, self.space_combo.currentIndex(), key=self.key_check.isChecked())


#keep a reference so the window doesnt get garbage collected
space_switch_window = None

def show_ui():
    global space_switch_window

    if space_switch_window:
        space_switch_window.close()
        space_switch_window.deleteLater()

    space_switch_window = SpaceSwitchUI(get_maya_window())
    space_switch_window.show()
