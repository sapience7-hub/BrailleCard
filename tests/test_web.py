from __future__ import annotations

import io
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.fixture()
def client(tmp_path: Path):
    from braille_card.web import create_app

    app = create_app({"TESTING": True, "JOBS_ROOT": tmp_path / "jobs"})
    return app.test_client()


def test_home_shows_local_preview_form(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert b"Create a Tactile Card Preview" in response.data
    assert b"Safety boundary" in response.data
    assert b"never uploads or starts a printer job" in response.data


def test_preview_job_persists_generated_artifacts(client, tmp_path: Path, monkeypatch) -> None:
    from braille_card import web

    def fake_generate_preview(image: Path, card: Path, output: Path) -> Path:
        output.mkdir()
        (output / "visual_preview.png").write_bytes(b"preview")
        (output / "tactile_preview.png").write_bytes(b"tactile")
        (output / "braille_review.html").write_text("<h1>Review</h1>", encoding="utf-8")
        (output / "render_manifest.json").write_text(
            '{"human_review":{"braille":"not yet human-reviewed"},"printer_interaction":{"contacted_printer":false,"submitted_to_printer":false,"print_started":false}}',
            encoding="utf-8",
        )
        return output

    monkeypatch.setattr(web, "generate_preview", fake_generate_preview)
    response = client.post(
        "/jobs",
        data={
            "image": (io.BytesIO(b"image"), "card.png"),
            "greeting": "With love",
            "message": "You make every day bright.",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Preview Ready" in response.data
    job_files = list((tmp_path / "jobs").glob("*/job.json"))
    assert len(job_files) == 1
    stored = job_files[0].read_text(encoding="utf-8")
    assert '"status": "preview_ready"' in stored
    assert '"braille_review": "not yet human-reviewed"' in stored


def test_validation_error_does_not_create_job(client, tmp_path: Path) -> None:
    response = client.post(
        "/jobs",
        data={"greeting": "", "message": "", "image": (io.BytesIO(b""), "")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"Select an image" in response.data
    assert not (tmp_path / "jobs").exists()


def test_remote_status_is_an_explicit_read_only_action(client, tmp_path: Path, monkeypatch) -> None:
    from braille_card import web

    job_id = "f" * 36
    job_dir = tmp_path / "jobs" / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "job.json").write_text(
        '{"job_id":"' + job_id + '","artifacts":[],"remote_status":null}', encoding="utf-8"
    )

    class FakeMoonraker:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def read_status(self):
            return {
                "webhooks": {"state": "ready"},
                "print_stats": {"state": "standby", "filename": ""},
                "virtual_sdcard": {"progress": 0},
            }

    monkeypatch.setattr(web, "MoonrakerClient", FakeMoonraker)
    app = client.application
    app.config["MOONRAKER_URL"] = "http://printer.local"

    response = client.post(f"/jobs/{job_id}/remote-status", follow_redirects=True)

    assert response.status_code == 200
    assert b"Klipper: ready" in response.data
    assert b"Print: standby" in response.data
    stored = (job_dir / "job.json").read_text(encoding="utf-8")
    assert '"connected": true' in stored


def test_remote_status_does_not_connect_without_local_configuration(client, tmp_path: Path) -> None:
    job_id = "e" * 36
    job_dir = tmp_path / "jobs" / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "job.json").write_text(
        '{"job_id":"' + job_id + '","artifacts":[],"remote_status":null}', encoding="utf-8"
    )

    response = client.post(f"/jobs/{job_id}/remote-status", follow_redirects=True)

    assert response.status_code == 200
    assert b"not configured" in response.data


def test_production_approval_requires_checkbox_and_exact_job_id(client, tmp_path: Path) -> None:
    job_id = "a" * 36
    job_dir = tmp_path / "jobs" / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "job.json").write_text(
        '{"job_id":"' + job_id + '","artifacts":[],"status":"preview_ready","remote_status":null}',
        encoding="utf-8",
    )

    rejected = client.post(
        f"/jobs/{job_id}/production-approval",
        data={"braille_and_tactile_reviewed": "yes", "confirm_job_id": "wrong"},
        follow_redirects=True,
    )
    assert b"was not recorded" in rejected.data
    assert '"status": "preview_ready"' in (job_dir / "job.json").read_text(encoding="utf-8")

    approved = client.post(
        f"/jobs/{job_id}/production-approval",
        data={"braille_and_tactile_reviewed": "yes", "confirm_job_id": job_id},
        follow_redirects=True,
    )
    assert b"Local slicing is now available" in approved.data
    assert '"status": "production_approved"' in (job_dir / "job.json").read_text(encoding="utf-8")


def test_offline_slice_requires_approval_and_never_contacts_printer(client, tmp_path: Path, monkeypatch) -> None:
    from braille_card import web

    job_id = "b" * 36
    job_dir = tmp_path / "jobs" / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "card.png").write_bytes(b"image")
    (job_dir / "card.json").write_text('{"greeting":"Hi","message":"Hello"}', encoding="utf-8")
    (job_dir / "job.json").write_text(
        '{"job_id":"' + job_id + '","artifacts":[],"status":"preview_ready","input":{"filename":"card.png"},"remote_status":null}',
        encoding="utf-8",
    )

    def fake_generate_package(image: Path, card: Path, output: Path, *, slicer_root) -> Path:
        assert image == job_dir / "card.png"
        assert card == job_dir / "card.json"
        assert slicer_root is None
        output.mkdir()
        (output / "card.gcode").write_text("; local gcode", encoding="utf-8")
        (output / "manifest.json").write_text(
            '{"printer_interaction":{"gcode_generated_offline":true,"submitted_to_printer":false,"print_started":false}}',
            encoding="utf-8",
        )
        return output

    monkeypatch.setattr(web, "generate_package", fake_generate_package)
    assert client.post(f"/jobs/{job_id}/slice").status_code == 409

    client.post(
        f"/jobs/{job_id}/production-approval",
        data={"braille_and_tactile_reviewed": "yes", "confirm_job_id": job_id},
    )
    response = client.post(f"/jobs/{job_id}/slice", follow_redirects=True)
    assert b"Offline SV07 slice completed" in response.data
    stored = (job_dir / "job.json").read_text(encoding="utf-8")
    assert '"status": "sliced"' in stored
    assert '"submitted_to_printer": false' in stored


def test_cli_exposes_local_web_server_help() -> None:
    repository = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "braille_card", "--help"],
        cwd=repository,
        env={"PYTHONPATH": str(repository / "src")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--serve" in result.stdout


def test_cli_accepts_serve_without_generator_inputs() -> None:
    repository = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "braille_card", "--serve", "--port", "invalid"],
        cwd=repository,
        env={"PYTHONPATH": str(repository / "src")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "invalid int value" in result.stderr
