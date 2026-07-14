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
        color: root.selected
               ? (backend.themeName === "Dark Blue" ? "#245D9B"
                  : backend.themeName === "Radio Green" ? "#247847"
                  : backend.themeName === "Amber Radio" ? "#9A661A"
                  : backend.themeName === "High Contrast" ? "#303030"
                  : "#0E7771")
               : (root.hovered ? "#122C39" : "transparent")
        Rectangle {
            visible: root.selected
            width: 4
            radius: 2
            color: backend.themeName === "Dark Blue" ? "#4DA3FF"
                   : backend.themeName === "Radio Green" ? "#53E58D"
                   : backend.themeName === "Amber Radio" ? "#F0B642"
                   : backend.themeName === "High Contrast" ? "#00FFFF"
                   : "#20C6B3"
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }
    }
}
