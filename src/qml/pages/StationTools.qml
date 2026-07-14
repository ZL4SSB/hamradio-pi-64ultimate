import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: page
    property int sectionIndex: 0

    RowLayout {
        anchors.fill: parent
        spacing: 12

        Rectangle {
            Layout.preferredWidth: 220
            Layout.fillHeight: true
            radius: 10
            color: "#0D202B"
            border.color: "#365E70"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 7

                Text {
                    text: "Station Tools"
                    color: "#F5F9FB"
                    font.pixelSize: 22
                    font.bold: true
                }

                Repeater {
                    model: [
                        "Hardware", "Drivers", "Audio", "Time Sync",
                        "Propagation", "Network", "Storage", "Updates",
                        "Diagnostics", "Backup"
                    ]

                    delegate: Button {
                        required property string modelData
                        required property int index
                        Layout.fillWidth: true
                        implicitHeight: 43
                        text: modelData
                        onClicked: page.sectionIndex = index

                        background: Rectangle {
                            radius: 7
                            color: page.sectionIndex === index
                                   ? "#0E7771"
                                   : (parent.hovered ? "#163846" : "#102A36")
                            border.color: page.sectionIndex === index
                                          ? "#26C9BC" : "#28566A"
                        }

                        contentItem: Text {
                            text: parent.text
                            color: "#F4F8FA"
                            font.pixelSize: 13
                            font.bold: page.sectionIndex === index
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: 10
                        }
                    }
                }

                Item { Layout.fillHeight: true }
            }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: page.sectionIndex

            ColumnLayout {
                spacing: 14
                Text { text: "Hardware"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                Text {
                    Layout.fillWidth: true
                    text: "Scan serial interfaces, USB hardware, radios, SDRs and audio devices."
                    color: "#B8C9D2"
                    wrapMode: Text.WordWrap
                }
                RowLayout {
                    Button { text: "Scan Hardware"; onClicked: backend.scanHardware() }
                    Button { text: "Scan USB"; onClicked: backend.runUsbTest() }
                    Button { text: "Detect Audio"; onClicked: backend.scanAudioDevices() }
                }
                Text { text: backend.lastHardwareScan; color: "#E5EEF3"; wrapMode: Text.WordWrap }
                Text { text: backend.usbTestResult; color: "#AFC1CB"; wrapMode: Text.WordWrap }
                Item { Layout.fillHeight: true }
            }

            Flickable {
                contentWidth: width
                contentHeight: driversColumn.implicitHeight + 20
                clip: true

                ColumnLayout {
                    id: driversColumn
                    width: parent.width
                    spacing: 12
                    Text { text: "Drivers"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                    Text {
                        Layout.fillWidth: true
                        text: "Linux uses built-in kernel modules. Windows uses Windows Update or official vendor driver packages."
                        color: "#B8C9D2"
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: [
                            ["FTDI", "ftdi_sio", "FTDI VCP"],
                            ["Prolific PL2303", "pl2303", "Prolific VCP"],
                            ["CH340 / CH341", "ch341", "WCH CH341SER"],
                            ["Silicon Labs CP210x", "cp210x", "Silicon Labs VCP"],
                            ["USB Audio CODEC", "snd-usb-audio", "USB Audio Class"]
                        ]
                        delegate: Rectangle {
                            required property var modelData
                            Layout.fillWidth: true
                            implicitHeight: 76
                            radius: 8
                            color: "#10212C"
                            border.color: "#365E70"
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Text { text: modelData[0]; color: "#F4F8FA"; font.bold: true }
                                    Text {
                                        text: "Linux: " + modelData[1] + "    Windows: " + modelData[2]
                                        color: "#AFC1CB"
                                    }
                                }
                                Text { text: "Supported"; color: "#61DC4C"; font.bold: true }
                            }
                        }
                    }
                }
            }

            SystemTools {}

            ColumnLayout {
                spacing: 14
                Text { text: "Time Synchronisation"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 12
                    Repeater {
                        model: [
                            ["Status", backend.timeSyncStatus],
                            ["Source", backend.timeSyncSource],
                            ["Quality", backend.timeSyncQuality],
                            ["GPS", backend.gpsStatus],
                            ["PPS", backend.ppsStatus]
                        ]
                        delegate: Rectangle {
                            required property var modelData
                            Layout.fillWidth: true
                            implicitHeight: 104
                            radius: 8
                            color: "#10212C"
                            border.color: "#365E70"
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                Text { text: modelData[0]; color: "#18D6D2"; font.bold: true }
                                Text {
                                    Layout.fillWidth: true
                                    text: modelData[1]
                                    color: "#F4F8FA"
                                    font.pixelSize: 17
                                    font.bold: true
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                }
                RowLayout {
                    Button { text: "Check Time"; onClicked: backend.checkTimeSync() }
                    Button { text: "Synchronise Now"; onClicked: backend.syncTimeNow() }
                }
                Item { Layout.fillHeight: true }
            }

            ColumnLayout {
                spacing: 14

                Text {
                    text: "Propagation Server"
                    color: "#F5F9FB"
                    font.pixelSize: 26
                    font.bold: true
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 12

                    Repeater {
                        model: [
                            [
                                "Server",
                                backend.propagationServerStatus
                            ],
                            [
                                "Cluster",
                                backend.propagationClusterStatus
                            ],
                            [
                                "Last update",
                                backend.propagationServerLastUpdate
                            ],
                            [
                                "Spots",
                                String(
                                    backend.propagationSpotCount
                                )
                            ]
                        ]

                        delegate: Rectangle {
                            required property var modelData
                            Layout.fillWidth: true
                            implicitHeight: 105
                            radius: 8
                            color: "#10212C"
                            border.color: "#365E70"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14

                                Text {
                                    text: modelData[0]
                                    color: "#18D6D2"
                                    font.bold: true
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: modelData[1]
                                    color: "#F4F8FA"
                                    font.pixelSize: 17
                                    font.bold: true
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: backend.propagationServerDetail
                    color: "#BFD0D8"
                    wrapMode: Text.WordWrap
                }

                RowLayout {
                    Button {
                        text: "Start"
                        onClicked:
                            backend.startPropagationServer()
                    }

                    Button {
                        text: "Stop"
                        onClicked:
                            backend.stopPropagationServer()
                    }

                    Button {
                        text: "Restart"
                        onClicked:
                            backend.restartPropagationServer()
                    }

                    Button {
                        text: "Refresh Status"
                        onClicked:
                            backend.refreshPropagationServerStatus()
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text:
                        "Internal address: http://127.0.0.1:8765"
                    color: "#8FA7B5"
                    font.pixelSize: 11
                }

                Item {
                    Layout.fillHeight: true
                }
            }

            ColumnLayout {
                spacing: 14
                Text { text: "Network"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                Text { Layout.fillWidth: true; text: backend.networkTestResult; color: "#BFD0D8"; wrapMode: Text.WordWrap }
                Button { text: "Test Cloudflare / Google"; onClicked: backend.runNetworkTest() }
                Item { Layout.fillHeight: true }
            }

            ColumnLayout {
                spacing: 14
                Text { text: "Storage"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                Text { Layout.fillWidth: true; text: backend.diskTestResult; color: "#BFD0D8"; wrapMode: Text.WordWrap }
                Button { text: "Check Disk"; onClicked: backend.runDiskTest() }
                Item { Layout.fillHeight: true }
            }

            ColumnLayout {
                spacing: 14
                Text { text: "Updates"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                Text { Layout.fillWidth: true; text: backend.updateStatus; color: "#BFD0D8"; wrapMode: Text.WordWrap }
                Button { text: "Check for Updates"; onClicked: backend.checkForUpdates() }
                Button { text: "Update Program"; onClicked: backend.updateProgram() }
                Button { text: "Update Dependencies"; onClicked: backend.updateDependencies() }
                Item { Layout.fillHeight: true }
            }

            ColumnLayout {
                spacing: 14
                Text { text: "Diagnostics"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                Text { Layout.fillWidth: true; text: backend.diagnosticsResult; color: "#BFD0D8"; wrapMode: Text.WordWrap }
                RowLayout {
                    Button { text: "Create Report"; onClicked: backend.runDiagnostics() }
                    Button { text: "Reports Folder"; onClicked: backend.openReportsFolder() }
                    Button { text: "Open Terminal"; onClicked: backend.openTerminal() }
                }
                Item { Layout.fillHeight: true }
            }

            ColumnLayout {
                spacing: 14
                Text { text: "Backup & Restore"; color: "#F5F9FB"; font.pixelSize: 26; font.bold: true }
                Text {
                    Layout.fillWidth: true
                    text: "Export settings or create a support bundle before major changes."
                    color: "#B8C9D2"
                    wrapMode: Text.WordWrap
                }
                Button { text: "Export Settings"; onClicked: backend.exportPreferences() }
                Button { text: "Create Support Bundle"; onClicked: backend.createSupportBundle() }
                Button { text: "Open Settings Folder"; onClicked: backend.openSettingsFolder() }
                Item { Layout.fillHeight: true }
            }
        }
    }

    Component.onCompleted: backend.checkTimeSync()
}
