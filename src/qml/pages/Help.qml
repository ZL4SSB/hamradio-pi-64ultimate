import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    property int selectedTopic: 0
    property string searchText: ""

    property var topics: [
        {
            "title": "Quick Start",
            "category": "Getting Started",
            "summary": "Install, start and complete the first setup.",
            "body": "1. Install HamRadio-Pi Ultimate using Install-Windows.bat or install.sh.\n\n2. From the Dashboard, select Edit Profile and enter your callsign, locator, operator name, QTH and DMR ID.\n\n3. Open Preferences and choose appearance, startup, hardware and update options.\n\n4. Use Station Tools → Hardware to scan connected radios, SDRs, USB audio and serial interfaces.\n\n5. Use the left menu to open Propagation, Radio Dashboards, Station Tools and the Applications manager.",
            "document": "QUICK-START.md"
        },
        {
            "title": "Windows Installation",
            "category": "Installation",
            "summary": "Install from an extracted ZIP on Windows 10 or 11.",
            "body": "Extract the ZIP to a normal folder and double-click Install-Windows.bat. The installer adds PyQt6, Qt WebEngine and audio support, creates shortcuts and starts Ultimate.\n\nIf Windows blocks a downloaded file, right-click the ZIP, choose Properties, tick Unblock, then extract it again.",
            "document": "WINDOWS-INSTALL.md"
        },
        {
            "title": "Raspberry Pi Installation",
            "category": "Installation",
            "summary": "Install from ZIP or anonymously from the public repository.",
            "body": "From an extracted ZIP:\n\nchmod +x install.sh\n./install.sh\n\nAnonymous public install:\n\ncurl -fsSL https://raw.githubusercontent.com/ZL4SSB/Ham-Radio-Pi-Ultimate/main/install-public.sh | bash\n\nNo GitHub account is required.",
            "document": "RPI-FRESH-INSTALL.md"
        },
        {
            "title": "Station Profile",
            "category": "Setup",
            "summary": "Configure callsign, locator and digital-radio identity.",
            "body": "Station Profile stores your callsign, Maidenhead locator, operator name, QTH, country and DMR ID. These details are reused by the Dashboard and future plug-in applications.",
            "document": "STATION-PROFILE.md"
        },
        {
            "title": "Preferences",
            "category": "Setup",
            "summary": "Configure startup, hardware defaults, updates and HamClock.",
            "body": "Preferences are stored in config/settings.json. Use Export Backup before major changes. Reset Preferences returns application options to defaults but preserves Station Profile details.",
            "document": "PREFERENCES.md"
        },
        {
            "title": "Ultimate Shack Clock",
            "category": "Features",
            "summary": "Native local/UTC clock, sunrise, sunset and station-time overview.",
            "body": "Ultimate Shack Clock is built into HamRadio-Pi Ultimate. It uses your Station Profile locator for sunrise and sunset for sunrise and sunset. No external HamClock server is required.",
            "document": "SHACK-CLOCK.md"
        },
        {
            "title": "Radio Dashboards",
            "category": "Features",
            "summary": "Embed EuroNode, Pi-Star, WPSD and other web dashboards.",
            "body": "Radio Dashboards can store multiple local URLs. EuroNode is preconfigured with http://dvmega-euronode.local/. Use Add Dashboard for Pi-Star, WPSD, OpenWebRX, KiwiSDR or another local web interface.",
            "document": "RADIO-DASHBOARDS.md"
        },
        {
            "title": "Propagation",
            "category": "Features",
            "summary": "View the live W5MMW solar and propagation dashboard.",
            "body": "Propagation displays the live Solar Conditions and Ham Radio Propagation page supplied by W5MMW. Use the built-in navigation buttons to refresh it or open it in your normal browser.",
            "document": "PROPAGATION.md"
        },
        {
            "title": "Station Tools",
            "category": "Features",
            "summary": "Test audio, network, disk, USB and create diagnostics.",
            "body": "Use Detect Devices before audio testing. Start Monitor shows live microphone level, clipping, spectrum, dominant frequency and estimated bandwidth. Speaker Test plays a tone. Microphone Test records three seconds and reports the level. Network, disk and USB tests help isolate common setup faults.",
            "document": "SYSTEM-TOOLS.md"
        },
        {
            "title": "Updates",
            "category": "Maintenance",
            "summary": "Update the program and required dependencies.",
            "body": "Update Program uses the public anonymous installer on Raspberry Pi. Windows opens the newest ZIP download. Update Dependencies opens a visible terminal so package progress and administrator prompts can be read.",
            "document": "UPDATES.md"
        },
        {
            "title": "Troubleshooting",
            "category": "Support",
            "summary": "Common startup, audio, WebEngine and installer fixes.",
            "body": "Startup failure: run the application from a terminal and inspect reports/qml-startup-error.log.\n\nNo audio devices: confirm the USB sound card is connected, then run Detect Devices.\n\nRadio Dashboard not loading: confirm the URL opens in a normal browser and that both devices are on the same local network.\n\nPropagation unavailable: confirm internet and DNS using Station Tools.",
            "document": "TROUBLESHOOTING.md"
        }
    ]

    RowLayout {
        anchors.fill: parent
        spacing: 12

        Rectangle {
            Layout.preferredWidth: 315
            Layout.fillHeight: true
            radius: 10
            color: "#0D202B"
            border.color: "#365E70"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                Text {
                    text: "Help & Support"
                    color: "#F5F9FB"
                    font.pixelSize: 23
                    font.bold: true
                }

                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Search help topics…"
                    color: "#172731"
                    placeholderTextColor: "#667985"

                    background: Rectangle {
                        radius: 7
                        color: "#EEF3F6"
                        border.color: searchField.activeFocus ? "#19C2AF" : "#8EA4B0"
                    }

                    onTextChanged: searchText = text.toLowerCase()
                }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true

                    ColumnLayout {
                        width: parent.width
                        spacing: 7

                        Repeater {
                            model: topics

                            delegate: Button {
                                required property var modelData
                                required property int index

                                Layout.fillWidth: true
                                implicitHeight: visible ? 72 : 0

                                visible: searchText === ""
                                         || modelData.title.toLowerCase().includes(searchText)
                                         || modelData.category.toLowerCase().includes(searchText)
                                         || modelData.summary.toLowerCase().includes(searchText)

                                onClicked: selectedTopic = index

                                contentItem: Column {
                                    spacing: 3

                                    Text {
                                        width: parent.width
                                        text: modelData.title
                                        color: selectedTopic === index ? "#FFFFFF" : "#E2ECF1"
                                        font.pixelSize: 14
                                        font.bold: true
                                        elide: Text.ElideRight
                                    }

                                    Text {
                                        width: parent.width
                                        text: modelData.category
                                        color: selectedTopic === index ? "#9FF1E9" : "#18D6D2"
                                        font.pixelSize: 10
                                    }

                                    Text {
                                        width: parent.width
                                        text: modelData.summary
                                        color: selectedTopic === index ? "#DBE9EE" : "#93AAB6"
                                        font.pixelSize: 10
                                        elide: Text.ElideRight
                                    }
                                }

                                background: Rectangle {
                                    radius: 7
                                    color: selectedTopic === index
                                           ? "#0E7771"
                                           : (parent.hovered ? "#163846" : "#102A36")
                                    border.color: selectedTopic === index ? "#26C9BC" : "#28566A"
                                }
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 10
            color: "#0D202B"
            border.color: "#365E70"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 14

                Text {
                    text: topics[selectedTopic].category
                    color: "#18D6D2"
                    font.pixelSize: 13
                    font.bold: true
                }

                Text {
                    text: topics[selectedTopic].title
                    color: "#F5F9FB"
                    font.pixelSize: 27
                    font.bold: true
                }

                Text {
                    Layout.fillWidth: true
                    text: topics[selectedTopic].summary
                    color: "#B8C9D2"
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#315565"
                }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    TextArea {
                        text: topics[selectedTopic].body
                        readOnly: true
                        wrapMode: Text.WordWrap
                        color: "#E5EEF3"
                        font.pixelSize: 14
                        background: Rectangle {
                            color: "transparent"
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: backend.helpStatus
                    color: "#18D6D2"
                    font.pixelSize: 12
                    elide: Text.ElideRight
                }

                RowLayout {
                    Layout.fillWidth: true

                    Button {
                        text: "Open Full Guide"
                        onClicked: backend.openHelpDocument(
                            topics[selectedTopic].document
                        )
                    }

                    Button {
                        text: "Open Reports Folder"
                        onClicked: backend.openReportsFolder()
                    }

                    Button {
                        text: "Create Support Bundle"
                        onClicked: backend.createSupportBundle()
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: "GitHub Project"
                        onClicked: backend.openGithubProject()
                    }

                    Button {
                        text: "Report an Issue"
                        onClicked: backend.openGithubIssues()
                    }
                }
            }
        }
    }
}
