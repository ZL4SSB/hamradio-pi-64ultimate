import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: aboutColumn.implicitHeight + 24
        clip: true

        ColumnLayout {
            id: aboutColumn
            width: parent.width
            spacing: 16

            Text {
                text: "About HamRadio-Pi Ultimate"
                color: "#F5F9FB"
                font.pixelSize: 28
                font.bold: true
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 520
                radius: 12
                color: "#0D202B"
                border.color: "#365E70"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 28
                    spacing: 28

                    Item {
                        Layout.preferredWidth: Math.min(320, parent.width * 0.33)
                        Layout.fillHeight: true

                        Image {
                            anchors.centerIn: parent
                            width: Math.min(parent.width - 20, 285)
                            height: Math.min(parent.height - 20, 285)
                            source: backend.assetRoot + "/dashboard-wordmark-clean.png"
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                        }
                    }

                    Rectangle {
                        Layout.preferredWidth: 1
                        Layout.fillHeight: true
                        color: "#294A5A"
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 13

                        Text {
                            text: backend.appName
                            color: "#F5F9FB"
                            font.pixelSize: 30
                            font.bold: true
                        }

                        Text {
                            text: "Version " + backend.appVersion
                            color: "#18D6D2"
                            font.pixelSize: 16
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "A modern amateur-radio station dashboard, application manager and hardware-control platform for Raspberry Pi and Windows."
                            color: "#C8D6DD"
                            font.pixelSize: 14
                            wrapMode: Text.WordWrap
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "#294A5A"
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Current focus"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Final pre‑1.0 testing: installers, menu flow, WPSD tools, propagation, Station Tools, preferences, help and responsive layouts."
                            color: "#B8C9D2"
                            wrapMode: Text.WordWrap
                        }

                        RowLayout {
                            spacing: 10

                            Button {
                                text: "Project Page"
                                onClicked: backend.openGithubProject()
                            }

                            Button {
                                text: "Report an Issue"
                                onClicked: backend.openGithubIssues()
                            }

                            Button {
                                text: "Donate"
                                onClicked: backend.openDonate()
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Text {
                            text: "GPL v3 core"
                            color: "#8FA7B5"
                        }

                        Text {
                            text: "Project: Glen McNeil · ZL4SSB"
                            color: "#8FA7B5"
                        }
                    }
                }
            }
        }
    }
}
