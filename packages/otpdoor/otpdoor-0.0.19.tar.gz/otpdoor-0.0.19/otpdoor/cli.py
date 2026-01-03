import argparse
import pyotp
import os
from .auth import app
from .config import config

def serve():
    parser = argparse.ArgumentParser(description="Run the OTPdoor authentication server.")
    parser.add_argument("-a", "--host", default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port to bind the server to.")
    parser.add_argument("-c", "--config", action="store_true", help="Enable the configuration endpoint (/_config).")
    parser.add_argument("--add-domain", help="Create a new authentication domain.")
    parser.add_argument("--remove-domain", help="Remove an existing authentication domain.")
    parser.add_argument("--list-domains", action="store_true", help="List all configured domains.")
    parser.add_argument("--show-config", action="store_true", help="Show the absolute path to the configuration file.")
    parser.add_argument("--export", help="Export the current configuration (unencrypted) to a file.")
    parser.add_argument("--import", dest="import_path", help="Import a configuration file (raw/unencrypted).")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode.")
    args = parser.parse_args()

    if args.list_domains:
        print("--- Configured Domains ---")
        for name in config.domains:
            print(f"- {name}")
        return

    if args.show_config:
        abs_path = os.path.abspath(config.config_path_file)
        print(f"\n[CONFIG PATH] {abs_path}")
        print("[!] Back up this file to preserve your domains and secrets during updates.\n")
        return

    if args.export:
        if config.export_config(args.export):
            print(f"Successfully exported configuration (unencrypted) to: {args.export}")
        else:
            print(f"Error: Failed to export configuration to {args.export}")
        return

    if args.import_path:
        if config.import_config(args.import_path):
            print(f"Successfully imported configuration from: {args.import_path}")
            print("[!] The configuration has been merged and saved to your active storage.")
        else:
            print(f"Error: Failed to import configuration from {args.import_path}")
        return

    if args.add_domain:
        domain_name = args.add_domain
        if domain_name in config.domains:
            print(f"Error: Domain '{domain_name}' already exists.")
        else:
            from .config import DomainConfig
            secret = pyotp.random_base32()
            config.domains[domain_name] = DomainConfig(domain_name, secret)
            config.save()
            print(f"Successfully added domain: {domain_name}")
            print(f"TOTP Secret: {secret}")
        return

    if args.remove_domain:
        domain_name = args.remove_domain
        if domain_name not in config.domains:
            print(f"Error: Domain '{domain_name}' does not exist.")
            return
        
        if domain_name == "default":
            print(f"\n[!] WARNING: The 'default' domain cannot be deleted.")
            print(f"    Its secret, session duration, and theme will be RESET to default values.")
        
        confirm = input(f"Are you sure you want to {'RESET' if domain_name == 'default' else 'REMOVE'} domain '{domain_name}'? [y/N]: ")
        if confirm.lower() == 'y':
            new_secret = config.remove_domain(domain_name)
            config.save()
            print(f"Successfully {'reset' if domain_name == 'default' else 'removed'} domain: {domain_name}")
            if domain_name == "default":
                print(f"New TOTP Secret: {new_secret}")
            print("\n[!] IMPORTANT: Please restart any running OTPdoor server for changes to take effect.")
        else:
            print("Operation cancelled.")
        return

    config.enable_config = args.config
    config.start_watcher()

    if args.config:
        print("\n" + "!" * 64)
        print("!!! WARNING: CONFIGURATION MODE ENABLED                          !!!")
        print("!!! The /_config endpoint is currently ACTIVE.                   !!!")
        print("!!! This mode is intended ONLY for initial setup and device      !!!")
        print("!!! provisioning. DO NOT run this in production with the -c flag. !!!")
        print("!" * 64 + "\n")

    print(f"Starting OTPdoor server on {args.host}:{args.port}...")
    if args.debug:
        app.run(host=args.host, port=args.port, debug=True)
    else:
        from waitress import serve as waitress_serve
        waitress_serve(app, host=args.host, port=args.port)

def init():
    secret = pyotp.random_base32()
    print("--- OTPdoor Initialization ---")
    print(f"TOTP Secret: {secret}")
    print("\nAdd this secret to your environment variables:")
    print(f"export OPTDOOR_TOTP_SECRET={secret}")
    
    issuer = os.environ.get("OPTDOOR_ISSUER", "OTPdoor")
    user = os.environ.get("OPTDOOR_USER", "admin")
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user, issuer_name=issuer)
    
    print("\nScan this QR code link with your authenticator app:")
    print(f"https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl={provisioning_uri}")
    print("-------------------------------")

if __name__ == "__main__":
    serve()
