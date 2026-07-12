import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: preferencesColumn.implicitHeight + 20
        clip: true

        ColumnLayout {
            id: preferencesColumn
            width: parent.width
            spacing: 14

            Text {
                text: "Preferences"
                color: "#F4F8FA"
                font.pixelSize: 27
                font.bold: true
            }

            Text {
                text: "Application appearance, startup and automatic actions."
                color: "#95ACB9"
                font.pixelSize: 14
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: 10
                rowSpacing: 10

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 250
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 13

                        Text {
                            text: "Appearance"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Label { text: "Theme" }
                        ComboBox {
                            id: themeBox
                            Layout.fillWidth: true
                            model: ["Dark", "Teal Dark", "High Contrast"]
                            Component.onCompleted: {
                                var i = find(backend.themeName)
                                if (i >= 0) currentIndex = i
                            }
                        }

                        CheckBox {
                            id: splashCheck
                            text: "Show splash screen"
                            checked: backend.showSplash
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 250
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 13

                        Text {
                            text: "Startup"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        CheckBox {
                            id: scanCheck
                            text: "Scan hardware at startup"
                            checked: backend.autoScan
                        }

                        CheckBox {
                            id: updateCheck
                            text: "Check for updates at startup"
                            checked: backend.checkUpdates
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Startup preferences are stored locally and will be used on Raspberry Pi OS."
                            color: "#95ACB9"
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 210
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 12

                        Text {
                            text: "Hardware defaults"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        TextField {
                            Layout.fillWidth: true
                            placeholderText: "Default CAT port"
                        }

                        TextField {
                            Layout.fillWidth: true
                            placeholderText: "Default audio device"
                        }

                        TextField {
                            Layout.fillWidth: true
                            placeholderText: "Preferred SDR"
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 210
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 12

                        Text {
                            text: "Updates"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        ComboBox {
                            Layout.fillWidth: true
                            model: ["Stable channel", "Preview channel"]
                        }

                        CheckBox {
                            text: "Create backup before updates"
                            checked: true
                        }

                        Text {
                            text: "Current application version: " + backend.appVersion
                            color: "#95ACB9"
                        }
                    }
                }
            }

            Button {
                text: "Save Preferences"
                onClicked: backend.savePreferences(
                    themeBox.currentText,
                    splashCheck.checked,
                    scanCheck.checked,
                    updateCheck.checked
                )
            }
        }
    }
}
