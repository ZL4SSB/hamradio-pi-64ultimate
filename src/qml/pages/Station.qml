import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: profileColumn.implicitHeight + 24
        clip: true

        ColumnLayout {
            id: profileColumn
            width: parent.width
            spacing: 16

            Text {
                text: "Station Profile"
                color: "#F4F8FA"
                font.pixelSize: 27
                font.bold: true
            }

            Text {
                text: "Your amateur-radio station identity and radio service IDs."
                color: "#B8C9D2"
                font.pixelSize: 14
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 500
                radius: 10
                color: "#10212C"
                border.color: "#365E70"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 28

                    GridLayout {
                        Layout.preferredWidth: Math.min(720, parent.width * 0.68)
                        Layout.alignment: Qt.AlignTop
                        columns: 2
                        columnSpacing: 18
                        rowSpacing: 16

                        Text {
                            text: "Callsign"
                            color: "#E3EDF2"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 155
                        }

                        DarkTextField {
                            id: callsignField
                            Layout.preferredWidth: 430
                            Layout.maximumWidth: 520
                            text: backend.callsign === "Not configured" ? "" : backend.callsign
                            placeholderText: "Example: ZL4SSB"
                        }

                        Text {
                            text: "Maidenhead locator"
                            color: "#E3EDF2"
                            font.pixelSize: 14
                            font.bold: true
                        }

                        DarkTextField {
                            id: locatorField
                            Layout.preferredWidth: 430
                            Layout.maximumWidth: 520
                            text: backend.locator === "Not configured" ? "" : backend.locator
                            placeholderText: "Example: RE54"
                        }

                        Text {
                            text: "Operator name"
                            color: "#E3EDF2"
                            font.pixelSize: 14
                            font.bold: true
                        }

                        DarkTextField {
                            id: operatorField
                            Layout.preferredWidth: 430
                            Layout.maximumWidth: 520
                            text: backend.operatorName === "Not configured" ? "" : backend.operatorName
                            placeholderText: "Operator name"
                        }

                        Text {
                            text: "QTH"
                            color: "#E3EDF2"
                            font.pixelSize: 14
                            font.bold: true
                        }

                        DarkTextField {
                            id: qthField
                            Layout.preferredWidth: 430
                            Layout.maximumWidth: 520
                            text: backend.qth === "Not configured" ? "" : backend.qth
                            placeholderText: "Town or region"
                        }

                        Text {
                            text: "Country"
                            color: "#E3EDF2"
                            font.pixelSize: 14
                            font.bold: true
                        }

                        DarkTextField {
                            id: countryField
                            Layout.preferredWidth: 430
                            Layout.maximumWidth: 520
                            text: backend.country
                            placeholderText: "Country"
                        }

                        Text {
                            text: "DMR ID"
                            color: "#E3EDF2"
                            font.pixelSize: 14
                            font.bold: true
                        }

                        DarkTextField {
                            id: dmrField
                            Layout.preferredWidth: 430
                            Layout.maximumWidth: 520
                            text: backend.dmrId === "Not configured" ? "" : backend.dmrId
                            placeholderText: "Example: 5300378"
                        }

                        Item {
                            Layout.preferredWidth: 155
                        }

                        Button {
                            text: "Save Station Profile"
                            onClicked: backend.saveStation(
                                callsignField.text,
                                locatorField.text,
                                operatorField.text,
                                qthField.text,
                                countryField.text,
                                dmrField.text
                            )
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 9
                        color: "#0B1B25"
                        border.color: "#294A5A"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 12

                            Text {
                                text: "Current Station"
                                color: "#18D6D2"
                                font.pixelSize: 18
                                font.bold: true
                            }

                            Text {
                                text: backend.callsign
                                color: "#F4F8FA"
                                font.pixelSize: 25
                                font.bold: true
                            }

                            Text {
                                text: backend.locator
                                color: "#8DE7DF"
                                font.pixelSize: 17
                                font.bold: true
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: "#294A5A"
                            }

                            Text {
                                text: "Operator"
                                color: "#AFC1CB"
                                font.pixelSize: 12
                            }

                            Text {
                                Layout.fillWidth: true
                                text: backend.operatorName
                                color: "#F4F8FA"
                                font.pixelSize: 15
                                font.bold: true
                                wrapMode: Text.WordWrap
                            }

                            Text {
                                text: "QTH"
                                color: "#AFC1CB"
                                font.pixelSize: 12
                            }

                            Text {
                                Layout.fillWidth: true
                                text: backend.qth
                                color: "#F4F8FA"
                                font.pixelSize: 15
                                wrapMode: Text.WordWrap
                            }

                            Text {
                                text: "DMR ID"
                                color: "#AFC1CB"
                                font.pixelSize: 12
                            }

                            Text {
                                text: backend.dmrId
                                color: "#F4F8FA"
                                font.pixelSize: 15
                                font.bold: true
                            }

                            Item { Layout.fillHeight: true }
                        }
                    }
                }
            }
        }
    }
}
