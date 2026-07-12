import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true
                Text {
                    text: "Hardware"
                    color: "#F4F8FA"
                    font.pixelSize: 27
                    font.bold: true
                }
                Text {
                    text: "Detect SDRs, CAT interfaces, audio and USB devices."
                    color: "#95ACB9"
                }
            }
            Button {
                text: "Scan Hardware"
                onClicked: backend.scanHardware()
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                width: parent.width
                spacing: 10

                Repeater {
                    model: backend.devices

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 105
                        radius: 10
                        color: "#10212C"
                        border.color: "#294A5A"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 14

                            Rectangle {
                                width: 58
                                height: 58
                                radius: 9
                                color: "#1C3747"
                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.icon
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
                                    Layout.fillWidth: true
                                    text: modelData.detail
                                    color: "#A7BBC6"
                                    wrapMode: Text.WordWrap
                                }
                            }

                            Text {
                                text: modelData.status
                                color: "#70D93D"
                                font.bold: true
                            }
                        }
                    }
                }
            }
        }
    }
}
