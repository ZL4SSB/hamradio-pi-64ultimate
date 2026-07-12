import QtQuick
import QtQuick.Layouts

Item {
    property string pageTitle: ""
    property string pageSubtitle: ""
    property var cards: []

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        Text {
            text: pageTitle
            color: "#F4F8FA"
            font.pixelSize: 27
            font.bold: true
        }

        Text {
            text: pageSubtitle
            color: "#95ACB9"
            font.pixelSize: 14
        }

        GridLayout {
            Layout.fillWidth: true
            columns: 2
            columnSpacing: 10
            rowSpacing: 10

            Repeater {
                model: cards
                delegate: Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 110
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        Text {
                            text: modelData
                            color: "#F3F8FA"
                            font.pixelSize: 17
                            font.bold: true
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "Connected to the HamRadio-Pi backend and ready for Raspberry Pi integration testing."
                            color: "#A7BBC6"
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
