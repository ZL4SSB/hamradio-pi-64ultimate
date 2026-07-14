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

    property string activeTheme: backend.themeName
    property color shellBackground:
        activeTheme === "Dark Blue" ? "#08111E" :
        activeTheme === "Radio Green" ? "#07120C" :
        activeTheme === "Amber Radio" ? "#171108" :
        activeTheme === "High Contrast" ? "#000000" :
        "#06151F"
    property color shellHeader:
        activeTheme === "Dark Blue" ? "#0B1728" :
        activeTheme === "Radio Green" ? "#0B1C12" :
        activeTheme === "Amber Radio" ? "#241907" :
        activeTheme === "High Contrast" ? "#080808" :
        "#04121B"
    property color shellSidebar:
        activeTheme === "Dark Blue" ? "#0B1728" :
        activeTheme === "Radio Green" ? "#0B1C12" :
        activeTheme === "Amber Radio" ? "#211707" :
        activeTheme === "High Contrast" ? "#080808" :
        "#071923"
    property color shellText: "#F4F8FA"

    color: shellBackground

    property var navItems: [
        ["Dashboard", "⌂"],
        ["Applications", "▦"],
        ["Radio Dashboards", "▤"],
        ["WPSD Centre", "▣"],
        ["Propagation", "☀"],
        ["Shack Clock", "◷"],
        ["Station Tools", "⚙"],
        ["Preferences", "⚙"],
        ["Help", "?"],
        ["About", "ⓘ"]
    ]

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 62
            color: window.shellHeader

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
                    color: window.shellText
                    font.pixelSize: 20
                    font.bold: true
                }

                Text {
                    text: "v" + backend.appVersion
                    color: "#9CB0BC"
                    font.pixelSize: 12
                }

                Item { Layout.fillWidth: true }

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
                color: window.shellSidebar
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
                            onClicked: backend.setPage(modelData[0])
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
                    case "Applications": return applications
                    case "Radio Dashboards": return radioDashboards
                    case "WPSD Centre": return wpsd
                    case "Propagation": return propagation
                    case "Shack Clock": return shackClock
                    case "Station Profile": return station
                    case "Station Tools": return stationTools
                    case "Preferences": return preferences
                    case "Help": return help
                    case "About": return about
                    default: return dashboard
                    }
                }
            }
        }
    }

    Component { id: dashboard; Dashboard {} }
    Component { id: applications; Applications {} }
    Component { id: radioDashboards; RadioDashboards {} }
    Component { id: station; Station {} }
    Component { id: stationTools; StationTools {} }
    Component { id: preferences; Preferences {} }

    Component { id: wpsd; WpsdCentre {} }

    Component { id: propagation; Propagation {} }
    Component { id: shackClock; ShackClock {} }



    Component { id: help; Help {} }

    Component { id: about; About {} }
}
