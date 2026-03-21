from PySide6 import QtWidgets

from src.register_file_type.register_file_type import (
    is_noui_file_type_registered,
    register_noui_file_type,
)


class NouiFileAssociationPopup(QtWidgets.QDialog):
    """Prompt the user to register .noui files for this app."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Association")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QtWidgets.QVBoxLayout(self)

        message = QtWidgets.QLabel(
            "The .noui file type is not registered for this user.\n"
            "Register it now to open game files directly from Explorer.\n"
            "You can also register it later from the Settings menu in the app.",
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addStretch()

        register_btn = QtWidgets.QPushButton("Ok")
        register_btn.clicked.connect(self._register)

        later_btn = QtWidgets.QPushButton("Not Now")
        later_btn.clicked.connect(self.reject)


        button_row.addWidget(register_btn)
        button_row.addWidget(later_btn)
        layout.addLayout(button_row)

    def _register(self) -> None:
        try:
            register_noui_file_type()
            QtWidgets.QMessageBox.information(
                self,
                "File Association",
                "Registered .noui file association for this user.",
            )
            self.accept()
        except Exception as exc:
            QtWidgets.QMessageBox.warning(
                self,
                "File Association",
                f"Could not register .noui association.\n{exc}",
            )


def show_noui_registration_popup_if_needed(parent=None) -> None:
    """Show startup prompt when .noui association is missing."""
    if is_noui_file_type_registered():
        return

    NouiFileAssociationPopup(parent=parent).exec()

