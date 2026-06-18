# CML stale-container guard

## Problem

CML can occasionally report a Docker-backed node as `STOPPED` while the backing
Docker container is still running on the controller. When that happens, starting
the node from the UI can fail with:

```text
container already running
```

This was confirmed in `Enterprise-network-labs` on 2026-06-18 for:

- `HQ-TACACS`
- `EXT-WEB1`

`BR-DSW1` had a normal node-state issue and recovered with a targeted CML
stop/start.

## Guard script

Use:

```bash
sudo /usr/local/sbin/cml-stale-container-guard --username leonel
```

The script prompts for the CML password. It does not store credentials.

Check-only mode is the default. It exits with:

- `0` when no stale containers are found.
- `2` when stale containers are found but no fix was requested.
- `3` if repair was attempted but nodes did not start before timeout.

To repair:

```bash
sudo /usr/local/sbin/cml-stale-container-guard --username leonel --fix
```

To limit repair to the known Docker-backed support nodes:

```bash
sudo /usr/local/sbin/cml-stale-container-guard --username leonel --fix \
  --target-label HQ-TACACS \
  --target-label EXT-WEB1
```

## Safety rule

The script only stops a Docker container when both conditions are true:

1. CML API says the node state is `STOPPED`.
2. Docker shows a running container whose name exactly matches that node UUID.

It does not wipe the lab, delete containers, or touch healthy nodes.

## Manual recovery path

If the script is not available:

1. SSH to the CML OS shell, not the console server:

   ```bash
   ssh -p 1122 leonel@192.168.10.177
   ```

2. Confirm the stale containers:

   ```bash
   sudo docker ps --format '{{.Names}} {{.Status}} {{.Image}}'
   ```

3. Stop only the stale containers whose CML node state is `STOPPED`.

4. Start those nodes from the CML UI or CML API.

Do not use lab wipe for this condition.
