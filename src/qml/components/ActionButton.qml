import QtQuick
import QtQuick.Controls

Button {
    id: root
    property string iconText: ""

    implicitHeight: 42
    hoverEnabled: true

    contentItem: Row {
        spacing: 10
        anchors.left: parent.left
        anchors.leftMargin: 13
        Text {
            anchors.verticalCenter: parent.verticalCenter
            width: 22
            text: root.iconText
            color: "#D7E6ED"
            font.pixelSize: 17
        }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: root.text
            color: "#EEF5F8"
            font.pixelSize: 13
            font.bold: true
        }
    }

    background: Rectangle {
        radius: 7
        color: root.hovered ? "#1A3C4C" : "#132D3A"
        border.color: "#315A6C"
    }
}
