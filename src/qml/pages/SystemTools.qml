import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: page
    property int section: 0

    RowLayout {
        anchors.fill: parent
        spacing: 14

        Rectangle {
            Layout.preferredWidth: 225
            Layout.fillHeight: true
            radius: 10
            color: "#0D202B"
            border.color: "#365E70"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 7

                Text {
                    text: "System Tools"
                    color: "#F5F9FB"
                    font.pixelSize: 22
                    font.bold: true
                }

                Repeater {
                    model: [
                        "Hardware Manager",
                        "Audio & Diagnostics",
                        "Station Profile",
                        "Preferences",
                        "Radio Audio Profile"
                    ]

                    delegate: Button {
                        required property string modelData
                        required property int index
                        Layout.fillWidth: true
                        implicitHeight: 44
                        text: modelData
                        onClicked: page.section = index

                        background: Rectangle {
                            radius: 7
                            color: page.section === index
                                   ? "#0E7771"
                                   : (parent.hovered ? "#163846" : "#102A36")
                            border.color: page.section === index
                                          ? "#26C9BC" : "#28566A"
                        }

                        contentItem: Text {
                            text: parent.text
                            color: "#F4F8FA"
                            font.pixelSize: 13
                            font.bold: page.section === index
                            leftPadding: 10
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }

                Item { Layout.fillHeight: true }
            }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: page.section

            Hardware {}
            SystemDiagnostics {}
            Station {}
            Preferences {}

            Rectangle {
                color: "transparent"
                property var radio: backend.radioState

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 14

                    Text {
                        text: "Radio Audio Profile"
                        color: "#F5F9FB"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: "Associate RX/TX audio routing with the shared HRPU radio state."
                        color: "#A4B7C2"
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 410
                        radius: 10
                        color: "#0D202B"
                        border.color: "#365E70"

                        GridLayout {
                            anchors.fill: parent
                            anchors.margins: 20
                            columns: 2
                            rowSpacing: 12
                            columnSpacing: 14

                            Text { text: "RX audio device"; color: "#AFC1CB" }
                            TextField { id: rxDevice; text: parent.parent.radio.audio_rx; Layout.fillWidth: true }

                            Text { text: "RX channel"; color: "#AFC1CB" }
                            ComboBox { id: rxChannel; model: ["Left","Right","Mono Mix"]; Layout.fillWidth: true }

                            Text { text: "RX gain"; color: "#AFC1CB" }
                            Slider { id: rxGain; from: -30; to: 30; value: parent.parent.radio.rx_gain_db; Layout.fillWidth: true }

                            Text { text: "TX audio device"; color: "#AFC1CB" }
                            TextField { id: txDevice; text: parent.parent.radio.audio_tx; Layout.fillWidth: true }

                            Text { text: "TX channel"; color: "#AFC1CB" }
                            ComboBox { id: txChannel; model: ["Left","Right","Mono Mix"]; Layout.fillWidth: true }

                            Text { text: "TX level"; color: "#AFC1CB" }
                            Slider { id: txLevel; from: 0; to: 100; value: parent.parent.radio.tx_level; Layout.fillWidth: true }

                            Item {}
                            Button {
                                text: "Save Radio Audio Profile"
                                onClicked: backend.saveRadioAudioProfile(
                                    rxDevice.text,
                                    txDevice.text,
                                    rxChannel.currentText,
                                    txChannel.currentText,
                                    rxGain.value,
                                    txLevel.value
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
