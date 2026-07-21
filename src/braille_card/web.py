"""Local browser workflow for creating reviewable Braille card previews."""

from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from flask import Flask, abort, redirect, render_template_string, request, send_from_directory, url_for
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .moonraker import MoonrakerClient, MoonrakerError
from .preview import generate_preview

ARTIFACT_NAMES = {
    "visual_preview.png",
    "tactile_preview.png",
    "tactile_layer.svg",
    "braille_review.html",
    "braille_source.txt",
    "braille_ueb_unicode.txt",
    "braille_ueb.brf",
    "render_manifest.json",
}

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#12231c">
  <title>BrailleCard Local Studio</title>
  <style>
    :root{color-scheme:light;--ink:#12231c;--pine:#235241;--paper:#f6f4ec;--line:#b8c4bc;--warn:#7d4900;--warn-bg:#fff3d7;--bad:#9b1c1c;--focus:#006ad4}
    *{box-sizing:border-box} body{margin:0;background:var(--paper);color:var(--ink);font:system-ui,sans-serif;line-height:1.5} a{color:#075f48} a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
    .skip{position:absolute;left:-999px}.skip:focus-visible{left:1rem;top:1rem;background:white;padding:.5rem;z-index:2}.shell{max-width:72rem;margin:auto;padding:2rem 1rem 4rem}.mast{border-bottom:1px solid var(--line);padding-bottom:1rem}.kicker{color:var(--pine);font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:.8rem}.notice{border:2px solid var(--warn);background:var(--warn-bg);padding:1rem;margin:1.5rem 0}.error{border-color:var(--bad);color:var(--bad)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:1rem}.card{background:white;border:1px solid var(--line);border-radius:.75rem;padding:1.25rem;min-width:0}.wide{grid-column:1/-1}label{display:block;font-weight:650;margin-top:.8rem}input,textarea{font:inherit;width:100%;padding:.65rem;border:1px solid #69776e;border-radius:.4rem;background:white}textarea{min-height:7rem;resize:vertical}small{color:#4e5b53}button{margin-top:1rem;background:var(--pine);color:white;border:0;border-radius:.45rem;padding:.7rem 1rem;font:inherit;font-weight:700;cursor:pointer}button:hover{background:#163d30}.stage{padding:.65rem;border-left:4px solid var(--line);background:#fafbf8}.stage strong{display:block}.art{width:100%;height:auto;border:1px solid var(--line);background:#fff}.links{display:flex;flex-wrap:wrap;gap:.75rem;padding:0;list-style:none}.links a{padding:.45rem .65rem;border:1px solid var(--line);border-radius:.35rem;background:#fff}.muted{color:#4e5b53}@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
  </style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <main id="main" class="shell">
    <header class="mast"><p class="kicker">Local-only workspace</p><h1>BrailleCard Studio</h1><p>Preview, slice, and print are separate operator-controlled stages.</p></header>
    <section class="notice" aria-live="polite"><strong>Preview only.</strong> Braille is not yet human-reviewed. No printer contacted, upload, or start occurs during rendering.</section>
    {% if error %}<section class="notice error" role="alert"><strong>Can’t create preview.</strong> {{ error }}</section>{% endif %}
    {% if job %}
      <h2>Preview Ready</h2>
      <p class="muted">Saved local job {{ job.job_id }}. The retained artifacts are shown below; no production action has occurred.</p>
      <div class="grid">
        <article class="card wide"><h3>Visual Layout</h3><img class="art" width="1064" height="711" fetchpriority="high" src="{{ url_for('artifact', job_id=job.job_id, name='visual_preview.png') }}" alt="Front and back visual card preview"></article>
        <article class="card"><h3>Tactile Preview</h3><p class="muted">Derived from the uploaded artwork for review; it is not printable geometry.</p><img class="art" width="635" height="889" loading="lazy" src="{{ url_for('artifact', job_id=job.job_id, name='tactile_preview.png') }}" alt="Source-derived tactile interpretation preview"></article>
        <article class="card"><h3>Braille Review</h3><p>Review source text, Unicode Braille, and BRF before any print approval.</p><p><a href="{{ url_for('artifact', job_id=job.job_id, name='braille_review.html') }}">Open side-by-side Braille review</a></p></article>
        <article class="card wide"><h3>Production Controls · Sovol SV07</h3><div class="grid"><div class="stage"><strong>1. Preview</strong>Complete</div><div class="stage"><strong>2. Offline Slice</strong>Blocked until source-derived tactile production geometry is available</div><div class="stage"><strong>3. Operator Print Approval</strong>Unavailable until a reviewed, sliced job exists</div><div class="stage"><strong>4. Remote Observation</strong>{% if job.remote_status %}{% if job.remote_status.connected %}Read-only check completed {{ job.remote_status.checked_at }}{% else %}{{ job.remote_status.message }}{% endif %}{% else %}Not checked{% endif %}</div></div><p class="muted">Slicer, printer, and remote options remain separate. Previewing cannot trigger them.</p>{% if job.remote_status and job.remote_status.connected %}<p class="muted">Klipper: {{ job.remote_status.klipper_state }} · Print: {{ job.remote_status.print_state }}{% if job.remote_status.filename %} · {{ job.remote_status.filename }}{% endif %}{% if job.remote_status.progress is not none %} · {{ job.remote_status.progress }}%{% endif %}</p>{% endif %}<form method="post" action="{{ url_for('refresh_remote_status', job_id=job.job_id) }}"><button type="submit">Check Remote Status (Read-only)</button></form></article>
        <article class="card wide"><h3>Saved Artifacts</h3><ul class="links">{% for name in job.artifacts %}<li><a href="{{ url_for('artifact', job_id=job.job_id, name=name) }}">{{ name }}</a></li>{% endfor %}</ul></article>
      </div>
    {% else %}
      <h2>Create a Tactile Card Preview</h2>
      <form class="grid" method="post" action="{{ url_for('create_job') }}" enctype="multipart/form-data">
        <section class="card"><label for="image">Artwork</label><input id="image" name="image" type="file" accept=".png,.jpg,.jpeg,.webp,.svg,image/png,image/jpeg,image/webp,image/svg+xml" required><small>PNG, JPEG, WebP, or SVG. Raster images: 600 × 600 pixels minimum, 15 MB maximum.</small></section>
        <section class="card"><label for="greeting">Front Greeting</label><input id="greeting" name="greeting" maxlength="30" autocomplete="off" required><small>Up to 30 characters.</small><label for="message">Back Message</label><textarea id="message" name="message" maxlength="140" autocomplete="off" required></textarea><small>Up to 140 characters.</small><button type="submit">Create Local Preview</button></section>
      </form>
    {% endif %}
  </main>
</body></html>"""


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _job_path(root: Path, job_id: str) -> Path:
    if not job_id or any(character not in "0123456789abcdef-" for character in job_id):
        abort(404)
    return root / job_id


def _load_job(root: Path, job_id: str) -> dict[str, Any]:
    path = _job_path(root, job_id) / "job.json"
    if not path.is_file():
        abort(404)
    return json.loads(path.read_text(encoding="utf-8"))


def _write_job(path: Path, payload: dict[str, Any]) -> None:
    (path / "job.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _remote_status_summary(status: dict[str, Any]) -> dict[str, Any]:
    """Keep only small, operator-useful fields in the local job record."""
    webhooks = status.get("webhooks", {})
    print_stats = status.get("print_stats", {})
    virtual_sdcard = status.get("virtual_sdcard", {})
    progress = virtual_sdcard.get("progress")
    return {
        "connected": True,
        "checked_at": _utc_now(),
        "klipper_state": str(webhooks.get("state", "unknown")),
        "print_state": str(print_stats.get("state", "unknown")),
        "filename": str(print_stats.get("filename", "")),
        "progress": round(float(progress) * 100, 1) if isinstance(progress, (int, float)) else None,
    }


def _save_upload(upload: FileStorage, path: Path) -> str:
    filename = secure_filename(upload.filename or "")
    if not filename:
        raise ValueError("Select an image before creating a preview")
    upload.save(path / filename)
    return filename


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        JOBS_ROOT=Path.cwd() / ".braillecard-jobs",
        MAX_CONTENT_LENGTH=15 * 1024 * 1024,
        MOONRAKER_URL=os.environ.get("MOONRAKER_URL"),
        MOONRAKER_API_KEY=os.environ.get("MOONRAKER_API_KEY"),
        MOONRAKER_BEARER_TOKEN=os.environ.get("MOONRAKER_BEARER_TOKEN"),
        MOONRAKER_TIMEOUT_SECONDS=5.0,
    )
    if test_config:
        app.config.update(test_config)

    def home(*, error: str | None = None, status: int = 200):
        return render_template_string(PAGE, error=error, job=None), status

    @app.get("/")
    def index():
        return home()

    @app.post("/jobs")
    def create_job():
        greeting = request.form.get("greeting", "").strip()
        message = request.form.get("message", "").strip()
        upload = request.files.get("image")
        if upload is None or not upload.filename:
            return home(error="Select an image before creating a preview", status=400)
        if not greeting or not message:
            return home(error="A greeting and message are both required", status=400)

        root = Path(app.config["JOBS_ROOT"])
        job_id = str(uuid.uuid4())
        job_dir = root / job_id
        job_dir.mkdir(parents=True)
        try:
            filename = _save_upload(upload, job_dir)
            card = job_dir / "card.json"
            card.write_text(json.dumps({"greeting": greeting, "message": message}) + "\n", encoding="utf-8")
            artifacts = job_dir / "artifacts"
            generate_preview(job_dir / filename, card, artifacts)
            available = sorted(name for name in ARTIFACT_NAMES if (artifacts / name).is_file())
            manifest = json.loads((artifacts / "render_manifest.json").read_text(encoding="utf-8"))
            _write_job(
                job_dir,
                {
                    "schema_version": 1,
                    "job_id": job_id,
                    "created_at": _utc_now(),
                    "status": "preview_ready",
                    "input": {"filename": filename, "greeting": greeting, "message": message},
                    "artifacts": available,
                    "safety": manifest["printer_interaction"],
                    "braille_review": manifest["human_review"]["braille"],
                    "remote_status": None,
                },
            )
        except (OSError, ValueError) as exc:
            shutil.rmtree(job_dir, ignore_errors=True)
            return home(error=str(exc), status=400)
        except Exception:
            shutil.rmtree(job_dir, ignore_errors=True)
            return home(error="The preview could not be rendered. Correct the input and try again.", status=500)
        return redirect(url_for("show_job", job_id=job_id))

    @app.get("/jobs/<job_id>")
    def show_job(job_id: str):
        job = _load_job(Path(app.config["JOBS_ROOT"]), job_id)
        return render_template_string(PAGE, error=None, job=job)

    @app.get("/jobs/<job_id>/artifacts/<name>")
    def artifact(job_id: str, name: str):
        job = _load_job(Path(app.config["JOBS_ROOT"]), job_id)
        if name not in job["artifacts"]:
            abort(404)
        return send_from_directory(_job_path(Path(app.config["JOBS_ROOT"]), job_id) / "artifacts", name)

    @app.post("/jobs/<job_id>/remote-status")
    def refresh_remote_status(job_id: str):
        root = Path(app.config["JOBS_ROOT"])
        job = _load_job(root, job_id)
        if not app.config["MOONRAKER_URL"]:
            job["remote_status"] = {
                "connected": False,
                "message": "Remote status is not configured on this computer.",
            }
        else:
            try:
                client = MoonrakerClient(
                    str(app.config["MOONRAKER_URL"]),
                    api_key=app.config["MOONRAKER_API_KEY"],
                    bearer_token=app.config["MOONRAKER_BEARER_TOKEN"],
                    timeout_seconds=float(app.config["MOONRAKER_TIMEOUT_SECONDS"]),
                )
                job["remote_status"] = _remote_status_summary(client.read_status())
            except (MoonrakerError, ValueError):
                job["remote_status"] = {
                    "connected": False,
                    "message": "Remote status could not be read. Check local Moonraker settings.",
                }
        _write_job(_job_path(root, job_id), job)
        return redirect(url_for("show_job", job_id=job_id))

    return app
