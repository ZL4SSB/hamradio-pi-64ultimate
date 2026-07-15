import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    property var radio: backend.radioState
    property var broker: backend.catBroker

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "Radio"; color: "#F5F9FB"; font.pixelSize: 28; font.bold: true }
                Text { text: "One shared HRPU radio state for CAT, Digital, Map, Logbook and hardware."; color: "#A4B7C2"; font.pixelSize: 13 }
            }
            Rectangle {
                radius: 8; implicitWidth: 116; implicitHeight: 34
                color: radio.cat_connected ? "#153B28" : "#3A3018"
                border.color: radio.cat_connected ? "#61DC4C" : "#F0C76D"
                Text { anchors.centerIn: parent; text: radio.cat_connected ? "CAT CONNECTED" : "CAT PREVIEW"; color: "#F5F9FB"; font.pixelSize: 10; font.bold: true }
            }
        }

        Rectangle {
            Layout.fillWidth: true; implicitHeight: 190; radius: 12
            color: "#0B202A"; border.color: "#2B667A"
            RowLayout {
                anchors.fill: parent; anchors.margins: 22; spacing: 20
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: radio.radio_name; color: "#8FA7B5"; font.pixelSize: 13 }
                    Text { text: radio.frequency + " MHz"; color: "#F5F9FB"; font.pixelSize: 44; font.bold: true }
                    RowLayout {
                        Text { text: radio.band; color: "#18D6D2"; font.pixelSize: 18; font.bold: true }
                        Text { text: radio.mode; color: "#F0C76D"; font.pixelSize: 18; font.bold: true }
                        Text { text: "VFO " + radio.vfo; color: "#AFC1CB"; font.pixelSize: 14 }
                        Text { text: radio.split ? "SPLIT" : "SIMPLEX"; color: radio.split ? "#F0C76D" : "#8FA7B5"; font.pixelSize: 12 }
                    }
                }
                Rectangle {
                    width: 110; height: 110; radius: 55
                    color: radio.ptt ? "#67252C" : "#143B2B"
                    border.color: radio.ptt ? "#F17982" : "#61DC4C"; border.width: 2
                    Text { anchors.centerIn: parent; text: radio.ptt_label; color: "#F5F9FB"; font.pixelSize: 30; font.bold: true }
                    MouseArea { anchors.fill: parent; onClicked: backend.setRadioPtt(!radio.ptt) }
                }
            }
        }

        GridLayout {
            Layout.fillWidth: true; columns: 2; columnSpacing: 14; rowSpacing: 14

            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 290; radius: 10; color: "#0D202B"; border.color: "#365E70"
                GridLayout {
                    anchors.fill: parent; anchors.margins: 18; columns: 2; rowSpacing: 10; columnSpacing: 12
                    Text { text: "Radio Context"; color: "#F5F9FB"; font.pixelSize: 18; font.bold: true; Layout.columnSpan: 2 }
                    Text { text: "Frequency MHz"; color: "#AFC1CB" }
                    TextField { id: freq; text: radio.frequency; Layout.fillWidth: true }
                    Text { text: "Mode"; color: "#AFC1CB" }
                    ComboBox { id: mode; model: ["LSB","USB","CW","CW-R","AM","FM","USB-D","LSB-D","DIGU","DIGL"]; Layout.fillWidth: true }
                    Button { text: "Apply"; onClicked: { backend.setRadioFrequency(parseFloat(freq.text)); backend.setRadioMode(mode.currentText) } }
                    CheckBox { text: "Split"; checked: radio.split; onClicked: backend.setRadioSplit(checked) }
                }
            }

            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 290; radius: 10; color: "#0D202B"; border.color: "#365E70"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 18; spacing: 9
                    Text { text: "HRPU CAT Broker"; color: "#F5F9FB"; font.pixelSize: 18; font.bold: true }
                    Text { text: broker.status + " — " + broker.detail; color: "#AFC1CB"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    Text { text: "Endpoint  " + broker.host + ":" + broker.port; color: "#18D6D2" }
                    Text { text: "Hamlib detected: " + (broker.hamlib_available ? "Yes" : "No"); color: "#AFC1CB" }
                    Button { text: "Probe CAT Backend"; onClicked: backend.probeCatBroker() }
                    RowLayout {
                        TextField { id: clientName; placeholderText: "External client name"; Layout.fillWidth: true }
                        Button { text: "Register Client"; onClicked: backend.registerCatClient(clientName.text) }
                    }
                    ListView {
                        Layout.fillWidth: true; Layout.fillHeight: true; model: broker.clients; clip: true
                        delegate: Text { required property var modelData; width: ListView.view.width; text: "● " + modelData.name + "   since " + modelData.since; color: "#61DC4C"; height: 24 }
                    }
                }
            }
        }
    }
}
