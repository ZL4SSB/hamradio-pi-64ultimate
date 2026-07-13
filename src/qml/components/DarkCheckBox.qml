import QtQuick
import QtQuick.Controls

CheckBox {
    id: control

    spacing: 10

    indicator: Rectangle {
        implicitWidth: 22
        implicitHeight: 22
        x: control.leftPadding
        y: parent.height / 2 - height / 2
        radius: 5
        color: control.checked ? "#16AFA5" : "#EEF3F6"
        border.width: 1
        border.color: control.checked ? "#4CE1D5" : "#8EA4B0"

        Text {
            anchors.centerIn: parent
            visible: control.checked
            text: "✓"
            color: "#FFFFFF"
            font.pixelSize: 15
            font.bold: true
        }
    }

    contentItem: Text {
        leftPadding: control.indicator.width + control.spacing
        text: control.text
        color: "#E5EEF3"
        font.pixelSize: 14
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WordWrap
    }
}
