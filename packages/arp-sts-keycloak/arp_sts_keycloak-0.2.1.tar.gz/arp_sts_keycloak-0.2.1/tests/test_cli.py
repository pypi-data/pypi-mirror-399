from __future__ import annotations

from pathlib import Path

from arp_sts_keycloak import cli


def test_init_writes_assets(tmp_path: Path) -> None:
    code = cli.main(["init", "--output", str(tmp_path)])
    assert code == 0

    for name in cli.ASSET_FILES:
        target = tmp_path / name
        assert target.exists()
        assert target.read_text(encoding="utf-8")


def test_init_refuses_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "docker-compose.yml"
    target.write_text("original", encoding="utf-8")

    code = cli.main(["init", "--output", str(tmp_path)])
    assert code == 1
    assert target.read_text(encoding="utf-8") == "original"
    assert not (tmp_path / "realm-export.json").exists()


def test_init_force_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "docker-compose.yml"
    target.write_text("original", encoding="utf-8")

    code = cli.main(["init", "--output", str(tmp_path), "--force"])
    assert code == 0
    assert "services:" in target.read_text(encoding="utf-8")
