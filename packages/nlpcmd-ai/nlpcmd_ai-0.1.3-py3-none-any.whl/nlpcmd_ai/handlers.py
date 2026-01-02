"""
Built-in Command Handlers

This module contains handler implementations for different command categories.
"""

import os
import platform
import socket
import requests
from pathlib import Path
from typing import Dict
from .base_handler import BaseHandler, CommandResult
from .platform_utils import platform_utils, command_mapper


class FileHandler(BaseHandler):
    """Handler for file and directory operations"""
    
    def can_handle(self, category: str, action: str) -> bool:
        return category == "file_operation"
    
    def execute(self, command: str, parameters: Dict, dry_run: bool = False) -> CommandResult:
        """Execute file operations"""
        if dry_run:
            return CommandResult(
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
                command=command
            )
        
        # Additional validation for file operations
        if "path" in parameters:
            path = parameters["path"]
            if not self.validate_path(path):
                return CommandResult(
                    success=False,
                    output="",
                    error=f"Operation not allowed on path: {path}",
                    exit_code=1,
                    command=command
                )
        
        return self.run_command(command)


class NetworkHandler(BaseHandler):
    """Handler for network operations"""
    
    def can_handle(self, category: str, action: str) -> bool:
        return category == "network"
    
    def execute(self, command: str, parameters: Dict, dry_run: bool = False) -> CommandResult:
        """Execute network operations"""
        action = parameters.get("action", "").lower().replace(" ", "_")
        
        # Handle special cases with Python instead of shell commands
        if action in ["get_ip", "get_ip_address", "get_ip_info", "ip", "ip_address", "show_ip"]:
            return self._get_ip_address(dry_run)
        elif action in ["get_mac", "get_mac_address", "mac", "mac_address", "show_mac"]:
            return self._get_mac_address(dry_run)
        elif action in ["check_port", "port_check", "check_port_status", "port_status", "is_port_open"]:
            return self._check_port(parameters, dry_run)
        elif action in ["http_request", "make_request"]:
            return self._http_request(parameters, dry_run)
        
        # Default to shell command
        if dry_run:
            return CommandResult(
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
                command=command
            )
        
        # Network commands like ping, tracert need longer timeout
        return self.run_command(command, timeout=120)
    
    def _get_ip_address(self, dry_run: bool) -> CommandResult:
        """Get IP addresses"""
        if dry_run:
            return CommandResult(
                success=True,
                output="[DRY RUN] Would fetch IP addresses"
            )
        
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Get public IP
            try:
                public_ip = requests.get("https://api.ipify.org", timeout=5).text
            except:
                public_ip = "Unable to fetch"
            
            output = f"Local IP: {local_ip}\nPublic IP: {public_ip}"
            
            return CommandResult(success=True, output=output)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to get IP: {str(e)}"
            )
    
    def _get_mac_address(self, dry_run: bool) -> CommandResult:
        """Get MAC address of network interfaces"""
        if dry_run:
            return CommandResult(
                success=True,
                output="[DRY RUN] Would fetch MAC addresses"
            )
        
        try:
            import uuid
            import psutil
            
            output = "Network Interface MAC Addresses:\n\n"
            
            # Get all network interfaces
            interfaces = psutil.net_if_addrs()
            
            for interface_name, addresses in interfaces.items():
                for addr in addresses:
                    # AF_LINK (17 on Unix, varies on Windows) or check for MAC format
                    if hasattr(socket, 'AF_LINK') and addr.family == socket.AF_LINK:
                        mac = addr.address
                        output += f"{interface_name}: {mac}\n"
                    elif '-' in str(addr.address) and len(addr.address) == 17:
                        # Windows format: XX-XX-XX-XX-XX-XX
                        output += f"{interface_name}: {addr.address}\n"
            
            # If no MAC found via psutil, use uuid method as fallback
            if output == "Network Interface MAC Addresses:\n\n":
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0,2*6,2)][::-1])
                output += f"Primary Interface: {mac}\n"
            
            return CommandResult(success=True, output=output.strip())
            
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to get MAC address: {str(e)}"
            )
    
    def _check_port(self, parameters: Dict, dry_run: bool) -> CommandResult:
        """Check if a port is open"""
        host = parameters.get("host", "localhost")
        port = parameters.get("port")
        
        # Try to extract port from various parameter keys
        if not port:
            port = parameters.get("port_number")
        if not port:
            # Try to find a number in the parameters
            for key, value in parameters.items():
                if isinstance(value, (int, str)) and str(value).isdigit():
                    port = value
                    break
        
        if not port:
            return CommandResult(
                success=False,
                output="",
                error="Port number required"
            )
        
        if dry_run:
            return CommandResult(
                success=True,
                output=f"[DRY RUN] Would check if port {port} is open on {host}"
            )
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            
            if result == 0:
                output = f"✅ Port {port} is OPEN on {host}"
            else:
                output = f"❌ Port {port} is CLOSED on {host}"
            
            return CommandResult(success=True, output=output)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to check port: {str(e)}"
            )
    
    def _http_request(self, parameters: Dict, dry_run: bool) -> CommandResult:
        """Make HTTP request"""
        url = parameters.get("url")
        method = parameters.get("method", "GET").upper()
        
        if not url:
            return CommandResult(
                success=False,
                output="",
                error="URL required"
            )
        
        if dry_run:
            return CommandResult(
                success=True,
                output=f"[DRY RUN] Would make {method} request to {url}"
            )
        
        try:
            response = requests.request(method, url, timeout=10)
            output = f"Status: {response.status_code}\n"
            output += f"Response Length: {len(response.content)} bytes"
            
            return CommandResult(success=True, output=output)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"HTTP request failed: {str(e)}"
            )


class SystemInfoHandler(BaseHandler):
    """Handler for system information queries"""
    
    def can_handle(self, category: str, action: str) -> bool:
        return category == "system_info"
    
    def execute(self, command: str, parameters: Dict, dry_run: bool = False) -> CommandResult:
        """Execute system info commands"""
        action = parameters.get("action", "").lower().replace(" ", "_")
        
        # Handle special cases
        if action in ["disk_usage", "get_disk_usage", "show_disk_usage"]:
            return self._get_disk_usage(parameters, dry_run)
        elif action in ["memory", "get_memory", "get_memory_usage", "memory_info"]:
            return self._get_memory_info(dry_run)
        elif action in ["cpu", "get_cpu", "get_cpu_usage", "cpu_usage"]:
            return self._get_cpu_usage(dry_run)
        elif action in ["uptime", "get_uptime", "get_system_uptime", "system_uptime"]:
            return self._get_uptime(dry_run)
        elif action in ["user", "get_user", "get_user_info", "user_info", "whoami"]:
            return self._get_user_info(dry_run)
        
        # Default to shell command
        if dry_run:
            return CommandResult(
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
                command=command
            )
        
        return self.run_command(command)
    
    def _get_disk_usage(self, parameters: Dict, dry_run: bool) -> CommandResult:
        """Get disk usage information"""
        if dry_run:
            return CommandResult(
                success=True,
                output="[DRY RUN] Would show disk usage"
            )
        
        path = parameters.get("path", ".")
        
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            
            output = f"Disk Usage for {path}:\n"
            output += f"Total: {self._format_bytes(total)}\n"
            output += f"Used: {self._format_bytes(used)}\n"
            output += f"Free: {self._format_bytes(free)}\n"
            output += f"Usage: {used/total*100:.1f}%"
            
            return CommandResult(success=True, output=output)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to get disk usage: {str(e)}"
            )
    
    def _get_memory_info(self, dry_run: bool) -> CommandResult:
        """Get memory information"""
        if dry_run:
            return CommandResult(
                success=True,
                output="[DRY RUN] Would show memory info"
            )
        
        try:
            # Try to use psutil if available
            import psutil
            mem = psutil.virtual_memory()
            
            output = "Memory Information:\n"
            output += f"Total: {self._format_bytes(mem.total)}\n"
            output += f"Available: {self._format_bytes(mem.available)}\n"
            output += f"Used: {self._format_bytes(mem.used)}\n"
            output += f"Usage: {mem.percent}%"
            
            return CommandResult(success=True, output=output)
        except ImportError:
            # Fall back to command-line tools
            command = command_mapper.get_memory_command()
            return self.run_command(command)
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to get memory info: {str(e)}"
            )
    
    def _get_cpu_usage(self, dry_run: bool) -> CommandResult:
        """Get CPU usage information"""
        if dry_run:
            return CommandResult(
                success=True,
                output="[DRY RUN] Would show CPU usage"
            )
        
        try:
            # Try to use psutil if available
            import psutil
            import time
            
            # Get CPU usage over 1 second interval
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            output = "CPU Information:\n"
            output += f"Usage: {cpu_percent}%\n"
            output += f"Cores: {cpu_count}\n"
            if cpu_freq:
                output += f"Current Speed: {cpu_freq.current:.0f} MHz\n"
                if cpu_freq.max > 0:
                    output += f"Max Speed: {cpu_freq.max:.0f} MHz"
            
            return CommandResult(success=True, output=output)
        except ImportError:
            return CommandResult(
                success=False,
                output="",
                error="psutil not installed. Install with: pip install psutil"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to get CPU usage: {str(e)}"
            )
    
    def _get_uptime(self, dry_run: bool) -> CommandResult:
        """Get system uptime"""
        if dry_run:
            return CommandResult(
                success=True,
                output="[DRY RUN] Would show system uptime"
            )
        
        try:
            import psutil
            from datetime import datetime, timedelta
            
            # Get boot time
            boot_timestamp = psutil.boot_time()
            boot_time = datetime.fromtimestamp(boot_timestamp)
            
            # Calculate uptime
            uptime = datetime.now() - boot_time
            
            # Format uptime
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            output = "System Uptime:\n"
            output += f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"Uptime: {days} days, {hours} hours, {minutes} minutes\n"
            
            # Add friendly message
            if days == 0:
                output += "Computer was rebooted today"
            elif days == 1:
                output += "Computer has been running for 1 day"
            else:
                output += f"Computer has been running for {days} days"
            
            return CommandResult(success=True, output=output)
        except ImportError:
            return CommandResult(
                success=False,
                output="",
                error="psutil not installed. Install with: pip install psutil"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to get uptime: {str(e)}"
            )
    
    def _get_user_info(self, dry_run: bool) -> CommandResult:
        """Get current user information"""
        if dry_run:
            return CommandResult(
                success=True,
                output="[DRY RUN] Would show user info"
            )
        
        try:
            import os
            import getpass
            import socket
            
            username = getpass.getuser()
            hostname = socket.gethostname()
            home_dir = os.path.expanduser("~")
            
            output = "Current User Information:\n"
            output += f"Username: {username}\n"
            output += f"Hostname: {hostname}\n"
            output += f"Home Directory: {home_dir}\n"
            output += f"OS: {platform.system()} {platform.release()}"
            
            return CommandResult(success=True, output=output)
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to get user info: {str(e)}"
            )
    
    @staticmethod
    def _format_bytes(bytes_val: int) -> str:
        """Format bytes to human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"


class ProcessHandler(BaseHandler):
    """Handler for process management"""
    
    def can_handle(self, category: str, action: str) -> bool:
        return category == "process_mgmt"
    
    def execute(self, command: str, parameters: Dict, dry_run: bool = False) -> CommandResult:
        """Execute process management commands"""
        if dry_run:
            return CommandResult(
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
                command=command
            )
        
        # Process commands are sensitive, always require confirmation
        return self.run_command(command)


class HelpHandler(BaseHandler):
    """Handler for help and capability queries"""
    
    def can_handle(self, category: str, action: str) -> bool:
        return category == "help"
    
    def execute(self, command: str, parameters: Dict, dry_run: bool = False) -> CommandResult:
        """Show help information"""
        
        # Check if this is a conversational query redirected to help
        action = parameters.get("action", "").lower()
        if action in ["inform", "greet", "chat", "conversation"]:
            response = """
👋 Hi! I'm a command-line tool, not a chatbot.

I can help you with system commands like:
  • "what is my ip" - Network information
  • "show disk usage" - System information  
  • "list files in C:" - File operations
  • "who am I" - User information

Type "help" to see all available commands!
"""
            return CommandResult(success=True, output=response.strip())
        
        # Regular help content
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         nlpcmd-ai - What I Can Do                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

I'm an AI-powered CLI assistant that understands natural language!
Just ask me what you want in plain English.

🌐 NETWORK COMMANDS:
   • "what is my ip" - Show local & public IP addresses
   • "show mac address" - Display MAC addresses
   • "is port 8080 open" - Check if a port is available
   • "ping google.com" - Test connectivity

💻 SYSTEM INFORMATION:
   • "what's my CPU usage" - Show CPU load and speed
   • "how much memory do I have" - RAM usage and availability
   • "show disk usage" - Disk space information
   • "how long has my computer been running" - System uptime
   • "who am I" - Current user and hostname

📁 FILE OPERATIONS:
   • "list all python files" - Find specific file types
   • "find files larger than 10MB" - Search by size
   • "show directory structure" - Tree view of folders
   • "show folders in C:" - List C: drive folders
   • "folder structure" - Current directory tree

⚙️ PROCESS MANAGEMENT:
   • "show running processes" - List all processes
   • "is python running" - Find specific processes

🛠️ DEVELOPMENT:
   • "show git status" - Git commands
   • "list docker containers" - Docker operations

💡 TIPS:
   • Use interactive mode: python -m nlpcmd_ai.cli -i
   • Auto-confirm commands: python -m nlpcmd_ai.cli --yes "command"
   • Test without executing: python -m nlpcmd_ai.cli --dry-run "command"
   
📚 MORE INFO:
   • Full command list: See SUPPORTED_COMMANDS.txt
   • Documentation: https://github.com/Avikg/nlp_terminal_cmd
   • PyPI: https://pypi.org/project/nlpcmd-ai/

Just ask naturally! I'll understand and help you. 🚀
"""
        
        return CommandResult(success=True, output=help_text.strip())


class DevelopmentHandler(BaseHandler):
    """Handler for development tools (git, docker, package managers, etc.)"""
    
    def can_handle(self, category: str, action: str) -> bool:
        return category == "development"
    
    def execute(self, command: str, parameters: Dict, dry_run: bool = False) -> CommandResult:
        """Execute development tool commands"""
        if dry_run:
            return CommandResult(
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
                command=command
            )
        
        return self.run_command(command, timeout=120)  # Longer timeout for dev tools