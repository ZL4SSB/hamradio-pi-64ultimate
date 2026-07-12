import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "pages"

ApplicationWindow {
    id: window
    width: 1440
    height: 900
    minimumWidth: 1120
    minimumHeight: 720
    visible: true
    title: backend.appName + " " + backend.appVersion
    color: "#07131C"

    property var navItems: [
        ["Dashboard", "⌂"],
        ["Applications", "▦"],
        ["Hardware", "⌁"],
        ["WPSD Centre", "▣"],
        ["Propagation", "☀"],
        ["Callsign & Station", "♙"],
        ["Updates", "↻"],
        ["Tools", "⌕"],
        ["Settings", "⚙"],
        ["Help & Logs", "?"],
        ["About", "ⓘ"]
    ]

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 245
            Layout.fillHeight: true
            color: "#081721"
            border.color: "#1D4353"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 4

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 76

                    Image {
                        source: backend.assetRoot + "/hamradio-pi-128.png"
                        sourceSize.width: 64
                        sourceSize.height: 64
                        fillMode: Image.PreserveAspectFit
                    }

                    ColumnLayout {
                        Text {
                            text: "HamRadio-Pi"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }
                        Text {
                            text: "ULTIMATE"
                            color: "#20C6B3"
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#254654"
                }

                Repeater {
                    model: window.navItems
                    delegate: NavButton {
                        Layout.fillWidth: true
                        text: modelData[0]
                        iconText: modelData[1]
                        selected: backend.currentPage === modelData[0]
                        onClicked: backend.setPage(modelData[0])
                    }
                }

                Item { Layout.fillHeight: true }

                Button {
                    Layout.fillWidth: true
                    text: "Donate"
                    onClicked: backend.openDonate()

                    background: Rectangle {
                        radius: 8
                        color: parent.hovered ? "#FFD95B" : "#F4C430"
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#111111"
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                Text {
                    text: "Version " + backend.appVersion
                    color: "#7893A1"
                    font.pixelSize: 11
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 58
                color: "#0B1D28"
                border.color: "#1D4353"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 18
                    spacing: 16

                    Rectangle {
                        width: 14
                        height: 14
                        radius: 7
                        color: backend.online ? "#72D936" : "#F17982"
                    }
                    Text {
                        text: backend.online ? "Online" : "Offline"
                        color: "#E6F0F5"
                        font.bold: true
                    }
                    Rectangle { width: 1; height: 28; color: "#245064" }
                    Text {
                        text: backend.piModel
                        color: "#D8E5EC"
                        font.bold: true
                    }
                    Rectangle { width: 1; height: 28; color: "#245064" }
                    Text {
                        text: "CPU " + backend.cpuTemp
                        color: "#D8E5EC"
                        font.bold: true
                    }
                    Rectangle { width: 1; height: 28; color: "#245064" }
                    Text {
                        text: "Memory " + backend.memoryPercent + "%"
                        color: "#D8E5EC"
                        font.bold: true
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: backend.callsign
                        color: "#20C6B3"
                        font.bold: true
                    }
                    Text {
                        text: backend.locator
                        color: "#D8E5EC"
                    }
                    Image {
                        source: backend.assetRoot + "/hamradio-pi-128.png"
                        sourceSize.width: 70
                        sourceSize.height: 70
                        fillMode: Image.PreserveAspectFit
                    }
                }
            }

            Loader {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.margins: 20

                sourceComponent: {
                    switch (backend.currentPage) {
                    case "Dashboard": return dashboard
                    case "Applications": return applications
                    case "Hardware": return hardware
                    case "Callsign & Station":
                    case "Settings": return station
                    case "WPSD Centre": return wpsd
                    case "Propagation": return propagation
                    case "Updates": return updates
                    case "Tools": return tools
                    case "Help & Logs": return help
                    case "About": return about
                    default: return dashboard
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 34
                color: "#061019"
                border.color: "#1D4353"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 14
                    anchors.rightMargin: 14

                    Text {
                        text: backend.appName + " " + backend.appVersion
                        color: "#C7D6DE"
                        font.pixelSize: 11
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: "One Command. One Wizard. One Ham Radio Station."
                        color: "#849DAA"
                        font.pixelSize: 11
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: "Built for Amateur Radio"
                        color: "#20C6B3"
                        font.pixelSize: 11
                    }
                }
            }
        }
    }

    Component { id: dashboard; Dashboard {} }
    Component { id: applications; Applications {} }
    Component { id: hardware; Hardware {} }
    Component { id: station; Station {} }

    Component {
        id: wpsd
        Generic {
            pageTitle: "WPSD Centre"
            pageSubtitle: "Download, flash, back up, restore and configure WPSD media."
            cards: ["Download Image", "Detect SD Cards", "Flash Image", "Verify Image",
                    "Backup Card", "Restore Card", "Configure Wi-Fi", "Configure Callsign"]
        }
    }
    Component {
        id: propagation
        Generic {
            pageTitle: "Propagation"
            pageSubtitle: "Solar, geomagnetic and HF band-condition information."
            cards: ["Solar Flux", "K Index", "A Index", "X-Ray", "Sunspots",
                    "Solar Wind", "Band Conditions", "Greyline"]
        }
    }
    Component {
        id: updates
        Generic {
            pageTitle: "Update Manager"
            pageSubtitle: "Check, review and install HamRadio-Pi Ultimate updates."
            cards: ["Current Version", "Check GitHub", "View Changelog",
                    "Download Update", "Create Backup", "Rollback"]
        }
    }
    Component {
        id: tools
        Generic {
            pageTitle: "System Tools"
            pageSubtitle: "Maintenance, reports and Raspberry Pi utilities."
            cards: ["System Report", "Package Repair", "Disk Check", "Network Test",
                    "USB Report", "Audio Test", "Open Terminal", "Diagnostics"]
        }
    }
    Component {
        id: help
        Generic {
            pageTitle: "Help & Logs"
            pageSubtitle: "Troubleshooting, documentation and application logs."
            cards: ["Quick Start", "User Guide", "Application Log", "Hardware Log",
                    "Installation Log", "Create Support Bundle"]
        }
    }
    Component {
        id: about
        Generic {
            pageTitle: "About"
            pageSubtitle: backend.appName + " " + backend.appVersion
            cards: ["Project Information", "Licence", "GitHub Repository",
                    "Donate", "Credits", "System Information"]
        }
    }
}
