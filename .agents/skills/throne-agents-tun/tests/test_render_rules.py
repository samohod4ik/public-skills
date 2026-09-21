from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from agent_families import FAMILY_IDS, OUTBOUND_DIRECT, OUTBOUND_PROXY, PROFILE_NAME
from render_agents_only_rules import render_profile


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_render_includes_four_families_and_direct_default() -> None:
    profile = render_profile(_load("discovered_processes.json"), _load("allowlist.json"))
    assert profile["profile_name"] == PROFILE_NAME
    assert profile["default_outbound_id"] == OUTBOUND_DIRECT
    assert set(profile["covered_families"]) == set(FAMILY_IDS)
    rules = profile["rules"]
    assert rules[0]["action"] == "hijack-dns"
    assert rules[0]["outbound_id"] == OUTBOUND_DIRECT
    proxy_rules = [r for r in rules if r["outbound_id"] == OUTBOUND_PROXY]
    direct_rules = [r for r in rules if r["outbound_id"] == OUTBOUND_DIRECT]
    assert direct_rules[-1]["rule_order"] < proxy_rules[0]["rule_order"]
    names = " ".join(r["process_name_json"] for r in proxy_rules)
    assert "node.exe" not in names
    assert "ChatGPT.exe" not in names
    assert "language_server_windows_x64.exe" not in names
    assert any("OpenAI.Codex" in r["process_path_json"] for r in proxy_rules)
    assert any("windsurf" in r["process_path_json"] for r in proxy_rules)
    assert any("language_server_windows_x64" in r["process_path_regex_json"] for r in proxy_rules)
    assert any(".example.test" in r["domain_suffix_json"] for r in rules)


def test_empty_discovery_does_not_invent_families() -> None:
    profile = render_profile({"families": {}}, {})
    assert profile["covered_families"] == []
    assert all(r["outbound_id"] == OUTBOUND_DIRECT for r in profile["rules"])


def test_cursor_only_discovery_does_not_add_other_families() -> None:
    discovered = {
        "families": {
            "cursor": {
                "process_names": ["Cursor.exe"],
                "process_paths": [
                    "C:\\Users\\fixture\\AppData\\Local\\Programs\\cursor\\Cursor.exe"
                ],
            }
        }
    }
    profile = render_profile(discovered, {})
    assert set(profile["covered_families"]) == {"cursor"}
    blob = json.dumps(profile)
    assert "claude" not in blob
    assert "codex" not in blob
    assert "devin" not in blob


def test_name_without_path_is_rejected() -> None:
    discovered = {
        "families": {
            "cursor": {
                "process_names": ["Cursor.exe"],
                "process_paths": [],
                "path_regexes": [],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="path or regex"):
        render_profile(discovered, {})


def test_bare_node_process_name_rejected() -> None:
    discovered = {
        "families": {
            "cursor": {
                "process_names": ["node.exe"],
                "process_paths": [
                    "C:\\Users\\fixture\\AppData\\Local\\Programs\\cursor\\Cursor.exe"
                ],
                "path_regexes": [],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="node.exe"):
        render_profile(discovered, {})


def test_program_files_node_path_rejected() -> None:
    discovered = {
        "families": {
            "cursor": {
                "process_names": ["Cursor.exe"],
                "process_paths": ["C:\\Program Files\\nodejs\\node.exe"],
                "path_regexes": ["(?i)Cursor\\.exe$"],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="node.exe"):
        render_profile(discovered, {})


def test_chatgpt_regex_rejected() -> None:
    discovered = {
        "families": {
            "codex": {
                "process_names": ["codex.exe"],
                "process_paths": [
                    "C:\\Users\\fixture\\AppData\\Local\\Programs\\OpenAI\\Codex\\bin\\codex.exe"
                ],
                "path_regexes": [r"(?i)ChatGPT\.exe$"],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="ChatGPT.exe"):
        render_profile(discovered, {})


def test_catalog_regexes_are_unioned_not_replaced() -> None:
    discovered = {
        "families": {
            "codex": {
                "process_names": ["codex.exe"],
                "process_paths": [
                    "C:\\Users\\fixture\\AppData\\Local\\Programs\\OpenAI\\Codex\\bin\\codex.exe"
                ],
                "path_regexes": [r"(?i)OpenAI[\\/]Codex[\\/]bin[\\/]codex\.exe$"],
            }
        }
    }
    profile = render_profile(discovered, {})
    regex_blob = " ".join(
        r["process_path_regex_json"] for r in profile["rules"] if r["process_path_regex_json"] != "[]"
    )
    assert "packages" in regex_blob
    assert "OpenAI.Codex" in regex_blob or "OpenAI\\\\.Codex" in regex_blob


def test_chatgpt_process_name_rejected() -> None:
    discovered = {
        "families": {
            "codex": {
                "process_names": ["ChatGPT.exe"],
                "process_paths": [
                    "C:\\Program Files\\WindowsApps\\OpenAI.Codex_1.0.0_x64__fixture\\app\\ChatGPT.exe"
                ],
                "path_regexes": [],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="ChatGPT.exe"):
        render_profile(discovered, {})


def test_language_server_process_name_rejected() -> None:
    discovered = {
        "families": {
            "devin": {
                "process_names": ["language_server_windows_x64.exe"],
                "process_paths": [
                    "C:\\Users\\fixture\\Devin\\resources\\app\\extensions\\windsurf\\bin\\language_server_windows_x64.exe"
                ],
                "path_regexes": [],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="language_server"):
        render_profile(discovered, {})


def test_language_server_regex_rejected() -> None:
    discovered = {
        "families": {
            "devin": {
                "process_names": ["Devin.exe"],
                "process_paths": ["C:\\Users\\fixture\\Devin\\Devin.exe"],
                "path_regexes": [r"(?i)language_server_windows_x64\.exe$"],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="language_server"):
        render_profile(discovered, {})


def test_language_server_path_outside_windsurf_rejected() -> None:
    discovered = {
        "families": {
            "devin": {
                "process_names": ["Devin.exe"],
                "process_paths": [
                    "C:\\Program Files\\SomeIDE\\language_server_windows_x64.exe"
                ],
                "path_regexes": [],
                "include_catalog_regexes": False,
            }
        }
    }
    with pytest.raises(ValueError, match="language_server"):
        render_profile(discovered, {})


def test_fixture_sqlite_materialize(tmp_path: Path) -> None:
    profile = render_profile(_load("discovered_processes.json"), _load("allowlist.json"))
    db = tmp_path / "throne.db"
    con = sqlite3.connect(db)
    con.execute(
        "CREATE TABLE route_profiles (id INTEGER PRIMARY KEY, name TEXT, default_outbound_id INTEGER)"
    )
    con.execute(
        """
        CREATE TABLE route_rules (
            id INTEGER PRIMARY KEY,
            route_profile_id INTEGER,
            rule_order INTEGER,
            name TEXT,
            type INTEGER,
            protocol TEXT,
            action TEXT,
            ip_is_private INTEGER,
            ip_cidr_json TEXT,
            domain_json TEXT,
            domain_suffix_json TEXT,
            domain_keyword_json TEXT,
            process_name_json TEXT,
            process_path_json TEXT,
            process_path_regex_json TEXT,
            outbound_id INTEGER
        )
        """
    )
    con.execute(
        "INSERT INTO route_profiles(name, default_outbound_id) VALUES (?, ?)",
        (profile["profile_name"], profile["default_outbound_id"]),
    )
    profile_id = con.execute("SELECT id FROM route_profiles").fetchone()[0]
    for rule in profile["rules"]:
        con.execute(
            """
            INSERT INTO route_rules (
                route_profile_id, rule_order, name, type, protocol, action,
                ip_is_private, ip_cidr_json, domain_json, domain_suffix_json,
                domain_keyword_json, process_name_json, process_path_json,
                process_path_regex_json, outbound_id
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                profile_id,
                rule["rule_order"],
                rule["name"],
                rule["type"],
                rule["protocol"],
                rule["action"],
                rule["ip_is_private"],
                rule["ip_cidr_json"],
                rule["domain_json"],
                rule["domain_suffix_json"],
                rule["domain_keyword_json"],
                rule["process_name_json"],
                rule["process_path_json"],
                rule["process_path_regex_json"],
                rule["outbound_id"],
            ),
        )
    con.commit()
    default = con.execute(
        "SELECT default_outbound_id FROM route_profiles WHERE name=?",
        (PROFILE_NAME,),
    ).fetchone()[0]
    assert default == OUTBOUND_DIRECT
    orders = [
        row[0]
        for row in con.execute(
            "SELECT outbound_id FROM route_rules ORDER BY rule_order"
        )
    ]
    first_proxy = orders.index(OUTBOUND_PROXY)
    assert all(item == OUTBOUND_DIRECT for item in orders[:first_proxy])
