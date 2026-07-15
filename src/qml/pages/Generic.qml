import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    property string pageTitle: ""
    property string pageSubtitle: ""
    property var cards: []
    signal cardClicked(string card)

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        Text {
            text: pageTitle
            color: "#F4F8FA"
            font.pixelSize: 27
            font.bold: true
        }

        Text {
            text: pageSubtitle
            color: "#95ACB9"
            font.pixelSize: 14
        }

        GridLayout {
            Layout.fillWidth: true
            columns: 2
            columnSpacing: 10
            rowSpacing: 10

            Repeater {
                model: cards
                delegate: Rectangle {
                    id: cardRoot
                    Layout.fillWidth: true
                    implicitHeight: 110
                    radius: 10
                    color: "#10212C"
                    border.color: "#294A5A"

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: page.cardClicked(modelData)
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        Text {
                            text: modelData
                            color: "#F3F8FA"
                            font.pixelSize: 17
                            font.bold: true
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "Select to open this function or view its current availability."
                            color: "#A7BBC6"
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
