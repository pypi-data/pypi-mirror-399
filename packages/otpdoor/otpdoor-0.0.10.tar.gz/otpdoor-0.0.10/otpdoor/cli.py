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
    parser.add_argument("--list-domains", action="store_true", help="List all configured domains.")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode.")
    args = parser.parse_args()

    if args.list_domains:
        print("--- Configured Domains ---")
        for name in config.domains:
            print(f"- {name}")
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

    config.enable_config = args.config

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
