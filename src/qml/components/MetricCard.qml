import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    property string title: ""
    property string value: "—"
    property string detail: ""
    property string iconText: "•"
    property color valueColor: "#F3F8FB"

    radius: 10
    color: "#142632"
    border.color: "#2A4B5D"
    border.width: 1
    implicitHeight: 118

    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        Rectangle {
            Layout.preferredWidth: 48
            Layout.preferredHeight: 48
            radius: 8
            color: "#1C3747"
            Text {
                anchors.centerIn: parent
                text: root.iconText
                color: "#20C6B3"
                font.pixelSize: 15
                font.bold: true
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 3
            Text {
                text: root.title
                color: "#B9CCD7"
                font.pixelSize: 13
                font.bold: true
            }
            Text {
                text: root.value
                color: root.valueColor
                font.pixelSize: 25
                font.bold: true
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            Text {
                text: root.detail
                color: "#8FA7B5"
                font.pixelSize: 11
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }
    }
}
