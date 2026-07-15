import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    property string selectedCategory: "All categories"

    function matches(app) {
        var query = search.text.toLowerCase().trim()
        var categoryOkay = selectedCategory === "All categories"
                           || app.category === selectedCategory
        var queryOkay = query.length === 0
                       || app.name.toLowerCase().indexOf(query) >= 0
                       || app.category.toLowerCase().indexOf(query) >= 0
                       || app.description.toLowerCase().indexOf(query) >= 0
        return categoryOkay && queryOkay
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    text: "Applications"
                    color: "#F4F8FA"
                    font.pixelSize: 27
                    font.bold: true
                }

                Text {
                    text: "Browse, search and manage amateur-radio software."
                    color: "#95ACB9"
                    font.pixelSize: 14
                }
            }

            ColumnLayout {
                spacing: 4

                Text {
                    text: appGrid.count + " application"
                          + (appGrid.count === 1 ? "" : "s")
                    color: "#8FA7B5"
                    font.pixelSize: 13
                    Layout.alignment: Qt.AlignRight
                }

                Button {
                    text: "Check Installed"
                    onClicked: backend.refreshApplications()
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            TextField {
                id: search
                Layout.fillWidth: true
                placeholderText: "Search applications…"
                selectByMouse: true
            }

            ComboBox {
                id: category
                Layout.preferredWidth: 220
                model: [
                    "All categories",
                    "Digital Modes",
                    "Radio Programming",
                    "SDR",
                    "Packet & APRS",
                    "Satellite",
                    "Logging",
                    "Images",
                    "Radio Control"
                ]
                onCurrentTextChanged: page.selectedCategory = currentText
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 10
            color: "#0C1B25"
            border.color: "#294A5A"
            clip: true

            GridView {
                id: appGrid
                anchors.fill: parent
                anchors.margins: 10
                cellWidth: Math.max(390, width / 2)
                cellHeight: 174
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                model: backend.applications

                ScrollBar.vertical: ScrollBar { }

                delegate: Item {
                    id: delegateRoot
                    required property var modelData
                    width: appGrid.cellWidth
                    height: page.matches(modelData) ? appGrid.cellHeight : 0
                    visible: page.matches(modelData)

                    Rectangle {
                        anchors.fill: parent
                        anchors.rightMargin: 10
                        anchors.bottomMargin: 10
                        radius: 10
                        color: "#10212C"
                        border.color: "#294A5A"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 8

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Rectangle {
                                    Layout.preferredWidth: 46
                                    Layout.preferredHeight: 42
                                    radius: 7
                                    color: "#1C3747"

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.name.substring(0, 2).toUpperCase()
                                        color: "#20C6B3"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        Layout.fillWidth: true
                                        text: modelData.name
                                        color: "#F3F8FA"
                                        font.pixelSize: 17
                                        font.bold: true
                                        elide: Text.ElideRight
                                    }

                                    Text {
                                        text: modelData.category
                                        color: "#20C6B3"
                                        font.pixelSize: 12
                                    }
                                }

                                Text {
                                    text: modelData.installed ? "● Installed" : "● Available"
                                    color: modelData.installed ? "#70D93D" : "#F0C76D"
                                    font.pixelSize: 12
                                    font.bold: true
                                }
                            }

                            Text {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                text: modelData.description
                                color: "#A7BBC6"
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                maximumLineCount: 2
                                elide: Text.ElideRight
                            }

                            Item { Layout.fillHeight: true }

                            RowLayout {
                                Layout.fillWidth: true

                                Button {
                                    text: modelData.installed ? "Launch" : "Install"
                                    onClicked: {
                                        if (modelData.installed) {
                                            backend.launchApplication(modelData.command)
                                        } else {
                                            backend.installApplication(modelData.package)
                                        }
                                    }
                                }

                                Button {
                                    text: "Help"
                                    onClicked: backend.openApplicationHelp(modelData.name)
                                }

                                Button {
                                    visible: modelData.installed
                                    text: "Remove"
                                    onClicked: {
                                        removeDialog.packageName = modelData.package
                                        removeDialog.appName = modelData.name
                                        removeDialog.open()
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                Text {
                                    visible: modelData.recommended
                                    text: "★ Recommended"
                                    color: "#66A8FF"
                                    font.pixelSize: 12
                                    font.bold: true
                                }
                            }
                        }
                    }
                }

                Text {
                    anchors.centerIn: parent
                    visible: appGrid.count === 0
                    text: "No applications match this search."
                    color: "#8FA7B5"
                    font.pixelSize: 15
                }
            }
        }
    }

    Dialog {
        id: removeDialog
        property string packageName: ""
        property string appName: ""

        title: "Remove " + appName + "?"
        modal: true
        anchors.centerIn: Overlay.overlay
        standardButtons: Dialog.Yes | Dialog.Cancel

        contentItem: Text {
            width: 410
            padding: 14
            text:
                "HRPU will hand removal to the operating system.\n\n"
                + "Raspberry Pi/Linux uses apt and asks for sudo confirmation.\n"
                + "Windows opens the registered application uninstaller."
            color: "#F4F8FA"
            wrapMode: Text.WordWrap
        }

        onAccepted: backend.removeApplication(packageName)
    }

}
