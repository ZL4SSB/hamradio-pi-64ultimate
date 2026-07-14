import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

Item {
    id: page
    property string localUrl: "http://127.0.0.1:8765"

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 82
            radius: 9
            color: "#0D202B"
            border.color: "#365E70"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 13
                spacing: 10

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 3

                    Text {
                        text: "Ultimate Live Propagation"
                        color: "#F5F9FB"
                        font.pixelSize: 23
                        font.bold: true
                    }

                    Text {
                        text: backend.propagationServerDetail
                        color: "#AFC1CB"
                        font.pixelSize: 11
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }

                Rectangle {
                    implicitWidth: 108
                    implicitHeight: 34
                    radius: 17
                    color:
                        backend.propagationServerStatus === "Running"
                        ? "#173D2A"
                        : backend.propagationServerStatus === "Connection Error"
                          ? "#4B2025"
                          : "#3B3118"
                    border.color:
                        backend.propagationServerStatus === "Running"
                        ? "#61DC4C"
                        : backend.propagationServerStatus === "Connection Error"
                          ? "#F15B64"
                          : "#F0C76D"

                    Text {
                        anchors.centerIn: parent
                        text: backend.propagationServerStatus
                        color: "#F4F8FA"
                        font.pixelSize: 11
                        font.bold: true
                    }
                }

                ColumnLayout {
                    spacing: 1

                    Text {
                        text: "Last update"
                        color: "#8FA7B5"
                        font.pixelSize: 9
                    }

                    Text {
                        text: backend.propagationServerLastUpdate
                        color: "#DCE8EE"
                        font.pixelSize: 10
                        font.bold: true
                    }
                }

                Button {
                    text: "Start"
                    enabled:
                        backend.propagationServerStatus !== "Running"
                    onClicked: backend.startPropagationServer()
                }

                Button {
                    text: "Stop"
                    enabled:
                        backend.propagationServerStatus === "Running"
                        || backend.propagationServerStatus === "Connection Error"
                    onClicked: backend.stopPropagationServer()
                }

                Button {
                    text: "Restart"
                    onClicked: backend.restartPropagationServer()
                }

                Button {
                    text: "Refresh"
                    onClicked: {
                        backend.refreshPropagationServerStatus()
                        propagationView.reload()
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 36
            radius: 7
            color: "#10212C"
            border.color: "#365E70"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12

                Text {
                    text:
                        "Cluster: "
                        + backend.propagationClusterStatus
                    color: "#BFD0D8"
                    font.pixelSize: 11
                }

                Text {
                    text:
                        "Spots: "
                        + backend.propagationSpotCount
                    color: "#BFD0D8"
                    font.pixelSize: 11
                }

                Item {
                    Layout.fillWidth: true
                }

                Text {
                    text:
                        backend.callsign.length > 0
                        ? backend.callsign
                          + " · "
                          + backend.locator
                        : "Set callsign and locator from Dashboard → Edit Profile"
                    color: "#18D6D2"
                    font.pixelSize: 11
                    font.bold: true
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 9
            color: "#06151F"
            border.color: "#365E70"
            clip: true

            WebEngineView {
                id: propagationView
                anchors.fill: parent
                anchors.margins: 1
                url: page.localUrl

                settings.javascriptEnabled: true
                settings.localStorageEnabled: true
                settings.fullScreenSupportEnabled: true

                onLoadingChanged: function(request) {
                    if (
                        request.status
                        === WebEngineView.LoadFailedStatus
                    ) {
                        errorText.text =
                            "The local propagation page did not respond.\n\n"
                            + request.errorString
                        errorPanel.visible = true
                    } else if (
                        request.status
                        === WebEngineView.LoadSucceededStatus
                    ) {
                        errorPanel.visible = false
                        backend.refreshPropagationServerStatus()
                    }
                }
            }

            Rectangle {
                id: errorPanel
                anchors.centerIn: parent
                width: Math.min(
                    parent.width - 50,
                    640
                )
                height: 220
                radius: 10
                visible:
                    backend.propagationServerStatus
                    !== "Running"
                color: "#10212C"
                border.color:
                    backend.propagationServerStatus
                    === "Connection Error"
                    ? "#F15B64"
                    : "#F0C76D"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 12

                    Text {
                        text:
                            "Local propagation server "
                            + backend.propagationServerStatus
                        color:
                            backend.propagationServerStatus
                            === "Connection Error"
                            ? "#F15B64"
                            : "#F0C76D"
                        font.pixelSize: 19
                        font.bold: true
                    }

                    Text {
                        id: errorText
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        text:
                            backend.propagationServerDetail
                        color: "#E5EEF3"
                        wrapMode: Text.WordWrap
                    }

                    RowLayout {
                        Button {
                            text: "Start Server"
                            onClicked:
                                backend.startPropagationServer()
                        }

                        Button {
                            text: "Restart"
                            onClicked:
                                backend.restartPropagationServer()
                        }

                        Button {
                            text: "Try Page Again"
                            onClicked: {
                                backend.refreshPropagationServerStatus()
                                propagationView.url = page.localUrl
                            }
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: backend

        function onPropagationServerChanged() {
            if (
                backend.propagationServerStatus
                === "Running"
                && errorPanel.visible
            ) {
                propagationView.url = page.localUrl
            }
        }
    }

    Component.onCompleted: {
        backend.ensurePropagationServer()
        backend.refreshPropagationServerStatus()
    }
}
