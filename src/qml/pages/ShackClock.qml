import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: contentColumn.implicitHeight + 20
        clip: true

        ColumnLayout {
            id: contentColumn
            width: parent.width
            spacing: 14

            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    Layout.fillWidth: true

                    Text {
                        text: "Ultimate Shack Clock"
                        color: "#F5F9FB"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: "Station time, propagation and operating overview."
                        color: "#A4B7C2"
                        font.pixelSize: 14
                    }
                }

                Button {
                    text: "Refresh"
                    onClicked: {
                        backend.refreshShackClock()
                        backend.refreshPropagation()
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 220
                    radius: 10
                    color: "#0D202B"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 6

                        Text {
                            text: "LOCAL"
                            color: "#18D6D2"
                            font.pixelSize: 15
                            font.bold: true
                        }

                        Text {
                            text: backend.shackLocalTime
                            color: "#F5F9FB"
                            font.pixelSize: 46
                            font.bold: true
                            font.family: "monospace"
                        }

                        Text {
                            text: backend.shackLocalDate
                            color: "#BFD0D8"
                            font.pixelSize: 14
                        }

                        Item { Layout.fillHeight: true }

                        Text {
                            text: backend.callsign + "  ·  " + backend.locator
                            color: "#8DE7DF"
                            font.pixelSize: 16
                            font.bold: true
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 220
                    radius: 10
                    color: "#0D202B"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 6

                        Text {
                            text: "UTC"
                            color: "#18D6D2"
                            font.pixelSize: 15
                            font.bold: true
                        }

                        Text {
                            text: backend.shackUtcTime
                            color: "#F5F9FB"
                            font.pixelSize: 46
                            font.bold: true
                            font.family: "monospace"
                        }

                        Text {
                            text: backend.shackUtcDate
                            color: "#BFD0D8"
                            font.pixelSize: 14
                        }

                        Item { Layout.fillHeight: true }

                        Text {
                            text: "Zulu operating time"
                            color: "#8FA7B5"
                            font.pixelSize: 13
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 220
                    radius: 10
                    color: "#0D202B"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 9

                        Text {
                            text: "SUN"
                            color: "#18D6D2"
                            font.pixelSize: 15
                            font.bold: true
                        }

                        RowLayout {
                            Text {
                                text: "Sunrise"
                                color: "#BFD0D8"
                                Layout.preferredWidth: 90
                            }
                            Text {
                                text: backend.shackSunrise
                                color: "#F5F9FB"
                                font.pixelSize: 20
                                font.bold: true
                            }
                        }

                        RowLayout {
                            Text {
                                text: "Sunset"
                                color: "#BFD0D8"
                                Layout.preferredWidth: 90
                            }
                            Text {
                                text: backend.shackSunset
                                color: "#F5F9FB"
                                font.pixelSize: 20
                                font.bold: true
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 42
                            radius: 7
                            color: backend.shackDaylight === "Daylight"
                                   ? "#5A4A12"
                                   : "#132B43"

                            Text {
                                anchors.centerIn: parent
                                text: backend.shackDaylight
                                color: backend.shackDaylight === "Daylight"
                                       ? "#FFD55A"
                                       : "#89C7F5"
                                font.pixelSize: 15
                                font.bold: true
                            }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 270
                radius: 10
                color: "#07151D"
                border.color: "#365E70"

                Item {
                    anchors.fill: parent
                    anchors.margins: 1

                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: parent.width * 0.55
                        color: "#143853"
                    }

                    Rectangle {
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: parent.width * 0.45
                        color: "#090F18"
                    }

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: 120
                        height: parent.height * 1.3
                        rotation: 12
                        color: "#304A52"
                        opacity: 0.45
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 22

                        Text {
                            text: "Greyline Overview"
                            color: "#F5F9FB"
                            font.pixelSize: 19
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "A simplified day/night display for quick operating reference. A full world map and station-to-DX greyline path can be added later."
                            color: "#D1DEE4"
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }

                        RowLayout {
                            Layout.fillWidth: true

                            Text {
                                text: "DAY"
                                color: "#FFD55A"
                                font.pixelSize: 24
                                font.bold: true
                            }

                            Item { Layout.fillWidth: true }

                            Text {
                                text: "GREYLINE"
                                color: "#C3D0D4"
                                font.pixelSize: 20
                                font.bold: true
                            }

                            Item { Layout.fillWidth: true }

                            Text {
                                text: "NIGHT"
                                color: "#8FCBFF"
                                font.pixelSize: 24
                                font.bold: true
                            }
                        }
                    }
                }
            }




        }
    }

    Component.onCompleted: {
        backend.refreshShackClock()
    }
}
