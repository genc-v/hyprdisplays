#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
from pathlib import Path
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio

APP_ID = "com.github.hyprdisplays.installer"
INSTALL_DIR = Path.home() / ".local/share/hyprdisplays"
DESKTOP_DIR = Path.home() / ".local/share/applications"
ICON_DIR = Path.home() / ".local/share/icons/hicolor/512x512/apps"
SYSTEMD_DIR = Path.home() / ".config/systemd/user"

class InstallManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
    
    def check_is_installed(self):
        return (INSTALL_DIR / "hyprdisplays.py").exists()

    def check_service_status(self):
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "hyprdisplays-daemon.service"],
                capture_output=True, text=True
            )
            return result.stdout.strip() == "active"
        except:
            return False

    def install(self):
        try:
            # Create directories
            for d in [INSTALL_DIR, DESKTOP_DIR, ICON_DIR, SYSTEMD_DIR]:
                d.mkdir(parents=True, exist_ok=True)

            # Copy source files
            files = ["hyprdisplays.py", "hyprdisplays-daemon.py"]
            for f in files:
                src = self.project_root / "src" / f
                dst = INSTALL_DIR / f
                if src.exists():
                    shutil.copy2(src, dst)
                    dst.chmod(0o755)

            # Copy icons
            icons = [
                ("logo.png", "hyprdisplays.png")
            ]
            for src_name, dst_name in icons:
                src = self.project_root / "assets" / src_name
                if src.exists():
                    shutil.copy2(src, ICON_DIR / dst_name)

            # Process and install desktop files
            desktop_files = ["hyprdisplays.desktop"]
            for f in desktop_files:
                src = self.project_root / "assets" / f
                if src.exists():
                    content = src.read_text()
                    # Fix Exec path
                    # We assume the .desktop file has Exec=python3 /path/to/script.py or Exec=script.py
                    # Replacing Exec=.*hyprdisplays.py with Exec=INSTALL_DIR/hyprdisplays.py
                    import re
                    content = re.sub(r'Exec=.*hyprdisplays\.py', f'Exec={INSTALL_DIR}/hyprdisplays.py', content)
                    
                    (DESKTOP_DIR / f).write_text(content)
                    (DESKTOP_DIR / f).chmod(0o755)

            # Create systemd service
            service_content = f"""[Unit]
Description=HyprDisplays Monitor Detection Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart={INSTALL_DIR}/hyprdisplays-daemon.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""
            (SYSTEMD_DIR / "hyprdisplays-daemon.service").write_text(service_content)

            # Reload and enable service
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "--user", "enable", "--now", "hyprdisplays-daemon.service"], check=True)
            
            return True, "Installation successful!"
        except Exception as e:
            return False, str(e)

    def uninstall(self):
        try:
            # Stop and disable service
            subprocess.run(["systemctl", "--user", "stop", "hyprdisplays-daemon.service"], check=False)
            subprocess.run(["systemctl", "--user", "disable", "hyprdisplays-daemon.service"], check=False)
            
            # Remove service file
            if (SYSTEMD_DIR / "hyprdisplays-daemon.service").exists():
                (SYSTEMD_DIR / "hyprdisplays-daemon.service").unlink()
            
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)

            # Remove files
            if INSTALL_DIR.exists():
                shutil.rmtree(INSTALL_DIR)
            
            # Remove desktop files
            for f in ["hyprdisplays.desktop", "hyprsettings.desktop"]:
                p = DESKTOP_DIR / f
                if p.exists(): p.unlink()
                
            return True, "Uninstallation successful!"
        except Exception as e:
            return False, str(e)

class InstallerWindow(Adw.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("HyprDisplays Installer")
        self.set_default_size(600, 450)
        self.manager = InstallManager()
        
        # Main Layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(box)

        # Header Bar
        header = Adw.HeaderBar()
        box.append(header)

        # Content
        clamp = Adw.Clamp(maximum_size=500)
        box.append(clamp)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin_top=24, margin_bottom=24, margin_start=12, margin_end=12)
        clamp.set_child(main_box)

        # Icon/Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        title_box.set_halign(Gtk.Align.CENTER)
        
        icon = Gtk.Image.new_from_icon_name("system-software-install-symbolic")
        icon.set_pixel_size(64)
        title_box.append(icon)
        
        title_label = Gtk.Label(label="HyprDisplays Setup")
        title_label.add_css_class("title-1")
        title_box.append(title_label)
        
        main_box.append(title_box)

        # Status Group
        self.status_group = Adw.PreferencesGroup(title="Status")
        main_box.append(self.status_group)
        
        self.app_status_row = Adw.ActionRow(title="Application Files")
        self.status_group.add(self.app_status_row)
        
        self.service_status_row = Adw.ActionRow(title="Background Service")
        self.status_group.add(self.service_status_row)
        
        self.app_status_icon = Gtk.Image()
        self.app_status_row.add_suffix(self.app_status_icon)
        
        self.service_status_icon = Gtk.Image()
        self.service_status_row.add_suffix(self.service_status_icon)

        # Actions Group
        action_group = Adw.PreferencesGroup(title="Actions")
        main_box.append(action_group)
        
        self.install_row = Adw.ActionRow(title="Install / Update")
        self.install_row.set_subtitle("Install application files and enable service")
        install_btn = Gtk.Button(label="Install", valign=Gtk.Align.CENTER)
        install_btn.add_css_class("suggested-action")
        install_btn.connect("clicked", self.on_install_clicked)
        self.install_row.add_suffix(install_btn)
        action_group.add(self.install_row)

        self.uninstall_row = Adw.ActionRow(title="Uninstall")
        self.uninstall_row.set_subtitle("Remove all components")
        uninstall_btn = Gtk.Button(label="Uninstall", valign=Gtk.Align.CENTER)
        uninstall_btn.add_css_class("destructive-action")
        uninstall_btn.connect("clicked", self.on_uninstall_clicked)
        self.uninstall_row.add_suffix(uninstall_btn)
        action_group.add(self.uninstall_row)

        self.refresh_status()

    def refresh_status(self):
        is_installed = self.manager.check_is_installed()
        service_active = self.manager.check_service_status()

        self.app_status_row.set_subtitle("Installed" if is_installed else "Not Installed")
        self.app_status_icon.set_from_icon_name("object-select-symbolic" if is_installed else "action-unavailable-symbolic")

        self.service_status_row.set_subtitle("Running" if service_active else "Stopped/Not Installed")
        self.service_status_icon.set_from_icon_name("object-select-symbolic" if service_active else "action-unavailable-symbolic")
        
        # Toggle visibility
        self.install_row.set_visible(not is_installed)
        self.uninstall_row.set_visible(is_installed)

    def show_message(self, message, is_error=False):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Installer",
            body=message
        )
        dialog.add_response("ok", "OK")
        dialog.present()

    def on_install_clicked(self, widget):
        success, msg = self.manager.install()
        self.refresh_status()
        self.show_message(msg)

    def on_uninstall_clicked(self, widget):
        success, msg = self.manager.uninstall()
        self.refresh_status()
        self.show_message(msg)

class InstallerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = InstallerWindow(application=self)
        win.present()

if __name__ == "__main__":
    app = InstallerApp()
    app.run(sys.argv)
