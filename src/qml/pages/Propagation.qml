import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: contentColumn.implicitHeight + 24
        clip: true

        ColumnLayout {
            id: contentColumn
            width: parent.width
            spacing: 14

            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: "Propagation"
                        color: "#F5F9FB"
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: "Live solar and geomagnetic conditions for amateur radio."
                        color: "#A4B7C2"
                        font.pixelSize: 14
                    }
                }

                ColumnLayout {
                    spacing: 2

                    Text {
                        Layout.alignment: Qt.AlignRight
                        text: backend.propagationStatus
                        color: backend.propagationLoading ? "#F0C76D" : "#AFC1CB"
                        font.pixelSize: 12
                    }

                    Text {
                        Layout.alignment: Qt.AlignRight
                        text: "Updated: " + backend.propagationUpdated
                        color: "#819AA7"
                        font.pixelSize: 11
                    }
                }

                Button {
                    text: backend.propagationLoading ? "Updating…" : "Refresh"
                    enabled: !backend.propagationLoading
                    onClicked: backend.refreshPropagation()
                }

                Button {
                    text: "Open NOAA"
                    onClicked: backend.openNoaaSpaceWeather()
                }
            }

            ProgressBar {
                Layout.fillWidth: true
                indeterminate: true
                visible: backend.propagationLoading
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 4
                columnSpacing: 12
                rowSpacing: 12

                Repeater {
                    model: [
                        {
                            "title": "Solar Flux",
                            "value": backend.solarFlux,
                            "detail": "10.7 cm radio flux",
                            "icon": "☀"
                        },
                        {
                            "title": "Planetary Kp",
                            "value": backend.kpIndex,
                            "detail": backend.geomagneticState,
                            "icon": "Kp"
                        },
                        {
                            "title": "Solar Wind",
                            "value": backend.solarWindSpeed,
                            "detail": backend.solarWindDensity,
                            "icon": "↝"
                        },
                        {
                            "title": "Interplanetary Bz",
                            "value": backend.solarWindBz,
                            "detail": "GSM magnetic field",
                            "icon": "Bz"
                        },
                        {
                            "title": "X-Ray Level",
                            "value": backend.xrayClass,
                            "detail": "GOES soft X-ray class",
                            "icon": "X"
                        },
                        {
                            "title": "Geomagnetic State",
                            "value": backend.geomagneticState,
                            "detail": "Based on latest Kp",
                            "icon": "◎"
                        }
                    ]

                    delegate: Rectangle {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.preferredHeight: 145
                        radius: 10
                        color: "#10212C"
                        border.color: "#365E70"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 13

                            Rectangle {
                                Layout.preferredWidth: 48
                                Layout.preferredHeight: 48
                                radius: 9
                                color: "#173746"

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.icon
                                    color: "#18D6D2"
                                    font.pixelSize: 20
                                    font.bold: true
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 5

                                Text {
                                    text: modelData.title
                                    color: "#C9D8E0"
                                    font.pixelSize: 13
                                    font.bold: true
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: modelData.value
                                    color: "#F5F9FB"
                                    font.pixelSize: 23
                                    font.bold: true
                                    elide: Text.ElideRight
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: modelData.detail
                                    color: "#8FA7B5"
                                    font.pixelSize: 11
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 260
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
                            text: "Estimated HF Band Conditions"
                            color: "#F5F9FB"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            text: "Guide only — actual paths vary by time, season and location"
                            color: "#8FA7B5"
                            font.pixelSize: 11
                        }
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 4
                        columnSpacing: 10
                        rowSpacing: 10

                        Repeater {
                            model: backend.hfConditions

                            delegate: Rectangle {
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumHeight: 76
                                radius: 8
                                color: "#12313F"
                                border.color: "#28566A"

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 4

                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.band
                                        color: "#F5F9FB"
                                        font.pixelSize: 17
                                        font.bold: true
                                    }

                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.condition
                                        color: modelData.colour
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 155
                radius: 10
                color: "#0D202B"
                border.color: "#365E70"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 8

                    Text {
                        text: "What the readings mean"
                        color: "#F5F9FB"
                        font.pixelSize: 18
                        font.bold: true
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "Higher solar flux generally supports the higher HF bands. A low Kp usually means a quieter geomagnetic field. Strong M- or X-class X-ray events can cause short-term radio blackouts on sunlit paths. Solar-wind Bz turning strongly southward can precede disturbed geomagnetic conditions."
                        color: "#C2D1D9"
                        font.pixelSize: 13
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "Data source: NOAA Space Weather Prediction Center. Automatic refresh every five minutes."
                        color: "#18D6D2"
                        font.pixelSize: 12
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        if (backend.propagationUpdated === "Never")
            backend.refreshPropagation()
    }
}
