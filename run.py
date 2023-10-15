import sys

from PyQt6.QtWidgets import QApplication

from nestui.__main__ import ToolboxUI

app = QApplication(sys.argv)
app.setStyle("Fusion")

main = ToolboxUI()
main.show()
main.resize(200,400)
sys.exit(app.exec())