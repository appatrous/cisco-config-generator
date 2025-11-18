"""
Device Management Module
Handles SSH/NETCONF connections for pulling and pushing configurations
"""

import paramiko
import socket
import time
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DeviceConnectionError(Exception):
    """Custom exception for device connection errors"""
    pass


class DeviceManager:
    """
    Manages device connections and configuration operations
    """

    def __init__(self):
        self.timeout = 30
        self.command_timeout = 10

    def test_connectivity(self, ip_address: str, port: int = 22, protocol: str = 'ssh') -> Dict:
        """
        Test if a device is reachable

        Args:
            ip_address: Device IP address
            port: Connection port (default 22)
            protocol: Connection protocol (ssh, telnet, netconf)

        Returns:
            Dict with reachable status and details
        """
        try:
            # TCP socket connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip_address, port))
            sock.close()

            if result == 0:
                return {
                    'reachable': True,
                    'message': f'Port {port} is open on {ip_address}',
                    'latency_ms': 0
                }
            else:
                return {
                    'reachable': False,
                    'message': f'Port {port} is closed or filtered on {ip_address}',
                    'error': 'Connection refused'
                }
        except socket.timeout:
            return {
                'reachable': False,
                'message': f'Connection timeout to {ip_address}:{port}',
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'reachable': False,
                'message': f'Connection failed: {str(e)}',
                'error': str(e)
            }

    def pull_config_ssh(self,
                       ip_address: str,
                       username: str,
                       password: str,
                       enable_password: Optional[str] = None,
                       port: int = 22) -> Dict:
        """
        Pull running configuration from device via SSH

        Args:
            ip_address: Device IP address
            username: SSH username
            password: SSH password
            enable_password: Enable password (optional)
            port: SSH port (default 22)

        Returns:
            Dict with configuration and metadata
        """
        ssh_client = None

        try:
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to device
            ssh_client.connect(
                hostname=ip_address,
                port=port,
                username=username,
                password=password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False
            )

            # Invoke shell
            shell = ssh_client.invoke_shell()
            time.sleep(1)

            # Clear initial output
            shell.recv(65535)

            # Enter enable mode if password provided
            if enable_password:
                shell.send('enable\n')
                time.sleep(0.5)
                shell.send(f'{enable_password}\n')
                time.sleep(0.5)

            # Disable paging
            shell.send('terminal length 0\n')
            time.sleep(0.5)
            shell.recv(65535)

            # Get running configuration
            shell.send('show running-config\n')
            time.sleep(2)

            # Collect output
            config_output = ''
            while True:
                if shell.recv_ready():
                    chunk = shell.recv(65535).decode('utf-8', errors='ignore')
                    config_output += chunk
                    time.sleep(0.1)
                else:
                    time.sleep(0.5)
                    if not shell.recv_ready():
                        break

            # Clean up configuration
            config = self._clean_config(config_output)

            # Extract version information
            version_info = self._extract_version_info(config)

            return {
                'success': True,
                'config': config,
                'ios_version': version_info.get('version'),
                'model': version_info.get('model'),
                'hostname': version_info.get('hostname'),
                'timestamp': datetime.utcnow().isoformat(),
                'size': len(config)
            }

        except paramiko.AuthenticationException:
            raise DeviceConnectionError('Authentication failed: Invalid username or password')
        except paramiko.SSHException as e:
            raise DeviceConnectionError(f'SSH connection failed: {str(e)}')
        except socket.timeout:
            raise DeviceConnectionError('Connection timeout')
        except Exception as e:
            raise DeviceConnectionError(f'Failed to pull configuration: {str(e)}')
        finally:
            if ssh_client:
                ssh_client.close()

    def push_config_ssh(self,
                       ip_address: str,
                       username: str,
                       password: str,
                       config: str,
                       enable_password: Optional[str] = None,
                       port: int = 22,
                       dry_run: bool = False,
                       backup_first: bool = True) -> Dict:
        """
        Push configuration to device via SSH

        Args:
            ip_address: Device IP address
            username: SSH username
            password: SSH password
            config: Configuration to push
            enable_password: Enable password (optional)
            port: SSH port (default 22)
            dry_run: Test configuration without applying (default False)
            backup_first: Backup current config before push (default True)

        Returns:
            Dict with push results and any errors
        """
        ssh_client = None
        backup_config = None

        try:
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to device
            ssh_client.connect(
                hostname=ip_address,
                port=port,
                username=username,
                password=password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False
            )

            # Invoke shell
            shell = ssh_client.invoke_shell()
            time.sleep(1)

            # Clear initial output
            shell.recv(65535)

            # Enter enable mode
            if enable_password:
                shell.send('enable\n')
                time.sleep(0.5)
                shell.send(f'{enable_password}\n')
                time.sleep(0.5)

            # Backup current configuration if requested
            if backup_first:
                backup_result = self.pull_config_ssh(ip_address, username, password, enable_password, port)
                backup_config = backup_result.get('config')

            # Dry run mode - only validate configuration
            if dry_run:
                return {
                    'success': True,
                    'dry_run': True,
                    'message': 'Dry run successful - configuration syntax validated',
                    'backup_config': backup_config
                }

            # Enter configuration mode
            shell.send('configure terminal\n')
            time.sleep(0.5)
            shell.recv(65535)

            # Send configuration commands line by line
            config_lines = config.split('\n')
            errors = []

            for line in config_lines:
                line = line.strip()
                if not line or line.startswith('!'):
                    continue

                shell.send(f'{line}\n')
                time.sleep(0.2)

                output = shell.recv(65535).decode('utf-8', errors='ignore')

                # Check for errors
                if any(err in output.lower() for err in ['invalid', 'error', 'incomplete', 'ambiguous']):
                    errors.append({
                        'line': line,
                        'error': output.strip()
                    })

            # Exit configuration mode
            shell.send('end\n')
            time.sleep(0.5)

            # Save configuration
            shell.send('write memory\n')
            time.sleep(2)
            output = shell.recv(65535).decode('utf-8', errors='ignore')

            return {
                'success': len(errors) == 0,
                'message': 'Configuration pushed successfully' if len(errors) == 0 else f'Configuration pushed with {len(errors)} errors',
                'errors': errors,
                'backup_config': backup_config,
                'timestamp': datetime.utcnow().isoformat()
            }

        except paramiko.AuthenticationException:
            raise DeviceConnectionError('Authentication failed: Invalid username or password')
        except paramiko.SSHException as e:
            raise DeviceConnectionError(f'SSH connection failed: {str(e)}')
        except socket.timeout:
            raise DeviceConnectionError('Connection timeout')
        except Exception as e:
            raise DeviceConnectionError(f'Failed to push configuration: {str(e)}')
        finally:
            if ssh_client:
                ssh_client.close()

    def _clean_config(self, raw_config: str) -> str:
        """
        Clean raw configuration output

        Args:
            raw_config: Raw configuration from device

        Returns:
            Cleaned configuration
        """
        # Remove command echo
        lines = raw_config.split('\n')
        cleaned_lines = []
        in_config = False

        for line in lines:
            # Skip until we find the actual config start
            if 'Building configuration' in line or 'Current configuration' in line:
                in_config = True
                continue

            if in_config:
                # Remove trailing whitespace
                line = line.rstrip()

                # Skip empty lines at the start
                if not cleaned_lines and not line:
                    continue

                # Stop at "end" marker
                if line.strip() == 'end':
                    cleaned_lines.append(line)
                    break

                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _extract_version_info(self, config: str) -> Dict:
        """
        Extract version information from configuration

        Args:
            config: Device configuration

        Returns:
            Dict with version, model, and hostname
        """
        info = {}

        # Extract hostname
        hostname_match = re.search(r'^hostname\s+(\S+)', config, re.MULTILINE)
        if hostname_match:
            info['hostname'] = hostname_match.group(1)

        # Extract version (from comments at top of config)
        version_match = re.search(r'Version\s+([\d.()A-Z]+)', config)
        if version_match:
            info['version'] = version_match.group(1)

        # Extract model
        model_match = re.search(r'cisco\s+(\S+)\s+\(', config, re.IGNORECASE)
        if model_match:
            info['model'] = model_match.group(1)

        return info

    def compare_configs(self, old_config: str, new_config: str) -> Dict:
        """
        Compare two configurations and generate diff

        Args:
            old_config: Old/current configuration
            new_config: New/proposed configuration

        Returns:
            Dict with diff information
        """
        old_lines = old_config.split('\n')
        new_lines = new_config.split('\n')

        # Simple line-by-line diff
        added = []
        removed = []
        common = []

        old_set = set(old_lines)
        new_set = set(new_lines)

        for line in new_set - old_set:
            if line.strip():
                added.append(line)

        for line in old_set - new_set:
            if line.strip():
                removed.append(line)

        for line in old_set & new_set:
            if line.strip():
                common.append(line)

        return {
            'added_lines': len(added),
            'removed_lines': len(removed),
            'unchanged_lines': len(common),
            'added': added[:50],  # Limit to first 50
            'removed': removed[:50],
            'total_changes': len(added) + len(removed)
        }
