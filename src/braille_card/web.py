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
from .package import generate_package
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

PRODUCTION_ARTIFACT_NAMES = {
    "card.gcode",
    "combined_card.3mf",
    "combined_card.stl",
    "checks.json",
    "geometry.json",
    "manifest.json",
}

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#071a2f">
  <title>BrailleCard Local Studio</title>
  <style>
    :root{color-scheme:dark;--ink:#f7ead1;--gold:#e9b95f;--pine:#80a885;--paper:#071a2f;--card:#0e2a43;--field:#0a2136;--line:#466674;--warn:#f0c773;--warn-bg:#132f47;--bad:#ffb4a9;--focus:#f6d681;--muted:#bdd0cf}
    *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:ui-sans-serif,system-ui,sans-serif;line-height:1.5}a{color:#f6d681}a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid var(--focus);outline-offset:3px}.skip{position:absolute;left:-999px}.skip:focus-visible{left:1rem;top:1rem;background:var(--card);padding:.5rem;z-index:2}.shell{max-width:92rem;margin:auto;padding:1.5rem 1rem 4rem}.mast{border-bottom:1px solid var(--line);padding-bottom:1rem}.brand-lockup{display:block;width:clamp(7rem,13vw,10rem);margin-bottom:1rem}.brand-lockup img{display:block;width:100%;height:auto}.mast h1{font-family:Georgia,serif;font-size:clamp(2rem,4vw,3.3rem);font-weight:500;letter-spacing:-.045em;line-height:1;margin:.2rem 0 .5rem}.mast p{margin:.4rem 0}.kicker{color:var(--gold);font-weight:750;letter-spacing:.1em;text-transform:uppercase;font-size:.76rem}.notice{border:1px solid var(--warn);background:var(--warn-bg);border-radius:.55rem;padding:1rem;margin:1.25rem 0}.error{border-color:var(--bad);color:var(--bad)}.workspace{display:grid;grid-template-columns:minmax(17rem,23rem) minmax(0,1fr);gap:1.25rem;align-items:start}.panel{background:var(--card);border:1px solid var(--line);border-radius:.75rem;padding:1.15rem;min-width:0}.inputs{position:sticky;top:1rem}.inputs h2,.output h2,.output h3{margin-top:0}.input-intro{color:var(--muted);font-size:.92rem;margin-top:0}.file-field{border:1px dashed var(--gold);border-radius:.5rem;color:var(--gold);cursor:pointer;display:block;font-weight:700;margin-top:1rem;padding:.8rem}.file-field input{display:block;margin-top:.5rem}.field-label{display:block;font-weight:650;margin-top:1rem}input,textarea{color:var(--ink);font:inherit;width:100%;padding:.65rem;border:1px solid var(--line);border-radius:.4rem;background:var(--field)}input[type=checkbox]{width:auto;margin-right:.5rem}textarea{min-height:7rem;resize:vertical}small{color:var(--muted);display:block;margin-top:.35rem}button{margin-top:1rem;background:var(--pine);color:#061a2c;border:0;border-radius:.45rem;padding:.7rem 1rem;font:inherit;font-weight:750;cursor:pointer}button:hover{background:var(--gold)}.output-head{display:flex;align-items:baseline;justify-content:space-between;gap:1rem;margin-bottom:1rem}.output-head p{color:var(--muted);font-size:.9rem;margin:0}.proof-grid{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(14rem,.75fr);gap:1rem}.card-panel{background:var(--field);border:1px solid var(--line);border-radius:.55rem;padding:1rem}.card-panel h3{font-size:1rem}.art{width:100%;height:auto;border:1px solid var(--line);background:#fff}.side-stack{display:grid;gap:1rem}.stage-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(9rem,1fr));gap:.65rem}.stage{padding:.65rem;border-left:4px solid var(--gold);background:var(--field)}.stage strong{display:block}.links{display:flex;flex-wrap:wrap;gap:.55rem;padding:0;list-style:none}.links a{padding:.45rem .65rem;border:1px solid var(--line);border-radius:.35rem;background:var(--field)}.muted{color:var(--muted)}.empty{align-content:center;display:grid;min-height:38rem;text-align:center}.empty .card-outline{aspect-ratio:3/4;border:1px dashed var(--gold);border-radius:.4rem;margin:1rem auto;width:min(14rem,70%);background:linear-gradient(145deg,#112f48,#0a2136)}@media(max-width:760px){.workspace{grid-template-columns:1fr}.inputs{position:static}.proof-grid{grid-template-columns:1fr}.empty{min-height:24rem}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
  </style>
  <style>
    .draft-output{min-height:38rem}.draft-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(13rem,.56fr);gap:1rem;align-items:center}.draft-card{aspect-ratio:3/4;background:#f7ead1;border:1px solid var(--gold);border-radius:.45rem;box-shadow:0 .7rem 1.8rem #020b16aa;color:#071a2f;display:flex;flex-direction:column;margin:auto;max-width:23rem;overflow:hidden;width:100%}.draft-art{align-items:center;background:linear-gradient(145deg,#b9d3d2,#6c9096);color:#173348;display:flex;flex:1;justify-content:center;min-height:0;position:relative}.draft-art img{height:100%;object-fit:cover;width:100%}.draft-art[data-empty=true]::after{border:1px dashed #315d6c;content:"Artwork preview";font-size:.85rem;font-weight:700;letter-spacing:.06em;padding:.5rem .7rem;text-transform:uppercase}.draft-copy{padding:1rem 1rem 1.15rem}.draft-greeting{font-family:Georgia,serif;font-size:clamp(1.35rem,3vw,2rem);font-weight:700;line-height:1.05;margin:0 0 .55rem;overflow-wrap:anywhere}.draft-message{font-size:.92rem;line-height:1.35;margin:0;overflow-wrap:anywhere}.draft-note{background:var(--field);border:1px solid var(--line);border-radius:.55rem;padding:1rem}.draft-note h3{margin:.1rem 0 .5rem}.draft-note p{margin:.5rem 0}.draft-note .kicker{display:block;margin-bottom:.7rem}@media(max-width:760px){.draft-output{min-height:0}.draft-grid{grid-template-columns:1fr}.draft-card{max-width:19rem}}
  </style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <main id="main" class="shell">
    <header class="mast"><a class="brand-lockup" href="https://dorqlabs.com/" aria-label="Dorq Labs home"><img src="{{ url_for('static', filename='dorq-labs-lockup.png') }}" alt="Dorq Labs"></a><p class="kicker">Local-only workspace</p><h1>BrailleCard Studio</h1><p>Preview, slice, and print are separate operator-controlled stages.</p></header>
    <section class="notice" aria-live="polite"><strong>Safety boundary.</strong> Braille requires human review. Preview, approval, and local slicing are separate; this workspace never uploads or starts a printer job.</section>
    {% if error %}<section class="notice error" role="alert"><strong>Can’t create preview.</strong> {{ error }}</section>{% endif %}
    <div class="workspace">
      <form id="studio-form" class="panel inputs" method="post" action="{{ url_for('create_job') }}" enctype="multipart/form-data">
        <h2>Input</h2><p class="input-intro">Create a new local proof. It appears alongside these controls.</p>
        <label class="file-field" for="image">Choose artwork<input id="image" name="image" type="file" accept=".png,.jpg,.jpeg,.webp,.svg,image/png,image/jpeg,image/webp,image/svg+xml" required></label><small>PNG, JPEG, WebP, or SVG. Raster images: 600 × 600 pixels minimum, 15 MB maximum.</small>
        <label class="field-label" for="greeting">Front Greeting</label><input id="greeting" name="greeting" maxlength="9" autocomplete="off" value="{{ job.input.greeting if job and job.input is defined else '' }}" required><small>Up to 9 characters on the 3 × 4 inch portrait card.</small>
        <label class="field-label" for="message">Back Message</label><textarea id="message" name="message" maxlength="27" autocomplete="off" required>{{ job.input.message if job and job.input is defined else '' }}</textarea><small>Up to 27 characters on the 3 × 4 inch portrait card.</small><button type="submit">Create Local Preview</button>
      </form>
      {% if job %}
        <section class="panel output" aria-labelledby="output-title"><div class="output-head"><div><h2 id="output-title">Preview Ready</h2><p>Saved local job {{ job.job_id }} · no printer action has occurred.</p></div><span class="kicker">Output</span></div>
          {% if job.action_message %}<section class="notice" aria-live="polite">{{ job.action_message }}</section>{% endif %}
          <div class="proof-grid"><article class="card-panel"><h3>Visual Layout</h3><p class="muted">Front and back faces of one flat card, shown side by side for review — not a fold-open card.</p><img class="art" width="658" height="406" fetchpriority="high" src="{{ url_for('artifact', job_id=job.job_id, name='visual_preview.png') }}" alt="Front and back visual card preview"></article><div class="side-stack"><article class="card-panel"><h3>Tactile Preview</h3><p class="muted">Derived from the artwork for review; it is not printable geometry.</p><img class="art" width="381" height="508" loading="lazy" src="{{ url_for('artifact', job_id=job.job_id, name='tactile_preview.png') }}" alt="Source-derived tactile interpretation preview"></article><article class="card-panel"><h3>Braille Review</h3><p>Review source text, Unicode Braille, and BRF before approval.</p><p><a href="{{ url_for('artifact', job_id=job.job_id, name='braille_review.html') }}">Open side-by-side Braille review</a></p></article></div></div>
          <article class="card-panel"><h3>Production Controls · Sovol SV07</h3><div class="stage-grid"><div class="stage"><strong>1. Preview</strong>Complete</div><div class="stage"><strong>2. Production Approval</strong>{% if job.status == 'production_approved' or job.status == 'sliced' %}Recorded{% else %}Required{% endif %}</div><div class="stage"><strong>3. Offline Slice</strong>{% if job.status == 'sliced' %}Complete{% else %}Not requested{% endif %}</div><div class="stage"><strong>4. Remote Observation</strong>{% if job.remote_status %}{% if job.remote_status.connected %}Read-only check completed {{ job.remote_status.checked_at }}{% else %}{{ job.remote_status.message }}{% endif %}{% else %}Not checked{% endif %}</div></div><p class="muted">Slicer, printer, and remote options remain separate. Previewing cannot trigger them.</p>{% if job.status == 'preview_ready' %}<form method="post" action="{{ url_for('approve_production', job_id=job.job_id) }}"><label><input name="braille_and_tactile_reviewed" type="checkbox" value="yes" required>I reviewed the Braille and source-derived tactile design for this job.</label><label class="field-label" for="confirm-job">Type the saved job ID to approve this production package</label><input id="confirm-job" name="confirm_job_id" autocomplete="off" required><button type="submit">Record Production Approval</button></form>{% elif job.status == 'production_approved' %}<form method="post" action="{{ url_for('slice_job', job_id=job.job_id) }}"><p class="muted">This runs the pinned OrcaSlicer profile locally. It does not upload or start a print.</p><button type="submit">Slice Locally for SV07</button></form>{% elif job.status == 'sliced' %}<p class="muted">Offline package created. It has not been uploaded or started.</p><ul class="links">{% for name in job.production.artifacts %}<li><a href="{{ url_for('production_artifact', job_id=job.job_id, name=name) }}">{{ name }}</a></li>{% endfor %}</ul>{% endif %}{% if job.remote_status and job.remote_status.connected %}<p class="muted">Klipper: {{ job.remote_status.klipper_state }} · Print: {{ job.remote_status.print_state }}{% if job.remote_status.filename %} · {{ job.remote_status.filename }}{% endif %}{% if job.remote_status.progress is not none %} · {{ job.remote_status.progress }}%{% endif %}</p>{% endif %}<form method="post" action="{{ url_for('refresh_remote_status', job_id=job.job_id) }}"><button type="submit">Check Remote Status (Read-only)</button></form></article>
          <article class="card-panel"><h3>Saved Artifacts</h3><ul class="links">{% for name in job.artifacts %}<li><a href="{{ url_for('artifact', job_id=job.job_id, name=name) }}">{{ name }}</a></li>{% endfor %}</ul></article>
        </section>
      {% else %}
        <section class="panel output draft-output" aria-labelledby="output-title"><div class="output-head"><div><h2 id="output-title">Live Card Draft</h2><p>Updates stay in this browser until you create the local preview.</p></div><span class="kicker">Output</span></div><div class="draft-grid"><article class="draft-card" aria-label="Live visual card draft"><div id="draft-art" class="draft-art" data-empty="true"><img id="draft-artwork" alt="Selected artwork preview" hidden></div><div class="draft-copy"><p id="draft-greeting" class="draft-greeting">Front greeting</p><p id="draft-message" class="draft-message">Back message</p></div></article><aside class="draft-note"><span class="kicker">Draft only</span><h3>Visual layout</h3><p class="muted">This is a visual composition aid for the 3 × 4 inch portrait card. It is not a tactile interpretation or UEB proof.</p><p class="muted">Create Local Preview to generate the saved visual, tactile, and Grade 1 UEB review artifacts.</p></aside></div></section>
      {% endif %}
    </div>
  </main>
  <script>
    (() => {
      const form = document.getElementById("studio-form");
      const image = document.getElementById("image");
      const greeting = document.getElementById("greeting");
      const message = document.getElementById("message");
      const artwork = document.getElementById("draft-artwork");
      const artFrame = document.getElementById("draft-art");
      const draftGreeting = document.getElementById("draft-greeting");
      const draftMessage = document.getElementById("draft-message");
      if (!form || !image || !greeting || !message || !artwork || !artFrame || !draftGreeting || !draftMessage) return;

      let objectUrl = null;
      const updateText = () => {
        draftGreeting.textContent = greeting.value.trim() || "Front greeting";
        draftMessage.textContent = message.value.trim() || "Back message";
      };
      const updateArtwork = () => {
        const file = image.files && image.files[0];
        if (objectUrl) URL.revokeObjectURL(objectUrl);
        objectUrl = null;
        if (!file || !file.type.startsWith("image/")) {
          artwork.hidden = true;
          artwork.removeAttribute("src");
          artFrame.dataset.empty = "true";
          return;
        }
        objectUrl = URL.createObjectURL(file);
        artwork.src = objectUrl;
        artwork.hidden = false;
        artFrame.dataset.empty = "false";
      };
      greeting.addEventListener("input", updateText);
      message.addEventListener("input", updateText);
      image.addEventListener("change", updateArtwork);
      window.addEventListener("beforeunload", () => { if (objectUrl) URL.revokeObjectURL(objectUrl); });
      updateText();
    })();
  </script>
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
        SLICER_ROOT=os.environ.get("ORCA_SLICER_ROOT"),
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
                    "production_approval": None,
                    "production": None,
                    "action_message": None,
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

    @app.post("/jobs/<job_id>/production-approval")
    def approve_production(job_id: str):
        root = Path(app.config["JOBS_ROOT"])
        job = _load_job(root, job_id)
        if job.get("status") != "preview_ready":
            abort(409)
        if request.form.get("braille_and_tactile_reviewed") != "yes" or request.form.get("confirm_job_id") != job_id:
            job["action_message"] = "Production approval was not recorded. Review the artifacts and enter this job ID exactly."
        else:
            job["status"] = "production_approved"
            job["production_approval"] = {"approved_at": _utc_now(), "job_id_confirmation": job_id}
            job["action_message"] = "Production approval recorded. Local slicing is now available."
        _write_job(_job_path(root, job_id), job)
        return redirect(url_for("show_job", job_id=job_id))

    @app.post("/jobs/<job_id>/slice")
    def slice_job(job_id: str):
        root = Path(app.config["JOBS_ROOT"])
        job_dir = _job_path(root, job_id)
        job = _load_job(root, job_id)
        if job.get("status") != "production_approved":
            abort(409)
        production_dir = job_dir / "production"
        if production_dir.exists():
            job["action_message"] = "A production package already exists for this job. Create a new preview to revise it."
            _write_job(job_dir, job)
            return redirect(url_for("show_job", job_id=job_id))
        try:
            slicer_root = Path(app.config["SLICER_ROOT"]) if app.config["SLICER_ROOT"] else None
            generate_package(
                job_dir / job["input"]["filename"], job_dir / "card.json", production_dir,
                slicer_root=slicer_root,
            )
            manifest = json.loads((production_dir / "manifest.json").read_text(encoding="utf-8"))
            artifacts = sorted(name for name in PRODUCTION_ARTIFACT_NAMES if (production_dir / name).is_file())
            job["status"] = "sliced"
            job["production"] = {
                "sliced_at": _utc_now(),
                "artifacts": artifacts,
                "safety": manifest["printer_interaction"],
            }
            job["action_message"] = "Offline SV07 slice completed. No upload or print start occurred."
        except Exception:
            shutil.rmtree(production_dir, ignore_errors=True)
            job["action_message"] = "Offline slicing failed. Review the local slicer setup and retry this approved job."
        _write_job(job_dir, job)
        return redirect(url_for("show_job", job_id=job_id))

    @app.get("/jobs/<job_id>/production/<name>")
    def production_artifact(job_id: str, name: str):
        job = _load_job(Path(app.config["JOBS_ROOT"]), job_id)
        if name not in job.get("production", {}).get("artifacts", []):
            abort(404)
        return send_from_directory(_job_path(Path(app.config["JOBS_ROOT"]), job_id) / "production", name)

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
