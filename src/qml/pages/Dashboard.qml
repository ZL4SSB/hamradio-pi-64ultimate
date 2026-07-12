import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: content.implicitHeight + 20
        clip: true

        ColumnLayout {
            id: content
            width: parent.width
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: "Dashboard"
                        color: "#F4F8FA"
                        font.pixelSize: 27
                        font.bold: true
                    }
                    Text {
                        text: "Your Raspberry Pi Ham Radio Control Centre"
                        color: "#95ACB9"
                        font.pixelSize: 14
                    }
                }
                Button {
                    text: "⟳  Refresh"
                    onClicked: backend.refreshSystem()
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 4
                columnSpacing: 10
                rowSpacing: 10

                MetricCard {
                    Layout.fillWidth: true
                    title: "CPU"
                    value: backend.cpuTemp
                    detail: "System temperature"
                    iconText: "CPU"
                    valueColor: "#79DF3B"
                }
                MetricCard {
                    Layout.fillWidth: true
                    title: "Memory"
                    value: backend.memoryPercent + "%"
                    detail: "Memory in use"
                    iconText: "RAM"
                    valueColor: "#79DF3B"
                }
                MetricCard {
                    Layout.fillWidth: true
                    title: "Disk"
                    value: backend.diskPercent + "%"
                    detail: backend.diskDetail
                    iconText: "SSD"
                    valueColor: "#79DF3B"
                }
                MetricCard {
                    Layout.fillWidth: true
                    title: "Network"
                    value: backend.online ? "Connected" : "Offline"
                    detail: backend.ipAddress
                    iconText: "NET"
                    valueColor: backend.online ? "#79DF3B" : "#F17982"
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 4
                columnSpacing: 10
                rowSpacing: 10

                MetricCard {
                    Layout.fillWidth: true
                    title: "Pi Model"
                    value: backend.piModel
                    detail: "Hardware platform"
                    iconText: "Pi"
                }
                MetricCard {
                    Layout.fillWidth: true
                    title: "Operating System"
                    value: backend.osName
                    detail: "Current operating system"
                    iconText: "OS"
                }
                MetricCard {
                    Layout.fillWidth: true
                    title: "Callsign"
                    value: backend.callsign
                    detail: "Station identity"
                    iconText: "ID"
                }
                MetricCard {
                    Layout.fillWidth: true
                    title: "Locator"
                    value: backend.locator
                    detail: "Maidenhead grid"
                    iconText: "LOC"
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 104
                radius: 10
                color: "#10212C"
                border.color: "#294A5A"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12

                    Repeater {
                        model: [
                            ["Last Hardware Scan", backend.lastHardwareScan],
                            ["Connected Radios", "0"],
                            ["Connected SDRs", "0"],
                            ["USB Devices", backend.usbDeviceCount],
                            ["Latest Log Entry", backend.latestLog]
                        ]

                        delegate: Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                Text {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    text: modelData[0]
                                    color: "#C9D8E0"
                                    font.pixelSize: 12
                                    font.bold: true
                                }
                                Text {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    text: modelData[1]
                                    color: "#F3F8FA"
                                    font.pixelSize: 15
                                    font.bold: true
                                }
                            }
                            Rectangle {
                                visible: index < 4
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                width: 1
                                color: "#244454"
                            }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 270
                spacing: 10

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 10

                        Text {
                            text: "System Status"
                            color: "#F3F8FA"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Repeater {
                            model: [
                                ["System services", "Running", true],
                                ["Internet connection", backend.online ? "Online" : "Offline", backend.online],
                                ["Package database", "Ready", true],
                                ["Disk health", backend.diskPercent < 90 ? "Good" : "Low Space", backend.diskPercent < 90],
                                ["Memory", backend.memoryPercent < 90 ? "Good" : "High", backend.memoryPercent < 90]
                            ]

                            delegate: RowLayout {
                                Layout.fillWidth: true
                                Rectangle {
                                    width: 15
                                    height: 15
                                    radius: 8
                                    color: modelData[2] ? "#70D93D" : "#F0C76D"
                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData[2] ? "✓" : "!"
                                        color: "#0A161D"
                                        font.pixelSize: 9
                                        font.bold: true
                                    }
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: modelData[0]
                                    color: "#D6E3EA"
                                }
                                Text {
                                    text: modelData[1]
                                    color: modelData[2] ? "#87E54A" : "#F0C76D"
                                    font.bold: true
                                }
                            }
                        }

                        ActionButton {
                            Layout.fillWidth: true
                            text: "System Report"
                            iconText: "▣"
                            onClicked: backend.createSystemReport()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 10

                        Text {
                            text: "Shack Report"
                            color: "#F3F8FA"
                            font.pixelSize: 17
                            font.bold: true
                        }
                        Text {
                            text: "Kia ora " + backend.callsign + "!"
                            color: "#F3F8FA"
                            font.pixelSize: 15
                            font.bold: true
                        }
                        Text {
                            Layout.fillWidth: true
                            text: backend.notification
                            color: "#CBD9E0"
                            wrapMode: Text.WordWrap
                        }
                        Item { Layout.fillHeight: true }
                        ActionButton {
                            Layout.fillWidth: true
                            text: "Scan Hardware"
                            iconText: "⌕"
                            onClicked: backend.scanHardware()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 8

                        Text {
                            text: "Quick Actions"
                            color: "#F3F8FA"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        ActionButton {
                            Layout.fillWidth: true
                            text: "Applications"
                            iconText: "▦"
                            onClicked: backend.setPage("Applications")
                        }
                        ActionButton {
                            Layout.fillWidth: true
                            text: "Hardware Scan"
                            iconText: "⌕"
                            onClicked: {
                                backend.setPage("Hardware")
                                backend.scanHardware()
                            }
                        }
                        ActionButton {
                            Layout.fillWidth: true
                            text: "WPSD Centre"
                            iconText: "▣"
                            onClicked: backend.setPage("WPSD Centre")
                        }
                        ActionButton {
                            Layout.fillWidth: true
                            text: "Propagation"
                            iconText: "☀"
                            onClicked: backend.setPage("Propagation")
                        }
                        ActionButton {
                            Layout.fillWidth: true
                            text: "Updates"
                            iconText: "↻"
                            onClicked: backend.setPage("Updates")
                        }
                    }
                }

                Item {
                    Layout.preferredWidth: 290
                    Layout.fillHeight: true

                    Image {
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        source: backend.assetRoot + "/mascot.png"
                        sourceSize.width: 270
                        sourceSize.height: 270
                        fillMode: Image.PreserveAspectFit
                    }

                    Rectangle {
                        anchors.left: parent.left
                        anchors.bottom: parent.bottom
                        width: 220
                        height: 100
                        radius: 12
                        color: "#F7EED9"
                        border.color: "#D2AD70"

                        Text {
                            anchors.fill: parent
                            anchors.margins: 13
                            text: backend.notification
                            color: "#202020"
                            wrapMode: Text.WordWrap
                            font.pixelSize: 12
                        }
                    }
                }
            }
        }
    }
}
