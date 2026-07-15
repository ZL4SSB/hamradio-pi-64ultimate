import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: pageColumn.implicitHeight + 30
        clip: true

        ColumnLayout {
            id: pageColumn
            width: parent.width
            spacing: 16

            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    Layout.fillWidth: true

                    Text {
                        text: "Preferences"
                        color: "#F4F8FA"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: "Configure startup, hardware, updates and browser integrations."
                        color: "#B8C9D2"
                        font.pixelSize: 14
                    }
                }

                Text {
                    text: backend.notification
                    color: "#18D6D2"
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignRight
                    elide: Text.ElideRight
                    Layout.maximumWidth: 440
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: width >= 940 ? 2 : 1
                columnSpacing: 14
                rowSpacing: 14

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 280
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
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkComboBox {
                            id: themeBox
                            Layout.fillWidth: true
                            model: ["Dark", "Teal Dark", "High Contrast"]

                            Component.onCompleted: {
                                var index = find(backend.themeName)
                                currentIndex = index >= 0 ? index : 0
                            }
                        }

                        DarkCheckBox {
                            id: splashCheck
                            Layout.fillWidth: true
                            text: "Show the five-second startup splash"
                            checked: backend.showSplash
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Theme names are saved now so additional colour schemes can be added without changing existing settings."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 280
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
                            text: "Scan radios, SDRs, audio and USB devices at startup"
                            checked: backend.autoScan
                        }

                        DarkCheckBox {
                            id: updateCheck
                            Layout.fillWidth: true
                            text: "Check HamRadio-Pi Ultimate for updates at startup"
                            checked: backend.checkUpdates
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Automatic checks begin after the Dashboard has opened so they do not delay startup."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 340
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 10

                        Text {
                            text: "Hardware Defaults"
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
                            id: catPortField
                            Layout.fillWidth: true
                            text: backend.defaultCatPort
                            placeholderText: "Raspberry Pi: /dev/ttyUSB0   Windows: COM3"
                        }

                        Text {
                            text: "Default audio device"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkTextField {
                            id: audioDeviceField
                            Layout.fillWidth: true
                            text: backend.defaultAudioDevice
                            placeholderText: "Example: USB Audio CODEC"
                        }

                        Text {
                            text: "Preferred SDR"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkTextField {
                            id: sdrField
                            Layout.fillWidth: true
                            text: backend.preferredSdr
                            placeholderText: "Example: RTL-SDR Blog V4"
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "These defaults are available to future radio applications and plug-ins."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 340
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
                            id: updateChannelBox
                            Layout.fillWidth: true
                            model: ["Stable channel", "Preview channel"]

                            Component.onCompleted: {
                                var index = find(backend.updateChannel)
                                currentIndex = index >= 0 ? index : 0
                            }
                        }

                        DarkCheckBox {
                            id: backupCheck
                            Layout.fillWidth: true
                            text: "Create a backup before program updates"
                            checked: backend.backupBeforeUpdates
                        }

                        Text {
                            text: "Installed version: " + backend.appVersion
                            color: "#B8C9D2"
                            font.pixelSize: 13
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Stable is recommended for normal use. Preview will eventually receive development builds first."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 310
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
                            text: "The Dashboard HamClock button opens this address in the normal browser."
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
                            Button {
                                text: "Test URL"
                                onClicked: backend.testWebUrl(hamClockUrlField.text)
                            }

                            Button {
                                text: "Open HamClock"
                                onClicked: backend.openHamClock()
                            }

                            Item { Layout.fillWidth: true }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 310
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 13

                        Text {
                            text: "Audio Spectrum Defaults"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        DarkCheckBox {
                            id: spectrumPeakHoldCheck
                            Layout.fillWidth: true
                            text: "Enable spectrum peak hold when monitoring starts"
                            checked: backend.spectrumPeakHoldDefault
                        }

                        Text {
                            text: "Peak marker decay"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkComboBox {
                            id: spectrumDecayBox
                            Layout.fillWidth: true
                            model: ["Fast", "Medium", "Slow"]

                            Component.onCompleted: {
                                var index = find(backend.spectrumPeakDecayDefault)
                                currentIndex = index >= 0 ? index : 1
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Peak Hold draws a bright marker above each spectrum bar. Medium decay is recommended for normal voice and radio-audio checks."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 310
                    radius: 10
                    color: "#10212C"
                    border.color: "#C99B16"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "Settings Maintenance"
                            color: "#FFD55A"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Saved settings file:\n" + backend.settingsPath
                            color: "#DCE8EE"
                            font.pixelSize: 12
                            wrapMode: Text.WrapAnywhere
                        }

                        RowLayout {
                            Layout.fillWidth: true

                            Button {
                                text: "Export Backup"
                                onClicked: backend.exportPreferences()
                            }

                            Button {
                                text: "Open Settings Folder"
                                onClicked: backend.openSettingsFolder()
                            }
                        }

                        Button {
                            text: "Reset Preferences to Defaults"
                            onClicked: resetDialog.open()
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Resetting preferences preserves the Station Profile."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true

                Button {
                    implicitWidth: 190
                    text: "Save Preferences"
                    onClicked: backend.savePreferences(
                        themeBox.currentText,
                        splashCheck.checked,
                        scanCheck.checked,
                        updateCheck.checked,
                        hamClockUrlField.text,
                        catPortField.text,
                        audioDeviceField.text,
                        sdrField.text,
                        updateChannelBox.currentText,
                        backupCheck.checked,
                        spectrumPeakHoldCheck.checked,
                        spectrumDecayBox.currentText
                    )
                }

                Button {
                    implicitWidth: 190
                    text: "Reload Saved Values"
                    onClicked: {
                        themeBox.currentIndex = Math.max(0, themeBox.find(backend.themeName))
                        splashCheck.checked = backend.showSplash
                        scanCheck.checked = backend.autoScan
                        updateCheck.checked = backend.checkUpdates
                        hamClockUrlField.text = backend.hamClockUrl
                        catPortField.text = backend.defaultCatPort
                        audioDeviceField.text = backend.defaultAudioDevice
                        sdrField.text = backend.preferredSdr
                        updateChannelBox.currentIndex = Math.max(
                            0,
                            updateChannelBox.find(backend.updateChannel)
                        )
                        backupCheck.checked = backend.backupBeforeUpdates
                        spectrumPeakHoldCheck.checked = backend.spectrumPeakHoldDefault
                        spectrumDecayBox.currentIndex = Math.max(
                            0,
                            spectrumDecayBox.find(backend.spectrumPeakDecayDefault)
                        )
                    }
                }

                Item { Layout.fillWidth: true }
            }
        }
    }

    Dialog {
        id: resetDialog
        modal: true
        anchors.centerIn: Overlay.overlay
        title: "Reset Preferences?"
        standardButtons: Dialog.Yes | Dialog.No

        contentItem: Text {
            text: "This resets application preferences but keeps callsign and station information."
            color: "#172731"
            wrapMode: Text.WordWrap
        }

        onAccepted: {
            backend.resetPreferences()
            themeBox.currentIndex = Math.max(0, themeBox.find(backend.themeName))
            splashCheck.checked = backend.showSplash
            scanCheck.checked = backend.autoScan
            updateCheck.checked = backend.checkUpdates
            hamClockUrlField.text = backend.hamClockUrl
            catPortField.text = backend.defaultCatPort
            audioDeviceField.text = backend.defaultAudioDevice
            sdrField.text = backend.preferredSdr
            updateChannelBox.currentIndex = Math.max(
                0,
                updateChannelBox.find(backend.updateChannel)
            )
            backupCheck.checked = backend.backupBeforeUpdates
        }
    }
}
