#!/usr/bin/env python3
from __future__ import annotations
import platform, subprocess, sys, threading, tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, ttk
from services.config_service import ConfigService
from services.weather_service import WeatherError, fetch_current_weather, format_weather_summary
from ui import AppTheme, ToolTip

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATION_FILE = PROJECT_DIR / "config" / "station.json"
SETTINGS_FILE = PROJECT_DIR / "config" / "settings.json"
APPLICATION_FILE = PROJECT_DIR / "src" / "data" / "applications.json"
VERSION_FILE = PROJECT_DIR / "config" / "version.json"
WPSD_SCRIPT = PROJECT_DIR / "scripts" / "wpsd-card-builder.sh"
STATION_WIZARD = PROJECT_DIR / "src" / "station_wizard.py"
STATION_BUILDER = PROJECT_DIR / "src" / "station_builder.py"
APPLICATION_BROWSER = PROJECT_DIR / "src" / "application_browser.py"
HARDWARE = PROJECT_DIR / "src" / "hardware.py"
UPDATER = PROJECT_DIR / "src" / "updater.py"
SETTINGS = PROJECT_DIR / "src" / "settings.py"

class HamRadioPiUltimate:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate")
        self.root.geometry("1120x760")
        self.root.minsize(960,650)
        AppTheme.apply(self.root)
        self.station = ConfigService.load_json(STATION_FILE,{})
        self.catalogue = ConfigService.load_json(APPLICATION_FILE,{"applications":[]})
        self.version_info = ConfigService.load_json(VERSION_FILE,{"version":"0.4.0","edition":"Community"})
        self.callsign_value=tk.StringVar(); self.grid_value=tk.StringVar(); self.local_time_value=tk.StringVar(); self.utc_time_value=tk.StringVar()
        self.radio_value=tk.StringVar(); self.sdr_value=tk.StringVar(); self.station_type_value=tk.StringVar(); self.weather_value=tk.StringVar(value="Loading...")
        self.health_value=tk.StringVar(value="Not checked")
        self.weather_refresh_job=None; self.weather_loading=False; self.tooltips=[]
        self.build_interface(); self.refresh_station_information(); self.update_clocks(); self.refresh_weather()

    def build_interface(self):
        main=ttk.Frame(self.root,padding=24,style="App.TFrame"); main.pack(fill="both",expand=True)
        header=ttk.Frame(main,style="App.TFrame"); header.pack(fill="x",pady=(0,18))
        title=ttk.Frame(header,style="App.TFrame"); title.pack(side="left")
        ttk.Label(title,text="HamRadio-Pi Ultimate",style="Header.TLabel").pack(anchor="w")
        ttk.Label(title,text="Build your station, not your software list.",style="Subheader.TLabel").pack(anchor="w",pady=(3,0))
        ttk.Label(header,text="COMMUNITY EDITION",style="StatusGood.TLabel").pack(side="right",anchor="n",pady=(8,0))
        content=ttk.Frame(main,style="App.TFrame"); content.pack(fill="both",expand=True)
        for c in (0,1): content.columnconfigure(c,weight=1,uniform="dashboard")
        for r in (0,1): content.rowconfigure(r,weight=1,uniform="dashboard")
        self.build_station_card(content); self.build_status_card(content); self.build_information_card(content); self.build_tools_card(content)
        version=self.version_info.get("version","Unknown"); edition=self.version_info.get("edition","Community")
        ttk.Label(main,text=f"HamRadio-Pi Ultimate {edition} Edition — Version {version}",style="Footer.TLabel").pack(pady=(16,0))

    @staticmethod
    def create_card(parent,title,row,column):
        outer=ttk.Frame(parent,style="Card.TFrame",padding=18); outer.grid(row=row,column=column,padx=9,pady=9,sticky="nsew")
        ttk.Label(outer,text=title,style="CardTitle.TLabel").pack(anchor="w",pady=(0,14)); return outer

    def add_card_row(self,parent,title,variable,value_style="CardValue.TLabel"):
        row=ttk.Frame(parent,style="Card.TFrame"); row.pack(fill="x",pady=5)
        ttk.Label(row,text=title,style="CardLabel.TLabel").pack(side="left")
        ttk.Label(row,textvariable=variable,style=value_style,wraplength=310,justify="right").pack(side="right")

    def add_tooltip(self,widget,text): self.tooltips.append(ToolTip(widget,text))

    def build_station_card(self,parent):
        card=self.create_card(parent,"My Station",0,0)
        for title,var in [("Callsign",self.callsign_value),("Grid",self.grid_value),("Station Type",self.station_type_value),("Current UTC",self.utc_time_value),("Local Time",self.local_time_value)]: self.add_card_row(card,title,var)
        b=ttk.Button(card,text="Edit Station Profile",command=self.open_station_wizard,style="Accent.TButton"); b.pack(fill="x",pady=(18,0))
        self.add_tooltip(b,"Edit your callsign, grid square, country, DMR ID, preferred radio and preferred SDR.")

    def build_status_card(self,parent):
        card=self.create_card(parent,"Station Status",0,1)
        self.add_card_row(card,"Station Health",self.health_value,"StatusGood.TLabel")
        self.add_card_row(card,"Connected Radio",self.radio_value); self.add_card_row(card,"Connected SDR",self.sdr_value)
        apps=self.catalogue.get("applications",[]); count=tk.StringVar(value=str(len(apps) if isinstance(apps,list) else 0)); self.add_card_row(card,"Catalogue Applications",count)
        ttk.Label(card,text="Hardware and station diagnostics will appear here as the Station Health module develops.",style="CardLabel.TLabel",wraplength=430,justify="left").pack(anchor="w",pady=(16,0))

    def build_information_card(self,parent):
        card=self.create_card(parent,"Radio Information",1,0)
        for title in ("Latest DX Cluster Spots","Solar Conditions","Propagation"):
            self.add_card_row(card,title,tk.StringVar(value="Coming soon"))
        self.add_card_row(card,"Weather",self.weather_value)
        b=ttk.Button(card,text="Refresh Weather",command=self.refresh_weather,style="Modern.TButton"); b.pack(fill="x",pady=(16,0))
        self.add_tooltip(b,"Download the latest weather for the grid square or exact location configured under Settings.")

    def build_tools_card(self,parent):
        card=self.create_card(parent,"Tools",1,1); grid=ttk.Frame(card,style="Card.TFrame"); grid.pack(fill="both",expand=True)
        for c in (0,1): grid.columnconfigure(c,weight=1)
        buttons=[
            ("Applications",self.open_application_browser,"Browse supported ham-radio software, view details, check installation status and install packages."),
            ("Build a Station",self.show_station_builder,"Choose a complete station type such as digital modes, SDR, APRS, satellite or MMDVM."),
            ("WPSD SD Card Builder",self.open_wpsd_builder,"Prepare an SD card for a separate WPSD MMDVM hotspot."),
            ("Hardware",self.open_hardware,"Detect USB devices, CAT cables, serial ports, audio interfaces, SDR receivers, GPS and MMDVM hardware."),
            ("Updates",self.open_updater,"Check GitHub for a newer version, back up settings and install the update."),
            ("Settings",self.open_settings,"Configure weather, data sources, location and application preferences."),
        ]
        for i,(text,cmd,tip) in enumerate(buttons):
            b=ttk.Button(grid,text=text,command=cmd,style="Modern.TButton"); b.grid(row=i//2,column=i%2,sticky="ew",padx=6,pady=6); self.add_tooltip(b,tip)

    def refresh_station_information(self):
        self.station=ConfigService.load_json(STATION_FILE,{})
        self.callsign_value.set(self.station.get("callsign") or "Not configured"); self.grid_value.set(self.station.get("grid_square") or "Not configured")
        self.station_type_value.set(self.station.get("station_type") or "Not selected"); self.radio_value.set(self.station.get("preferred_radio") or "Not configured"); self.sdr_value.set(self.station.get("preferred_sdr") or "Not configured")

    def update_clocks(self):
        self.utc_time_value.set(datetime.now(timezone.utc).strftime("%H:%M:%S UTC")); self.local_time_value.set(datetime.now().astimezone().strftime("%H:%M:%S")); self.root.after(1000,self.update_clocks)

    def refresh_weather(self):
        if self.weather_loading: return
        if self.weather_refresh_job is not None: self.root.after_cancel(self.weather_refresh_job); self.weather_refresh_job=None
        self.weather_loading=True; self.weather_value.set("Updating..."); threading.Thread(target=self._weather_worker,daemon=True).start()

    def _weather_worker(self):
        settings=ConfigService.load_json(SETTINGS_FILE,{}); station=ConfigService.load_json(STATION_FILE,{})
        try: summary=format_weather_summary(fetch_current_weather(settings,station))
        except WeatherError as error: summary=str(error)
        self.root.after(0,lambda:self._finish_weather_refresh(summary,settings))

    def _finish_weather_refresh(self,summary,settings):
        self.weather_value.set(summary); self.weather_loading=False; weather=settings.get("weather",{}); refresh=20
        if isinstance(weather,dict):
            try: refresh=int(weather.get("refresh_minutes",20))
            except (TypeError,ValueError): refresh=20
        refresh=max(5,min(refresh,120)); self.weather_refresh_job=self.root.after(refresh*60*1000,self.refresh_weather)

    def run_python_tool(self,path,title):
        if not path.exists(): messagebox.showerror(title,f"{title} could not be found."); return
        try: subprocess.run([sys.executable,str(path)],check=False)
        except OSError as error: messagebox.showerror(title, f"{title} could not start: {error}")

    def open_station_wizard(self): self.run_python_tool(STATION_WIZARD,"Station Setup Wizard"); self.refresh_station_information(); self.refresh_weather()
    def show_station_builder(self): self.run_python_tool(STATION_BUILDER,"Station Builder"); self.refresh_station_information()
    def open_application_browser(self): self.run_python_tool(APPLICATION_BROWSER,"Applications")
    def open_hardware(self): self.run_python_tool(HARDWARE,"Hardware Detection")
    def open_updater(self): self.run_python_tool(UPDATER,"Update Manager")
    def open_settings(self): self.run_python_tool(SETTINGS,"Settings"); self.refresh_station_information(); self.refresh_weather()

    def open_wpsd_builder(self):
        if platform.system() != "Linux": messagebox.showinfo("WPSD SD Card Builder","The WPSD SD Card Builder runs on Raspberry Pi OS."); return
        if not WPSD_SCRIPT.exists(): messagebox.showerror("WPSD SD Card Builder","The WPSD builder script could not be found."); return
        try: subprocess.Popen(["bash",str(WPSD_SCRIPT)])
        except OSError as error: messagebox.showerror("WPSD SD Card Builder",f"The WPSD builder could not start: {error}")

def main():
    root=tk.Tk(); HamRadioPiUltimate(root); root.mainloop()

if __name__ == "__main__": main()
