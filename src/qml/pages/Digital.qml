import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    property var digital: backend.digitalState
    property var radio: backend.radioState

    ColumnLayout {
        anchors.fill: parent; spacing: 12

        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "Digital"; color: "#F5F9FB"; font.pixelSize: 28; font.bold: true }
                Text { text: "Unified digital operating workspace — independent HRPU engine boundary."; color: "#A4B7C2"; font.pixelSize: 13 }
            }
            Text { text: radio.frequency + " MHz   " + radio.band + "   " + digital.mode; color: "#18D6D2"; font.pixelSize: 18; font.bold: true }
        }

        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 160; radius: 10; color: "#0B202A"; border.color: "#2B667A"
            Canvas {
                anchors.fill: parent; anchors.margins: 12
                onPaint: {
                    var ctx=getContext("2d"); ctx.reset()
                    ctx.fillStyle="#071117";ctx.fillRect(0,0,width,height)
                    ctx.strokeStyle="#18D6D2";ctx.lineWidth=1.5;ctx.beginPath()
                    for(var x=0;x<width;x++){
                        var y=height*0.68
                            - Math.sin(x*0.035)*8
                            - Math.max(0,35-Math.abs(x-width*0.22))*0.9
                            - Math.max(0,28-Math.abs(x-width*0.51))*1.1
                            - Math.max(0,42-Math.abs(x-width*0.79))*0.75
                        if(x===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)
                    }
                    ctx.stroke()
                    ctx.fillStyle="#819AA7";ctx.font="10px sans-serif";ctx.fillText("PANADAPTER PREVIEW — live FFT service plugs into this workspace",10,14)
                }
                Component.onCompleted: requestPaint()
            }
        }

        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 150; radius: 10; color: "#0D202B"; border.color: "#365E70"
            Canvas {
                anchors.fill: parent; anchors.margins: 10
                onPaint: {
                    var ctx=getContext("2d");ctx.reset();ctx.fillStyle="#071117";ctx.fillRect(0,0,width,height)
                    for(var y=0;y<height;y+=5){
                        for(var x=0;x<width;x+=8){
                            var v=(Math.sin(x*0.08+y*0.035)+Math.sin(x*0.021-y*0.07)+2)/4
                            ctx.fillStyle="rgba(24,214,210,"+(0.04+v*0.42)+")";ctx.fillRect(x,y,6,4)
                        }
                    }
                    ctx.fillStyle="#819AA7";ctx.font="10px sans-serif";ctx.fillText("WATERFALL DISPLAY SURFACE",10,14)
                }
                Component.onCompleted: requestPaint()
            }
        }

        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 12

            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 10; color: "#0D202B"; border.color: "#365E70"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 14
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Decode Activity"; color: "#F5F9FB"; font.pixelSize: 17; font.bold: true; Layout.fillWidth: true }
                        Button { text: "Load Preview"; onClicked: backend.loadDigitalPreview() }
                    }
                    Text { text: digital.status; color: "#F0C76D"; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    ListView {
                        Layout.fillWidth: true; Layout.fillHeight: true; model: digital.decoded; clip: true
                        delegate: Rectangle {
                            required property var modelData
                            width: ListView.view.width; height: 34; color: index % 2 ? "#102630" : "#0B202A"
                            RowLayout {
                                anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                                Text { text: modelData.utc; color: "#819AA7"; Layout.preferredWidth: 65 }
                                Text { text: modelData.snr + " dB"; color: "#F0C76D"; Layout.preferredWidth: 55 }
                                Text { text: modelData.call; color: "#18D6D2"; font.bold: true; Layout.preferredWidth: 80 }
                                Text { text: modelData.grid; color: "#AFC1CB"; Layout.preferredWidth: 55 }
                                Text { text: modelData.message; color: "#F5F9FB"; Layout.fillWidth: true; elide: Text.ElideRight }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.preferredWidth: 330; Layout.fillHeight: true; radius: 10; color: "#0D202B"; border.color: "#365E70"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 14; spacing: 8
                    Text { text: "Operating Control"; color: "#F5F9FB"; font.pixelSize: 17; font.bold: true }
                    ComboBox {
                        id: digitalMode; Layout.fillWidth: true; model: digital.modes
                        onActivated: backend.setDigitalMode(currentText)
                    }
                    CheckBox { text: "Enable TX"; checked: digital.tx_enabled; onClicked: backend.setDigitalTxEnabled(checked) }
                    CheckBox { text: "Auto sequence"; checked: digital.auto_sequence; onClicked: backend.setDigitalAutoSequence(checked) }
                    RowLayout {
                        Button { text: "HALT"; Layout.fillWidth: true; onClicked: backend.setDigitalTxEnabled(false) }
                        Button { text: "TUNE"; Layout.fillWidth: true; onClicked: backend.requestDigitalTune() }
                    }
                    Rectangle { Layout.fillWidth: true; height: 1; color: "#28566A" }
                    Text { text: "ENGINE STATUS"; color: "#18D6D2"; font.pixelSize: 10; font.bold: true }
                    Text { Layout.fillWidth: true; text: digital.status; color: "#AFC1CB"; wrapMode: Text.WordWrap; font.pixelSize: 11 }
                    Text { Layout.fillWidth: true; text: "The R7 workspace is wired to shared radio state and map activity. Live weak-signal decode/modulation remains a separately implemented HRPU engine task."; color: "#819AA7"; wrapMode: Text.WordWrap; font.pixelSize: 10 }
                    Item { Layout.fillHeight: true }
                }
            }
        }
    }
}
