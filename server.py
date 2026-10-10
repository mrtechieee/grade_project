"""Unified backend & web server for Student Grade Management System.

Serves the full web application and SQLite REST API on a single localhost link.
Usage: python server.py
URL:   http://localhost:8000/
"""
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import database
import student_service as service

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


class GradeSystemHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/students":
            records = service.list_students()
            self._send_json(records)
        elif path == "/api/stats":
            stats = service.get_statistics()
            self._send_json(stats or {})
        elif path == "/api/search":
            query = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
            results = service.find_students(query)
            self._send_json(results)
        else:
            if path in ("", "/"):
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/students":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                name = data.get("name")
                subjects = data.get("subjects", {})
                if not name or not subjects:
                    self._send_json({"error": "Name and subjects required"}, status=400)
                    return
                record = service.create_student(name, subjects)
                self._send_json(record, status=201)
            except database.DuplicateStudentError:
                self._send_json({"error": "Student already exists"}, status=400)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
        else:
            self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        if self.path.startswith("/api/students/"):
            student_id_str = self.path.split("/")[-1]
            try:
                student_id = int(student_id_str)
                database.delete_student(student_id)
                self._send_json({"success": True})
            except ValueError:
                self._send_json({"error": "Invalid student ID"}, status=400)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
        else:
            self.send_error(404, "Endpoint not found")

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_server(port=8000):
    database.initialize_database()
    server_address = ("", port)
    httpd = HTTPServer(server_address, GradeSystemHandler)
    print(f"==================================================")
    print(f" Student Grade Management System Unified Web Server")
    print(f" Live Link: http://localhost:{port}/")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
