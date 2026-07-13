import QtQuick
import QtQuick.Controls

TextField {
    id: control

    implicitHeight: 42
    leftPadding: 12
    rightPadding: 12

    color: "#162630"
    selectionColor: "#0D8C88"
    selectedTextColor: "#FFFFFF"
    placeholderTextColor: "#667985"
    font.pixelSize: 14

    background: Rectangle {
        radius: 7
        color: control.activeFocus ? "#F7FAFC" : "#EEF3F6"
        border.width: control.activeFocus ? 2 : 1
        border.color: control.activeFocus ? "#19C2AF" : "#8EA4B0"
    }
}
