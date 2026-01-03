import pyotp
import html
import os
from flask import Flask, request, make_response, redirect, render_template, url_for, send_from_directory
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from .config import config, DEFAULT_TOTP_SECRET
import qrcode
import io
import base64

app = Flask(__name__)
# Flask's secret key is for sessions/signing, but we use config.fernet for the auth cookie
app.secret_key = config.cookie_secret

@app.route('/_auth_style.css')
def serve_css():
    return send_from_directory(os.path.join(app.root_path, 'static'), '_auth_style.css')

def is_authenticated(domain_name):
    cookie_name = get_cookie_name(domain_name)
    token = request.cookies.get(cookie_name)
    if not token:
        return False
    expires_at = decrypt_session(token)
    return expires_at and expires_at > datetime.now(timezone.utc)

def is_safe_origin(origin):
    if not origin:
        return False
    if origin.startswith("/"):
        return True
    
    try:
        u = urlparse(origin)
        if not u.hostname:
            return False
        
        if not config.allowed_domains or config.allowed_domains == ['']:
            return False

        return any(u.hostname.endswith(domain.strip()) for domain in config.allowed_domains if domain.strip())
    except Exception:
        return False

def get_totp(domain_cfg):
    return pyotp.TOTP(domain_cfg.totp_secret)

def encrypt_session(expires_at: datetime) -> str:
    payload = expires_at.isoformat().encode()
    return config.fernet.encrypt(payload).decode()

def decrypt_session(token: str) -> datetime:
    try:
        payload = config.fernet.decrypt(token.encode())
        return datetime.fromisoformat(payload.decode())
    except Exception:
        return None

def get_cookie_name(domain_name):
    return f"{config.cookie_name_prefix}_{domain_name}"

@app.route(config.check_path, methods=['GET'])
def check():
    domain_name = request.args.get("domain", "default")
    cookie_name = get_cookie_name(domain_name)
    token = request.cookies.get(cookie_name)
    if token:
        expires_at = decrypt_session(token)
        if expires_at and expires_at > datetime.now(timezone.utc):
            return "OK", 200
    
    return "Unauthorized", 401

@app.route(config.auth_path, methods=['GET'])
def auth_get():
    domain_name = request.args.get("domain", "default")
    domain_cfg = config.get_domain(domain_name)
    origin = request.args.get("originator", "/")
    if not is_safe_origin(origin):
        origin = "/"
    
    return render_template("login.html", 
                           origin=origin, 
                           auth_path=config.auth_path, 
                           theme=domain_cfg.theme,
                           domain=domain_name)

@app.route(config.auth_path, methods=['POST'])
def auth_post():
    domain_name = request.args.get("domain", "default")
    domain_cfg = config.get_domain(domain_name)
    code = request.form.get("code")
    origin = request.form.get("originator", "/")
    if not is_safe_origin(origin):
        origin = "/"

    totp = get_totp(domain_cfg)
    if totp.verify(code):
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=domain_cfg.session_duration)
        token = encrypt_session(expires_at)
        
        resp = make_response(redirect(origin))
        cookie_name = get_cookie_name(domain_name)
        resp.set_cookie(
            cookie_name,
            token,
            max_age=domain_cfg.session_duration,
            httponly=config.cookie_httponly,
            secure=config.cookie_secure,
            samesite=config.cookie_samesite,
            domain=config.cookie_domain
        )
        return resp
    
    return render_template("login.html", 
                           origin=origin, 
                           auth_path=config.auth_path, 
                           error="Invalid code", 
                           theme=domain_cfg.theme,
                           domain=domain_name), 403

def generate_qr_base64(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

@app.route(config.config_path, methods=['GET'])
def config_get():
    if not config.enable_config:
        return "Not Found", 404
    
    # REQUIRE authentication for the 'default' domain to access ANY config
    if not is_authenticated("default"):
        return redirect(url_for('auth_get', domain='default', originator=request.full_path))

    domain_name = request.args.get("domain", "default")
    domain_cfg = config.get_domain(domain_name)
    
    issuer = os.environ.get("OTPDOOR_ISSUER", "OTPdoor")
    user = os.environ.get("OTPDOOR_USER", "admin")
    # Differentiation in the account name: admin (domain)
    provisioning_uri = pyotp.totp.TOTP(domain_cfg.totp_secret).provisioning_uri(
        name=f"{user} ({domain_name})", 
        issuer_name=issuer
    )
    
    qr_code_b64 = generate_qr_base64(provisioning_uri)
    
    # Calculate display duration and unit
    display_duration = domain_cfg.session_duration
    unit = "seconds"
    if display_duration % 3600 == 0:
        display_duration //= 3600
        unit = "hours"
    elif display_duration % 60 == 0:
        display_duration //= 60
        unit = "minutes"

    default_cfg = config.get_domain("default")
    is_default_secret = default_cfg.totp_secret == DEFAULT_TOTP_SECRET

    return render_template("config.html", 
                           secret=domain_cfg.totp_secret, 
                           display_duration=display_duration,
                           unit=unit,
                           theme=domain_cfg.theme,
                           provisioning_uri=provisioning_uri,
                           qr_code_b64=qr_code_b64,
                           auth_path=config.auth_path,
                           domain=domain_name,
                           is_default_secret=is_default_secret,
                           domains=list(config.domains.keys()))

@app.route(config.config_path, methods=['POST'])
def config_post():
    if not config.enable_config:
        return "Not Found", 404

    # REQUIRE authentication for the 'default' domain
    if not is_authenticated("default"):
        return redirect(url_for('auth_get', domain='default', originator=request.full_path))

    domain_name = request.args.get("domain", "default")
    domain_cfg = config.get_domain(domain_name)
    
    action = request.form.get("action")
    message = ""
    test_message = ""
    if action == "new_secret":
        domain_cfg.totp_secret = pyotp.random_base32()
        config.save()
        message = f"New TOTP secret generated for {domain_name}!"
    elif action == "add_domain":
        new_domain = request.form.get("new_domain", "").strip()
        if not new_domain:
            message = "Error: Domain name cannot be empty."
        elif new_domain in config.domains:
            message = f"Error: Domain '{new_domain}' already exists."
        else:
            from .config import DomainConfig
            secret = pyotp.random_base32()
            config.domains[new_domain] = DomainConfig(new_domain, secret)
            config.save()
            return redirect(url_for('config_get', domain=new_domain))
    elif action == "update_duration":
        try:
            val = int(request.form.get("duration", 86400))
            unit = request.form.get("unit", "seconds")
            if unit == "minutes":
                val *= 60
            elif unit == "hours":
                val *= 3600
            domain_cfg.session_duration = val
            config.save()
            message = f"Session duration for {domain_name} updated to {domain_cfg.session_duration} seconds."
        except ValueError:
            message = "Error: Invalid duration value."
    elif action == "update_theme":
        domain_cfg.theme = request.form.get("theme", "dark")
        config.save()
        message = f"Theme for {domain_name} updated to {domain_cfg.theme} mode."
    elif action == "test_code":
        code = request.form.get("test_code", "").strip()
        totp = get_totp(domain_cfg)
        if totp.verify(code):
            test_message = "✅ Success! The TOTP code is valid."
        else:
            test_message = "❌ Error: Invalid TOTP code."

    # ... provisioning logic ...
    issuer = os.environ.get("OTPDOOR_ISSUER", "OTPdoor")
    user = os.environ.get("OTPDOOR_USER", "admin")
    provisioning_uri = pyotp.totp.TOTP(domain_cfg.totp_secret).provisioning_uri(
        name=f"{user} ({domain_name})", 
        issuer_name=issuer
    )

    # Calculate display duration and unit for the refresh
    # Calculate display duration and unit for the refresh
    display_duration = domain_cfg.session_duration
    unit = "seconds"
    if display_duration % 3600 == 0:
        display_duration //= 3600
        unit = "hours"
    elif display_duration % 60 == 0:
        display_duration //= 60
        unit = "minutes"
        
    qr_code_b64 = generate_qr_base64(provisioning_uri)

    return render_template("config.html", 
                           secret=domain_cfg.totp_secret, 
                           display_duration=display_duration,
                           unit=unit,
                           theme=domain_cfg.theme,
                           provisioning_uri=provisioning_uri,
                           qr_code_b64=qr_code_b64,
                           auth_path=config.auth_path,
                           message=message,
                           test_message=test_message,
                           domain=domain_name,
                           domains=list(config.domains.keys()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
