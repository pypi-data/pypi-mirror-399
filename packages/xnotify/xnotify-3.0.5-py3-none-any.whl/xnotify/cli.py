#!/usr/bin/env python3

# File: xnotify/xnotify/cli.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-30
# Description: Command-line interface for xnotify.
# License: MIT

"""Command-line interface for xnotify."""

import sys
import argparse
try:
    from licface import CustomRichHelpFormatter
except:
    CustomRichHelpFormatter = argparse.RawDescriptionHelpFormatter
from .logger import setup_logger
logger = setup_logger('xnotify.cli')
from pathlib import Path
from typing import Dict, Any, Optional

RICH_AVAILABLE=False

try:
    from rich import print as rich_print
    RICH_AVAILABLE=True
except:
    rich_print = print

from . import __version__, __description__
from .core import XNotify
from .config import Config
from .plugins import list_plugins, get_plugin, AVAILABLE_PLUGINS
from .server import XNotifyServer, XNotifyRouter
from .client import send_notification
from .logger import setup_colored_logger
from .utils import find_config_file


class XNotifyCLI:
    """Command-line interface for xnotify."""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.config: Optional[Config] = None
        self.notifier: Optional[XNotify] = None
        self.logger = setup_logger('xnotify.cli')
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create main argument parser with subparsers for each plugin."""
        parser = argparse.ArgumentParser(
            prog='xnotify',
            description=__description__,
            formatter_class=CustomRichHelpFormatter,
            epilog="""
Examples:
  # Send notification via ntfy
  xnotify send "Title" "Message" -p ntfy
  
  # Send via multiple plugins
  xnotify send "Alert" "Server down" -p ntfy pushbullet telegram
  
  # Send using ntfy plugin with custom options
  xnotify ntfy send "Alert" "High priority" --priority 5 --tags warning,server
  
  # Start server
  xnotify server --host 0.0.0.0 --port 33000
  
  # Start router (server that forwards to plugins)
  xnotify router --host 0.0.0.0 --port 33000
  
  # List available plugins
  xnotify list-plugins
  
  # Show plugin status
  xnotify status
  
  # Show configuration
  xnotify config show
  
For more information: https://github.com/licface/xnotify
            """
        )
        
        # Global arguments
        parser.add_argument(
            '--version',
            action='version',
            version=f'%(prog)s {__version__}'
        )
        
        parser.add_argument(
            '-c', '--config',
            metavar='FILE',
            help='Configuration file path'
        )
        
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )
        
        # Create subparsers
        subparsers = parser.add_subparsers(
            title='commands',
            dest='command',
            help='Available commands'
        )
        
        # Send command (generic)
        self._add_send_command(subparsers)
        
        # Auto-detect and create plugin-specific subparsers
        self._add_plugin_subparsers(subparsers)
        
        # Server commands
        self._add_server_command(subparsers)
        self._add_router_command(subparsers)
        self._add_client_command(subparsers)
        
        # Utility commands
        self._add_list_plugins_command(subparsers)
        self._add_status_command(subparsers)
        self._add_config_command(subparsers)
        
        return parser
    
    def _add_send_command(self, subparsers):
        """Add generic send command."""
        send_parser = subparsers.add_parser(
            'send',
            help='Send notification via specified plugins',
            formatter_class=CustomRichHelpFormatter,
            description='Send notification through one or more plugins',
            epilog="""
Examples:
  xnotify send "Title" "Message"
  xnotify send "Alert" "Server down" -p ntfy telegram
  xnotify send "Warning" "Disk full" -p pushover --priority 2
            """
        )
        
        send_parser.add_argument(
            'title',
            help='Notification title'
        )
        
        send_parser.add_argument(
            'message',
            help='Notification message'
        )
        
        send_parser.add_argument(
            '-p', '--plugins',
            nargs='+',
            metavar='PLUGIN',
            help=f'Plugins to use (available: {", ".join(list_plugins())})'
        )
        
        send_parser.add_argument(
            '--all',
            action='store_true',
            help='Send via all enabled plugins'
        )
        
        # Common notification options
        send_parser.add_argument(
            '--priority',
            type=int,
            help='Notification priority (1-5)'
        )
        
        send_parser.add_argument(
            '--tags',
            help='Comma-separated tags'
        )
        
        send_parser.add_argument(
            '-i', '--icon',
            help='Icon URL or file path'
        )
    
    def _add_plugin_subparsers(self, subparsers):
        """Auto-detect and create subparser for each plugin."""
        for plugin_name in list_plugins():
            try:
                plugin_class = get_plugin(plugin_name)
                plugin_parser = subparsers.add_parser(
                    plugin_name,
                    help=f'Commands for {plugin_name} plugin',
                    formatter_class=CustomRichHelpFormatter
                )
                
                # Add plugin-specific subcommands
                plugin_subparsers = plugin_parser.add_subparsers(
                    dest='plugin_command',
                    help=f'{plugin_name} commands'
                )
                
                # Send command for plugin
                self._add_plugin_send_command(
                    plugin_subparsers,
                    plugin_name,
                    plugin_class
                )
                
                # Test command for plugin
                self._add_plugin_test_command(
                    plugin_subparsers,
                    plugin_name
                )
                
            except Exception as e:
                logger.warning(f"Failed to create subparser for {plugin_name}: {e}")
    
    def _add_plugin_send_command(self, plugin_subparsers, plugin_name: str, plugin_class):
        """Add plugin-specific send command with custom arguments."""
        send_parser = plugin_subparsers.add_parser(
            'send',
            help=f'Send notification via {plugin_name}',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        send_parser.add_argument('title', help='Notification title')
        send_parser.add_argument('message', help='Notification message')
        
        # Add plugin-specific arguments based on plugin name
        if plugin_name == 'ntfy':
            send_parser.add_argument('--topic', help='Ntfy topic')
            send_parser.add_argument('--server', help='Ntfy server URL')
            send_parser.add_argument('--priority', type=int, choices=[1,2,3,4,5], help='Priority (1-5)')
            send_parser.add_argument('--tags', help='Comma-separated tags')
            send_parser.add_argument('-i', '--icon', help='Icon URL')
            send_parser.add_argument('--click', help='Click action URL')
            send_parser.add_argument('--attach', help='Attachment URL')
            send_parser.add_argument('--email', help='Email address for delivery')
            send_parser.add_argument('--filename', help='Filename for attachment')
            
        elif plugin_name == 'pushbullet':
            send_parser.add_argument('--api-key', help='Pushbullet API key')
            send_parser.add_argument('--device', help='Device identifier')
            send_parser.add_argument('--email', help='Email address')
            send_parser.add_argument('--channel', help='Channel tag')
            
        elif plugin_name == 'pushover':
            send_parser.add_argument('--user-key', help='User key')
            send_parser.add_argument('--api-token', help='API token')
            send_parser.add_argument('--device', help='Device name')
            send_parser.add_argument('--priority', type=int, choices=[-2,-1,0,1,2], help='Priority (-2 to 2)')
            send_parser.add_argument('--sound', help='Notification sound')
            send_parser.add_argument('--url', help='Supplementary URL')
            send_parser.add_argument('--url-title', help='URL title')
            
        elif plugin_name == 'telegram':
            send_parser.add_argument('--bot-token', help='Bot token')
            send_parser.add_argument('--chat-id', help='Chat ID')
            send_parser.add_argument('--parse-mode', choices=['HTML', 'Markdown'], help='Parse mode')
            send_parser.add_argument('--disable-notification', action='store_true', help='Silent notification')
            
        elif plugin_name == 'discord':
            send_parser.add_argument('--webhook-url', help='Webhook URL')
            send_parser.add_argument('--username', help='Bot username')
            send_parser.add_argument('--avatar-url', help='Avatar URL')
            send_parser.add_argument('--color', type=lambda x: int(x, 0), help='Embed color (hex)')
            
        elif plugin_name == 'slack':
            send_parser.add_argument('--webhook-url', help='Webhook URL')
            send_parser.add_argument('--channel', help='Channel name')
            send_parser.add_argument('--username', help='Bot username')
            send_parser.add_argument('--icon-emoji', help='Icon emoji')
            send_parser.add_argument('--icon-url', help='Icon URL')
            
        elif plugin_name == 'growl':
            send_parser.add_argument('--host', help='Growl host(s)', nargs='+')
            send_parser.add_argument('--app-name', help='Application name')
            send_parser.add_argument('--notification-type', help='Notification type')
            send_parser.add_argument('--priority', type=int, help='Priority')
            send_parser.add_argument('--sticky', action='store_true', help='Sticky notification')
            send_parser.add_argument('-i', '--icon', help='Icon path or URL')
            
        elif plugin_name == 'syslog':
            send_parser.add_argument('--server', help='Syslog server(s)', nargs='+')
            send_parser.add_argument('--facility', help='Syslog facility')
            send_parser.add_argument('--severity', help='Syslog severity')
    
    def _add_plugin_test_command(self, plugin_subparsers, plugin_name: str):
        """Add test command for plugin."""
        test_parser = plugin_subparsers.add_parser(
            'test',
            help=f'Test {plugin_name} plugin connection'
        )
        
        test_parser.add_argument(
            '--show-config',
            action='store_true',
            help='Show current configuration'
        )
    
    def _add_server_command(self, subparsers):
        """Add server command."""
        server_parser = subparsers.add_parser(
            'server',
            help='Start notification server',
            description='Start UDP server to receive notifications',
            formatter_class=CustomRichHelpFormatter
        )
        
        server_parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='Host to bind to (default: 0.0.0.0)'
        )
        
        server_parser.add_argument(
            '--port',
            type=int,
            default=33000,
            help='Port to bind to (default: 33000)'
        )
    
    def _add_router_command(self, subparsers):
        """Add router command."""
        router_parser = subparsers.add_parser(
            'router',
            help='Start notification router',
            description='Start server that forwards notifications to plugins',
            formatter_class=CustomRichHelpFormatter
        )
        
        router_parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='Host to bind to (default: 0.0.0.0)'
        )
        
        router_parser.add_argument(
            '--port',
            type=int,
            default=33000,
            help='Port to bind to (default: 33000)'
        )
    
    def _add_client_command(self, subparsers):
        """Add client command."""
        client_parser = subparsers.add_parser(
            'client',
            help='Send notification to xnotify server',
            description='Send notification to running xnotify server',
            formatter_class=CustomRichHelpFormatter
        )
        
        client_parser.add_argument('title', help='Notification title')
        client_parser.add_argument('message', help='Notification message')
        
        client_parser.add_argument(
            '--host',
            default='127.0.0.1',
            help='Server host (default: 127.0.0.1)'
        )
        
        client_parser.add_argument(
            '--port',
            type=int,
            default=33000,
            help='Server port (default: 33000)'
        )
    
    def _add_list_plugins_command(self, subparsers):
        """Add list-plugins command."""
        subparsers.add_parser(
            'list-plugins',
            help='List available plugins',
            description='Show all available notification plugins',
            formatter_class=CustomRichHelpFormatter
        )
    
    def _add_status_command(self, subparsers):
        """Add status command."""
        status_parser = subparsers.add_parser(
            'status',
            help='Show plugin status',
            description='Display status of all plugins',
            formatter_class=CustomRichHelpFormatter
        )
        
        status_parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
    
    def _add_config_command(self, subparsers):
        """Add config command."""
        config_parser = subparsers.add_parser(
            'config',
            help='Configuration management',
            description='Manage xnotify configuration',
            formatter_class=CustomRichHelpFormatter
        )
        
        config_subparsers = config_parser.add_subparsers(
            dest='config_command',
            help='Config commands'
        )
        
        # Show config
        show_parser = config_subparsers.add_parser(
            'show',
            help='Show current configuration'
        )
        
        show_parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        
        # Set config
        set_parser = config_subparsers.add_parser(
            'set',
            help='Set configuration value'
        )
        
        set_parser.add_argument('key', help='Configuration key (e.g., plugins.ntfy.topic)')
        set_parser.add_argument('value', help='Configuration value')
        
        # Get config
        get_parser = config_subparsers.add_parser(
            'get',
            help='Get configuration value'
        )
        
        get_parser.add_argument('key', help='Configuration key')
        
        # Init config
        init_parser = config_subparsers.add_parser(
            'init',
            help='Initialize configuration file'
        )
        
        init_parser.add_argument(
            '--output',
            help='Output file path (default: ~/.xnotify/config.yaml)'
        )
        
        init_parser.add_argument(
            '--format',
            choices=['yaml', 'json'],
            default='yaml',
            help='Configuration format'
        )
    
    def _setup_logging(self, args):
        """Setup logging based on arguments."""
        if args.debug:
            level = 'DEBUG'
        elif args.verbose:
            level = 'INFO'
        else:
            level = 'WARNING'
        
        self.logger = setup_colored_logger('xnotify', level)
    
    def _load_config(self, args):
        """Load configuration."""
        config_file = args.config if hasattr(args, 'config') and args.config else None
        
        if not config_file:
            config_file = find_config_file()
        if config_file:
            self.logger.info(f"Using config file: {config_file}")
        
        self.config = Config(config_file)  # type: ignore
    
    def _init_notifier(self):
        """Initialize XNotify instance."""
        if self.config:
            self.notifier = XNotify(self.config._config)  # type: ignore
        else:
            self.notifier = XNotify()
    
    def run(self, args=None):
        """Run CLI with given arguments."""
        args = self.parser.parse_args(args)
        
        # Setup logging
        self._setup_logging(args)
        
        # Handle no command
        if not args.command:
            self.parser.print_help()
            return 0
        
        # Load config and init notifier for most commands
        if args.command not in ['config']:
            self._load_config(args)
            if args.command not in ['server', 'client', 'list-plugins']:
                self._init_notifier()
        
        # Route to command handler
        try:
            if args.command == 'send':
                return self._handle_send(args)
            elif args.command == 'server':
                return self._handle_server(args)
            elif args.command == 'router':
                return self._handle_router(args)
            elif args.command == 'client':
                return self._handle_client(args)
            elif args.command == 'list-plugins':
                return self._handle_list_plugins(args)
            elif args.command == 'status':
                return self._handle_status(args)
            elif args.command == 'config':
                return self._handle_config(args)
            elif args.command in list_plugins():
                return self._handle_plugin_command(args)
            else:
                self.logger.error(f"Unknown command: {args.command}")
                return 1
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            return 130
        except Exception as e:
            self.logger.error(f"Error: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1
    
    def _handle_send(self, args) -> int:
        """Handle send command."""
        plugins = args.plugins if not args.all else None
        
        # Build kwargs from args
        kwargs = {}
        if hasattr(args, 'priority') and args.priority:
            kwargs['priority'] = args.priority
        if hasattr(args, 'tags') and args.tags:
            kwargs['tags'] = args.tags.split(',')
        if hasattr(args, 'icon') and args.icon:
            kwargs['icon'] = args.icon
        
        results = self.notifier.send(args.title, args.message, plugins=plugins, **kwargs)  # type: ignore
        
        # Print results
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        print(f"\n📨 Notification sent to {success_count}/{total_count} plugins")
        
        for plugin, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {plugin}")
        
        return 0 if success_count > 0 else 1
    
    def _handle_plugin_command(self, args) -> int:
        """Handle plugin-specific commands."""
        plugin_name = args.command
        
        if not hasattr(args, 'plugin_command') or not args.plugin_command:
            self.parser.parse_args([plugin_name, '--help'])
            return 0
        
        if args.plugin_command == 'send':
            return self._handle_plugin_send(args, plugin_name)
        elif args.plugin_command == 'test':
            return self._handle_plugin_test(args, plugin_name)
        
        return 1
    
    def _handle_plugin_send(self, args, plugin_name: str) -> int:
        """Handle plugin-specific send command."""
        # Build kwargs from plugin-specific args
        kwargs = {}
        
        # Extract all non-standard arguments
        for key, value in vars(args).items():
            if key not in ['command', 'plugin_command', 'title', 'message', 'config', 'verbose', 'debug']:
                if value is not None:
                    kwargs[key.replace('_', '-')] = value
        
        results = self.notifier.send(  # type: ignore
            args.title,
            args.message,
            plugins=[plugin_name],
            **kwargs
        )
        
        if results.get(plugin_name):
            print(f"✅ Notification sent via {plugin_name}")
            return 0
        else:
            print(f"❌ Failed to send via {plugin_name}")
            return 1
    
    def _handle_plugin_test(self, args, plugin_name: str) -> int:
        """Handle plugin test command."""
        if args.show_config:
            config = self.config.get(f'plugins.{plugin_name}', {})  # type: ignore
            print(f"\n📋 Configuration for {plugin_name}:")
            import json
            print(json.dumps(config, indent=2))
        
        # Try to send test notification
        print(f"\n🧪 Testing {plugin_name} plugin...")
        
        try:
            results = self.notifier.send(  # type: ignore
                "Test Notification",
                f"This is a test from xnotify {plugin_name} plugin",
                plugins=[plugin_name]
            )
            
            if results.get(plugin_name):
                print(f"✅ {plugin_name} plugin is working!")
                return 0
            else:
                print(f"❌ {plugin_name} plugin test failed")
                return 1
                
        except Exception as e:
            print(f"❌ Error testing {plugin_name}: {e}")
            return 1
    
    def _handle_server(self, args) -> int:
        """Handle server command."""
        print(f"🚀 Starting xnotify server on {args.host}:{args.port}")
        server = XNotifyServer(args.host, args.port)
        server.start()
        return 0
    
    def _handle_router(self, args) -> int:
        """Handle router command."""
        self._load_config(args)
        self._init_notifier()
        
        print(f"🔄 Starting xnotify router on {args.host}:{args.port}")
        router = XNotifyRouter(args.host, args.port, self.notifier)
        router.start()
        return 0
    
    def _handle_client(self, args) -> int:
        """Handle client command."""
        success = send_notification(
            args.title,
            args.message,
            args.host,
            args.port
        )
        
        if success:
            print(f"✅ Notification sent to {args.host}:{args.port}")
            return 0
        else:
            print(f"❌ Failed to send to {args.host}:{args.port}")
            return 1
    
    def _handle_list_plugins(self, args) -> int:
        """Handle list-plugins command."""
        plugins = list_plugins()
        
        print(f"\n📦 Available Plugins ({len(plugins)}):\n")
        
        for plugin_name in sorted(plugins):
            try:
                plugin_class = get_plugin(plugin_name)
                doc = plugin_class.__doc__ or "No description available"
                print(f"  • {plugin_name:15} - {doc.strip()}")
            except:
                print(f"  • {plugin_name:15} - (unable to load)")
        
        print("\nUse 'xnotify <plugin> --help' for plugin-specific options")
        return 0
    
    def _handle_status(self, args) -> int:
        """Handle status command."""
        status = self.notifier.get_plugin_status()  # type: ignore
        
        if args.json:
            import json
            print(json.dumps(status, indent=2))
        else:
            print("\n📊 Plugin Status:\n")
            for plugin, enabled in sorted(status.items()):
                status_icon = "✅" if enabled else "❌"
                status_text = "enabled" if enabled else "disabled"
                print(f"  {status_icon} {plugin:15} - {status_text}")
        
        return 0
    
    def _handle_config(self, args) -> int:
        """Handle config commands."""
        if not args.config_command:
            self.parser.parse_args(['config', '--help'])
            return 0
        
        if args.config_command == 'show':
            return self._handle_config_show(args)
        elif args.config_command == 'set':
            return self._handle_config_set(args)
        elif args.config_command == 'get':
            return self._handle_config_get(args)
        elif args.config_command == 'init':
            return self._handle_config_init(args)
        
        return 1
    
    def _handle_config_show(self, args) -> int:
        """Show configuration."""
        self._load_config(args)
        
        if args.json:
            import json
            print(json.dumps(self.config._config, indent=2))  # type: ignore
        else:
            print("\n⚙️  Current Configuration:\n")
            self._print_config_tree(self.config._config)  # type: ignore
        
        return 0
    
    def _print_config_tree(self, config, indent=0):
        """Print configuration as tree."""
        for key, value in sorted(config.items()):
            if isinstance(value, dict):
                if RICH_AVAILABLE:
                    rich_print("  " * indent + f"[bold #00FFFF]📦 {key}:[/]")
                else:
                    print("  " * indent + f"📦 {key}:")

                self._print_config_tree(value, indent + 1)
            else:
                if RICH_AVAILABLE:
                    rich_print("  " * indent + f"[bold #FFFF00]  . {key}:[/] [bold #00AAFF]{value if value is not None else ''}[/]")
                else:
                    print("  " * indent + f"  . {key}: {value if value is not None else ''}")
    
    def _handle_config_set(self, args) -> int:
        """Set configuration value."""
        self._load_config(args)
        self.config.set(args.key, args.value)  # type: ignore
        print(f"✅ Set {args.key} = {args.value}")
        return 0
    
    def _handle_config_get(self, args) -> int:
        """Get configuration value."""
        self._load_config(args)
        value = self.config.get(args.key)  # type: ignore
        
        if value is not None:
            print(value)
            return 0
        else:
            print(f"❌ Key not found: {args.key}")
            return 1
    
    def _handle_config_init(self, args) -> int:
        """Initialize configuration file."""
        output = args.output
        if not output:
            home = Path.home()
            config_dir = home / '.xnotify'
            config_dir.mkdir(parents=True, exist_ok=True)
            output = str(config_dir / f'config.{args.format}')
        
        config = Config()
        config.save_to_file(output)
        
        print(f"✅ Configuration initialized: {output}")
        return 0


def main():
    """Main entry point."""
    cli = XNotifyCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())