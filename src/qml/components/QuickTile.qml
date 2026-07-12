import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: root
    property string iconText: ""

    implicitHeight: 62
    hoverEnabled: true

    contentItem: RowLayout {
        spacing: 12

        Text {
            text: root.iconText
            color: "#18D6D2"
            font.pixelSize: 23
            Layout.preferredWidth: 34
        }

        Text {
            Layout.fillWidth: true
            text: root.text
            color: "#F2F7FA"
            font.pixelSize: 15
            font.bold: true
        }

        Text {
            text: "›"
            color: "#E4EDF2"
            font.pixelSize: 25
        }
    }

    background: Rectangle {
        radius: 8
        color: root.hovered ? "#183D4D" : "#12313F"
        border.color: "#26596A"
    }
}
