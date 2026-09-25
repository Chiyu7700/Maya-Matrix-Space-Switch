from PySide6 import QtWidgets


class SpaceSwitchUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Maya Matrix Space Swich")
        self.setMinimumWidth(320)

        self.setup_ui()

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


def show_ui():
    window = SpaceSwitchUI()
    window.show()