from __future__ import annotations
import base64
import os
import time
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]


def _secret(name: str, default: str | None = None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)


def configured() -> bool:
    return bool(_secret("GITHUB_TOKEN") and _secret("GITHUB_REPO"))


def repo() -> str:
    return _secret("GITHUB_REPO", "andreapoi/GOT")


def branch() -> str:
    return _secret("GITHUB_BRANCH", "main")


def _headers():
    token = _secret("GITHUB_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def read_text(path: str) -> str:
    if not configured():
        return (ROOT / path).read_text(encoding="utf-8")

    url = f"https://api.github.com/repos/{repo()}/contents/{path}"
    r = requests.get(url, headers=_headers(), params={"ref": branch()}, timeout=20)
    r.raise_for_status()
    payload = r.json()
    return base64.b64decode(payload["content"]).decode("utf-8")


def _remote(path: str):
    url = f"https://api.github.com/repos/{repo()}/contents/{path}"
    r = requests.get(url, headers=_headers(), params={"ref": branch()}, timeout=20)
    if r.status_code == 404:
        return None, None
    r.raise_for_status()
    data = r.json()
    return url, data["sha"]


def write_text(path: str, content: str, message: str, retries: int = 4):
    if not configured():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return

    for attempt in range(retries):
        url, sha = _remote(path)
        if url is None:
            url = f"https://api.github.com/repos/{repo()}/contents/{path}"

        body = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch(),
        }
        if sha:
            body["sha"] = sha

        r = requests.put(url, headers=_headers(), json=body, timeout=20)
        if r.status_code in (200, 201):
            return
        if r.status_code in (409, 422) and attempt < retries - 1:
            time.sleep(0.4 * (attempt + 1))
            continue
        r.raise_for_status()

    raise RuntimeError(f"Impossibile salvare {path}")
