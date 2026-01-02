# OTPdoor

**OTPdoor** is a premium, lightweight Python library for creating and managing TOTP (One-Time Password) authentication, specifically designed to be used as an `auth_request` backend for Nginx.

It provides a modern, glassmorphic UI for user login and a dedicated configuration portal for initial setup and device provisioning.

## Features

-   **Multi-Domain Support**: Protect multiple independent applications with a single OTPdoor instance, each with its own secret and settings.
-   **TOTP Authentication**: Industry-standard Time-based One-Time Passwords (RFC 6238).
-   **Premium UI**: Modern, glassmorphic design with support for **Light** and **Dark** modes.
-   **Runtime Configuration**: Update session durations and TOTP secrets on the fly via the `/_config` endpoint.
-   **Flexible Sessions**: Configure session duration in seconds, minutes, or hours.
-   **Security First**:
    -   Secure, encrypted session cookies using Fernet (AES-128).
    -   Restricted configuration mode with explicit CLI activation and warnings.
    -   Safety confirmation dialogs for critical actions.
-   **Production Ready**: Powered by **Waitress**, a stable production-grade WSGI server.
-   **Easy Provisioning**: Built-in QR code generation for quick configuration with apps like Google Authenticator or Authy.

## Installation

Install OTPdoor using pip:

```shell
pip install otpdoor
```

## Quick Start

### 1. Initialize your secret
Run the built-in initialization to generate your first TOTP secret:

```shell
python -m otpdoor --init
```

### 2. Set Environment Variables
Configure the essential settings:

```shell
export OPTDOOR_TOTP_SECRET="YOUR_GENERATE_SECRET"
export OPTDOOR_COOKIE_SECRET="YOUR_FERNET_KEY"
```

### 3. Run the Server
Start the server on a specific host and port:

```shell
python -m otpdoor -a 127.0.0.1 -p 8080
```

## Multi-Domain Support

OTPdoor allows you to manage multiple authentication domains. Each domain has its own secret, session duration, and theme. Configurations are persisted in `optdoor_config.json`.

### Managing Domains
- **Add a domain**: `python -m otpdoor --add-domain myapp`
- **List domains**: `python -m otpdoor --list-domains`

### Using Domains in URLs
Access routes for a specific domain by adding the `domain` parameter:
- `http://127.0.0.1:8080/_auth?domain=myapp`
- `http://127.0.0.1:8080/_check?domain=myapp`
- `http://127.0.0.1:8080/_config?domain=myapp`

If no domain is provided, it defaults to `default`.

## Step-by-Step Tutorial: First Setup

### 1. Installation
```shell
pip install otpdoor
```

### 2. Initial Setup
```shell
python -m otpdoor --init
```

### 3. Environment Configuration
```shell
export OPTDOOR_TOTP_SECRET="YOUR_GENERATED_SECRET"
export OPTDOOR_COOKIE_SECRET="something-very-random-and-long"
```

### 4. Provisioning your Device
```shell
python -m otpdoor -c
```
- Open `http://127.0.0.1:8080/_config?domain=default`.
- Scan the QR code.
- Stop the server (`Ctrl+C`).

### 5. Nginx Configuration (Multi-Domain)
To protect a specific app (`myapp`), pass the `domain` parameter in the proxy requests:

```nginx
upstream otpdoor_backend {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name myapp.example.com;

    location / {
        # Pass the domain to the check endpoint
        auth_request /_check;
        error_page 401 = @error401;
        proxy_pass http://your_app_backend;
    }

    location = /_check {
        internal;
        # Pass domain=myapp to use the correct secret
        proxy_pass http://otpdoor_backend/_check?domain=myapp;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
    }

    location /_auth {
        # Pass domain=myapp so the login page uses the correct configuration
        proxy_pass http://otpdoor_backend/_auth?domain=myapp;
        proxy_set_header Host $host;
    }

    location @error401 {
        # Redirect to the domain-specific auth page
        return 302 $scheme://$http_host/_auth?domain=myapp&originator=$request_uri;
    }
}
```

## Configuration Reference

- `OPTDOOR_TOTP_SECRET`: Shared secret for the `default` domain.
- `OPTDOOR_COOKIE_SECRET`: Key used to encrypt session cookies.
- `OPTDOOR_CONFIG_FILE`: Path to the JSON configuration file (default: `optdoor_config.json`).
- `OPTDOOR_SESSION_DURATION`: Default session duration in seconds.
- `OPTDOOR_THEME`: Default theme (`dark` or `light`).
- `OPTDOOR_ALLOWED_DOMAINS`: Allowed domains for redirects.
- `OPTDOOR_COOKIE_SECURE`: Set to `false` for local HTTP testing.

## License
MIT License - see the LICENSE file for details.

## Contact
[germanespinosa@gmail.com]
