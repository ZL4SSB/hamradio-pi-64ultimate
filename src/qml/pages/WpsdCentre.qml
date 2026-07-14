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
            spacing: 16

            Text {
                text: "WPSD Centre"
                color: "#F5F9FB"
                font.pixelSize: 28
                font.bold: true
            }

            Text {
                Layout.fillWidth: true
                text: "Download, prepare, configure and access WPSD hotspot installations."
                color: "#B8C9D2"
                font.pixelSize: 14
                wrapMode: Text.WordWrap
            }

            GridLayout {
                Layout.fillWidth: true
                columns: width >= 900 ? 3 : 2
                columnSpacing: 14
                rowSpacing: 14

                Repeater {
                    model: [
                        {
                            "title": "Open Local WPSD",
                            "detail": "Open the standard local WPSD dashboard address.",
                            "button": "Open wpsd.local",
                            "action": "local"
                        },
                        {
                            "title": "Radio Dashboards",
                            "detail": "Open configured EuroNode, WPSD or MMDVM dashboards.",
                            "button": "Open Dashboards",
                            "action": "dashboard"
                        },
                        {
                            "title": "WPSD Project",
                            "detail": "Open the official WPSD project website.",
                            "button": "Open Project",
                            "action": "project"
                        },
                        {
                            "title": "Download WPSD",
                            "detail": "Choose the correct official image for your hotspot hardware.",
                            "button": "Open Downloads",
                            "action": "download"
                        },
                        {
                            "title": "Installation Manual",
                            "detail": "Open the official WPSD user manual and installation guide.",
                            "button": "Read Manual",
                            "action": "manual"
                        },
                        {
                            "title": "Raspberry Pi Imager",
                            "detail": "Download the official imaging tool used to write WPSD to a card.",
                            "button": "Open Imager",
                            "action": "imager"
                        },
                        {
                            "title": "Backup HRPU Settings",
                            "detail": "Back up HRPU station and dashboard settings before card work.",
                            "button": "Create Backup",
                            "action": "backup"
                        }
                    ]

                    delegate: Rectangle {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.preferredHeight: 205
                        radius: 10
                        color: "#10212C"
                        border.color: "#365E70"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 18
                            spacing: 9

                            Text {
                                text: modelData.title
                                color: "#18D6D2"
                                font.pixelSize: 18
                                font.bold: true
                            }

                            Text {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                text: modelData.detail
                                color: "#C5D3DA"
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                            }

                            Button {
                                Layout.fillWidth: true
                                text: modelData.button

                                onClicked: {
                                    if (modelData.action === "local")
                                        backend.openLocalWpsd()
                                    else if (modelData.action === "dashboard")
                                        backend.openWpsdDashboard()
                                    else if (modelData.action === "project")
                                        backend.openWpsdProject()
                                    else if (modelData.action === "download")
                                        backend.openWpsdDownloads()
                                    else if (modelData.action === "manual")
                                        backend.openWpsdManual()
                                    else if (modelData.action === "imager")
                                        backend.openRaspberryPiImager()
                                    else if (modelData.action === "backup")
                                        backend.exportPreferences()
                                }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 150
                radius: 10
                color: "#0D202B"
                border.color: "#365E70"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 8

                    Text {
                        text: "Recommended workflow"
                        color: "#F5F9FB"
                        font.pixelSize: 18
                        font.bold: true
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "Download the official WPSD image, write it with Raspberry Pi Imager, complete WPSD first-boot configuration, then add its dashboard address under Radio Dashboards."
                        color: "#BFD0D8"
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }
    }
}
