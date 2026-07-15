import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    property var radio: backend.radioState

    ColumnLayout {
        anchors.fill: parent; spacing: 12
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "Logbook"; color: "#F5F9FB"; font.pixelSize: 28; font.bold: true }
                Text { text: "HRPU local SQLite logbook using the shared radio state."; color: "#A4B7C2"; font.pixelSize: 13 }
            }
            Button { text: "Export ADIF"; onClicked: backend.exportAdif() }
        }

        Rectangle {
            Layout.fillWidth: true; implicitHeight: 138; radius: 10; color: "#0D202B"; border.color: "#365E70"
            GridLayout {
                anchors.fill: parent; anchors.margins: 14; columns: 6; columnSpacing: 8; rowSpacing: 6
                TextField { id: call; placeholderText: "DX callsign"; Layout.fillWidth: true }
                TextField { id: grid; placeholderText: "Grid"; Layout.fillWidth: true }
                TextField { id: sent; placeholderText: "RST sent"; text: "59"; Layout.fillWidth: true }
                TextField { id: rcvd; placeholderText: "RST received"; text: "59"; Layout.fillWidth: true }
                TextField { id: notes; placeholderText: "Notes"; Layout.fillWidth: true }
                Button { text: "ADD QSO"; onClicked: backend.addQso(call.text, grid.text, sent.text, rcvd.text, notes.text) }
                Text { text: "Current radio"; color: "#819AA7" }
                Text { text: radio.frequency + " MHz"; color: "#18D6D2"; font.bold: true }
                Text { text: radio.band; color: "#F5F9FB" }
                Text { text: backend.digitalState.mode; color: "#F0C76D" }
                Item { Layout.columnSpan: 2 }
            }
        }

        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; radius: 10; color: "#0D202B"; border.color: "#365E70"
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 12
                RowLayout {
                    Layout.fillWidth: true
                    Repeater {
                        model: ["UTC","CALL","GRID","BAND","MODE","RST S/R","NOTES"]
                        delegate: Text { required property string modelData; text: modelData; color: "#18D6D2"; font.bold: true; font.pixelSize: 10; Layout.fillWidth: true }
                    }
                }
                ListView {
                    Layout.fillWidth: true; Layout.fillHeight: true; model: backend.logbookRows; clip: true
                    delegate: Rectangle {
                        required property var modelData
                        width: ListView.view.width; height: 34; color: index % 2 ? "#102630" : "#0B202A"
                        RowLayout {
                            anchors.fill: parent; anchors.leftMargin: 5; anchors.rightMargin: 5
                            Text { text: modelData.utc; color: "#AFC1CB"; font.pixelSize: 10; Layout.fillWidth: true; elide: Text.ElideRight }
                            Text { text: modelData.callsign; color: "#18D6D2"; font.bold: true; Layout.fillWidth: true }
                            Text { text: modelData.grid || "—"; color: "#AFC1CB"; Layout.fillWidth: true }
                            Text { text: modelData.band; color: "#F5F9FB"; Layout.fillWidth: true }
                            Text { text: modelData.mode; color: "#F0C76D"; Layout.fillWidth: true }
                            Text { text: (modelData.rst_sent || "—") + " / " + (modelData.rst_received || "—"); color: "#AFC1CB"; Layout.fillWidth: true }
                            Text { text: modelData.notes || ""; color: "#819AA7"; Layout.fillWidth: true; elide: Text.ElideRight }
                        }
                    }
                }
            }
        }
    }
}
