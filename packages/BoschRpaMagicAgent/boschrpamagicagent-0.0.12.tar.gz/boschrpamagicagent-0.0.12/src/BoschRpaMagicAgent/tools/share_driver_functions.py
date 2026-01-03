import datetime
import io
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import smbclient
from browser_use import ActionResult


# -------------------------
# Shared Helpers (LLM-friendly)
# -------------------------

def _json_dumps(payload: Dict[str, Any]) -> str:
    """Serialize payload to compact JSON string for LLM consumption."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _normalize_remote_relative_path(remote_relative_path: str) -> str:
    """Normalize a remote path relative to the SMB share and block traversal.

    - Converts backslashes to slashes
    - Removes leading slashes to keep it share-relative
    - Blocks '..' to prevent path traversal
    """
    normalized = (remote_relative_path or "").strip().replace("\\", "/").lstrip("/")
    if ".." in normalized.split("/"):
        raise ValueError("Invalid remote_relative_path: path traversal is not allowed ('..').")
    return normalized


def _build_unc_path(server_host: str, share_name: str, remote_relative_path: str) -> str:
    """Build SMB UNC path: //server/share/path."""
    remote_relative_path = _normalize_remote_relative_path(remote_relative_path)
    return f"//{server_host}/{share_name}/{remote_relative_path}"


def _format_epoch_seconds_to_iso(epoch_seconds: Optional[float]) -> str:
    """Format epoch seconds to ISO string, return empty string if not available."""
    if not epoch_seconds:
        return ""
    try:
        return datetime.datetime.fromtimestamp(epoch_seconds).isoformat()
    except Exception:
        return ""


def _ensure_local_parent_directory(local_file_path: str) -> None:
    """Create local parent directory if needed (safe local operation)."""
    parent_dir = os.path.dirname(os.path.abspath(local_file_path))
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)


def _register_smb_session(
    server_host: str,
    username: str,
    password: str,
    server_port: int,
    connection_cache: Dict[str, Any],
) -> None:
    """Register SMB session with explicit connection cache to allow cleanup."""
    smbclient.register_session(
        server_host,
        username=username,
        password=password,
        port=int(server_port),
        encrypt=True,
        connection_cache=connection_cache,
    )


def _cleanup_smb_cache(connection_cache: Dict[str, Any]) -> None:
    """Reset SMB connection cache safely."""
    try:
        smbclient.reset_connection_cache(connection_cache=connection_cache)
    except Exception:
        pass


def _action_ok(operation: str, payload: Dict[str, Any], memory: str) -> ActionResult:
    payload = {"status": "ok", "operation": operation, **payload}
    return ActionResult(extracted_content=_json_dumps(payload), long_term_memory=memory)


def _action_error(operation: str, error_type: str, payload: Dict[str, Any], memory: str) -> ActionResult:
    payload = {"status": "error", "operation": operation, "error_type": error_type, **payload}
    return ActionResult(extracted_content=_json_dumps(payload), long_term_memory=memory)


# -------------------------
# File Metadata / Existence
# -------------------------

def smb_get_remote_file_metadata(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    remote_relative_file_path: str,
    server_port: int = 445,
) -> ActionResult:
    """Get SMB remote file metadata (existence + size + modified time).

    This tool is low-risk (read-only). It does NOT download file content.

    Args:
        username: SMB username.
        password: SMB password.
        server_host: SMB server host, e.g. "szh0fs06.apac.bosch.com".
        share_name: SMB share name, e.g. "GS_ACC_CN$".
        remote_relative_file_path: File path relative to the share root, e.g. "folder/report.xlsx".
        server_port: SMB port, usually 445.

    Returns:
        ActionResult.extracted_content JSON fields:
            - exists: true/false
            - unc_path: full UNC path
            - remote_relative_file_path: normalized relative path
            - size_bytes: file size (if exists)
            - modified_time_iso: ISO timestamp (if exists)
    """
    connection_cache: Dict[str, Any] = {}
    try:
        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_path = _normalize_remote_relative_path(remote_relative_file_path)
        unc_path = _build_unc_path(server_host, share_name, normalized_path)

        try:
            stat_result = smbclient.stat(unc_path, connection_cache=connection_cache)
            return _action_ok(
                operation="smb_get_remote_file_metadata",
                payload={
                    "exists": True,
                    "server_host": server_host,
                    "share_name": share_name,
                    "remote_relative_file_path": normalized_path,
                    "unc_path": unc_path,
                    "size_bytes": getattr(stat_result, "st_size", None),
                    "modified_time_iso": _format_epoch_seconds_to_iso(getattr(stat_result, "st_mtime", None)),
                },
                memory=f"SMB file exists: {unc_path}",
            )
        except FileNotFoundError:
            return _action_ok(
                operation="smb_get_remote_file_metadata",
                payload={
                    "exists": False,
                    "server_host": server_host,
                    "share_name": share_name,
                    "remote_relative_file_path": normalized_path,
                    "unc_path": unc_path,
                },
                memory=f"SMB file not found: {unc_path}",
            )

    except PermissionError as e:
        return _action_error(
            operation="smb_get_remote_file_metadata",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB permission error while stat file: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    except Exception as e:
        return _action_error(
            operation="smb_get_remote_file_metadata",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB error while stat file: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    finally:
        _cleanup_smb_cache(connection_cache)


# -------------------------
# File Copy (Remote <-> Local)
# -------------------------

def smb_download_remote_file_to_local(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    remote_relative_file_path: str,
    local_file_path: str,
    server_port: int = 445,
    overwrite_existing: bool = False,
    chunk_size_bytes: int = 1024 * 1024,
) -> ActionResult:
    """Copy a remote SMB file to a local file path (remote -> local).

    Args:
        username: SMB username.
        password: SMB password.
        server_host: SMB server host.
        share_name: SMB share name.
        remote_relative_file_path: Remote file path relative to share.
        local_file_path: Destination local file path.
        server_port: SMB port, usually 445.
        overwrite_existing: If False and local file exists, return error without overwriting.
        chunk_size_bytes: Streaming chunk size for copying.

    Returns:
        ActionResult.extracted_content JSON fields:
            - unc_path
            - local_file_path
            - bytes_written
            - expected_size_bytes (from stat)
            - modified_time_iso
    """
    connection_cache: Dict[str, Any] = {}
    try:
        local_file_path = os.path.abspath(local_file_path)
        if os.path.exists(local_file_path) and not overwrite_existing:
            return _action_error(
                operation="smb_download_remote_file_to_local",
                error_type="local_exists",
                payload={"local_file_path": local_file_path, "overwrite_existing": overwrite_existing},
                memory=f"Local file exists (no overwrite): {local_file_path}",
            )

        _ensure_local_parent_directory(local_file_path)

        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_path = _normalize_remote_relative_path(remote_relative_file_path)
        unc_path = _build_unc_path(server_host, share_name, normalized_path)

        # stat first for clear not_found + metadata
        stat_result = smbclient.stat(unc_path, connection_cache=connection_cache)
        expected_size = getattr(stat_result, "st_size", None)
        modified_time_iso = _format_epoch_seconds_to_iso(getattr(stat_result, "st_mtime", None))

        bytes_written = 0
        with smbclient.open_file(unc_path, mode="rb", connection_cache=connection_cache) as remote_file:
            with open(local_file_path, mode="wb") as local_file:
                while True:
                    chunk = remote_file.read(chunk_size_bytes)
                    if not chunk:
                        break
                    local_file.write(chunk)
                    bytes_written += len(chunk)

        return _action_ok(
            operation="smb_download_remote_file_to_local",
            payload={
                "server_host": server_host,
                "share_name": share_name,
                "remote_relative_file_path": normalized_path,
                "unc_path": unc_path,
                "local_file_path": local_file_path,
                "bytes_written": bytes_written,
                "expected_size_bytes": expected_size,
                "modified_time_iso": modified_time_iso,
                "overwrite_existing": overwrite_existing,
            },
            memory=f"Downloaded SMB->local: {unc_path} -> {local_file_path}",
        )

    except FileNotFoundError:
        return _action_error(
            operation="smb_download_remote_file_to_local",
            error_type="not_found",
            payload={
                "server_host": server_host,
                "share_name": share_name,
                "remote_relative_file_path": remote_relative_file_path,
                "local_file_path": os.path.abspath(local_file_path),
            },
            memory=f"SMB file not found for download: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    except PermissionError as e:
        return _action_error(
            operation="smb_download_remote_file_to_local",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB permission error while download: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    except Exception as e:
        return _action_error(
            operation="smb_download_remote_file_to_local",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB error while download: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    finally:
        _cleanup_smb_cache(connection_cache)


def smb_upload_local_file_to_remote(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    local_file_path: str,
    remote_relative_file_path: str,
    server_port: int = 445,
    overwrite_existing: bool = False,
    chunk_size_bytes: int = 1024 * 1024,
) -> ActionResult:
    """Copy a local file to SMB remote path (local -> remote).

    This is a "copy" operation. No rename/move/delete operations are provided.
    Default behavior is low-risk: it will NOT overwrite an existing remote file unless overwrite_existing=True.

    Args:
        username: SMB username.
        password: SMB password.
        server_host: SMB server host.
        share_name: SMB share name.
        local_file_path: Source local file path.
        remote_relative_file_path: Destination path relative to share.
        server_port: SMB port, usually 445.
        overwrite_existing: If False and remote exists, return error without overwriting.
        chunk_size_bytes: Streaming chunk size for copying.

    Returns:
        ActionResult.extracted_content JSON fields:
            - local_file_path
            - unc_path
            - bytes_written
            - overwrite_existing
    """
    connection_cache: Dict[str, Any] = {}
    try:
        local_file_path = os.path.abspath(local_file_path)
        if not os.path.isfile(local_file_path):
            return _action_error(
                operation="smb_upload_local_file_to_remote",
                error_type="local_missing",
                payload={"local_file_path": local_file_path},
                memory=f"Local file missing: {local_file_path}",
            )

        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_path = _normalize_remote_relative_path(remote_relative_file_path)
        unc_path = _build_unc_path(server_host, share_name, normalized_path)

        if not overwrite_existing:
            try:
                smbclient.stat(unc_path, connection_cache=connection_cache)
                return _action_error(
                    operation="smb_upload_local_file_to_remote",
                    error_type="remote_exists",
                    payload={
                        "local_file_path": local_file_path,
                        "unc_path": unc_path,
                        "overwrite_existing": overwrite_existing,
                    },
                    memory=f"Remote exists (no overwrite): {unc_path}",
                )
            except FileNotFoundError:
                pass

        bytes_written = 0
        with open(local_file_path, mode="rb") as local_file:
            with smbclient.open_file(unc_path, mode="wb", connection_cache=connection_cache) as remote_file:
                while True:
                    chunk = local_file.read(chunk_size_bytes)
                    if not chunk:
                        break
                    remote_file.write(chunk)
                    bytes_written += len(chunk)

        return _action_ok(
            operation="smb_upload_local_file_to_remote",
            payload={
                "server_host": server_host,
                "share_name": share_name,
                "local_file_path": local_file_path,
                "remote_relative_file_path": normalized_path,
                "unc_path": unc_path,
                "bytes_written": bytes_written,
                "overwrite_existing": overwrite_existing,
            },
            memory=f"Uploaded local->SMB: {local_file_path} -> {unc_path}",
        )

    except PermissionError as e:
        return _action_error(
            operation="smb_upload_local_file_to_remote",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB permission error while upload: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    except Exception as e:
        return _action_error(
            operation="smb_upload_local_file_to_remote",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB error while upload: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    finally:
        _cleanup_smb_cache(connection_cache)


def smb_upload_bytesio_to_remote_file(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    remote_relative_file_path: str,
    file_bytes_buffer: io.BytesIO,
    server_port: int = 445,
    overwrite_existing: bool = False,
    chunk_size_bytes: int = 1024 * 1024,
) -> ActionResult:
    """Upload a BytesIO buffer to SMB remote file path (BytesIO -> remote file).

    Notes:
        - LLM should NOT handle raw bytes directly. This tool is intended for programmatic usage.
        - For LLM workflows, prefer: save BytesIO to a local temp file, then call smb_upload_local_file_to_remote.

    Args:
        username: SMB username.
        password: SMB password.
        server_host: SMB server host.
        share_name: SMB share name.
        remote_relative_file_path: Destination path relative to share.
        file_bytes_buffer: BytesIO holding file content.
        server_port: SMB port, usually 445.
        overwrite_existing: If False and remote exists, return error without overwriting.
        chunk_size_bytes: Streaming chunk size for copying.

    Returns:
        ActionResult with structured JSON.
    """
    connection_cache: Dict[str, Any] = {}
    try:
        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_path = _normalize_remote_relative_path(remote_relative_file_path)
        unc_path = _build_unc_path(server_host, share_name, normalized_path)

        if not overwrite_existing:
            try:
                smbclient.stat(unc_path, connection_cache=connection_cache)
                return _action_error(
                    operation="smb_upload_bytesio_to_remote_file",
                    error_type="remote_exists",
                    payload={"unc_path": unc_path, "overwrite_existing": overwrite_existing},
                    memory=f"Remote exists (no overwrite): {unc_path}",
                )
            except FileNotFoundError:
                pass

        bytes_written = 0
        file_bytes_buffer.seek(0)

        with smbclient.open_file(unc_path, mode="wb", connection_cache=connection_cache) as remote_file:
            while True:
                chunk = file_bytes_buffer.read(chunk_size_bytes)
                if not chunk:
                    break
                remote_file.write(chunk)
                bytes_written += len(chunk)

        return _action_ok(
            operation="smb_upload_bytesio_to_remote_file",
            payload={
                "server_host": server_host,
                "share_name": share_name,
                "remote_relative_file_path": normalized_path,
                "unc_path": unc_path,
                "bytes_written": bytes_written,
                "overwrite_existing": overwrite_existing,
            },
            memory=f"Uploaded BytesIO->SMB: {unc_path}",
        )

    except PermissionError as e:
        return _action_error(
            operation="smb_upload_bytesio_to_remote_file",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB permission error while upload BytesIO: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    except Exception as e:
        return _action_error(
            operation="smb_upload_bytesio_to_remote_file",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB error while upload BytesIO: {server_host}/{share_name}/{remote_relative_file_path}",
        )
    finally:
        _cleanup_smb_cache(connection_cache)


# -------------------------
# Folder / Directory Operations (read-only traversal + optional mkdir)
# -------------------------

def smb_get_remote_folder_metadata(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    remote_relative_folder_path: str,
    server_port: int = 445,
) -> ActionResult:
    """Check whether a remote folder exists and return basic metadata (read-only).

    Args:
        username: SMB username.
        password: SMB password.
        server_host: SMB server host.
        share_name: SMB share name.
        remote_relative_folder_path: Folder path relative to share.
        server_port: SMB port.

    Returns:
        JSON fields:
            - exists: true/false
            - is_directory: true/false
            - unc_path
    """
    connection_cache: Dict[str, Any] = {}
    try:
        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_path = _normalize_remote_relative_path(remote_relative_folder_path).rstrip("/")
        unc_path = f"//{server_host}/{share_name}/{normalized_path}"

        try:
            stat_result = smbclient.stat(unc_path, connection_cache=connection_cache)
            is_directory = bool(getattr(stat_result, "st_file_attributes", 0) & 0x10)
            return _action_ok(
                operation="smb_get_remote_folder_metadata",
                payload={
                    "exists": True,
                    "is_directory": is_directory,
                    "server_host": server_host,
                    "share_name": share_name,
                    "remote_relative_folder_path": normalized_path,
                    "unc_path": unc_path,
                },
                memory=f"SMB folder checked: {unc_path}",
            )
        except FileNotFoundError:
            return _action_ok(
                operation="smb_get_remote_folder_metadata",
                payload={
                    "exists": False,
                    "is_directory": False,
                    "server_host": server_host,
                    "share_name": share_name,
                    "remote_relative_folder_path": normalized_path,
                    "unc_path": unc_path,
                },
                memory=f"SMB folder not found: {unc_path}",
            )

    except PermissionError as e:
        return _action_error(
            operation="smb_get_remote_folder_metadata",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB permission error while stat folder: {server_host}/{share_name}/{remote_relative_folder_path}",
        )
    except Exception as e:
        return _action_error(
            operation="smb_get_remote_folder_metadata",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB error while stat folder: {server_host}/{share_name}/{remote_relative_folder_path}",
        )
    finally:
        _cleanup_smb_cache(connection_cache)


def smb_list_remote_folder_entries(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    remote_relative_folder_path: str,
    server_port: int = 445,
    include_hidden_temporary_files: bool = False,
    max_entries: int = 200,
) -> ActionResult:
    """List files and folders under a remote SMB folder (read-only).

    The output is intentionally simplified to keep LLM context small.

    Args:
        username: SMB username.
        password: SMB password.
        server_host: SMB server host.
        share_name: SMB share name.
        remote_relative_folder_path: Folder path relative to share.
        server_port: SMB port.
        include_hidden_temporary_files: If False, skip entries like "~$xxx" or "."/"..".
        max_entries: Maximum number of entries to return.

    Returns:
        JSON fields:
            - entries: list of {name, entry_type, size_bytes, modified_time_iso}
            - unc_path
            - truncated: true/false
    """
    connection_cache: Dict[str, Any] = {}
    try:
        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_folder = _normalize_remote_relative_path(remote_relative_folder_path).rstrip("/")
        unc_folder_path = f"//{server_host}/{share_name}/{normalized_folder}"

        entries: List[Dict[str, Any]] = []
        for entry in smbclient.scandir(unc_folder_path, connection_cache=connection_cache):
            name = entry.name
            if not include_hidden_temporary_files:
                if name in (".", "..") or name.startswith("~$"):
                    continue

            stat_result = entry.stat()
            entry_type = "folder" if entry.is_dir() else "file" if entry.is_file() else "unknown"
            entries.append({
                "name": name,
                "entry_type": entry_type,
                "size_bytes": getattr(stat_result, "st_size", None),
                "modified_time_iso": _format_epoch_seconds_to_iso(getattr(stat_result, "st_mtime", None)),
            })

            if len(entries) >= max_entries:
                break

        truncated = len(entries) >= max_entries
        return _action_ok(
            operation="smb_list_remote_folder_entries",
            payload={
                "server_host": server_host,
                "share_name": share_name,
                "remote_relative_folder_path": normalized_folder,
                "unc_path": unc_folder_path,
                "entries": entries,
                "truncated": truncated,
                "max_entries": max_entries,
            },
            memory=f"Listed SMB folder: {unc_folder_path} (entries={len(entries)})",
        )

    except FileNotFoundError:
        return _action_error(
            operation="smb_list_remote_folder_entries",
            error_type="not_found",
            payload={
                "server_host": server_host,
                "share_name": share_name,
                "remote_relative_folder_path": remote_relative_folder_path,
            },
            memory=f"SMB folder not found for listing: {server_host}/{share_name}/{remote_relative_folder_path}",
        )
    except PermissionError as e:
        return _action_error(
            operation="smb_list_remote_folder_entries",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB permission error while listing folder: {server_host}/{share_name}/{remote_relative_folder_path}",
        )
    except Exception as e:
        return _action_error(
            operation="smb_list_remote_folder_entries",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB error while listing folder: {server_host}/{share_name}/{remote_relative_folder_path}",
        )
    finally:
        _cleanup_smb_cache(connection_cache)


def smb_create_remote_folder(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    remote_relative_folder_path: str,
    server_port: int = 445,
) -> ActionResult:
    """Create a remote SMB folder (non-destructive).

    Notes:
        - This is a write operation (mkdir). If your SMB_SHARED_DRIVER policy is copy-only,
          you can choose NOT to register this tool for the agent.

    Args:
        username: SMB username.
        password: SMB password.
        server_host: SMB server host.
        share_name: SMB share name.
        remote_relative_folder_path: Folder path relative to share.
        server_port: SMB port.

    Returns:
        JSON fields:
            - created: true/false
            - unc_path
    """
    connection_cache: Dict[str, Any] = {}
    try:
        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_folder = _normalize_remote_relative_path(remote_relative_folder_path).rstrip("/")
        unc_folder_path = f"//{server_host}/{share_name}/{normalized_folder}"

        smbclient.makedirs(unc_folder_path, connection_cache=connection_cache, exist_ok=True)

        return _action_ok(
            operation="smb_create_remote_folder",
            payload={
                "created": True,
                "server_host": server_host,
                "share_name": share_name,
                "remote_relative_folder_path": normalized_folder,
                "unc_path": unc_folder_path,
            },
            memory=f"Created SMB folder: {unc_folder_path}",
        )

    except PermissionError as e:
        return _action_error(
            operation="smb_create_remote_folder",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB permission error while creating folder: {server_host}/{share_name}/{remote_relative_folder_path}",
        )
    except Exception as e:
        return _action_error(
            operation="smb_create_remote_folder",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory=f"SMB error while creating folder: {server_host}/{share_name}/{remote_relative_folder_path}",
        )
    finally:
        _cleanup_smb_cache(connection_cache)


# -------------------------
# Remote-to-Remote Copy (streaming, no BytesIO)
# -------------------------

def smb_copy_remote_file_to_remote(
    username: str,
    password: str,
    source_server_host: str,
    source_share_name: str,
    source_remote_relative_file_path: str,
    destination_server_host: str,
    destination_share_name: str,
    destination_remote_relative_file_path: str,
    server_port: int = 445,
    overwrite_existing: bool = False,
    chunk_size_bytes: int = 1024 * 1024,
) -> ActionResult:
    """Copy a remote SMB file to another SMB location (remote -> remote).

    This avoids returning BytesIO and streams data from source to destination.

    Args:
        username: SMB username.
        password: SMB password.
        source_server_host: Source SMB server host.
        source_share_name: Source share name.
        source_remote_relative_file_path: Source file relative path.
        destination_server_host: Destination SMB server host.
        destination_share_name: Destination share name.
        destination_remote_relative_file_path: Destination file relative path.
        server_port: SMB port.
        overwrite_existing: If False and destination exists, return error.
        chunk_size_bytes: Streaming chunk size.

    Returns:
        JSON fields:
            - source_unc_path
            - destination_unc_path
            - bytes_copied
    """
    source_cache: Dict[str, Any] = {}
    destination_cache: Dict[str, Any] = {}
    try:
        _register_smb_session(source_server_host, username, password, server_port, source_cache)
        _register_smb_session(destination_server_host, username, password, server_port, destination_cache)

        source_relative = _normalize_remote_relative_path(source_remote_relative_file_path)
        destination_relative = _normalize_remote_relative_path(destination_remote_relative_file_path)

        source_unc = _build_unc_path(source_server_host, source_share_name, source_relative)
        destination_unc = _build_unc_path(destination_server_host, destination_share_name, destination_relative)

        # Verify source exists
        smbclient.stat(source_unc, connection_cache=source_cache)

        # Low-risk: default no overwrite
        if not overwrite_existing:
            try:
                smbclient.stat(destination_unc, connection_cache=destination_cache)
                return _action_error(
                    operation="smb_copy_remote_file_to_remote",
                    error_type="destination_exists",
                    payload={"destination_unc_path": destination_unc, "overwrite_existing": overwrite_existing},
                    memory=f"Destination exists (no overwrite): {destination_unc}",
                )
            except FileNotFoundError:
                pass

        bytes_copied = 0
        with smbclient.open_file(source_unc, mode="rb", connection_cache=source_cache) as source_file:
            with smbclient.open_file(destination_unc, mode="wb", connection_cache=destination_cache) as destination_file:
                while True:
                    chunk = source_file.read(chunk_size_bytes)
                    if not chunk:
                        break
                    destination_file.write(chunk)
                    bytes_copied += len(chunk)

        return _action_ok(
            operation="smb_copy_remote_file_to_remote",
            payload={
                "source_unc_path": source_unc,
                "destination_unc_path": destination_unc,
                "bytes_copied": bytes_copied,
                "overwrite_existing": overwrite_existing,
            },
            memory=f"Copied SMB remote->remote: {source_unc} -> {destination_unc}",
        )

    except FileNotFoundError:
        return _action_error(
            operation="smb_copy_remote_file_to_remote",
            error_type="source_not_found",
            payload={
                "source_server_host": source_server_host,
                "source_share_name": source_share_name,
                "source_remote_relative_file_path": source_remote_relative_file_path,
            },
            memory=f"Source SMB file not found: {source_server_host}/{source_share_name}/{source_remote_relative_file_path}",
        )
    except PermissionError as e:
        return _action_error(
            operation="smb_copy_remote_file_to_remote",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory="SMB permission error during remote->remote copy",
        )
    except Exception as e:
        return _action_error(
            operation="smb_copy_remote_file_to_remote",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory="SMB error during remote->remote copy",
        )
    finally:
        _cleanup_smb_cache(source_cache)
        _cleanup_smb_cache(destination_cache)


def smb_copy_remote_folder_to_remote(
    username: str,
    password: str,
    source_server_host: str,
    source_share_name: str,
    source_remote_relative_folder_path: str,
    destination_server_host: str,
    destination_share_name: str,
    destination_remote_relative_folder_path: str,
    server_port: int = 445,
    overwrite_existing_files: bool = False,
    max_total_entries: int = 2000,
) -> ActionResult:
    """Recursively copy a remote SMB folder to another SMB folder (remote folder -> remote folder).

    Notes:
        - This operation may be expensive for large folders.
        - For LLM safety, we limit the total number of entries copied via max_total_entries.

    Args:
        username: SMB username.
        password: SMB password.
        source_server_host: Source server host.
        source_share_name: Source share name.
        source_remote_relative_folder_path: Source folder relative path.
        destination_server_host: Destination server host.
        destination_share_name: Destination share name.
        destination_remote_relative_folder_path: Destination folder relative path.
        server_port: SMB port.
        overwrite_existing_files: If True, overwrite destination files when copying.
        max_total_entries: Safety limit to avoid copying huge folder trees.

    Returns:
        JSON fields:
            - source_unc_path
            - destination_unc_path
            - files_copied
            - folders_created
            - truncated: whether stopped due to max_total_entries
    """
    source_cache: Dict[str, Any] = {}
    destination_cache: Dict[str, Any] = {}
    files_copied = 0
    folders_created = 0
    processed_entries = 0
    truncated = False

    try:
        _register_smb_session(source_server_host, username, password, server_port, source_cache)
        _register_smb_session(destination_server_host, username, password, server_port, destination_cache)

        source_folder_rel = _normalize_remote_relative_path(source_remote_relative_folder_path).rstrip("/")
        dest_folder_rel = _normalize_remote_relative_path(destination_remote_relative_folder_path).rstrip("/")

        source_unc_folder = f"//{source_server_host}/{source_share_name}/{source_folder_rel}"
        dest_unc_folder = f"//{destination_server_host}/{destination_share_name}/{dest_folder_rel}"

        # Ensure destination folder exists (mkdir is non-destructive)
        smbclient.makedirs(dest_unc_folder, connection_cache=destination_cache, exist_ok=True)
        folders_created += 1

        def _copy_folder_recursive(current_source_unc: str, current_dest_unc: str) -> None:
            nonlocal files_copied, folders_created, processed_entries, truncated

            for entry in smbclient.scandir(current_source_unc, connection_cache=source_cache):
                if entry.name in (".", "..") or entry.name.startswith("~$"):
                    continue

                processed_entries += 1
                if processed_entries > max_total_entries:
                    truncated = True
                    return

                entry_source_unc = f"{current_source_unc}/{entry.name}"
                entry_dest_unc = f"{current_dest_unc}/{entry.name}"

                if entry.is_dir():
                    smbclient.makedirs(entry_dest_unc, connection_cache=destination_cache, exist_ok=True)
                    folders_created += 1
                    _copy_folder_recursive(entry_source_unc, entry_dest_unc)
                    if truncated:
                        return
                elif entry.is_file():
                    # Stream file copy
                    if not overwrite_existing_files:
                        try:
                            smbclient.stat(entry_dest_unc, connection_cache=destination_cache)
                            # Skip existing
                            continue
                        except FileNotFoundError:
                            pass

                    with smbclient.open_file(entry_source_unc, mode="rb", connection_cache=source_cache) as sf:
                        with smbclient.open_file(entry_dest_unc, mode="wb", connection_cache=destination_cache) as df:
                            while True:
                                chunk = sf.read(1024 * 1024)
                                if not chunk:
                                    break
                                df.write(chunk)
                    files_copied += 1

        # Verify source exists and is directory
        source_stat = smbclient.stat(source_unc_folder, connection_cache=source_cache)
        is_directory = bool(getattr(source_stat, "st_file_attributes", 0) & 0x10)
        if not is_directory:
            return _action_error(
                operation="smb_copy_remote_folder_to_remote",
                error_type="source_not_directory",
                payload={"source_unc_path": source_unc_folder},
                memory=f"Source path is not a directory: {source_unc_folder}",
            )

        _copy_folder_recursive(source_unc_folder, dest_unc_folder)

        return _action_ok(
            operation="smb_copy_remote_folder_to_remote",
            payload={
                "source_unc_path": source_unc_folder,
                "destination_unc_path": dest_unc_folder,
                "files_copied": files_copied,
                "folders_created": folders_created,
                "processed_entries": processed_entries,
                "max_total_entries": max_total_entries,
                "truncated": truncated,
                "overwrite_existing_files": overwrite_existing_files,
            },
            memory=f"Copied SMB folder remote->remote: {source_unc_folder} -> {dest_unc_folder}",
        )

    except FileNotFoundError:
        return _action_error(
            operation="smb_copy_remote_folder_to_remote",
            error_type="source_not_found",
            payload={
                "source_server_host": source_server_host,
                "source_share_name": source_share_name,
                "source_remote_relative_folder_path": source_remote_relative_folder_path,
            },
            memory=f"Source SMB folder not found: {source_server_host}/{source_share_name}/{source_remote_relative_folder_path}",
        )
    except PermissionError as e:
        return _action_error(
            operation="smb_copy_remote_folder_to_remote",
            error_type="permission",
            payload={"error_message": str(e)[:300]},
            memory="SMB permission error during folder remote->remote copy",
        )
    except Exception as e:
        return _action_error(
            operation="smb_copy_remote_folder_to_remote",
            error_type="unknown",
            payload={"error_message": str(e)[:300]},
            memory="SMB error during folder remote->remote copy",
        )
    finally:
        _cleanup_smb_cache(source_cache)
        _cleanup_smb_cache(destination_cache)


# -------------------------
# Optional: BytesIO reader (NOT recommended for LLM, restricted)
# -------------------------

def smb_read_remote_file_to_bytesio(
    username: str,
    password: str,
    server_host: str,
    share_name: str,
    remote_relative_file_path: str,
    server_port: int = 445,
    max_bytes_to_read: int = 2 * 1024 * 1024,
) -> Tuple[ActionResult, Optional[io.BytesIO]]:
    """Read a remote SMB file into a BytesIO buffer (restricted).

    Warning:
        This is usually NOT suitable for LLM workflows because it produces binary data.
        Use smb_download_remote_file_to_local instead.

    Safety:
        - max_bytes_to_read prevents loading huge files into memory.

    Returns:
        (ActionResult, BytesIO or None)
        ActionResult.extracted_content includes metadata and how many bytes were read.
    """
    connection_cache: Dict[str, Any] = {}
    try:
        _register_smb_session(server_host, username, password, server_port, connection_cache)

        normalized_path = _normalize_remote_relative_path(remote_relative_file_path)
        unc_path = _build_unc_path(server_host, share_name, normalized_path)

        stat_result = smbclient.stat(unc_path, connection_cache=connection_cache)
        size_bytes = getattr(stat_result, "st_size", None)

        if size_bytes is not None and size_bytes > max_bytes_to_read:
            return (
                _action_error(
                    operation="smb_read_remote_file_to_bytesio",
                    error_type="too_large",
                    payload={"unc_path": unc_path, "size_bytes": size_bytes, "max_bytes_to_read": max_bytes_to_read},
                    memory=f"SMB read blocked (too large): {unc_path}",
                ),
                None,
            )

        buffer = io.BytesIO()
        bytes_read = 0
        with smbclient.open_file(unc_path, mode="rb", connection_cache=connection_cache) as remote_file:
            while True:
                chunk = remote_file.read(256 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)
                bytes_read += len(chunk)
                if bytes_read > max_bytes_to_read:
                    return (
                        _action_error(
                            operation="smb_read_remote_file_to_bytesio",
                            error_type="too_large",
                            payload={"unc_path": unc_path, "bytes_read": bytes_read, "max_bytes_to_read": max_bytes_to_read},
                            memory=f"SMB read blocked mid-stream (too large): {unc_path}",
                        ),
                        None,
                    )

        buffer.seek(0)
        return (
            _action_ok(
                operation="smb_read_remote_file_to_bytesio",
                payload={
                    "unc_path": unc_path,
                    "size_bytes": size_bytes,
                    "bytes_read": bytes_read,
                    "max_bytes_to_read": max_bytes_to_read,
                },
                memory=f"Read SMB file to BytesIO: {unc_path}",
            ),
            buffer,
        )

    except FileNotFoundError:
        return (
            _action_error(
                operation="smb_read_remote_file_to_bytesio",
                error_type="not_found",
                payload={"server_host": server_host, "share_name": share_name, "remote_relative_file_path": remote_relative_file_path},
                memory=f"SMB file not found: {server_host}/{share_name}/{remote_relative_file_path}",
            ),
            None,
        )
    except PermissionError as e:
        return (
            _action_error(
                operation="smb_read_remote_file_to_bytesio",
                error_type="permission",
                payload={"error_message": str(e)[:300]},
                memory="SMB permission error during BytesIO read",
            ),
            None,
        )
    except Exception as e:
        return (
            _action_error(
                operation="smb_read_remote_file_to_bytesio",
                error_type="unknown",
                payload={"error_message": str(e)[:300]},
                memory="SMB error during BytesIO read",
            ),
            None,
        )
    finally:
        _cleanup_smb_cache(connection_cache)
