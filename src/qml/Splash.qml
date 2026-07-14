import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtMultimedia

Window {
    id: splash

    width: 1120
    height: 700
    visible: true
    color: "#01060A"
    flags: Qt.SplashScreen | Qt.FramelessWindowHint
    title: backend.appName

    property bool skipEnabled: false
    property bool videoFailed: false
    property bool videoStarted: false
    property real fallbackPhase: 0

    readonly property string video720:
        backend.assetRoot + "/../video/hrpu-intro-720p.webm"
    readonly property string video1080:
        backend.assetRoot + "/../video/hrpu-intro-1080p.webm"

    readonly property string selectedVideo:
        Screen.width >= 1600 ? video1080 : video720

    NumberAnimation on fallbackPhase {
        from: 0
        to: 360
        duration: 14000
        loops: Animation.Infinite
        running: fallbackScene.visible
    }

    Timer {
        interval: 2000
        running: true
        repeat: false
        onTriggered: splash.skipEnabled = true
    }

    Timer {
        interval: 1000
        running: true
        repeat: false
        onTriggered: {
            if (!splash.videoStarted)
                splash.videoFailed = true
        }
    }

    MediaPlayer {
        id: player
        source: splash.selectedVideo
        audioOutput: AudioOutput {
            volume: 0.0
            muted: true
        }
        videoOutput: videoOutput

        onPlaybackStateChanged: {
            if (playbackState === MediaPlayer.PlayingState)
                splash.videoStarted = true
        }

        onErrorOccurred: function(error, errorString) {
            splash.videoFailed = true
        }

        Component.onCompleted: play()
    }

    VideoOutput {
        id: videoOutput
        anchors.fill: parent
        fillMode: VideoOutput.PreserveAspectCrop
        visible: splash.videoStarted && !splash.videoFailed
    }

    Item {
        id: fallbackScene
        anchors.fill: parent
        visible: splash.videoFailed || !splash.videoStarted

        Canvas {
            id: backgroundCanvas
            anchors.fill: parent

            onPaint: {
                var ctx = getContext("2d")
                ctx.reset()

                var gradient = ctx.createRadialGradient(
                    width * 0.52,
                    height * 0.44,
                    20,
                    width * 0.52,
                    height * 0.44,
                    Math.max(width, height) * 0.72
                )
                gradient.addColorStop(0.0, "#0B2638")
                gradient.addColorStop(0.35, "#06131D")
                gradient.addColorStop(1.0, "#010408")
                ctx.fillStyle = gradient
                ctx.fillRect(0, 0, width, height)

                for (var i = 0; i < 220; i++) {
                    var x = (i * 97 + 31) % width
                    var y = (i * 53 + 17) % height
                    var size = 0.7 + ((i * 11) % 4) * 0.45
                    var alpha = 0.22 + ((i * 13) % 65) / 100
                    ctx.fillStyle = "rgba(225,242,255," + alpha + ")"
                    ctx.beginPath()
                    ctx.arc(x, y, size, 0, Math.PI * 2)
                    ctx.fill()
                }
            }

            Component.onCompleted: requestPaint()
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
        }

        Item {
            id: earthGroup
            width: 430
            height: 430
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: -35

            Rectangle {
                id: atmosphericGlow
                anchors.fill: parent
                radius: width / 2
                color: "#0B4E72"
                opacity: 0.18
                scale: 1.10
            }

            Rectangle {
                id: earth
                width: 390
                height: 390
                anchors.centerIn: parent
                radius: width / 2
                clip: true
                color: "#0A557A"
                border.width: 2
                border.color: "#8DE7FF"

                Rectangle {
                    width: parent.width * 1.55
                    height: parent.height
                    x: -parent.width * 0.29
                       + Math.sin(splash.fallbackPhase * Math.PI / 180) * 70
                    color: "transparent"

                    Repeater {
                        model: 13

                        delegate: Rectangle {
                            required property int index
                            width: 70 + (index % 4) * 37
                            height: 28 + (index % 3) * 25
                            radius: height / 2
                            x: (index * 81) % 500
                            y: 20 + (index * 59) % 330
                            rotation: -24 + index * 8
                            color:
                                index % 3 === 0
                                ? "#3E8E60"
                                : index % 3 === 1
                                  ? "#74AD7D"
                                  : "#B3C990"
                            opacity: 0.88
                        }
                    }

                    Repeater {
                        model: 16

                        delegate: Rectangle {
                            required property int index
                            width: 55 + (index % 5) * 20
                            height: 7 + (index % 3) * 4
                            radius: height / 2
                            x: (index * 101 + 19) % 520
                            y: 16 + (index * 47) % 350
                            rotation: -32 + index * 5
                            color: "#F4FBFF"
                            opacity: 0.24
                        }
                    }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: parent.width * 0.40
                    color: "#01050A"
                    opacity: 0.58
                }

                Rectangle {
                    anchors.fill: parent
                    radius: width / 2
                    color: "transparent"
                    border.color: "#B8F1FF"
                    border.width: 2
                    opacity: 0.76
                }
            }

            Repeater {
                model: 3

                delegate: Rectangle {
                    required property int index
                    width: 490 + index * 45
                    height: 200 + index * 22
                    radius: height / 2
                    anchors.centerIn: parent
                    color: "transparent"
                    border.width: 2
                    border.color:
                        index === 0 ? "#18D6D2" : "#2EA4CB"
                    opacity: 0.42 - index * 0.08
                    rotation: -18 + index * 12
                    scale:
                        0.96
                        + 0.035
                          * Math.sin(
                              (splash.fallbackPhase + index * 55)
                              * Math.PI / 180
                          )
                }
            }
        }

        Item {
            id: board
            width: 185
            height: 110
            x: earthGroup.x + earthGroup.width / 2
               + Math.cos(splash.fallbackPhase * Math.PI / 180) * 330
               - width / 2
            y: earthGroup.y + earthGroup.height / 2
               + Math.sin(splash.fallbackPhase * Math.PI / 180) * 145
               - height / 2
            rotation: splash.fallbackPhase * 0.33 - 12
            z: Math.sin(splash.fallbackPhase * Math.PI / 180) > 0 ? 5 : -1
            scale:
                0.78
                + 0.22
                  * (
                      Math.sin(splash.fallbackPhase * Math.PI / 180)
                      + 1
                    ) / 2

            Rectangle {
                anchors.fill: parent
                radius: 10
                color: "#176B4A"
                border.color: "#67E4AA"
                border.width: 2

                Rectangle {
                    width: 49
                    height: 49
                    radius: 5
                    anchors.centerIn: parent
                    color: "#1B262C"
                    border.color: "#9AAAB0"
                }

                Repeater {
                    model: 14

                    delegate: Rectangle {
                        required property int index
                        width: 10 + (index % 4) * 7
                        height: 7 + (index % 3) * 5
                        radius: 2
                        x: 10 + (index * 31) % 145
                        y: 10 + (index * 23) % 78
                        color:
                            index % 3 === 0
                            ? "#1D292F"
                            : "#B7C6C9"
                    }
                }

                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    anchors.top: parent.top
                    anchors.topMargin: 10
                    color: "#68FF76"
                    opacity:
                        0.45
                        + 0.55
                          * Math.abs(
                              Math.sin(splash.fallbackPhase * 0.18)
                          )
                }
            }
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 190
        color: "#01070C"
        opacity: 0.90
    }

    ColumnLayout {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 38
        anchors.rightMargin: 38
        anchors.bottomMargin: 26
        spacing: 8

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "HAMRADIO-PI ULTIMATE"
            color: "#F4FBFD"
            font.pixelSize: 29
            font.bold: true
            font.letterSpacing: 3
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: backend.startupStage
            color: "#18D6D2"
            font.pixelSize: 13
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.maximumWidth: 680
            Layout.alignment: Qt.AlignHCenter
            implicitHeight: 11
            radius: 6
            color: "#15313C"
            border.color: "#315B6C"

            Rectangle {
                height: parent.height
                width: parent.width * backend.startupProgress / 100
                radius: parent.radius
                color: "#18D6D2"

                Behavior on width {
                    NumberAnimation {
                        duration: 350
                        easing.type: Easing.OutCubic
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.maximumWidth: 680
            Layout.alignment: Qt.AlignHCenter

            Text {
                text: "Version " + backend.appVersion
                color: "#8FA7B5"
                font.pixelSize: 10
            }

            Item {
                Layout.fillWidth: true
            }

            Text {
                text: backend.startupProgress + "%"
                color: "#BFD0D8"
                font.pixelSize: 10
                font.bold: true
            }
        }
    }

    Button {
        anchors.left: parent.left
        anchors.leftMargin: 24
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 28
        text: "♥  Donate $1+"
        z: 20
        onClicked: backend.openDonate()
    }

    Button {
        anchors.right: parent.right
        anchors.rightMargin: 24
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 28
        visible: splash.skipEnabled
        text: "Skip"
        z: 20
        onClicked: backend.requestSkipSplash()
    }
}
