import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtWebEngine

Item {
    id: page
    property bool editingExisting: false

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "Radio over IP dashboards and hotspot status."; color: "#F5F9FB"; font.pixelSize: 28; font.bold: true }
                Text { text: "EuroNode, Pi-Star, WPSD and other local ROIP dashboards."; color: "#A4B7C2"; font.pixelSize: 14 }
            }
            Button { text: "+ Add"; onClicked: { page.editingExisting=false; nameField.text=""; urlField.text="http://"; editor.open() } }
            Button { text: "Edit"; onClicked: { page.editingExisting=true; nameField.text=backend.selectedDashboardName; urlField.text=backend.selectedDashboardUrl; editor.open() } }
            Button { text: "Delete"; onClicked: deleteDialog.open() }
        }

        Rectangle {
            Layout.fillWidth: true; implicitHeight: 66; radius: 9; color: "#0D202B"; border.color: "#285263"
            RowLayout {
                anchors.fill: parent; anchors.margins: 10; spacing: 8
                Button {
                    implicitWidth: 48
                    implicitHeight: 42
                    enabled: webView.canGoBack
                    onClicked: webView.goBack()
                    contentItem: Text {
                        text: "‹"
                        color: parent.enabled ? "#17313E" : "#8D9BA2"
                        font.pixelSize: 31
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 7
                        color: parent.hovered ? "#D7E3E8" : "#EEF3F6"
                        border.color: "#6F8793"
                    }
                }
                Button {
                    implicitWidth: 48
                    implicitHeight: 42
                    enabled: webView.canGoForward
                    onClicked: webView.goForward()
                    contentItem: Text {
                        text: "›"
                        color: parent.enabled ? "#17313E" : "#8D9BA2"
                        font.pixelSize: 31
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 7
                        color: parent.hovered ? "#D7E3E8" : "#EEF3F6"
                        border.color: "#6F8793"
                    }
                }
                Button {
                    implicitWidth: 48
                    implicitHeight: 42
                    onClicked: webView.reload()
                    contentItem: Text {
                        text: "⟳"
                        color: "#17313E"
                        font.pixelSize: 25
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 7
                        color: parent.hovered ? "#D7E3E8" : "#EEF3F6"
                        border.color: "#6F8793"
                    }
                }
                Button {
                    implicitHeight: 42
                    text: "Home"
                    onClicked: webView.url=backend.selectedDashboardHomeUrl
                }
                ComboBox {
                    id: selector; Layout.preferredWidth: 230; model: backend.dashboards; textRole: "name"; currentIndex: backend.selectedDashboardIndex
                    onActivated: function(index) { backend.selectDashboard(index); webView.url=backend.selectedDashboardUrl }
                }
                TextField { id: address; Layout.fillWidth: true; text: webView.url; selectByMouse: true; onAccepted: webView.url=text }
                Button { text: "Go"; onClicked: webView.url=address.text }
                Button { text: "Open Browser"; onClicked: backend.openDashboardInBrowser() }
            }
        }

        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; radius: 9; color: "white"; border.color: "#285263"; clip: true
            WebEngineView {
                id: webView; anchors.fill: parent; anchors.margins: 1; url: backend.selectedDashboardUrl
                settings.javascriptEnabled: true
                settings.localStorageEnabled: true
                settings.autoLoadImages: true
                onUrlChanged: address.text=url
                onLoadingChanged: function(r) {
                    if (r.status===WebEngineView.LoadStartedStatus) status.text="Loading…"
                    else if (r.status===WebEngineView.LoadSucceededStatus) status.text="Connected to "+backend.selectedDashboardName
                    else if (r.status===WebEngineView.LoadFailedStatus) status.text="Load failed: "+r.errorString
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Text { id: status; Layout.fillWidth: true; text: backend.dashboardStatus; color: "#AFC1CA"; elide: Text.ElideRight }
            ProgressBar { from:0; to:100; value:webView.loadProgress; visible:webView.loading; Layout.preferredWidth:160 }
            Button { text:"−"; onClicked:webView.zoomFactor=Math.max(0.5,webView.zoomFactor-0.1) }
            Text { text:webView.zoomFactor.toFixed(1)+"×"; color:"#AFC1CA" }
            Button { text:"+"; onClicked:webView.zoomFactor=Math.min(3.0,webView.zoomFactor+0.1) }
        }
    }

    Dialog {
        id: editor; modal: true; title: page.editingExisting ? "Edit Radio Dashboard" : "Add Radio Dashboard"; width:560; height:300; anchors.centerIn: Overlay.overlay
        contentItem: ColumnLayout {
            Label { text:"Dashboard name" }
            TextField { id:nameField; Layout.fillWidth:true; placeholderText:"EuroNode" }
            Label { text:"Dashboard URL" }
            TextField { id:urlField; Layout.fillWidth:true; placeholderText:"http://dvmega-euronode.local/" }
            Text { Layout.fillWidth:true; text:backend.dashboardStatus; color:"#AFC1CA"; wrapMode:Text.WordWrap }
            RowLayout {
                Layout.fillWidth:true
                Button { text:"Test"; onClicked:backend.testDashboardUrl(urlField.text) }
                Item { Layout.fillWidth:true }
                Button { text:"Cancel"; onClicked:editor.close() }
                Button { text:"Save"; onClicked: {
                    if (page.editingExisting) backend.updateDashboard(backend.selectedDashboardIndex,nameField.text,urlField.text)
                    else backend.addDashboard(nameField.text,urlField.text)
                    selector.currentIndex=backend.selectedDashboardIndex; webView.url=backend.selectedDashboardUrl; editor.close()
                } }
            }
        }
    }

    MessageDialog {
        id: deleteDialog; title:"Delete Dashboard"; text:"Delete "+backend.selectedDashboardName+"?"; buttons:MessageDialog.Yes|MessageDialog.No
        onButtonClicked:function(button,role) { if (button===MessageDialog.Yes) { backend.deleteDashboard(backend.selectedDashboardIndex); webView.url=backend.selectedDashboardUrl } }
    }
}
