import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: pageColumn.implicitHeight + 24
        clip: true

        ColumnLayout {
            id: pageColumn
            width: parent.width
            spacing: 14

            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    Layout.fillWidth: true

                    Text {
                        text: "System Tools"
                        color: "#F5F9FB"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: "Audio, network, storage, USB, diagnostics and updates."
                        color: "#A4B7C2"
                        font.pixelSize: 14
                    }
                }

                Text {
                    text: backend.toolStatus
                    color: "#18D6D2"
                    font.pixelSize: 12
                    elide: Text.ElideRight
                    Layout.maximumWidth: 480
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 620
                radius: 10
                color: "#0D202B"
                border.color: "#365E70"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            Layout.fillWidth: true
                            text: "Audio Test"
                            color: "#F5F9FB"
                            font.pixelSize: 19
                            font.bold: true
                        }

                        Button {
                            text: "Detect Devices"
                            enabled: !backend.audioBusy
                            onClicked: backend.scanAudioDevices()
                        }

                        Button {
                            text: "Test Speakers"
                            enabled: !backend.audioBusy
                            onClicked: backend.testSpeakers()
                        }

                        Button {
                            text: "Test Microphone"
                            enabled: !backend.audioBusy
                            onClicked: backend.testMicrophone()
                        }
                    }

                    ProgressBar {
                        Layout.fillWidth: true
                        indeterminate: true
                        visible: backend.audioBusy
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 235
                        radius: 9
                        color: "#081923"
                        border.color: backend.audioClip ? "#F15B64" : "#28566A"
                        border.width: backend.audioClip ? 2 : 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            RowLayout {
                                Layout.fillWidth: true

                                Text {
                                    text: "Live Microphone Level & Spectrum"
                                    color: "#F5F9FB"
                                    font.pixelSize: 16
                                    font.bold: true
                                }

                                Item { Layout.fillWidth: true }

                                Text {
                                    text: backend.audioClip ? "CLIPPING" : (
                                        backend.audioMonitoring ? "LIVE" : "STOPPED"
                                    )
                                    color: backend.audioClip ? "#F15B64" : (
                                        backend.audioMonitoring ? "#61DC4C" : "#93AAB6"
                                    )
                                    font.pixelSize: 12
                                    font.bold: true
                                }

                                DarkCheckBox {
                                    text: "Peak Hold"
                                    checked: backend.audioPeakHold
                                    onToggled: backend.setAudioPeakHold(checked)
                                }

                                DarkComboBox {
                                    implicitWidth: 110
                                    model: ["Fast", "Medium", "Slow"]
                                    Component.onCompleted: {
                                        var i = find(backend.audioPeakDecay)
                                        currentIndex = i >= 0 ? i : 1
                                    }
                                    onActivated: backend.setAudioPeakDecay(currentText)
                                }

                                Button {
                                    text: "Clear Peaks"
                                    enabled: backend.audioPeakHold
                                    onClicked: backend.clearAudioPeaks()
                                }

                                Button {
                                    text: backend.audioMonitoring
                                          ? "Stop Monitor"
                                          : "Start Monitor"
                                    enabled: !backend.audioBusy
                                    onClicked: {
                                        if (backend.audioMonitoring)
                                            backend.stopAudioMonitor()
                                        else
                                            backend.startAudioMonitor()
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                Text {
                                    text: "Level"
                                    color: "#C9D8E0"
                                    font.pixelSize: 12
                                    Layout.preferredWidth: 58
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 24
                                    radius: 5
                                    color: "#102A36"
                                    border.color: "#315B6C"

                                    Rectangle {
                                        width: parent.width * backend.audioLevel
                                        height: parent.height
                                        radius: 5
                                        color: backend.audioLevel > 0.85
                                               ? "#F15B64"
                                               : backend.audioLevel > 0.65
                                                 ? "#F0C76D"
                                                 : "#38D27A"
                                    }

                                    Text {
                                        anchors.centerIn: parent
                                        text: Math.round(backend.audioLevel * 100) + "%"
                                        color: "#F5F9FB"
                                        font.pixelSize: 11
                                        font.bold: true
                                    }
                                }

                                Text {
                                    text: "Peak " + Math.round(backend.audioPeak * 100) + "%"
                                    color: "#C9D8E0"
                                    font.pixelSize: 12
                                    Layout.preferredWidth: 80
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                radius: 8
                                color: "#050F16"
                                border.color: backend.audioClip ? "#F15B64" : "#315B6C"
                                border.width: backend.audioClip ? 2 : 1

                                Canvas {
                                    id: spectrumGrid
                                    anchors.fill: parent
                                    anchors.margins: 8

                                    onPaint: {
                                        var ctx = getContext("2d")
                                        ctx.reset()
                                        ctx.strokeStyle = "#17313E"
                                        ctx.lineWidth = 1

                                        for (var x = 0; x <= 4; x++) {
                                            var px = x * width / 4
                                            ctx.beginPath()
                                            ctx.moveTo(px, 0)
                                            ctx.lineTo(px, height)
                                            ctx.stroke()
                                        }

                                        for (var y = 0; y <= 4; y++) {
                                            var py = y * height / 4
                                            ctx.beginPath()
                                            ctx.moveTo(0, py)
                                            ctx.lineTo(width, py)
                                            ctx.stroke()
                                        }
                                    }

                                    onWidthChanged: requestPaint()
                                    onHeightChanged: requestPaint()
                                }

                                Row {
                                    id: liveBars
                                    anchors.fill: parent
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 10
                                    anchors.topMargin: 10
                                    anchors.bottomMargin: 24
                                    spacing: 2

                                    Repeater {
                                        model: backend.audioSpectrum

                                        delegate: Item {
                                            required property real modelData
                                            required property int index

                                            width: (
                                                liveBars.width - (47 * liveBars.spacing)
                                            ) / 48
                                            height: liveBars.height

                                            Rectangle {
                                                anchors.bottom: parent.bottom
                                                width: parent.width
                                                height: Math.max(1, parent.height * modelData)
                                                radius: Math.max(1, width / 3)
                                                color: modelData > 0.85
                                                       ? "#F15B64"
                                                       : modelData > 0.55
                                                         ? "#F0C76D"
                                                         : "#16CFC5"
                                            }

                                            Rectangle {
                                                visible: backend.audioPeakHold
                                                         && backend.audioSpectrumPeaks[index] > 0.01
                                                x: 0
                                                y: Math.max(
                                                    0,
                                                    parent.height
                                                    - parent.height
                                                      * backend.audioSpectrumPeaks[index]
                                                    - 2
                                                )
                                                width: parent.width
                                                height: 2
                                                color: "#F7F3B6"
                                            }
                                        }
                                    }
                                }

                                Text {
                                    anchors.left: parent.left
                                    anchors.leftMargin: 10
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 4
                                    text: "0"
                                    color: "#9AB0BB"
                                    font.pixelSize: 10
                                }
                                Text {
                                    anchors.left: parent.left
                                    anchors.leftMargin: parent.width * 0.25 - width / 2
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 4
                                    text: "1.5 kHz"
                                    color: "#9AB0BB"
                                    font.pixelSize: 10
                                }
                                Text {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 4
                                    text: "3 kHz"
                                    color: "#9AB0BB"
                                    font.pixelSize: 10
                                }
                                Text {
                                    anchors.right: parent.right
                                    anchors.rightMargin: parent.width * 0.25 - width / 2
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 4
                                    text: "4.5 kHz"
                                    color: "#9AB0BB"
                                    font.pixelSize: 10
                                }
                                Text {
                                    anchors.right: parent.right
                                    anchors.rightMargin: 10
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 4
                                    text: "6 kHz"
                                    color: "#9AB0BB"
                                    font.pixelSize: 10
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true

                                Text {
                                    text: "Dominant frequency: "
                                          + backend.audioDominantFrequency
                                    color: "#BFD0D8"
                                    font.pixelSize: 12
                                }

                                Item { Layout.fillWidth: true }

                                Text {
                                    text: "Estimated occupied bandwidth: "
                                          + backend.audioBandwidth
                                    color: "#BFD0D8"
                                    font.pixelSize: 12
                                }
                            }
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: backend.audioStatus
                        color: "#BFD0D8"
                        font.pixelSize: 13
                        wrapMode: Text.WordWrap
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 12

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 8
                            color: "#102A37"
                            border.color: "#28566A"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 13
                                spacing: 8

                                Text {
                                    text: "Microphones / Inputs"
                                    color: "#18D6D2"
                                    font.pixelSize: 15
                                    font.bold: true
                                }

                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true

                                    ColumnLayout {
                                        width: parent.width
                                        spacing: 6

                                        Repeater {
                                            model: backend.audioInputs

                                            delegate: Rectangle {
                                                required property var modelData
                                                Layout.fillWidth: true
                                                implicitHeight: 52
                                                radius: 6
                                                color: "#143542"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 8
                                                    spacing: 2

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.name
                                                        color: "#F2F7FA"
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                        elide: Text.ElideRight
                                                    }

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.detail
                                                        color: "#93AAB6"
                                                        font.pixelSize: 10
                                                        elide: Text.ElideRight
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 8
                            color: "#102A37"
                            border.color: "#28566A"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 13
                                spacing: 8

                                Text {
                                    text: "Speakers / Outputs"
                                    color: "#18D6D2"
                                    font.pixelSize: 15
                                    font.bold: true
                                }

                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true

                                    ColumnLayout {
                                        width: parent.width
                                        spacing: 6

                                        Repeater {
                                            model: backend.audioOutputs

                                            delegate: Rectangle {
                                                required property var modelData
                                                Layout.fillWidth: true
                                                implicitHeight: 52
                                                radius: 6
                                                color: "#143542"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 8
                                                    spacing: 2

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.name
                                                        color: "#F2F7FA"
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                        elide: Text.ElideRight
                                                    }

                                                    Text {
                                                        Layout.fillWidth: true
                                                        text: modelData.detail
                                                        color: "#93AAB6"
                                                        font.pixelSize: 10
                                                        elide: Text.ElideRight
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: width >= 900 ? 2 : 1
                columnSpacing: 12
                rowSpacing: 12

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "Network Test"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.networkTestResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Run Network Test"
                            onClicked: backend.runNetworkTest()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "Disk Test"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.diskTestResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Run Disk Test"
                            onClicked: backend.runDiskTest()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "USB Test"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.usbTestResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Scan USB Devices"
                            onClicked: backend.runUsbTest()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 175
                    radius: 10
                    color: "#10212C"
                    border.color: "#365E70"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 9

                        Text {
                            text: "Diagnostics"
                            color: "#F5F9FB"
                            font.pixelSize: 17
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: backend.diagnosticsResult
                            color: "#BFD0D8"
                            wrapMode: Text.WordWrap
                        }

                        RowLayout {
                            Button {
                                text: "Create Report"
                                onClicked: backend.runDiagnostics()
                            }

                            Button {
                                text: "Open Terminal"
                                onClicked: backend.openTerminal()
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 190
                radius: 10
                color: "#0D202B"
                border.color: "#C99B16"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 20

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 7

                        Text {
                            text: "Program and Dependency Updates"
                            color: "#FFD55A"
                            font.pixelSize: 19
                            font.bold: true
                        }

                        Text {
                            Layout.fillWidth: true
                            text: backend.updateStatus
                            color: "#DDE8ED"
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "The Raspberry Pi program updater uses the public GitHub ZIP installer and does not require a GitHub account."
                            color: "#AFC1CB"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }

                    ColumnLayout {
                        spacing: 10

                        Button {
                            Layout.preferredWidth: 220
                            text: "Update Program"
                            enabled: !backend.updateBusy
                            onClicked: backend.updateProgram()
                        }

                        Button {
                            Layout.preferredWidth: 220
                            text: "Update Dependencies"
                            enabled: !backend.updateBusy
                            onClicked: backend.updateDependencies()
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: backend.scanAudioDevices()
}
