import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Text {
            text: "Applications"
            color: "#F4F8FA"
            font.pixelSize: 27
            font.bold: true
        }

        TextField {
            id: search
            Layout.fillWidth: true
            placeholderText: "Search applications…"
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            GridLayout {
                width: parent.width
                columns: 2
                columnSpacing: 10
                rowSpacing: 10

                Repeater {
                    model: backend.applications

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 150
                        visible: search.text === ""
                                 || modelData.name.toLowerCase().includes(search.text.toLowerCase())
                                 || modelData.category.toLowerCase().includes(search.text.toLowerCase())
                        radius: 10
                        color: "#10212C"
                        border.color: "#294A5A"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14

                            RowLayout {
                                Layout.fillWidth: true
                                Rectangle {
                                    width: 46
                                    height: 42
                                    radius: 7
                                    color: "#1C3747"
                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.name.substring(0, 2).toUpperCase()
                                        color: "#20C6B3"
                                        font.bold: true
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: modelData.name
                                        color: "#F3F8FA"
                                        font.pixelSize: 17
                                        font.bold: true
                                    }
                                    Text {
                                        text: modelData.category
                                        color: "#20C6B3"
                                    }
                                }
                                Text {
                                    text: modelData.installed ? "● Installed" : "● Available"
                                    color: modelData.installed ? "#70D93D" : "#F0C76D"
                                    font.bold: true
                                }
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.description
                                color: "#A7BBC6"
                                wrapMode: Text.WordWrap
                            }

                            Item { Layout.fillHeight: true }

                            Button {
                                text: modelData.installed ? "Launch" : "Install"
                                onClicked: {
                                    if (modelData.installed)
                                        backend.launchApplication(modelData.command)
                                    else
                                        backend.setNotification(
                                            "Application installation is enabled on Raspberry Pi OS."
                                        )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
