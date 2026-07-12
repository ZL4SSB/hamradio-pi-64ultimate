import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: profileColumn.implicitHeight + 20
        clip: true

        ColumnLayout {
            id: profileColumn
            width: parent.width
            spacing: 14

            Text {
                text: "Station Profile"
                color: "#F4F8FA"
                font.pixelSize: 27
                font.bold: true
            }

            Text {
                text: "Your amateur-radio station identity and radio service IDs."
                color: "#95ACB9"
                font.pixelSize: 14
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 455
                radius: 10
                color: "#10212C"
                border.color: "#294A5A"

                GridLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    columns: 2
                    columnSpacing: 22
                    rowSpacing: 15

                    Label { text: "Callsign" }
                    TextField {
                        id: callsignField
                        Layout.fillWidth: true
                        text: backend.callsign === "Not configured" ? "" : backend.callsign
                        placeholderText: "Example: ZL4SSB"
                    }

                    Label { text: "Maidenhead locator" }
                    TextField {
                        id: locatorField
                        Layout.fillWidth: true
                        text: backend.locator === "Not configured" ? "" : backend.locator
                        placeholderText: "Example: RE54"
                    }

                    Label { text: "Operator name" }
                    TextField {
                        id: operatorField
                        Layout.fillWidth: true
                        text: backend.operatorName
                    }

                    Label { text: "QTH" }
                    TextField {
                        id: qthField
                        Layout.fillWidth: true
                        text: backend.qth
                        placeholderText: "Town or region"
                    }

                    Label { text: "Country" }
                    TextField {
                        id: countryField
                        Layout.fillWidth: true
                        text: backend.country
                    }

                    Label { text: "DMR ID" }
                    TextField {
                        id: dmrField
                        Layout.fillWidth: true
                        text: backend.dmrId
                        placeholderText: "Example: 5300378"
                    }

                    Item { Layout.fillWidth: true }

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
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 115
                radius: 10
                color: "#0C1B25"
                border.color: "#294A5A"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18

                    ColumnLayout {
                        Layout.fillWidth: true
                        Text {
                            text: "Current station"
                            color: "#95ACB9"
                        }
                        Text {
                            text: backend.callsign + " · " + backend.locator
                            color: "#20C6B3"
                            font.pixelSize: 20
                            font.bold: true
                        }
                    }

                    ColumnLayout {
                        Text {
                            text: backend.operatorName.length > 0
                                  ? backend.operatorName
                                  : "Operator not entered"
                            color: "#F4F8FA"
                            font.bold: true
                        }
                        Text {
                            text: backend.qth.length > 0
                                  ? backend.qth
                                  : "QTH not entered"
                            color: "#95ACB9"
                        }
                    }
                }
            }
        }
    }
}
