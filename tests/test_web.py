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
    assert b"Preview only" in response.data
    assert b"No printer contacted" in response.data


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
    assert b"not yet human-reviewed" in response.data
    job_files = list((tmp_path / "jobs").glob("*/job.json"))
    assert len(job_files) == 1
    assert '"status": "preview_ready"' in job_files[0].read_text(encoding="utf-8")


def test_validation_error_does_not_create_job(client, tmp_path: Path) -> None:
    response = client.post(
        "/jobs",
        data={"greeting": "", "message": "", "image": (io.BytesIO(b""), "")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"Select an image" in response.data
    assert not (tmp_path / "jobs").exists()


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
