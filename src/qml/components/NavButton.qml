import QtQuick
import QtQuick.Controls

Button {
    id: root
    property bool selected: false
    property string iconText: ""

    implicitHeight: 46
    hoverEnabled: true
    leftPadding: 16

    contentItem: Row {
        spacing: 12
        Text {
            width: 24
            anchors.verticalCenter: parent.verticalCenter
            text: root.iconText
            color: root.selected ? "white" : "#B9CCD7"
            font.pixelSize: 17
        }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: root.text
            color: root.selected ? "white" : "#D6E3EA"
            font.pixelSize: 14
            font.bold: root.selected
        }
    }

    background: Rectangle {
        radius: 8
        color: root.selected ? "#0E7771" : (root.hovered ? "#122C39" : "transparent")
        Rectangle {
            visible: root.selected
            width: 4
            radius: 2
            color: "#20C6B3"
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }
    }
}
