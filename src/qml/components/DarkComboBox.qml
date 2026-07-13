import QtQuick
import QtQuick.Controls

ComboBox {
    id: control

    implicitHeight: 42
    leftPadding: 12
    rightPadding: 34

    contentItem: Text {
        leftPadding: 2
        text: control.displayText
        color: "#162630"
        font.pixelSize: 14
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    indicator: Text {
        x: control.width - width - 12
        y: control.height / 2 - height / 2
        text: "▼"
        color: "#405967"
        font.pixelSize: 11
    }

    background: Rectangle {
        radius: 7
        color: "#EEF3F6"
        border.width: control.activeFocus ? 2 : 1
        border.color: control.activeFocus ? "#19C2AF" : "#8EA4B0"
    }

    popup: Popup {
        y: control.height + 3
        width: control.width
        padding: 4

        background: Rectangle {
            radius: 7
            color: "#EEF3F6"
            border.color: "#8EA4B0"
        }

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
        }
    }

    delegate: ItemDelegate {
        required property var modelData
        width: control.width - 8

        contentItem: Text {
            text: modelData
            color: "#162630"
            font.pixelSize: 14
            verticalAlignment: Text.AlignVCenter
        }

        background: Rectangle {
            color: highlighted ? "#D7EBEB" : "transparent"
            radius: 5
        }
    }
}
