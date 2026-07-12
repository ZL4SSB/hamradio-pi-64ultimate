APP_QSS = """
QWidget {
    background: #0F1621;
    color: #F1F6FB;
    font-family: "DejaVu Sans";
    font-size: 10pt;
}
QMainWindow, QDialog {
    background: #0F1621;
}
QFrame#Sidebar {
    background: #09111B;
}
QFrame#TopBar {
    background: #121C29;
    border-bottom: 1px solid #2A3D55;
}
QFrame#Card {
    background: #182535;
    border: 1px solid #2A3D55;
    border-radius: 10px;
}
QFrame#SoftCard {
    background: #152131;
    border: 1px solid #24384E;
    border-radius: 8px;
}
QLabel#PageTitle {
    font-size: 22pt;
    font-weight: 700;
}
QLabel#PageSubtitle {
    color: #9CB0C3;
}
QLabel#MetricValue {
    font-size: 20pt;
    font-weight: 700;
}
QLabel#Muted {
    color: #9CB0C3;
}
QLabel#Teal {
    color: #19C2AF;
}
QLabel#Success {
    color: #4BD9A8;
}
QLabel#Warning {
    color: #F0C76D;
}
QLabel#Danger {
    color: #F17982;
}
QLabel#TopMetric {
    color: #D9E6F1;
    font-size: 9pt;
    font-weight: 600;
}
QPushButton {
    background: #0F887C;
    color: white;
    border: none;
    border-radius: 7px;
    padding: 8px 14px;
    font-weight: 700;
}
QPushButton:hover {
    background: #16A596;
}
QPushButton:pressed {
    background: #0D756B;
}
QPushButton[secondary="true"] {
    background: #202F43;
    border: 1px solid #2A3D55;
}
QPushButton[secondary="true"]:hover {
    background: #2A3D55;
}
QPushButton#Donate {
    background: #F4C430;
    color: #111111;
}
QPushButton#Donate:hover {
    background: #FFD95B;
}
QPushButton#NavButton {
    background: transparent;
    text-align: left;
    padding: 11px 14px;
    border-radius: 7px;
}
QPushButton#NavButton:hover {
    background: #132131;
}
QPushButton#NavButton:checked {
    background: #132131;
    border-left: 4px solid #19C2AF;
}
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {
    background: #202F43;
    border: 1px solid #2A3D55;
    border-radius: 7px;
    padding: 7px;
}
QScrollArea {
    border: none;
}
QScrollBar:vertical {
    background: #0F1621;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #0F887C;
    min-height: 28px;
    border-radius: 5px;
}
QProgressBar {
    background: #152131;
    border: 1px solid #2A3D55;
    border-radius: 7px;
    text-align: center;
}
QProgressBar::chunk {
    background: #19C2AF;
    border-radius: 6px;
}
"""
