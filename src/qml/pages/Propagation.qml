import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    property bool showDx: true
    property bool showDecoded: true
    property bool showWspr: true
    property bool showBeacons: true
    property bool showGrid: false
    property bool showSun: true
    property bool showPath: true

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: contentColumn.implicitHeight + 28
        clip: true

        ColumnLayout {
            id: contentColumn
            width: parent.width
            spacing: 14

            RowLayout {
                Layout.fillWidth: true
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "Propagation"; color: "#F5F9FB"; font.pixelSize: 28; font.bold: true }
                    Text { text: "Radio conditions, VHF awareness and live greyline operating map."; color: "#A4B7C2"; font.pixelSize: 14 }
                }
                ColumnLayout {
                    Text { Layout.alignment: Qt.AlignRight; text: backend.propagationStatus; color: "#AFC1CB"; font.pixelSize: 12 }
                    Text { Layout.alignment: Qt.AlignRight; text: "Updated: " + backend.propagationUpdated; color: "#819AA7"; font.pixelSize: 11 }
                }
                Button { text: backend.propagationLoading ? "Updating…" : "Refresh"; enabled: !backend.propagationLoading; onClicked: backend.refreshPropagation() }
            }

            GridLayout {
                Layout.fillWidth: true; columns: 4; columnSpacing: 12; rowSpacing: 12
                Repeater {
                    model: [
                        {"title":"Solar Flux","value":backend.solarFlux,"detail":"10.7 cm radio flux","icon":"☀"},
                        {"title":"Planetary Kp","value":backend.kpIndex,"detail":backend.geomagneticState,"icon":"Kp"},
                        {"title":"X-Ray Level","value":backend.xrayClass,"detail":"GOES soft X-ray class","icon":"X"},
                        {"title":"Geomagnetic State","value":backend.geomagneticState,"detail":"Latest Kp assessment","icon":"◎"}
                    ]
                    delegate: Rectangle {
                        required property var modelData
                        Layout.fillWidth: true; Layout.preferredHeight: 132; radius: 10
                        color: "#10212C"; border.color: "#365E70"
                        RowLayout {
                            anchors.fill: parent; anchors.margins: 15; spacing: 12
                            Rectangle {
                                Layout.preferredWidth: 46; Layout.preferredHeight: 46; radius: 9; color: "#173746"
                                Text { anchors.centerIn: parent; text: modelData.icon; color: "#18D6D2"; font.pixelSize: 19; font.bold: true }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true; spacing: 4
                                Text { text: modelData.title; color: "#C9D8E0"; font.pixelSize: 13; font.bold: true }
                                Text { Layout.fillWidth: true; text: modelData.value; color: "#F5F9FB"; font.pixelSize: 22; font.bold: true; elide: Text.ElideRight }
                                Text { Layout.fillWidth: true; text: modelData.detail; color: "#8FA7B5"; font.pixelSize: 11; wrapMode: Text.WordWrap }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true; implicitHeight: 245; radius: 10; color: "#0D202B"; border.color: "#365E70"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 16; spacing: 10
                    Text { text: "Estimated HF Band Conditions"; color: "#F5F9FB"; font.pixelSize: 18; font.bold: true }
                    GridLayout {
                        Layout.fillWidth: true; Layout.fillHeight: true; columns: 4; columnSpacing: 9; rowSpacing: 9
                        Repeater {
                            model: backend.hfConditions
                            delegate: Rectangle {
                                required property var modelData
                                Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 72
                                radius: 8; color: "#12313F"; border.color: modelData.colour
                                ColumnLayout {
                                    anchors.centerIn: parent; spacing: 3
                                    Text { Layout.alignment: Qt.AlignHCenter; text: modelData.band; color: "#F5F9FB"; font.pixelSize: 17; font.bold: true }
                                    Text { Layout.alignment: Qt.AlignHCenter; text: modelData.condition; color: modelData.colour; font.pixelSize: 12; font.bold: true }
                                }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true; implicitHeight: 610; radius: 10; color: "#0D202B"; border.color: "#365E70"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 16; spacing: 9
                    RowLayout {
                        Layout.fillWidth: true
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 2
                            Text { text: "Radio Map — Greyline"; color: "#F5F9FB"; font.pixelSize: 20; font.bold: true }
                            Text { text: "Click anywhere for bearing, distance, sunrise, sunset and greyline window."; color: "#8FA7B5"; font.pixelSize: 11 }
                        }
                        Rectangle {
                            radius: 8; implicitWidth: demoText.implicitWidth + 20; implicitHeight: 28
                            color: backend.mapDemoMode ? "#463A1D" : "#143C34"; border.color: backend.mapDemoMode ? "#A98735" : "#28A98F"
                            Text { id: demoText; anchors.centerIn: parent; text: backend.mapDemoMode ? "DEMO SPOTS" : "LIVE"; color: "#F5F9FB"; font.pixelSize: 11; font.bold: true }
                        }
                        Text { id: utcClock; text: Qt.formatDateTime(new Date(), "HH:mm:ss 'UTC'"); color: "#18D6D2"; font.bold: true }
                    }

                    RowLayout {
                        spacing: 6
                        Repeater {
                            model: [
                                {"label":"DX","key":"dx"}, {"label":"DECODED","key":"decoded"},
                                {"label":"WSPR","key":"wspr"}, {"label":"BEACONS","key":"beacons"},
                                {"label":"GRID","key":"grid"}, {"label":"SUN","key":"sun"}, {"label":"PATH","key":"path"}
                            ]
                            delegate: Button {
                                required property var modelData
                                text: modelData.label
                                checkable: true
                                checked: modelData.key === "dx" ? page.showDx :
                                         modelData.key === "decoded" ? page.showDecoded :
                                         modelData.key === "wspr" ? page.showWspr :
                                         modelData.key === "beacons" ? page.showBeacons :
                                         modelData.key === "grid" ? page.showGrid :
                                         modelData.key === "sun" ? page.showSun : page.showPath
                                onClicked: {
                                    if (modelData.key === "dx") page.showDx = checked
                                    else if (modelData.key === "decoded") page.showDecoded = checked
                                    else if (modelData.key === "wspr") page.showWspr = checked
                                    else if (modelData.key === "beacons") page.showBeacons = checked
                                    else if (modelData.key === "grid") page.showGrid = checked
                                    else if (modelData.key === "sun") page.showSun = checked
                                    else page.showPath = checked
                                    radioCanvas.requestPaint()
                                }
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true; Layout.fillHeight: true; spacing: 12

                        Canvas {
                            id: radioCanvas
                            Layout.fillWidth: true; Layout.fillHeight: true
                            property date utcNow: new Date()

                            Timer {
                                interval: 1000; running: true; repeat: true
                                onTriggered: {
                                    radioCanvas.utcNow = new Date()
                                    utcClock.text = Qt.formatDateTime(radioCanvas.utcNow, "HH:mm:ss 'UTC'")
                                    radioCanvas.requestPaint()
                                }
                            }
                            Connections {
                                target: backend
                                function onRadioMapChanged() { radioCanvas.requestPaint() }
                                function onStationChanged() { radioCanvas.requestPaint() }
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: function(mouse) {
                                    var lon = mouse.x / width * 360 - 180
                                    var lat = 90 - mouse.y / height * 180
                                    backend.selectMapTarget(lat, lon)
                                    radioCanvas.requestPaint()
                                }
                            }

                            function x(lon) { return (lon + 180) / 360 * width }
                            function y(lat) { return (90 - lat) / 180 * height }
                            function gridCentre(loc) {
                                if (!loc || loc.length < 4 || loc.indexOf("Not ") === 0) return null
                                loc = loc.toUpperCase()
                                var a=loc.charCodeAt(0)-65, b=loc.charCodeAt(1)-65
                                var c=parseInt(loc.charAt(2)), d=parseInt(loc.charAt(3))
                                if (a<0 || a>17 || b<0 || b>17 || isNaN(c) || isNaN(d)) return null
                                return {"lon":-180+a*20+c*2+1, "lat":-90+b*10+d+0.5}
                            }
                            function solar(now) {
                                var start=Date.UTC(now.getUTCFullYear(),0,0)
                                var day=Math.floor((now.getTime()-start)/86400000)
                                var hour=now.getUTCHours()+now.getUTCMinutes()/60+now.getUTCSeconds()/3600
                                var g=2*Math.PI/365*(day-1+(hour-12)/24)
                                var dec=0.006918-0.399912*Math.cos(g)+0.070257*Math.sin(g)-0.006758*Math.cos(2*g)+0.000907*Math.sin(2*g)-0.002697*Math.cos(3*g)+0.00148*Math.sin(3*g)
                                var eq=229.18*(0.000075+0.001868*Math.cos(g)-0.032077*Math.sin(g)-0.014615*Math.cos(2*g)-0.040849*Math.sin(2*g))
                                var lon=-15*(hour-12+eq/60)
                                while(lon>180) lon-=360; while(lon<-180) lon+=360
                                return {"dec":dec,"lon":lon}
                            }
                            function elev(lat,lon,s) {
                                var r=Math.PI/180, p=lat*r, ha=(lon-s.lon)*r
                                return Math.asin(Math.sin(p)*Math.sin(s.dec)+Math.cos(p)*Math.cos(s.dec)*Math.cos(ha))/r
                            }
                            function land(ctx, pts) {
                                ctx.beginPath()
                                for(var i=0;i<pts.length;i++) {
                                    if(i===0) ctx.moveTo(x(pts[i][0]),y(pts[i][1]))
                                    else ctx.lineTo(x(pts[i][0]),y(pts[i][1]))
                                }
                                ctx.closePath(); ctx.fill(); ctx.stroke()
                            }
                            onPaint: {
                                var ctx=getContext("2d"); ctx.reset()
                                var w=width,h=height,s=solar(utcNow)
                                ctx.fillStyle="#10191F"; ctx.fillRect(0,0,w,h)

                                ctx.strokeStyle="#26343C"; ctx.lineWidth=1
                                for(var lo=-150;lo<=150;lo+=30){ctx.beginPath();ctx.moveTo(x(lo),0);ctx.lineTo(x(lo),h);ctx.stroke()}
                                for(var la=-60;la<=60;la+=30){ctx.beginPath();ctx.moveTo(0,y(la));ctx.lineTo(w,y(la));ctx.stroke()}

                                var shapes=[
                                  [[-168,72],[-140,70],[-125,55],[-124,40],[-115,31],[-100,20],[-86,18],[-80,27],[-66,44],[-53,48],[-55,60],[-78,72],[-110,73]],
                                  [[-82,13],[-72,9],[-64,-3],[-60,-16],[-66,-31],[-72,-45],[-68,-55],[-54,-50],[-45,-30],[-35,-7],[-50,5],[-65,10]],
                                  [[-11,72],[18,70],[40,66],[70,72],[105,74],[135,60],[165,60],[178,50],[150,38],[126,20],[108,8],[82,8],[62,25],[45,32],[30,36],[15,45],[0,50]],
                                  [[-17,36],[4,37],[25,31],[38,15],[50,3],[43,-15],[32,-34],[18,-35],[5,-28],[-5,-5],[-15,15]],
                                  [[112,-11],[132,-10],[153,-24],[146,-39],[128,-44],[114,-31]],
                                  [[166,-34],[178,-38],[174,-47],[166,-45]], [[-52,83],[-22,80],[-20,69],[-42,60],[-62,68]]
                                ]
                                ctx.fillStyle="#727E84";ctx.strokeStyle="#A6B0B5";ctx.lineWidth=1
                                for(var q=0;q<shapes.length;q++) land(ctx,shapes[q])

                                var cell=5
                                for(var py=0;py<h;py+=cell){
                                  var mla=90-(py+cell/2)/h*180
                                  for(var px=0;px<w;px+=cell){
                                    var mlo=(px+cell/2)/w*360-180, el=elev(mla,mlo,s)
                                    if(el<-18)ctx.fillStyle="rgba(0,0,0,0.65)"
                                    else if(el<-6)ctx.fillStyle="rgba(5,15,22,0.50)"
                                    else if(el<0)ctx.fillStyle="rgba(24,110,110,0.25)"
                                    else continue
                                    ctx.fillRect(px,py,cell,cell)
                                  }
                                }

                                if(page.showGrid){
                                  ctx.fillStyle="#AFC1CB";ctx.font="9px sans-serif"
                                  for(var gl=-150;gl<=150;gl+=30)ctx.fillText(gl+"°",x(gl)+2,12)
                                  for(var gt=-60;gt<=60;gt+=30)ctx.fillText(gt+"°",3,y(gt)-2)
                                }

                                var home=gridCentre(backend.locator)
                                if(home){
                                  var hx=x(home.lon),hy=y(home.lat)
                                  ctx.fillStyle="#18D6D2";ctx.beginPath();ctx.arc(hx,hy,5,0,Math.PI*2);ctx.fill()
                                  ctx.fillStyle="#F5F9FB";ctx.font="bold 11px sans-serif";ctx.fillText(backend.callsign,hx+8,hy-7)
                                }

                                var spots=backend.mapSpots
                                for(var i=0;i<spots.length;i++){
                                  var sp=spots[i]
                                  if((sp.source==="DX"&&!page.showDx)||(sp.source==="DECODED"&&!page.showDecoded)||(sp.source==="WSPR"&&!page.showWspr))continue
                                  var pos=gridCentre(sp.grid); if(!pos)continue
                                  var sx=x(pos.lon),sy=y(pos.lat)
                                  if(page.showPath&&home){ctx.strokeStyle="rgba(24,214,210,0.48)";ctx.beginPath();ctx.moveTo(x(home.lon),y(home.lat));ctx.lineTo(sx,sy);ctx.stroke()}
                                  ctx.fillStyle=sp.source==="DX"?"#F0C76D":sp.source==="WSPR"?"#A987E8":"#18D6D2"
                                  ctx.beginPath();ctx.arc(sx,sy,4,0,Math.PI*2);ctx.fill()
                                  ctx.fillStyle="#F5F9FB";ctx.font="10px sans-serif";ctx.fillText(sp.call+" "+sp.band+" "+sp.mode,sx+6,sy-5)
                                }

                                if(page.showSun){
                                  var sunLat=s.dec*180/Math.PI
                                  ctx.fillStyle="#F0C76D";ctx.beginPath();ctx.arc(x(s.lon),y(sunLat),5,0,Math.PI*2);ctx.fill()
                                  ctx.fillStyle="#F0C76D";ctx.fillText("SUN",x(s.lon)+8,y(sunLat)-5)
                                }

                                ctx.fillStyle="#F5F9FB";ctx.font="10px sans-serif";ctx.fillText("DAY",10,h-10)
                                ctx.fillStyle="#18D6D2";ctx.fillText("GREYLINE",45,h-10)
                                ctx.fillStyle="#819AA7";ctx.fillText("NIGHT",108,h-10)
                            }
                            Component.onCompleted: requestPaint()
                            onWidthChanged: requestPaint()
                            onHeightChanged: requestPaint()
                        }

                        Rectangle {
                            Layout.preferredWidth: 260; Layout.fillHeight: true; radius: 8; color: "#102630"; border.color: "#28566A"
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 14; spacing: 7
                                Text { text: "CLICKED TARGET"; color: "#18D6D2"; font.pixelSize: 11; font.bold: true }
                                Text { text: backend.mapTarget.name || "Click the map"; color: "#F5F9FB"; font.pixelSize: 18; font.bold: true; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Repeater {
                                    model: [
                                      {"n":"Bearing","v":backend.mapTarget.bearing},{"n":"Long Path","v":backend.mapTarget.long_path},
                                      {"n":"Distance","v":backend.mapTarget.distance},{"n":"Sunrise","v":backend.mapTarget.sunrise},
                                      {"n":"Sunset","v":backend.mapTarget.sunset},{"n":"Greyline","v":backend.mapTarget.greyline}
                                    ]
                                    delegate: RowLayout {
                                        required property var modelData
                                        Layout.fillWidth: true
                                        Text { Layout.fillWidth: true; text: modelData.n; color: "#8FA7B5"; font.pixelSize: 11 }
                                        Text { text: modelData.v || "—"; color: "#F5F9FB"; font.pixelSize: 11; font.bold: true }
                                    }
                                }
                                Rectangle { Layout.fillWidth: true; height: 1; color: "#28566A" }
                                Text { text: "NCDXF / IARU BEACONS"; color: "#18D6D2"; font.pixelSize: 11; font.bold: true }
                                Text { text: "NOW  " + (backend.beaconStatus.current || "—"); color: "#F5F9FB"; font.pixelSize: 16; font.bold: true }
                                Text { text: "NEXT  " + (backend.beaconStatus.next || "—") + "  •  " + (backend.beaconStatus.seconds || "—") + " s"; color: "#AFC1CB"; font.pixelSize: 11 }
                                Text { Layout.fillWidth: true; text: backend.beaconStatus.bands || ""; color: "#819AA7"; font.pixelSize: 10; wrapMode: Text.WordWrap }
                                Item { Layout.fillHeight: true }
                            }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true; spacing: 12
                Rectangle {
                    Layout.fillWidth: true; implicitHeight: 205; radius: 10; color: "#0D202B"; border.color: "#365E70"
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 15; spacing: 8
                        Text { text: "VHF Propagation"; color: "#F5F9FB"; font.pixelSize: 18; font.bold: true }
                        Repeater {
                            model: backend.vhfConditions
                            delegate: RowLayout {
                                required property var modelData
                                Layout.fillWidth: true
                                Text { Layout.fillWidth: true; text: modelData.name; color: "#AFC1CB"; font.pixelSize: 12 }
                                Text { text: modelData.state; color: modelData.state.indexOf("HIGH") >= 0 || modelData.state.indexOf("ACTIVE") >= 0 ? "#61DC4C" : "#F0C76D"; font.pixelSize: 12; font.bold: true }
                            }
                        }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true; implicitHeight: 205; radius: 10; color: "#0D202B"; border.color: "#365E70"
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 15; spacing: 7
                        Text { text: "Meteor Scatter"; color: "#F5F9FB"; font.pixelSize: 18; font.bold: true }
                        Text { text: backend.meteorStatus.name || "—"; color: "#18D6D2"; font.pixelSize: 22; font.bold: true }
                        Text { text: "Status: " + (backend.meteorStatus.state || "—"); color: "#F5F9FB"; font.pixelSize: 12 }
                        Text { text: "Peak: " + (backend.meteorStatus.peak || "—") + "   ZHR: " + (backend.meteorStatus.zhr || "—"); color: "#AFC1CB"; font.pixelSize: 12 }
                        Text { Layout.fillWidth: true; text: backend.meteorStatus.detail || ""; color: "#8FA7B5"; font.pixelSize: 11; wrapMode: Text.WordWrap }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true; implicitHeight: 205; radius: 10; color: "#0D202B"; border.color: "#365E70"
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 15; spacing: 7
                        Text { text: "HRPU Propagation Confidence"; color: "#F5F9FB"; font.pixelSize: 18; font.bold: true }
                        Repeater {
                            model: backend.propagationConfidence.slice(3, 7)
                            delegate: RowLayout {
                                required property var modelData
                                Layout.fillWidth: true
                                Text { text: modelData.band; color: "#AFC1CB"; font.pixelSize: 11; Layout.preferredWidth: 40 }
                                ProgressBar { Layout.fillWidth: true; from: 0; to: 100; value: modelData.confidence }
                                Text { text: modelData.confidence + "%"; color: "#18D6D2"; font.pixelSize: 11; font.bold: true }
                            }
                        }
                        Text { text: "Model framework ready for live WSPR / PSK / DX observation feeds."; color: "#819AA7"; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    }
                }
            }
        }
    }
}
