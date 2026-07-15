import QtQuick
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Layouts

Window {
    id: splash
    width: 540
    height: 690
    visible: true
    flags: Qt.SplashScreen | Qt.WindowStaysOnTopHint
    color: "#07131C"

    Rectangle {
        anchors.fill: parent
        radius: 14
        color: "#07131C"
        border.color: "#20C6B3"
        border.width: 2

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 10

            Image {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 340
                Layout.preferredHeight: 340
                source: backend.assetRoot + "/hamradio-pi-logo.png"
                fillMode: Image.PreserveAspectFit
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: backend.appName
                color: "#F4F8FA"
                font.pixelSize: 25
                font.bold: true
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Ham Shack Control Centre for Raspberry Pi"
                color: "#A6BBC6"
                font.pixelSize: 13
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Loading interface…"
                color: "#F4F8FA"
                font.pixelSize: 14
            }

            ProgressBar {
                Layout.fillWidth: true
                indeterminate: true
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Version " + backend.appVersion
                color: "#819AA8"
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 132
                radius: 10
                color: "#111923"
                border.color: "#C99B16"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 14

                    ColumnLayout {
                        Layout.fillWidth: true
                        Text {
                            text: "♥  Support HamRadio-Pi Ultimate"
                            color: "#FFD55A"
                            font.pixelSize: 18
                            font.bold: true
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "If the project is useful, please consider supporting development."
                            color: "#E7F0F4"
                            wrapMode: Text.WordWrap
                        }
                        Text {
                            text: "Minimum $1 USD"
                            color: "#FFD55A"
                            font.bold: true
                        }
                    }

                    Button {
                        implicitWidth: 130
                        implicitHeight: 50
                        text: "Donate $1+"
                        onClicked: backend.openDonate()

                        background: Rectangle {
                            radius: 8
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
                }
            }
        }
    }
}
