#!/usr/bin/env python3
"""
HyprDisplays Daemon - Background monitor detection service

This runs in the background and automatically applies monitor configurations
when displays are connected/disconnected. No GUI required.
"""

import json
import subprocess
import time
import sys
from pathlib import Path
from datetime import datetime

class ConfigurationManager:
    """Manages saved monitor configurations based on connected monitors"""
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "hypr"
        self.profiles_path = self.config_dir / "hyprdisplays_profiles.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profiles = self.load_profiles()
    
    def load_profiles(self):
        """Load saved monitor profiles"""
        if self.profiles_path.exists():
            try:
                with open(self.profiles_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {"profiles": {}, "history": []}
        return {"profiles": {}, "history": []}
    
    def get_monitor_fingerprint(self, monitors_info):
        """Create a unique fingerprint for a set of monitors"""
        monitor_ids = []
        for monitor in monitors_info:
            make = monitor.get('make', '').strip()
            model = monitor.get('model', '').strip()
            serial = monitor.get('serial', '').strip()
            name = monitor.get('name', 'unknown')
            
            if make or model or serial:
                monitor_id = f"{name}|{make}|{model}|{serial}"
            else:
                monitor_id = name
            
            monitor_ids.append(monitor_id)
        
        sorted_ids = sorted(monitor_ids)
        fingerprint = ";;".join(sorted_ids)
        return fingerprint
    
    def load_configuration(self, monitors_info):
        """Load saved configuration for this monitor setup"""
        fingerprint = self.get_monitor_fingerprint(monitors_info)
        
        if fingerprint in self.profiles.get("profiles", {}):
            config = self.profiles["profiles"][fingerprint]
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Found saved configuration")
            print(f"  Fingerprint: {fingerprint[:60]}...")
            print(f"  Saved at: {config.get('saved_at', 'unknown')}")
            return config.get("monitors", {})
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No saved configuration found")
        return None

class MonitorDaemon:
    """Background daemon for monitor detection"""
    
    def __init__(self, check_interval=3):
        self.config_manager = ConfigurationManager()
        self.check_interval = check_interval
        self.last_fingerprint = None
        self.running = True
        print(f"[{datetime.now().strftime('%H:%M:%S')}] HyprDisplays Daemon started")
        print(f"  Check interval: {check_interval} seconds")
        print(f"  Profiles: {self.config_manager.profiles_path}")
    
    def get_monitors_info(self):
        """Get current monitor information from Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'monitors', '-j'], 
                                  capture_output=True, text=True, check=True)
            displays_data = json.loads(result.stdout)
            
            monitors_info = []
            for d in displays_data:
                monitors_info.append({
                    'name': d.get('name'),
                    'make': d.get('make', ''),
                    'model': d.get('model', ''),
                    'serial': d.get('serial', ''),
                    'description': d.get('description', '')
                })
            
            return monitors_info
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error getting monitors: {e}")
            return []
    
    def apply_configuration(self, saved_config):
        """Apply a saved configuration"""
        try:
            applied_count = 0
            for monitor_name, config in saved_config.items():
                if config.get('disabled'):
                    cmd = f"{monitor_name},disabled"
                else:
                    resolution = config.get('resolution', f"{config.get('width')}x{config.get('height')}")
                    refresh = config.get('refresh_rate', 60)
                    x = config.get('x', 0)
                    y = config.get('y', 0)
                    scale = config.get('scale', 1.0)
                    transform = config.get('transform', 0)
                    
                    cmd = f"{monitor_name},{resolution}@{refresh},{x}x{y},{scale},transform,{transform}"
                
                result = subprocess.run(['hyprctl', 'keyword', 'monitor', cmd], 
                                      capture_output=True, text=True, check=False)
                
                if result.returncode == 0:
                    applied_count += 1
                else:
                    print(f"  Warning: Failed to configure {monitor_name}")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Applied configuration to {applied_count} monitor(s)")
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error applying configuration: {e}")
            return False
    
    def check_and_apply(self):
        """Check for monitor changes and apply configuration if needed"""
        monitors_info = self.get_monitors_info()
        
        if not monitors_info:
            return
        
        current_fingerprint = self.config_manager.get_monitor_fingerprint(monitors_info)
        
        # Check if setup has changed
        if current_fingerprint != self.last_fingerprint:
            monitor_names = [m['name'] for m in monitors_info]
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Monitor setup changed!")
            print(f"  Detected monitors: {', '.join(monitor_names)}")
            
            # Try to load saved configuration
            saved_config = self.config_manager.load_configuration(monitors_info)
            
            if saved_config:
                print(f"  Applying saved configuration...")
                if self.apply_configuration(saved_config):
                    print(f"  ✓ Configuration applied successfully")
                else:
                    print(f"  ✗ Failed to apply configuration")
            else:
                print(f"  No saved configuration for this setup")
                print(f"  Use HyprDisplays GUI to configure and save")
            
            self.last_fingerprint = current_fingerprint
    
    def run(self):
        """Main daemon loop"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring for display changes...")
        print(f"  Press Ctrl+C to stop\n")
        
        # Initial check
        self.check_and_apply()
        
        try:
            while self.running:
                time.sleep(self.check_interval)
                self.check_and_apply()
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Daemon stopped by user")
        except Exception as e:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HyprDisplays Background Daemon')
    parser.add_argument('--interval', type=int, default=3,
                      help='Check interval in seconds (default: 3)')
    parser.add_argument('--verbose', action='store_true',
                      help='Verbose output')
    
    args = parser.parse_args()
    
    daemon = MonitorDaemon(check_interval=args.interval)
    daemon.run()

if __name__ == '__main__':
    main()
