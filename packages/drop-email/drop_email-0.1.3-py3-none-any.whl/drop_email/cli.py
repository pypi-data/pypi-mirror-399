"""
Command-line interface for drop_email
"""
import sys
import argparse
from .config import init_config, get_config_path
from .email_sender import send


def main():
    """Main CLI entry point."""
    # Check if first argument is a subcommand
    if len(sys.argv) > 1 and sys.argv[1] in ["init", "config"]:
        # Handle subcommands
        command = sys.argv[1]
        
        if command == "init":
            parser = argparse.ArgumentParser(description="Initialize configuration file")
            parser.add_argument(
                "command",
                choices=["init"],
                help="Initialize configuration file"
            )
            parser.add_argument(
                "--force",
                action="store_true",
                help="Overwrite existing configuration file"
            )
            args = parser.parse_args()
            config_path = init_config(force=args.force)
            print(f"\nConfiguration file location: {config_path}")
            print("\nEdit this file to configure your email settings.")
        
        elif command == "config":
            parser = argparse.ArgumentParser(description="Show configuration file path")
            parser.add_argument(
                "command",
                choices=["config"],
                help="Show configuration file path"
            )
            args = parser.parse_args()
            config_path = get_config_path()
            print(f"Configuration file path: {config_path}")
            if config_path.exists():
                print("✓ Configuration file exists")
            else:
                print("✗ Configuration file does not exist")
                print("Run 'drop_email init' to create it")
    
    else:
        # Handle message sending
        parser = argparse.ArgumentParser(
            description="drop_email - Send data as beautiful HTML emails",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Send a simple message
  drop_email "hello world!"
  
  # Send with custom subject
  drop_email "hello world!" --subject "My Message"
  
  # Initialize configuration file
  drop_email init
  
  # Send data using Python API
  python -c "import drop_email as de; import pandas as pd; df = pd.DataFrame({'A': [1,2,3]}); de.send(df)"
            """
        )
        
        parser.add_argument(
            "message",
            nargs="?",
            help="Message to send via email"
        )
        parser.add_argument(
            "--subject",
            "-s",
            default="Message from drop_email",
            help="Email subject (default: 'Message from drop_email')"
        )
        
        args = parser.parse_args()
        
        if args.message:
            # Send message directly
            try:
                send(args.message, subject=args.subject)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Default: show help if no message provided
            parser.print_help()
            print("\nTip: Use 'drop_email init' to create the configuration file.")


if __name__ == "__main__":
    main()
