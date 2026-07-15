import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    property var sat: backend.satelliteState
    property var radio: backend.radioState

    ColumnLayout {
        anchors.fill: parent; spacing: 14

        Text { text: "Satellites & Rotator"; color: "#F5F9FB"; font.pixelSize: 28; font.bold: true }
        Text { text: "Shared satellite geometry, rotator state and future CAT Doppler correction."; color: "#A4B7C2"; font.pixelSize: 13 }

        GridLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; columns: 2; columnSpacing: 14; rowSpacing: 14

            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 10; color: "#0D202B"; border.color: "#365E70"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 18; spacing: 10
                    Text { text: "Satellite Target"; color: "#F5F9FB"; font.pixelSize: 19; font.bold: true }
                    ComboBox {
                        id: target; Layout.fillWidth: true; model: ["ISS","AO-91","SO-50"]
                        onActivated: backend.selectSatellitePreview(currentText)
                    }
                    Text { text: sat.target; color: "#18D6D2"; font.pixelSize: 25; font.bold: true }
                    Text { text: sat.status; color: "#F0C76D"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    CheckBox { text: "Auto track"; checked: sat.tracking; onClicked: backend.setSatelliteTracking(checked) }
                    Text { text: "Doppler correction: " + sat.doppler_hz + " Hz"; color: "#AFC1CB" }
                    Text { text: "Radio context: " + radio.frequency + " MHz " + radio.mode; color: "#819AA7" }
                    Item { Layout.fillHeight: true }
                }
            }

            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 10; color: "#0B202A"; border.color: "#2B667A"
                Canvas {
                    anchors.fill: parent; anchors.margins: 20
                    onPaint: {
                        var ctx=getContext("2d");ctx.reset()
                        var cx=width/2,cy=height/2,r=Math.min(width,height)*0.4
                        ctx.fillStyle="#071117";ctx.fillRect(0,0,width,height)
                        ctx.strokeStyle="#365E70";ctx.lineWidth=1
                        for(var q=1;q<=4;q++){ctx.beginPath();ctx.arc(cx,cy,r*q/4,0,Math.PI*2);ctx.stroke()}
                        ctx.beginPath();ctx.moveTo(cx-r,cy);ctx.lineTo(cx+r,cy);ctx.moveTo(cx,cy-r);ctx.lineTo(cx,cy+r);ctx.stroke()
                        var az=sat.azimuth*Math.PI/180, el=sat.elevation
                        var rr=r*(1-Math.max(0,Math.min(90,el))/90)
                        var sx=cx+Math.sin(az)*rr,sy=cy-Math.cos(az)*rr
                        ctx.strokeStyle="#18D6D2";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(sx,sy);ctx.stroke()
                        ctx.fillStyle="#F0C76D";ctx.beginPath();ctx.arc(sx,sy,6,0,Math.PI*2);ctx.fill()
                        ctx.fillStyle="#F5F9FB";ctx.font="bold 11px sans-serif";ctx.fillText(sat.target,sx+9,sy-7)
                        ctx.fillStyle="#819AA7";ctx.fillText("N",cx-4,12);ctx.fillText("E",width-15,cy);ctx.fillText("S",cx-4,height-5);ctx.fillText("W",5,cy)
                    }
                    Connections { target: backend; function onSatelliteChanged() { parent.requestPaint() } }
                    Component.onCompleted: requestPaint()
                }
                Column {
                    anchors.left: parent.left; anchors.bottom: parent.bottom; anchors.margins: 18
                    Text { text: "AZ  " + sat.azimuth + "°"; color: "#18D6D2"; font.pixelSize: 18; font.bold: true }
                    Text { text: "EL  " + sat.elevation + "°"; color: "#F0C76D"; font.pixelSize: 18; font.bold: true }
                }
            }
        }
    }
}
