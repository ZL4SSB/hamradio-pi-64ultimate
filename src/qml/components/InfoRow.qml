import QtQuick
import QtQuick.Layouts

RowLayout {
    id: root
    property string label: ""
    property string value: ""
    property string iconText: "•"

    spacing: 8

    Text {
        text: root.iconText
        color: "#C9D8E0"
        font.pixelSize: 14
        Layout.preferredWidth: 22
    }

    Text {
        text: root.label
        color: "#C9D8E0"
        font.pixelSize: 13
        Layout.preferredWidth: 150
    }

    Text {
        Layout.fillWidth: true
        text: root.value
        color: "#F3F8FA"
        font.pixelSize: 13
        font.bold: true
        elide: Text.ElideRight
    }
}
