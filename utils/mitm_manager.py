import subprocess
import os
import time
import sys

MITM_PORT = 8080


def start_mitmproxy():
    """
    Starts mitmdump in background
    """
    return subprocess.Popen(
        ["mitmdump", "-p", str(MITM_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )


def ensure_cert_exists():
    """
    Run mitmproxy once to generate cert if missing
    """
    cert_dir = os.path.expanduser("~/.mitmproxy")
    cert_path = os.path.join(cert_dir, "mitmproxy-ca-cert.cer")

    if not os.path.exists(cert_path):
        print("[*] Generating mitmproxy certificate...")
        subprocess.run(["mitmproxy", "--quit"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return cert_path


def install_certificate(cert_path):
    """
    Install cert into Windows root store (requires admin)
    """
    print("[*] Installing certificate...")

    cmd = f'certutil -addstore -f Root "{cert_path}"'
    subprocess.run(cmd, shell=True)


def setup_mitm():
    """
    Full setup:
    - ensure cert
    - install cert
    - start proxy
    """
    cert_path = ensure_cert_exists()
    install_certificate(cert_path)

    proc = start_mitmproxy()
    time.sleep(2)  # give proxy time to start

    return proc