#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 4312
MAX_UPLOAD_BYTES = 512 * 1024 * 1024

HTML = """<!doctype html>
<html lang="sv">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Borstbindare Wenman</title>
    <style>
      :root {
        --bg1: #e7efe8;
        --bg2: #ccd8c5;
        --panel: rgba(251, 249, 242, 0.92);
        --ink: #1c281e;
        --muted: #526152;
        --line: rgba(28, 40, 30, 0.12);
        --accent: #2f6c45;
        --accent-strong: #1f4c30;
        --shadow: 0 24px 60px rgba(33, 47, 36, 0.12);
      }

      * { box-sizing: border-box; }
      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Avenir Next", "Segoe UI", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top right, rgba(255, 255, 255, 0.65), transparent 35%),
          linear-gradient(160deg, var(--bg1), var(--bg2));
      }

      main {
        width: min(860px, calc(100% - 32px));
        margin: 48px auto;
        display: grid;
        gap: 24px;
      }

      section {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: var(--panel);
        box-shadow: var(--shadow);
        padding: 28px;
      }

      .eyebrow {
        margin: 0 0 8px;
        font-size: 0.8rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: var(--accent);
      }

      h1, h2 {
        margin: 0;
        font-family: "Georgia", "Times New Roman", serif;
      }

      h1 {
        font-size: clamp(2.2rem, 5vw, 4rem);
        line-height: 0.95;
        max-width: 10ch;
      }

      p, .meta, .status { color: var(--muted); line-height: 1.5; }
      .form { display: grid; gap: 16px; margin-top: 24px; }

      label {
        display: grid;
        gap: 10px;
        padding: 18px;
        border: 1px dashed rgba(47, 108, 69, 0.32);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.55);
      }

      label span { font-weight: 600; color: var(--ink); }
      input[type="file"] { font: inherit; }

      button {
        appearance: none;
        border: 0;
        border-radius: 999px;
        padding: 14px 20px;
        font: inherit;
        font-weight: 700;
        color: white;
        background: linear-gradient(135deg, var(--accent), var(--accent-strong));
        cursor: pointer;
      }

      button:disabled { opacity: 0.6; cursor: wait; }

      .status {
        margin-top: 18px;
        padding: 14px 16px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.6);
        min-height: 52px;
      }

      .status.success { color: #174c2d; }
      .status.error { color: #8b1e1e; }

      @media (max-width: 640px) {
        main { width: min(100%, calc(100% - 20px)); margin: 20px auto; }
        section { padding: 20px; border-radius: 18px; }
      }
    </style>
  </head>
  <body>
    <main>
      <section>
        <p class="eyebrow">Offline Media Converter</p>
        <h1>Borstbindare Wenman</h1>
        <p>Detta är den lokala Mac-versionen. Den kör på din egen dator och konverterar MP4 till WAV.</p>
      </section>

      <section>
        <h2>MP4 till WAV</h2>
        <p>Välj en MP4-fil, konvertera lokalt och ladda ner WAV-resultatet.</p>

        <form id="form" class="form">
          <label>
            <span>Välj MP4-fil</span>
            <input id="file" type="file" accept=".mp4,video/mp4" required>
          </label>
          <div id="meta" class="meta">Ingen fil vald.</div>
          <button id="submit" type="submit">Konvertera till WAV</button>
        </form>

        <div id="status" class="status">Väntar på fil.</div>
      </section>
    </main>

    <script>
      const form = document.getElementById("form");
      const fileInput = document.getElementById("file");
      const meta = document.getElementById("meta");
      const submit = document.getElementById("submit");
      const statusBox = document.getElementById("status");

      function setStatus(kind, message) {
        statusBox.className = "status" + (kind ? " " + kind : "");
        statusBox.textContent = message;
      }

      function formatBytes(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(1) + " MB";
      }

      fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (!file) {
          meta.textContent = "Ingen fil vald.";
          setStatus("", "Väntar på fil.");
          return;
        }

        meta.textContent = file.name + " (" + formatBytes(file.size) + ")";
        setStatus("", "Redo att konvertera.");
      });

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const file = fileInput.files[0];

        if (!file) {
          setStatus("error", "Välj en MP4-fil först.");
          return;
        }

        submit.disabled = true;
        setStatus("", "Konverterar lokalt. Detta kan ta en stund.");

        try {
          const response = await fetch("/api/convert/mp4-to-wav", {
            method: "POST",
            headers: { "Content-Type": file.type || "video/mp4" },
            body: file
          });

          if (!response.ok) {
            let message = "Konverteringen misslyckades.";
            try {
              const payload = await response.json();
              if (payload.error) message = payload.error;
            } catch (error) {}
            throw new Error(message);
          }

          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const anchor = document.createElement("a");
          const baseName = file.name.replace(/\\.[^.]+$/, "") || "converted";
          anchor.href = url;
          anchor.download = baseName + ".wav";
          anchor.click();
          URL.revokeObjectURL(url);
          setStatus("success", "Klart. Din WAV-fil laddas ner nu.");
        } catch (error) {
          setStatus("error", error.message || "Konverteringen misslyckades.");
        } finally {
          submit.disabled = false;
        }
      });
    </script>
  </body>
</html>
"""


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/":
            json_response(self, 404, {"error": "Not found"})
            return

        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/convert/mp4-to-wav":
          json_response(self, 404, {"error": "Not found"})
          return

        content_length = self.headers.get("Content-Length")
        if not content_length:
            json_response(self, 400, {"error": "Ingen fil mottogs."})
            return

        try:
            size = int(content_length)
        except ValueError:
            json_response(self, 400, {"error": "Ogiltig filstorlek."})
            return

        if size < 1:
            json_response(self, 400, {"error": "Ingen fil mottogs."})
            return

        if size > MAX_UPLOAD_BYTES:
            json_response(self, 413, {"error": "Filen är för stor."})
            return

        ffmpeg_path = os.environ.get("BORSTBINDAR_FFMPEG") or shutil.which("ffmpeg")
        if not ffmpeg_path:
            json_response(self, 500, {"error": "ffmpeg hittades inte på datorn."})
            return

        work_dir = Path(tempfile.mkdtemp(prefix="borstbindare-"))
        input_path = work_dir / "input.mp4"
        output_path = work_dir / "output.wav"

        try:
            with input_path.open("wb") as handle:
                remaining = size
                while remaining > 0:
                    chunk = self.rfile.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    handle.write(chunk)
                    remaining -= len(chunk)

            subprocess.run(
                [
                    ffmpeg_path,
                    "-y",
                    "-i",
                    str(input_path),
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    str(output_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )

            body = output_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Disposition", 'attachment; filename="converted.wav"')
            self.end_headers()
            self.wfile.write(body)
        except subprocess.CalledProcessError as error:
            message = error.stderr.decode("utf-8", "replace").strip().splitlines()[-1]
            json_response(self, 500, {"error": message or "Konverteringen misslyckades."})
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Borstbindare Wenman UI kör på http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
