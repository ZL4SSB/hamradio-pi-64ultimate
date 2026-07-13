import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: preferencesColumn.implicitHeight + 24
        clip: true

        ColumnLayout {
            id: preferencesColumn
            width: parent.width
            spacing: 16

            Text {
                text: "Preferences"
                color: "#F4F8FA"
                font.pixelSize: 27
                font.bold: true
            }

            Text {
                text: "Application appearance, startup and automatic actions."
                color: "#B8C9D2"
                font.pixelSize: 14
            }

            GridLayout {
                Layout.fillWidth: true
                columns: width >= 900 ? 2 : 1
                columnSpacing: 14
                rowSpacing: 14

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 270
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 14

                        Text {
                            text: "Appearance"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            text: "Theme"
                            color: "#DCE8EE"
                            font.pixelSize: 14
                            font.bold: true
                        }

                        DarkComboBox {
                            id: themeBox
                            Layout.fillWidth: true
                            model: ["Dark", "Teal Dark", "High Contrast"]
                            Component.onCompleted: {
                                var i = find(backend.themeName)
                                if (i >= 0) currentIndex = i
                            }
                        }

                        DarkCheckBox {
                            id: splashCheck
                            Layout.fillWidth: true
                            text: "Show splash screen"
                            checked: backend.showSplash
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 270
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 14

                        Text {
                            text: "Startup"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        DarkCheckBox {
                            id: scanCheck
                            Layout.fillWidth: true
                            text: "Scan hardware at startup"
                            checked: backend.autoScan
                        }

                        DarkCheckBox {
                            id: updateCheck
                            Layout.fillWidth: true
                            text: "Check for updates at startup"
                            checked: backend.checkUpdates
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "These settings are stored locally and used automatically on Raspberry Pi OS."
                            color: "#B8C9D2"
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 260
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 11

                        Text {
                            text: "Hardware defaults"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            text: "Default CAT port"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkTextField {
                            Layout.fillWidth: true
                            placeholderText: "Example: /dev/ttyUSB0"
                        }

                        Text {
                            text: "Default audio device"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkTextField {
                            Layout.fillWidth: true
                            placeholderText: "Example: USB Audio CODEC"
                        }

                        Text {
                            text: "Preferred SDR"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkTextField {
                            Layout.fillWidth: true
                            placeholderText: "Example: RTL-SDR"
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 260
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 14

                        Text {
                            text: "Updates"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            text: "Update channel"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkComboBox {
                            Layout.fillWidth: true
                            model: ["Stable channel", "Preview channel"]
                        }

                        DarkCheckBox {
                            Layout.fillWidth: true
                            text: "Create a backup before updates"
                            checked: true
                        }

                        Text {
                            text: "Current version: " + backend.appVersion
                            color: "#B8C9D2"
                            font.pixelSize: 13
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 270
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "HamClock"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "HamClock opens in your normal browser for full-screen viewing."
                            color: "#B8C9D2"
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            text: "HamClock URL"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkTextField {
                            id: hamClockUrlField
                            Layout.fillWidth: true
                            text: backend.hamClockUrl
                            placeholderText: "Example: http://hamclock.local/"
                            selectByMouse: true
                        }

                        RowLayout {
                            spacing: 10

                            Button {
                                text: "Test"
                                onClicked: backend.testWebUrl(hamClockUrlField.text)
                            }

                            Button {
                                text: "Open"
                                onClicked: backend.openHamClock()
                            }

                            Item { Layout.fillWidth: true }
                        }
                    }
                }
            }

            Button {
                Layout.alignment: Qt.AlignLeft
                text: "Save Preferences"
                onClicked: backend.savePreferences(
                    themeBox.currentText,
                    splashCheck.checked,
                    scanCheck.checked,
                    updateCheck.checked,
                    hamClockUrlField.text
                )
            }

            Item {
                Layout.preferredHeight: 12
            }
        }
    }
}
