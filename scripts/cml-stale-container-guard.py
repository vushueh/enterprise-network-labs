#!/usr/bin/env python3
"""Detect and repair CML Docker containers that outlive their CML node state.

This protects against the CML failure mode where the UI/API reports a Docker-
backed node as STOPPED, but Docker still has a running container with the node
UUID as its name. Starting the node then fails with "container already running".
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def api_request(method, base_url, path, token=None, payload=None, timeout=30):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif method in {"PUT", "POST"}:
        data = b""
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=data,
        headers=headers,
        method=method,
    )
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            if not body:
                return resp.status, None
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
        return err.code, {"error": body}


def authenticate(base_url, username, password):
    status, body = api_request(
        "POST",
        base_url,
        "/authenticate",
        payload={"username": username, "password": password},
    )
    if status >= 300:
        raise RuntimeError(f"CML auth failed: HTTP {status}: {body}")
    if isinstance(body, str):
        token = body.strip('"')
    elif isinstance(body, dict):
        token = body.get("token") or body.get("id") or body.get("access_token")
    else:
        token = None
    if not token:
        raise RuntimeError(f"CML auth did not return a token: {body!r}")
    return token


def find_lab(base_url, token, lab_id, lab_title):
    if lab_id:
        return lab_id

    status, lab_ids = api_request("GET", base_url, "/labs?show_all=true", token=token)
    if status >= 300:
        raise RuntimeError(f"Could not list labs: HTTP {status}: {lab_ids}")
    for candidate in lab_ids:
        status, detail = api_request("GET", base_url, f"/labs/{candidate}", token=token)
        if status >= 300 or not isinstance(detail, dict):
            continue
        names = {
            str(detail.get("lab_title", "")),
            str(detail.get("title", "")),
            str(detail.get("name", "")),
        }
        if lab_title in names:
            return candidate

    raise RuntimeError(f"Could not find lab titled {lab_title!r}")


def get_nodes(base_url, token, lab_id):
    status, node_ids = api_request("GET", base_url, f"/labs/{lab_id}/nodes", token=token)
    if status >= 300:
        raise RuntimeError(f"Could not list lab nodes: HTTP {status}: {node_ids}")

    nodes = []
    for node_id in node_ids:
        status, node = api_request(
            "GET", base_url, f"/labs/{lab_id}/nodes/{node_id}", token=token
        )
        if status >= 300:
            print(f"WARN: could not read node {node_id}: HTTP {status}: {node}", file=sys.stderr)
            continue
        if isinstance(node, dict):
            node["id"] = node.get("id") or node_id
            nodes.append(node)
    return nodes


def get_system_orphans(base_url, token):
    status, stats = api_request("GET", base_url, "/system_stats", token=token)
    if status >= 300 or not isinstance(stats, dict):
        return None

    total = 0
    running = 0
    computes = stats.get("computes") or {}
    for compute in computes.values():
        dominfo = ((compute or {}).get("stats") or {}).get("dominfo") or {}
        total += int(dominfo.get("total_orphans") or 0)
        running += int(dominfo.get("running_orphans") or 0)
    return {"total_orphans": total, "running_orphans": running}


def docker_command(args, allow_sudo):
    command = ["docker", *args]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode == 0 or not allow_sudo or os.geteuid() == 0:
        return result
    sudo_result = subprocess.run(
        ["sudo", "-n", "docker", *args],
        text=True,
        capture_output=True,
        check=False,
    )
    return sudo_result


def running_docker_node_ids(allow_sudo=True):
    result = docker_command(["ps", "--format", "{{.Names}}"], allow_sudo)
    if result.returncode != 0:
        raise RuntimeError(
            "Could not query Docker. Run this on the CML controller with sudo, "
            f"or ensure the user can run docker. stderr: {result.stderr.strip()}"
        )
    names = set()
    for raw in result.stdout.splitlines():
        name = raw.strip().lstrip("/")
        if UUID_RE.match(name):
            names.add(name)
    return names


def stop_container(node_id, allow_sudo=True):
    result = docker_command(["stop", node_id], allow_sudo)
    if result.returncode != 0:
        raise RuntimeError(f"docker stop {node_id} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect or repair stale CML Docker containers for a lab."
    )
    parser.add_argument("--base-url", default="https://127.0.0.1/api/v0")
    parser.add_argument("--username", default=os.environ.get("CML_USERNAME"))
    parser.add_argument("--password-env", default="CML_PASSWORD")
    parser.add_argument("--lab-id")
    parser.add_argument("--lab-title", default="Enterprise-network-labs")
    parser.add_argument(
        "--target-label",
        action="append",
        default=[],
        help="Only inspect this node label. Can be repeated.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Stop stale Docker containers and start those nodes again through CML.",
    )
    parser.add_argument(
        "--no-start",
        action="store_true",
        help="With --fix, stop stale containers but do not start the nodes again.",
    )
    parser.add_argument(
        "--no-sudo",
        action="store_true",
        help="Do not try sudo -n docker if plain docker fails.",
    )
    parser.add_argument("--poll-seconds", type=int, default=90)
    return parser.parse_args()


def main():
    args = parse_args()
    username = args.username or input("CML username: ").strip()
    password = os.environ.get(args.password_env)
    if not password:
        password = getpass.getpass("CML password: ")

    token = authenticate(args.base_url, username, password)
    lab_id = find_lab(args.base_url, token, args.lab_id, args.lab_title)
    nodes = get_nodes(args.base_url, token, lab_id)
    running_ids = running_docker_node_ids(allow_sudo=not args.no_sudo)
    orphan_stats = get_system_orphans(args.base_url, token)

    targets = set(args.target_label)
    stale = []
    for node in nodes:
        node_id = node.get("id")
        label = node.get("label") or node_id
        state = node.get("state")
        if targets and label not in targets:
            continue
        if state == "STOPPED" and node_id in running_ids:
            stale.append({"id": node_id, "label": label, "state": state})

    print(f"Lab: {args.lab_title} ({lab_id})")
    if orphan_stats:
        print(
            "CML orphan counters: "
            f"total={orphan_stats['total_orphans']} "
            f"running={orphan_stats['running_orphans']}"
        )

    if not stale:
        print("No stale CML Docker containers found.")
        return 0

    print("Stale containers found:")
    for item in stale:
        print(f"- {item['label']} {item['id']} is STOPPED in CML but running in Docker")

    if not args.fix:
        print("No changes made. Re-run with --fix to repair.")
        return 2

    print("Repairing stale containers:")
    for item in stale:
        stopped = stop_container(item["id"], allow_sudo=not args.no_sudo)
        print(f"- stopped Docker container for {item['label']}: {stopped}")

    if args.no_start:
        print("Skipped CML node start because --no-start was supplied.")
        return 0

    for item in stale:
        status, body = api_request(
            "PUT",
            args.base_url,
            f"/labs/{lab_id}/nodes/{item['id']}/state/start",
            token=token,
            timeout=60,
        )
        if status >= 300:
            print(f"- failed to start {item['label']}: HTTP {status}: {body}")
        else:
            print(f"- start requested for {item['label']}")

    deadline = time.time() + args.poll_seconds
    wanted = {item["id"]: item["label"] for item in stale}
    while time.time() < deadline:
        remaining = []
        for node_id, label in wanted.items():
            status, body = api_request(
                "GET", args.base_url, f"/labs/{lab_id}/nodes/{node_id}/state", token=token
            )
            state = body.get("state") if isinstance(body, dict) else body
            print(f"poll {label}: {state}")
            if state not in {"STARTED", "BOOTED"}:
                remaining.append(node_id)
        if not remaining:
            print("Repair complete.")
            return 0
        time.sleep(5)

    print("Timed out waiting for repaired nodes to start.")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
