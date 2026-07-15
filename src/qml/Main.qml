import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "pages"

ApplicationWindow {
    id: window
    width: 1536
    height: 1024
    minimumWidth: 1150
    minimumHeight: 760
    visible: true
    title: backend.appName + " " + backend.appVersion
    color: "#06151F"

    property var navItems: [
        ["Dashboard", "⌂"],
        ["Radio", "◉"],
        ["Digital", "≈"],
        ["Logbook", "✎"],
        ["Applications", "▦"],
        ["ROIP Dashboards", "▤"],
        ["WPSD Centre", "▣"],
        ["Propagation", "☀"],
        ["Satellites & Rotator", "◌"],
        ["System Tools", "⌕"],
        ["Help", "?"],
        ["About", "ⓘ"]
    ]

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 62
            color: "#04121B"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 22
                anchors.rightMargin: 20
                spacing: 14

                Text {
                    text: "☰"
                    color: "#DBE8EE"
                    font.pixelSize: 24
                }

                Text {
                    text: backend.appName
                    color: "#F4F8FA"
                    font.pixelSize: 20
                    font.bold: true
                }

                Text {
                    text: "v" + backend.appVersion
                    color: "#9CB0BC"
                    font.pixelSize: 12
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: backend.radioState.frequency + " MHz"
                          + "   " + backend.radioState.band
                          + "   " + backend.radioState.mode
                    color: "#18D6D2"
                    font.pixelSize: 13
                    font.bold: true
                }

                Rectangle {
                    radius: 8
                    color: backend.online ? "#0A482C" : "#4A3A0A"
                    implicitWidth: 118
                    implicitHeight: 34

                    Text {
                        anchors.centerIn: parent
                        text: backend.online ? "System Ready" : "Local Mode"
                        color: backend.online ? "#9AF176" : "#F0C76D"
                        font.pixelSize: 12
                        font.bold: true
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                Layout.preferredWidth: 250
                Layout.fillHeight: true
                color: "#071923"
                border.color: "#244D5D"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 5

                    Repeater {
                        model: window.navItems

                        delegate: NavButton {
                            required property var modelData
                            Layout.fillWidth: true
                            text: modelData[0]
                            iconText: modelData[1]
                            selected: backend.currentPage === modelData[0]
                            onClicked: {
                                var page = modelData[0]
                                if (page === "Hardware Manager")
                                    page = "Hardware"
                                else if (page === "System Tools")
                                    page = "Tools"
                                else if (page === "Help")
                                    page = "Help & Logs"
                                backend.setPage(page)
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    Button {
                        Layout.fillWidth: true
                        implicitHeight: 52
                        text: "♥  Donate $1+"
                        onClicked: backend.openDonate()

                        background: Rectangle {
                            radius: 9
                            color: parent.hovered ? "#FFD95B" : "#F4C430"
                            border.color: "#FFF0A8"
                        }

                        contentItem: Text {
                            text: parent.text
                            color: "#1B1B1B"
                            font.pixelSize: 15
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 104
                        radius: 9
                        color: "#0C2531"
                        border.color: "#29586A"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 7

                            RowLayout {
                                Rectangle {
                                    width: 12
                                    height: 12
                                    radius: 6
                                    color: backend.online ? "#61DC4C" : "#F0C76D"
                                }

                                Text {
                                    text: "System Status"
                                    color: "#F1F6F9"
                                    font.pixelSize: 14
                                    font.bold: true
                                }
                            }

                            Text {
                                text: backend.online
                                      ? "All systems operational"
                                      : "Local services available"
                                color: backend.online ? "#61DC4C" : "#F0C76D"
                                font.pixelSize: 12
                            }
                        }
                    }
                }
            }

            Loader {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.leftMargin: 40
                Layout.rightMargin: 40
                Layout.topMargin: 20
                Layout.bottomMargin: 20

                sourceComponent: {
                    switch (backend.currentPage) {
                    case "Dashboard": return dashboard
                    case "Radio": return radioControl
                    case "Digital": return digital
                    case "Logbook": return logbook
                    case "Applications": return applications
                    case "ROIP Dashboards": return radioDashboards
                    case "WPSD Centre": return wpsd
                    case "Propagation": return propagation
                    case "Satellites & Rotator": return satellites
                    case "Tools": return tools
                    case "Help & Logs": return help
                    case "About": return about
                    default: return dashboard
                    }
                }
            }
        }
    }

    Component { id: dashboard; Dashboard {} }
    Component { id: radioControl; RadioControl {} }
    Component { id: digital; Digital {} }
    Component { id: logbook; Logbook {} }
    Component { id: applications; Applications {} }
    Component { id: radioDashboards; RadioDashboards {} }

    Component {
        id: wpsd
        Generic {
            pageTitle: "WPSD Centre"
            pageSubtitle: "Download, flash, back up, restore and configure WPSD media."
            cards: [
                "Download WPSD Image",
                "Detect SD Cards",
                "Flash Image",
                "Verify Image",
                "Back Up Card",
                "Restore Card",
                "Configure Wi-Fi",
                "Configure Callsign"
            ]
            onCardClicked: function(card) { backend.runWorkspaceAction("WPSD Centre", card) }
        }
    }

    Component { id: propagation; Propagation {} }
    Component { id: satellites; Satellites {} }

    Component { id: tools; SystemTools {} }

    Component { id: help; Help {} }

    Component {
        id: about
        Generic {
            pageTitle: "About"
            pageSubtitle: backend.appName + " " + backend.appVersion
            cards: [
                "Project Information",
                "Licence",
                "GitHub Repository",
                "Donate",
                "Credits",
                "System Information"
            ]
            onCardClicked: function(card) { backend.runWorkspaceAction("About", card) }
        }
    }
}
