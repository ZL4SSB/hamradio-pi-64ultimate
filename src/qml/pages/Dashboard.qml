import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: dashboard.implicitHeight + 18
        clip: true

        ColumnLayout {
            id: dashboard
            width: parent.width
            spacing: 12

            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: "Dashboard"
                        color: "#F5F9FB"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: "Overview of your Ham Radio Pi system"
                        color: "#A4B7C2"
                        font.pixelSize: 14
                    }
                }

                Text {
                    text: "◷  " + backend.currentDateTime
                    color: "#E7EFF3"
                    font.pixelSize: 13
                }

                Rectangle {
                    radius: 8
                    color: "#0A482C"
                    implicitWidth: 124
                    implicitHeight: 38

                    Text {
                        anchors.centerIn: parent
                        text: "System Ready"
                        color: "#9AF176"
                        font.pixelSize: 13
                        font.bold: true
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 270
                radius: 10
                color: "#0D202B"
                border.color: "#285263"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 18

                    ColumnLayout {
                        Layout.preferredWidth: 345
                        Layout.minimumWidth: 300
                        Layout.fillHeight: true
                        spacing: 9

                        Text {
                            text: "Station Profile"
                            color: "#18D6D2"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        InfoRow { label: "Callsign:"; value: backend.callsign; iconText: "♧" }
                        InfoRow { label: "Locator:"; value: backend.locator; iconText: "⌖" }
                        InfoRow { label: "Operator:"; value: backend.operatorName; iconText: "♙" }
                        InfoRow { label: "QTH:"; value: backend.qth; iconText: "⌾" }
                        InfoRow { label: "DMR ID:"; value: backend.dmrId; iconText: "▦" }

                        Item { Layout.fillHeight: true }

                        Button {
                            text: "♙  Edit Profile"
                            onClicked: backend.setPage("Station Profile")
                        }
                    }

                    Rectangle {
                        Layout.preferredWidth: 1
                        Layout.fillHeight: true
                        color: "#214654"
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 3
                        columnSpacing: 18

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 150
                            spacing: 10

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "▣"
                                color: "#18D6D2"
                                font.pixelSize: 44
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "CPU Temperature"
                                color: "#D8E5EC"
                                font.pixelSize: 14
                                font.bold: true
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: backend.cpuTemp
                                color: "#F5F9FB"
                                font.pixelSize: 28
                                font.bold: true
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "Normal"
                                color: "#61DC4C"
                                font.pixelSize: 13
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 150
                            spacing: 10

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "◴"
                                color: "#18D6D2"
                                font.pixelSize: 44
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "System Load"
                                color: "#D8E5EC"
                                font.pixelSize: 14
                                font.bold: true
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: backend.systemLoad
                                color: "#F5F9FB"
                                font.pixelSize: 28
                                font.bold: true
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.maximumWidth: 180
                                text: backend.loadDetail
                                color: "#61DC4C"
                                font.pixelSize: 12
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.WordWrap
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 165
                            spacing: 10

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "▤"
                                color: "#18D6D2"
                                font.pixelSize: 44
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "Disk Usage"
                                color: "#D8E5EC"
                                font.pixelSize: 14
                                font.bold: true
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: backend.diskPercent + "%"
                                color: "#F5F9FB"
                                font.pixelSize: 28
                                font.bold: true
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.maximumWidth: 190
                                text: backend.diskDetail
                                color: "#61DC4C"
                                font.pixelSize: 12
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    Rectangle {
                        Layout.preferredWidth: 1
                        Layout.fillHeight: true
                        color: "#214654"
                    }

                    Item {
                        Layout.preferredWidth: 245
                        Layout.minimumWidth: 210
                        Layout.fillHeight: true

                        Image {
                            anchors.centerIn: parent
                            anchors.horizontalCenterOffset: 16
                            anchors.verticalCenterOffset: -18
                            width: Math.min(parent.width - 34, 212)
                            height: Math.min(parent.height - 44, 194)
                            source: backend.assetRoot + "/dashboard-wordmark-clean.png"
                            fillMode: Image.PreserveAspectFit
                            sourceSize.width: 430
                            sourceSize.height: 330
                            smooth: true
                            mipmap: true
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 358
                spacing: 12

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 10
                    color: "#0D202B"
                    border.color: "#285263"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "Quick Actions"
                            color: "#F5F9FB"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 2
                            columnSpacing: 14
                            rowSpacing: 12

                            QuickTile {
                                Layout.fillWidth: true
                                text: "Applications"
                                iconText: "▦"
                                onClicked: backend.setPage("Applications")
                            }
                            QuickTile {
                                Layout.fillWidth: true
                                text: "Hardware Scan"
                                iconText: "⌕"
                                onClicked: {
                                    backend.setPage("Station Tools")
                                    backend.scanHardware()
                                }
                            }
                            QuickTile {
                                Layout.fillWidth: true
                                text: "WPSD Centre"
                                iconText: "▣"
                                onClicked: backend.setPage("WPSD Centre")
                            }
                            QuickTile {
                                Layout.fillWidth: true
                                text: "Propagation"
                                iconText: "⌁"
                                onClicked: backend.setPage("Propagation")
                            }
                            QuickTile {
                                Layout.fillWidth: true
                                text: "System Tools"
                                iconText: "⚙"
                                onClicked: backend.setPage("Station Tools")
                            }
                            QuickTile {
                                Layout.fillWidth: true
                                text: "System Report"
                                iconText: "▤"
                                onClicked: backend.createSystemReport()
                            }
                            QuickTile {
                                Layout.fillWidth: true
                                text: "Shack Clock"
                                iconText: "◷"
                                onClicked: backend.setPage("Shack Clock")
                            }
                            QuickTile {
                                Layout.fillWidth: true
                                text: "Check Updates"
                                iconText: "⇩"
                                onClicked: backend.checkForUpdates()
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 10
                    color: "#0D202B"
                    border.color: "#285263"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 10

                        Text {
                            text: "System Information"
                            color: "#F5F9FB"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        InfoRow { label: "Hostname:"; value: backend.hostname; iconText: "▱" }
                        InfoRow { label: "Operating System:"; value: backend.osName; iconText: "♜" }
                        InfoRow { label: "Kernel:"; value: backend.kernel; iconText: ">_" }
                        InfoRow { label: "Uptime:"; value: backend.uptime; iconText: "◷" }
                        InfoRow { label: "Local IP:"; value: backend.ipAddress; iconText: "⌘" }
                        InfoRow { label: "CPU:"; value: backend.piModel; iconText: "▣" }
                        InfoRow { label: "Memory:"; value: backend.memoryDetail + " (" + backend.memoryPercent + "%)"; iconText: "▤" }
                        InfoRow { label: "SD Card:"; value: backend.sdCard; iconText: "▱" }
                        InfoRow { label: "Last Boot:"; value: backend.lastBoot; iconText: "◴" }

                        Item { Layout.fillHeight: true }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 210
                spacing: 12

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 10
                    color: "#0D202B"
                    border.color: "#285263"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "Active Services"
                            color: "#F5F9FB"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 4
                            columnSpacing: 10
                            rowSpacing: 10

                            Repeater {
                                model: backend.activeServices

                                delegate: ServiceChip {
                                    required property var modelData
                                    Layout.fillWidth: true
                                    serviceName: modelData.name
                                    running: modelData.running
                                }
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Button {
                            text: "⚙  Manage Services"
                            onClicked: backend.setPage("Station Tools")
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 10
                    color: "#0D202B"
                    border.color: "#285263"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 9

                        Text {
                            text: "Recent Activity"
                            color: "#F5F9FB"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Repeater {
                            model: backend.recentActivity

                            delegate: RowLayout {
                                required property var modelData
                                Layout.fillWidth: true

                                Text {
                                    text: "●"
                                    color: "#61DC4C"
                                    font.pixelSize: 14
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: modelData.message
                                    color: "#E2EBF0"
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }

                                Text {
                                    text: modelData.time
                                    color: "#A8BAC4"
                                    font.pixelSize: 11
                                }
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Button {
                            text: "▤  View Full Log"
                            onClicked: backend.openActivityLog()
                        }
                    }
                }
            }
        }
    }
}
