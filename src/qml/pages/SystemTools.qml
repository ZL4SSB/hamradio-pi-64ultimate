import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: pageColumn.implicitHeight + 24
        clip: true

        ColumnLayout {
            id: pageColumn
            width: parent.width
            spacing: 14

            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    Layout.fillWidth: true

                    Text {
                        text: "System Tools"
                        color: "#F5F9FB"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: "Audio, network, storage, USB, diagnostics and updates."
                        color: "#A4B7C2"
                        font.pixelSize: 14
                    }
                }

                Text {
                    text: backend.toolStatus
                    color: "#18D6D2"
                    font.pixelSize: 12
                    elide: Text.ElideRight
                    Layout.maximumWidth: 480
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 360
                radius: 10
                color: "#0D202B"
                border.color: "#365E70"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            Layout.fillWidth: true
                            text: "Audio Test"
                            color: "#F5F9FB"
                            font.pixelSize: 19
                            font.bold: true
                        }

                        Button {
                            text: "Detect Devices"
                            enabled: !backend.audioBusy
                            onClicked: backend.scanAudioDevices()
                        }

                        Button {
                            text: "Test Speakers"
                            enabled: !backend.audioBusy
                            onClicked: backend.testSpeakers()
                        }

                        Button {
                            text: "Test Microphone"
                            enabled: !backend.audioBusy
                            onClicked: backend.testMicrophone()
                        }
                    }

                    ProgressBar {
                        Layout.fillWidth: true
                        indeterminate: true
                        visible: backend.audioBusy
                    }

                    Text {
                        Layout.fillWidth: true
                        text: backend.audioStatus
                        color: "#BFD0D8"
                        font.pixelSize: 13
                        wrapMode: Text.WordWrap
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 12

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 8
                            color: "#102A37"
                            border.color: "#28566A"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 13
                                spacing: 8

                                Text {
                                    text: "Microphones / Inputs"
                                    color: "#18D6D2"
                                    font.pixelSize: 15
                                    font.bold: true
                                }

                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true

                                    ColumnLayout {
                                        width: parent.width
                                        spacing: 6

                                        Repeater {
                                            model: backend.audioInputs

                                            delegate: Rectangle {
                                                required property var modelData
                                                Layout.fillWidth: true
                                                implicitHeight: 52
                                                radius: 6
                                                color: "#143542"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 8
                                                    spacing: 2

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.name
                                                        color: "#F2F7FA"
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                        elide: Text.ElideRight
                                                    }

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.detail
                                                        color: "#93AAB6"
                                                        font.pixelSize: 10
                                                        elide: Text.ElideRight
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 8
                            color: "#102A37"
                            border.color: "#28566A"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 13
                                spacing: 8

                                Text {
                                    text: "Speakers / Outputs"
                                    color: "#18D6D2"
                                    font.pixelSize: 15
                                    font.bold: true
                                }

                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true

                                    ColumnLayout {
                                        width: parent.width
                                        spacing: 6

                                        Repeater {
                                            model: backend.audioOutputs

                                            delegate: Rectangle {
                                                required property var modelData
                                                Layout.fillWidth: true
                                                implicitHeight: 52
                                                radius: 6
                                                color: "#143542"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 8
                                                    spacing: 2

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.name
                                                        color: "#F2F7FA"
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                        elide: Text.ElideRight
                                                    }

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.detail
                                                        color: "#93AAB6"
                                                        font.pixelSize: 10
                                                        elide: Text.ElideRight
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: width >= 900 ? 2 : 1
                columnSpacing: 12
                rowSpacing: 12

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "Network Test"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.networkTestResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Run Network Test"
                            onClicked: backend.runNetworkTest()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "Disk Test"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.diskTestResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Run Disk Test"
                            onClicked: backend.runDiskTest()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "USB Test"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.usbTestResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Scan USB Devices"
                            onClicked: backend.runUsbTest()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "Diagnostics"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.diagnosticsResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        RowLayout {
                            Button {
                                text: "Create Report"
                                onClicked: backend.runDiagnostics()
                            }

                            Button {
                                text: "Open Terminal"
                                onClicked: backend.openTerminal()
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 190
                radius: 10
                color: "#0D202B"
                border.color: "#C99B16"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 20

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 7

                        Text {
                            text: "Program and Dependency Updates"
                            color: "#FFD55A"
                            font.pixelSize: 19
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: backend.updateStatus
                            color: "#DDE8ED"
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "The Raspberry Pi program updater uses the public GitHub ZIP installer and does not require a GitHub account."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }

                    ColumnLayout {
                        spacing: 10

                        Button {
                            Layout.preferredWidth: 220
                            text: "Update Program"
                            enabled: !backend.updateBusy
                            onClicked: backend.updateProgram()
                        }

                        Button {
                            Layout.preferredWidth: 220
                            text: "Update Dependencies"
                            enabled: !backend.updateBusy
                            onClicked: backend.updateDependencies()
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: backend.scanAudioDevices()
}
