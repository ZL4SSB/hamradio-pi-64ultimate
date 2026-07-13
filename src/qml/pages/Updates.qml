import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        Text {
            text: "Updates"
            color: "#F5F9FB"
            font.pixelSize: 28
            font.bold: true
        }

        Text {
            text: "Update HamRadio-Pi Ultimate and its supporting software."
            color: "#A4B7C2"
            font.pixelSize: 14
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 220
            radius: 10
            color: "#0D202B"
            border.color: "#365E70"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 24

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Text {
                        text: "Installed Version"
                        color: "#AFC1CB"
                        font.pixelSize: 13
                    }

                    Text {
                        text: backend.appVersion
                        color: "#18D6D2"
                        font.pixelSize: 30
                        font.bold: true
                    }

                    Text {
                        Layout.fillWidth: true
                        text: backend.updateStatus
                        color: "#E3EDF2"
                        wrapMode: Text.WordWrap
                    }
                }

                ColumnLayout {
                    spacing: 12

                    Button {
                        Layout.preferredWidth: 245
                        text: "Check for Updates"
                        onClicked: backend.checkForUpdates()
                    }

                    Button {
                        Layout.preferredWidth: 245
                        text: "Update Program"
                        enabled: !backend.updateBusy
                        onClicked: backend.updateProgram()
                    }

                    Button {
                        Layout.preferredWidth: 245
                        text: "Update Dependencies"
                        enabled: !backend.updateBusy
                        onClicked: backend.updateDependencies()
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 150
            radius: 10
            color: "#10212C"
            border.color: "#365E70"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 9

                Text {
                    text: "How updating works"
                    color: "#F5F9FB"
                    font.pixelSize: 18
                    font.bold: true
                }

                Text {
                    Layout.fillWidth: true
                    text: "On Raspberry Pi, Update Program opens the anonymous public installer. On Windows, it opens the newest project ZIP. Dependency Update opens a terminal or command window so progress and any administrator prompt remain visible."
                    color: "#BFD0D8"
                    wrapMode: Text.WordWrap
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
