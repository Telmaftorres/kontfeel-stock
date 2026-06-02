"""
Serveur webhook de déploiement automatique.
Lance en systemd sur le VPS — reçoit les push GitHub et redéploie.
"""
import hashlib
import hmac
import json
import logging
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = os.environ.get("DEPLOY_SECRET", "")
REPO   = os.environ.get("REPO_DIR", "/home/ubuntu/kontfeel-stock")
LOG    = logging.getLogger("autodeploy")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def verify_signature(body: bytes, sig_header: str) -> bool:
    if not SECRET or not sig_header:
        return False
    expected = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header)


def deploy():
    LOG.info("Déploiement démarré…")
    result = subprocess.run(
        ["bash", "-c", f"cd {REPO} && git pull && docker compose up -d --build"],
        capture_output=True, text=True
    )
    LOG.info(result.stdout)
    if result.returncode != 0:
        LOG.error(result.stderr)
    else:
        LOG.info("Déploiement terminé ✓")
    return result.returncode == 0


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/webhook/deploy":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        sig    = self.headers.get("X-Hub-Signature-256", "")

        if not verify_signature(body, sig):
            LOG.warning("Signature invalide — requête ignorée")
            self.send_response(403); self.end_headers(); return

        try:
            event = json.loads(body)
            branch = event.get("ref", "")
            if branch and branch != "refs/heads/main":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"not main branch, skipped")
                return
        except Exception:
            pass

        threading.Thread(target=deploy, daemon=True).start()
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b"deploy started")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("DEPLOY_PORT", 9000))
    LOG.info(f"Webhook autodeploy sur :{port}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
