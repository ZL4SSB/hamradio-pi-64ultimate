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
                        text: "Appearance, startup, hardware defaults and update safety."
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
                    Layout.maximumWidth: 430
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: width >= 940 ? 2 : 1
                columnSpacing: 14
                rowSpacing: 14

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 360
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "Appearance"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            text: "Application theme"
                            color: "#DCE8EE"
                            font.pixelSize: 13
                            font.bold: true
                        }

                        DarkComboBox {
                            id: themeBox
                            Layout.fillWidth: true
                            model: [
                                "Ultimate Teal",
                                "Dark Blue",
                                "Radio Green",
                                "Amber Radio",
                                "High Contrast"
                            ]

                            Component.onCompleted: {
                                var index = find(backend.themeName)
                                currentIndex = index >= 0 ? index : 0
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 5
                            columnSpacing: 7

                            Repeater {
                                model: [
                                    ["Teal", "#18D6D2", "#10212C"],
                                    ["Blue", "#4DA3FF", "#101E33"],
                                    ["Green", "#53E58D", "#10251A"],
                                    ["Amber", "#F0B642", "#2A2110"],
                                    ["Contrast", "#00FFFF", "#050505"]
                                ]

                                delegate: Rectangle {
                                    required property var modelData
                                    Layout.fillWidth: true
                                    implicitHeight: 68
                                    radius: 7
                                    color: modelData[2]
                                    border.color: modelData[1]
                                    border.width: 2

                                    Column {
                                        anchors.centerIn: parent
                                        spacing: 4

                                        Rectangle {
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            width: 22
                                            height: 8
                                            radius: 4
                                            color: modelData[1]
                                        }

                                        Text {
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            text: modelData[0]
                                            color: "#F4F8FA"
                                            font.pixelSize: 10
                                            font.bold: true
                                        }
                                    }
                                }
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Save Preferences to apply the selected theme to the application shell and navigation."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }

                        DarkCheckBox {
                            id: splashCheck
                            Layout.fillWidth: true
                            text: "Show the cinematic startup splash"
                            checked: backend.showSplash
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 360
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 13

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
                            text: "Check for HRPU updates at startup"
                            checked: backend.checkUpdates
                        }

                        DarkCheckBox {
                            id: startAtLoginCheck
                            Layout.fillWidth: true
                            text: "Start HRPU when I sign in"
                            checked: backend.startAtLogin
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Startup scans begin after the main Dashboard opens."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 350
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
                            font.bold: true
                        }

                        DarkTextField {
                            id: catPortField
                            Layout.fillWidth: true
                            text: backend.defaultCatPort
                            placeholderText: "/dev/ttyUSB0 or COM3"
                        }

                        Text {
                            text: "Default audio device"
                            color: "#DCE8EE"
                            font.bold: true
                        }

                        DarkTextField {
                            id: audioDeviceField
                            Layout.fillWidth: true
                            text: backend.defaultAudioDevice
                            placeholderText: "USB Audio CODEC"
                        }

                        Text {
                            text: "Preferred SDR"
                            color: "#DCE8EE"
                            font.bold: true
                        }

                        DarkTextField {
                            id: sdrField
                            Layout.fillWidth: true
                            text: backend.preferredSdr
                            placeholderText: "RTL-SDR, Airspy, SDRplay…"
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 350
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "Updates & Audio"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            text: "Update channel"
                            color: "#DCE8EE"
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
                            text: "Create a settings backup before updates"
                            checked: backend.backupBeforeUpdates
                        }

                        DarkCheckBox {
                            id: spectrumPeakHoldCheck
                            Layout.fillWidth: true
                            text: "Enable spectrum Peak Hold by default"
                            checked: backend.spectrumPeakHoldDefault
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
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 385
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 10

                        Text {
                            text: "Live Propagation / DX Cluster"
                            color: "#F4F8FA"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text:
                                "The callsign and locator come automatically "
                                + "from the HRPU station profile."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }

                        DarkCheckBox {
                            id: dxClusterEnabledCheck
                            Layout.fillWidth: true
                            text: "Connect to a live DX cluster"
                            checked: backend.dxClusterEnabled
                        }

                        Text {
                            text: "DX-cluster host"
                            color: "#DCE8EE"
                            font.bold: true
                        }

                        DarkTextField {
                            id: dxClusterHostField
                            Layout.fillWidth: true
                            enabled: dxClusterEnabledCheck.checked
                            text: backend.dxClusterHost
                            placeholderText: "Example: cluster.example.net"
                        }

                        RowLayout {
                            Layout.fillWidth: true

                            ColumnLayout {
                                Layout.fillWidth: true

                                Text {
                                    text: "Port"
                                    color: "#DCE8EE"
                                    font.bold: true
                                }

                                SpinBox {
                                    id: dxClusterPortBox
                                    Layout.fillWidth: true
                                    enabled:
                                        dxClusterEnabledCheck.checked
                                    from: 1
                                    to: 65535
                                    value: backend.dxClusterPort
                                    editable: true
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true

                                Text {
                                    text: "Login callsign"
                                    color: "#DCE8EE"
                                    font.bold: true
                                }

                                DarkTextField {
                                    id: dxClusterLoginField
                                    Layout.fillWidth: true
                                    enabled:
                                        dxClusterEnabledCheck.checked
                                    text: backend.dxClusterLogin
                                    placeholderText:
                                        "Blank uses station callsign"
                                }
                            }
                        }

                        DarkCheckBox {
                            id: propagationDemoCheck
                            Layout.fillWidth: true
                            text:
                                "Use demo spots when no live spots are available"
                            checked: backend.propagationDemoMode
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 280
                    radius: 10
                    color: "#10212C"
                    border.color: "#C99B16"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "Maintenance & Privacy"
                            color: "#FFD55A"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Fresh installations contain no callsign, locator, DMR ID, email address, password, API key or private URL."
                            color: "#DCE8EE"
                            wrapMode: Text.WordWrap
                        }

                        RowLayout {
                            Button {
                                text: "Export Settings"
                                onClicked: backend.exportPreferences()
                            }

                            Button {
                                text: "Open Settings Folder"
                                onClicked: backend.openSettingsFolder()
                            }
                        }

                        Button {
                            text: "Reset Preferences"
                            onClicked: backend.resetPreferences()
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
                        catPortField.text,
                        audioDeviceField.text,
                        sdrField.text,
                        updateChannelBox.currentText,
                        backupCheck.checked,
                        spectrumPeakHoldCheck.checked,
                        spectrumDecayBox.currentText,
                        startAtLoginCheck.checked,
                        dxClusterHostField.text,
                        dxClusterPortBox.value,
                        dxClusterLoginField.text,
                        dxClusterEnabledCheck.checked,
                        propagationDemoCheck.checked
                    )
                }

                Button {
                    implicitWidth: 180
                    text: "Reload Saved Values"

                    onClicked: {
                        themeBox.currentIndex = Math.max(
                            0,
                            themeBox.find(backend.themeName)
                        )
                        splashCheck.checked = backend.showSplash
                        scanCheck.checked = backend.autoScan
                        updateCheck.checked = backend.checkUpdates
                        startAtLoginCheck.checked = backend.startAtLogin
                        catPortField.text = backend.defaultCatPort
                        audioDeviceField.text = backend.defaultAudioDevice
                        sdrField.text = backend.preferredSdr
                        updateChannelBox.currentIndex = Math.max(
                            0,
                            updateChannelBox.find(backend.updateChannel)
                        )
                        backupCheck.checked = backend.backupBeforeUpdates
                        spectrumPeakHoldCheck.checked =
                            backend.spectrumPeakHoldDefault
                        spectrumDecayBox.currentIndex = Math.max(
                            0,
                            spectrumDecayBox.find(
                                backend.spectrumPeakDecayDefault
                            )
                        )
                        dxClusterHostField.text =
                            backend.dxClusterHost
                        dxClusterPortBox.value =
                            backend.dxClusterPort
                        dxClusterLoginField.text =
                            backend.dxClusterLogin
                        dxClusterEnabledCheck.checked =
                            backend.dxClusterEnabled
                        propagationDemoCheck.checked =
                            backend.propagationDemoMode
                    }
                }

                Item {
                    Layout.fillWidth: true
                }
            }
        }
    }
}
