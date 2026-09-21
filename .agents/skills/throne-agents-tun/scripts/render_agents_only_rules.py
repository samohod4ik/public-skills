"""Render an Agents-only Throne route profile. Never writes throne.db."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_families import (
    FAMILIES,
    FAMILY_IDS,
    FORBIDDEN_PROCESS_NAMES,
    OUTBOUND_DIRECT,
    OUTBOUND_PROXY,
    PATH_ONLY_PROCESS_NAMES,
    PROFILE_NAME,
    is_codex_chatgpt_path,
    is_cursor_agent_node_path,
    is_devin_language_server_path,
    regex_allows_language_server,
    should_emit_process_name,
)


def empty_json_list() -> str:
    return "[]"


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _norm_name(name: str) -> str:
    return Path(name).name


def reject_broad_process(name: str) -> None:
    base = _norm_name(name)
    if base in FORBIDDEN_PROCESS_NAMES or base.lower() == "node.exe":
        raise ValueError(
            f"Refusing broad process matcher {name!r}. "
            "Match a resolved agent helper path/regex instead of node.exe."
        )
    if not should_emit_process_name(base) or base in PATH_ONLY_PROCESS_NAMES:
        raise ValueError(
            f"Refusing process-name matcher {name!r}. "
            "Qualify ChatGPT.exe under OpenAI.Codex and "
            "language_server_windows_x64.exe under extensions\\windsurf\\bin."
        )


def reject_broad_path(path: str) -> None:
    text = path.replace("/", "\\").rstrip("\\")
    lowered = text.lower()
    if lowered.endswith("\\appdata\\local") or lowered.endswith("%localappdata%"):
        raise ValueError(f"Refusing directory-only path matcher {path!r}")
    if not Path(path).suffix:
        raise ValueError(f"Refusing path without executable suffix: {path!r}")
    if lowered.endswith("node.exe"):
        if not is_cursor_agent_node_path(path):
            raise ValueError(
                f"Refusing node.exe path {path!r}. Only cursor-agent versioned node is allowed."
            )
    if lowered.endswith("chatgpt.exe") and not is_codex_chatgpt_path(path):
        raise ValueError(
            f"Refusing ChatGPT.exe path {path!r} outside OpenAI.Codex."
        )
    if lowered.endswith("language_server_windows_x64.exe") and not is_devin_language_server_path(
        path
    ):
        raise ValueError(
            f"Refusing language_server path {path!r} outside extensions\\windsurf\\bin."
        )


def _rule(
    order: int,
    name: str,
    type_id: int,
    outbound_id: int,
    **fields,
) -> dict:
    row = {
        "rule_order": order,
        "name": name,
        "type": type_id,
        "protocol": fields.get("protocol", ""),
        "action": fields.get("action", "route"),
        "ip_is_private": fields.get("ip_is_private", 0),
        "ip_cidr_json": fields.get("ip_cidr_json", empty_json_list()),
        "domain_json": fields.get("domain_json", empty_json_list()),
        "domain_suffix_json": fields.get("domain_suffix_json", empty_json_list()),
        "domain_keyword_json": fields.get("domain_keyword_json", empty_json_list()),
        "process_name_json": fields.get("process_name_json", empty_json_list()),
        "process_path_json": fields.get("process_path_json", empty_json_list()),
        "process_path_regex_json": fields.get("process_path_regex_json", empty_json_list()),
        "outbound_id": outbound_id,
    }
    return row


def _json_arr(items: list[str]) -> str:
    return json.dumps(list(items), ensure_ascii=True)


def load_json(path: Path | None) -> dict:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def baseline_direct_rules() -> list[dict]:
    return [
        _rule(
            0,
            "Route DNS",
            0,
            OUTBOUND_DIRECT,
            protocol="dns",
            action="hijack-dns",
        ),
        _rule(1, "Private IPs", 2, OUTBOUND_DIRECT, ip_is_private=1),
        _rule(
            2,
            "LAN CIDRs",
            2,
            OUTBOUND_DIRECT,
            ip_cidr_json=_json_arr(
                ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16"]
            ),
        ),
    ]


def allowlist_rules(allowlist: dict, start_order: int) -> list[dict]:
    rules: list[dict] = []
    order = start_order
    extra_cidrs = _as_list(allowlist.get("cidrs"))
    suffixes = _as_list(allowlist.get("suffixes"))
    hosts = _as_list(allowlist.get("hosts"))
    keywords = _as_list(allowlist.get("keywords"))
    if extra_cidrs:
        rules.append(
            _rule(
                order,
                "Allowlist extra CIDRs",
                2,
                OUTBOUND_DIRECT,
                ip_cidr_json=_json_arr(extra_cidrs),
            )
        )
        order += 1
    if suffixes:
        rules.append(
            _rule(
                order,
                "Allowlist suffixes",
                2,
                OUTBOUND_DIRECT,
                domain_suffix_json=_json_arr(suffixes),
            )
        )
        order += 1
    if hosts:
        rules.append(
            _rule(
                order,
                "Allowlist hosts",
                2,
                OUTBOUND_DIRECT,
                domain_json=_json_arr(hosts),
            )
        )
        order += 1
    if keywords:
        rules.append(
            _rule(
                order,
                "Allowlist keywords",
                2,
                OUTBOUND_DIRECT,
                domain_keyword_json=_json_arr(keywords),
            )
        )
        order += 1
    return rules


def reject_broad_regex(regex: str) -> None:
    lowered = regex.lower().replace("\\", "")
    if "node.exe" in lowered and "cursor-agent" not in lowered:
        raise ValueError(
            f"Refusing node.exe regex without cursor-agent: {regex!r}"
        )
    if "chatgpt.exe" in lowered and "openai.codex" not in lowered:
        raise ValueError(
            f"Refusing ChatGPT.exe regex without OpenAI.Codex: {regex!r}"
        )
    collapsed = lowered.replace("/", "")
    if (
        "language_server_windows_x64.exe" in collapsed
        and not regex_allows_language_server(regex)
    ):
        raise ValueError(
            f"Refusing language_server regex without extensions/windsurf/bin: {regex!r}"
        )


def _family_payload(discovered: dict, family_id: str) -> dict:
    families = discovered.get("families") or discovered
    payload = families.get(family_id) or {}
    catalog = FAMILIES[family_id]
    names = _as_list(payload.get("process_names"))
    paths = _as_list(payload.get("process_paths"))
    regexes = list(_as_list(payload.get("path_regexes")))
    present = bool(names or paths or regexes)
    if payload.get("include_catalog_regexes", True) and present:
        for item in catalog["path_regexes"]:
            if item not in regexes:
                regexes.append(item)
    return {"process_names": names, "process_paths": paths, "path_regexes": regexes}


def family_has_path_evidence(payload: dict) -> bool:
    return bool(payload["process_paths"] or payload["path_regexes"])


def proxy_rules_for_families(discovered: dict, start_order: int) -> list[dict]:
    rules: list[dict] = []
    order = start_order
    missing_path = []
    for family_id in FAMILY_IDS:
        payload = _family_payload(discovered, family_id)
        names = payload["process_names"]
        paths = payload["process_paths"]
        regexes = payload["path_regexes"]
        if not (names or paths or regexes):
            continue
        if names and not family_has_path_evidence(payload):
            missing_path.append(family_id)
            continue
        for name in names:
            reject_broad_process(name)
            rules.append(
                _rule(
                    order,
                    f"{family_id} process name",
                    4,
                    OUTBOUND_PROXY,
                    process_name_json=_json_arr([name]),
                )
            )
            order += 1
        for path in paths:
            reject_broad_path(path)
            rules.append(
                _rule(
                    order,
                    f"{family_id} process path",
                    7,
                    OUTBOUND_PROXY,
                    process_path_json=_json_arr([path]),
                )
            )
            order += 1
        for regex in regexes:
            reject_broad_regex(regex)
            rules.append(
                _rule(
                    order,
                    f"{family_id} process regex",
                    0,
                    OUTBOUND_PROXY,
                    process_path_regex_json=_json_arr([regex]),
                )
            )
            order += 1
    if missing_path:
        raise ValueError(
            "Process-name proxy rules require a path or regex for: "
            + ", ".join(missing_path)
        )
    return rules


def render_profile(discovered: dict, allowlist: dict | None = None) -> dict:
    allowlist = allowlist or {}
    rules = baseline_direct_rules()
    rules.extend(allowlist_rules(allowlist, start_order=len(rules)))
    rules.extend(proxy_rules_for_families(discovered, start_order=len(rules)))
    covered = sorted(
        {
            (r["name"].split(" ", 1)[0])
            for r in rules
            if r["outbound_id"] == OUTBOUND_PROXY
        }
    )
    return {
        "profile_name": PROFILE_NAME,
        "default_outbound_id": OUTBOUND_DIRECT,
        "rules": rules,
        "covered_families": covered,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovered", type=Path, required=True)
    parser.add_argument("--allowlist", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    discovered = load_json(args.discovered)
    allowlist = load_json(args.allowlist)
    profile = render_profile(discovered, allowlist)
    if not profile["covered_families"]:
        print(
            "warning: no agent families in profile; everything stays direct",
            file=sys.stderr,
        )
    text = json.dumps(profile, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
