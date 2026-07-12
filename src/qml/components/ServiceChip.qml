import QtQuick
import QtQuick.Layouts

Rectangle {
    property string serviceName: ""
    property bool running: false

    radius: 7
    color: "#12313F"
    border.color: "#26596A"
    implicitWidth: 120
    implicitHeight: 38

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10

        Rectangle {
            width: 10
            height: 10
            radius: 5
            color: running ? "#66D849" : "#647984"
        }

        Text {
            Layout.fillWidth: true
            text: serviceName
            color: "#EAF2F6"
            font.pixelSize: 12
            elide: Text.ElideRight
        }
    }
}
