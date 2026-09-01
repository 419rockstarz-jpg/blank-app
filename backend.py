import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from streamlit_app import build_delivery_records_payload, build_registry_payload, get_properties


class LedgerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        if parsed.path == "/city-ledger":
            records = get_properties()
            payload = {
                "properties": records,
                "registryPayload": build_registry_payload(records, "City Ledger"),
                "deliveryRecords": build_delivery_records_payload(),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))
            return

        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), LedgerHandler)
    print(f"Serving city ledger backend on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
push
git add .
git commit -m "Configure Streamlit entry point for Railway in main
