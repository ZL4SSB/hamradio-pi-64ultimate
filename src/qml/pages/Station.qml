import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        Text {
            text: "Callsign & Station"
            color: "#F4F8FA"
            font.pixelSize: 27
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 240
            radius: 10
            color: "#10212C"
            border.color: "#294A5A"

            GridLayout {
                anchors.fill: parent
                anchors.margins: 20
                columns: 2
                columnSpacing: 18
                rowSpacing: 14

                Label { text: "Callsign" }
                TextField {
                    id: callsign
                    Layout.fillWidth: true
                    text: backend.callsign === "Not configured" ? "" : backend.callsign
                }

                Label { text: "Maidenhead locator" }
                TextField {
                    id: locator
                    Layout.fillWidth: true
                    text: backend.locator === "Not configured" ? "" : backend.locator
                }

                Item { Layout.fillWidth: true }
                Button {
                    text: "Save Station Details"
                    onClicked: backend.saveStation(callsign.text, locator.text)
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
