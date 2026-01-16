# NOTE: mcp import removed - tool is deprecated (use chromium_portmanteau or browser_bookmarks)
import json
import os
from pathlib import Path
from typing import Any


def _expand(path: str) -> Path:
    return Path(os.path.expandvars(path))


CHROME_BOOKMARK_PATHS = [
    r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks",
    r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default\Bookmarks",
]

EDGE_BOOKMARK_PATHS = [
    r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Bookmarks",
    r"%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Default\Bookmarks",
]

BRAVE_BOOKMARK_PATHS = [
    r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Bookmarks",
    r"%USERPROFILE%\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Bookmarks",
]


def _find_first_existing(paths: list[str]) -> Path | None:
    for p in paths:
        path = _expand(p)
        if path.exists():
            return path
    return None


def _flatten_chromium_tree(node: dict[str, Any], parent: str | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    node_type = node.get("type")
    if node_type == "url":
        items.append(
            {
                "title": node.get("name"),
                "url": node.get("url"),
                "parent": parent,
            }
        )
    elif node_type == "folder":
        name = node.get("name")
        for child in node.get("children", []) or []:
            items.extend(_flatten_chromium_tree(child, parent=name or parent))
    return items


def read_chromium_bookmarks(path: Path | None) -> dict[str, Any]:
    """Read and flatten Chromium-based bookmarks JSON.

    Parameters:
        path: Path to the Bookmarks JSON

    Returns:
        dict: {status, count, bookmarks|error, error_code, context, fix}
    """
    if not path or not path.exists():
        return {
            "status": "error",
            "error_code": "CHROMIUM_FILE_NOT_FOUND",
            "error": f"bookmarks_file missing: {path}",
            "context": {"file_path": str(path) if path else None},
            "fix": "verify browser installed | check file path | ensure file exists",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        roots = data.get("roots", {})
        all_items: list[dict[str, Any]] = []
        for root in ("bookmark_bar", "other", "synced"):
            if root in roots:
                all_items.extend(_flatten_chromium_tree(roots[root]))
        return {"status": "success", "count": len(all_items), "bookmarks": all_items}
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_code": "CHROMIUM_INVALID_JSON",
            "error": f"json_decode_failed: {str(e)}",
            "context": {
                "file_path": str(path),
                "line": getattr(e, "lineno", None),
                "column": getattr(e, "colno", None),
                "exception": type(e).__name__,
            },
            "fix": "validate JSON syntax | check file corruption | restore from backup",
        }
    except Exception as e:
        import traceback

        tb_lines = traceback.format_exc().splitlines()
        return {
            "status": "error",
            "error_code": "CHROMIUM_READ_FAILED",
            "error": f"read_failed: {type(e).__name__}: {str(e)}",
            "context": {
                "file_path": str(path),
                "exception": type(e).__name__,
                "traceback": tb_lines[-3:] if tb_lines else None,
            },
            "fix": "check file permissions | validate file integrity | review traceback",
        }


def _walk_ids(node: dict[str, Any], ids: list[int]) -> None:
    node_id = node.get("id")
    try:
        if isinstance(node_id, str):
            ids.append(int(node_id))
        elif isinstance(node_id, int):
            ids.append(node_id)
    except Exception:
        pass
    for child in node.get("children", []) or []:
        _walk_ids(child, ids)


def _next_id(roots: dict[str, Any]) -> str:
    ids: list[int] = []
    for key in ("bookmark_bar", "other", "synced"):
        node = roots.get(key)
        if isinstance(node, dict):
            _walk_ids(node, ids)
    next_int = (max(ids) + 1) if ids else 1
    return str(next_int)


def write_chromium_bookmark(
    path: Path | None,
    title: str,
    url: str,
    folder: str | None = None,
    allow_duplicates: bool = False,
) -> dict[str, Any]:
    """Append a URL entry to a Chromium Bookmarks file.

    Parameters:
        path: Bookmarks JSON path
        title: Bookmark title
        url: Bookmark URL
        folder: Optional target folder name
        allow_duplicates: If False, skip when URL already exists

    Returns:
        dict: {status, ...}
    """
    if not path or not path.exists():
        return {"status": "error", "message": "Bookmarks file not found"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        roots = data.setdefault("roots", {})

        # pick target folder
        target = roots.get("other") or roots.get("bookmark_bar")
        if folder:
            # try to find a matching folder under 'other' first
            stack = [roots.get("other"), roots.get("bookmark_bar")]
            found = None
            while stack:
                node = stack.pop()
                if isinstance(node, dict) and node.get("type") == "folder":
                    if node.get("name") == folder:
                        found = node
                        break
                    for c in node.get("children", []) or []:
                        stack.append(c)
            if found is not None:
                target = found

        if not isinstance(target, dict):
            return {
                "status": "error",
                "error_code": "CHROMIUM_INVALID_STRUCTURE",
                "error": "invalid_bookmarks_file_structure",
                "context": {
                    "file_path": str(path),
                    "expected": "dict with 'roots' containing 'other' or 'bookmark_bar'",
                },
                "fix": (
                    "validate bookmarks file format | restore from backup | check file corruption"
                ),
            }

        # avoid duplicates
        if not allow_duplicates:
            existing = read_chromium_bookmarks(path).get("bookmarks", [])
            if any(b.get("url") == url for b in existing):
                return {"status": "success", "message": "Duplicate skipped", "duplicate": True}

        node = {
            "type": "url",
            "id": _next_id(roots),
            "name": title or url,
            "url": url,
        }
        target.setdefault("children", []).append(node)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"status": "success", "bookmark": {"title": node["name"], "url": url}}
    except PermissionError as e:
        return {
            "status": "error",
            "error_code": "CHROMIUM_PERMISSION_DENIED",
            "error": f"permission_denied: {str(e)}",
            "context": {
                "file_path": str(path),
                "exception": type(e).__name__,
                "operation": "write",
            },
            "fix": "close browser completely | check file permissions | run elevated",
        }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_code": "CHROMIUM_INVALID_JSON",
            "error": f"json_decode_failed: {str(e)}",
            "context": {
                "file_path": str(path),
                "line": getattr(e, "lineno", None),
                "column": getattr(e, "colno", None),
                "operation": "write",
            },
            "fix": "validate JSON syntax before write | check file corruption",
        }
    except Exception as e:
        import traceback

        tb_lines = traceback.format_exc().splitlines()
        return {
            "status": "error",
            "error_code": "CHROMIUM_WRITE_FAILED",
            "error": f"write_failed: {type(e).__name__}: {str(e)}",
            "context": {
                "file_path": str(path),
                "exception": type(e).__name__,
                "operation": "write",
                "traceback": tb_lines[-3:] if tb_lines else None,
            },
            "fix": "check disk space | validate file integrity | review traceback",
        }


# DEPRECATED: Utility function - use chromium_portmanteau or browser_bookmarks portmanteau instead
async def chromium_roots(path: str | None) -> dict[str, Any]:
    """List root keys from a Chromium Bookmarks JSON file.

    DEPRECATED: This is a utility function. Use chromium_portmanteau or browser_bookmarks instead.

    Parameters:
        path: Path to the Bookmarks JSON (environment variables allowed)

    Returns:
        dict: {status, roots|message}
    """
    p = _expand(path) if path else None
    if not p or not p.exists():
        return {"status": "error", "message": "Bookmarks file not found"}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        roots_obj = data.get("roots") or {}
        roots = list(roots_obj.keys())
        return {"status": "success", "roots": roots}
    except Exception as e:
        return {"status": "error", "message": f"Failed to parse bookmarks: {e}"}


def _find_node_and_parent_by(
    node: dict[str, Any],
    *,
    match_id: str | None = None,
    match_url: str | None = None,
    parent: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    node_type = node.get("type")
    if node_type == "url":
        if (match_id is not None and str(node.get("id")) == str(match_id)) or (
            match_url is not None and node.get("url") == match_url
        ):
            return node, parent
        return None, None
    if node_type == "folder":
        for child in node.get("children", []) or []:
            found, found_parent = _find_node_and_parent_by(
                child, match_id=match_id, match_url=match_url, parent=node
            )
            if found is not None:
                return found, found_parent
    return None, None


def _ensure_folder_path(roots: dict[str, Any], folder_path: str) -> dict[str, Any]:
    """Ensure nested folder path exists under roots['other'] (fallback: bookmark_bar)."""
    parts = [p for p in folder_path.split("/") if p]
    base = roots.get("other") or roots.get("bookmark_bar")
    if not isinstance(base, dict):
        raise ValueError("Invalid bookmarks file structure")
    current = base
    for part in parts:
        children = current.setdefault("children", [])
        next_folder = None
        for c in children:
            if isinstance(c, dict) and c.get("type") == "folder" and c.get("name") == part:
                next_folder = c
                break
        if next_folder is None:
            next_folder = {
                "type": "folder",
                "id": _next_id(roots),
                "name": part,
                "children": [],
            }
            children.append(next_folder)
        current = next_folder
    return current


def edit_chromium_bookmark(
    path: Path | None,
    *,
    id: str | None = None,
    url: str | None = None,
    new_title: str | None = None,
    new_folder: str | None = None,
    allow_duplicates: bool = False,
    create_folders: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Edit a Chromium bookmark: rename title and/or move to folder.

    One of id or url must be provided.
    """
    if not path or not path.exists():
        return {"status": "error", "message": "Bookmarks file not found"}
    if id is None and url is None:
        return {"status": "error", "message": "Must provide id or url"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        roots = data.get("roots", {})
        # search in typical roots
        target_node = None
        parent_node = None
        for root_key in ("bookmark_bar", "other", "synced"):
            root = roots.get(root_key)
            if isinstance(root, dict):
                target_node, parent_node = _find_node_and_parent_by(
                    root, match_id=id, match_url=url
                )
                if target_node is not None:
                    break
        if target_node is None or parent_node is None:
            return {"status": "error", "message": "Bookmark not found"}

        # rename
        if new_title:
            target_node["name"] = new_title

        # move
        if new_folder:
            if not allow_duplicates:
                # prevent duplicate URL in destination
                existing = read_chromium_bookmarks(path).get("bookmarks", [])
                if url:
                    if any(b.get("url") == url for b in existing):
                        # allowed duplicate check is about overall duplicates;
                        # keep behavior consistent
                        pass
            # locate or create destination folder
            if create_folders:
                dest_folder = _ensure_folder_path(roots, new_folder)
            else:
                # try to find an existing folder path exactly
                dest_folder = None
                stack = [roots.get("other"), roots.get("bookmark_bar")]
                while stack:
                    node = stack.pop()
                    if isinstance(node, dict) and node.get("type") == "folder":
                        if node.get("name") == new_folder:
                            dest_folder = node
                            break
                        for c in node.get("children", []) or []:
                            stack.append(c)
                if dest_folder is None:
                    return {"status": "error", "message": "Destination folder not found"}

            # remove from old parent
            try:
                parent_children = parent_node.get("children", []) or []
                parent_children.remove(target_node)
            except ValueError:
                pass
            # add to destination
            dest_folder.setdefault("children", []).append(target_node)

        if dry_run:
            return {
                "status": "planned",
                "action": "edit",
                "edited": bool(new_title),
                "moved": bool(new_folder),
            }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "status": "success",
            "bookmark": {
                "id": str(target_node.get("id")),
                "title": target_node.get("name"),
                "url": target_node.get("url"),
            },
        }
    except PermissionError as e:
        return {"status": "error", "message": f"Failed to write bookmarks: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to edit bookmark: {e}"}


def delete_chromium_bookmark(
    path: Path | None,
    *,
    id: str | None = None,
    url: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Delete a Chromium bookmark by id or url."""
    if not path or not path.exists():
        return {"status": "error", "message": "Bookmarks file not found"}
    if id is None and url is None:
        return {"status": "error", "message": "Must provide id or url"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        roots = data.get("roots", {})
        target_node = None
        parent_node = None
        for root_key in ("bookmark_bar", "other", "synced"):
            root = roots.get(root_key)
            if isinstance(root, dict):
                target_node, parent_node = _find_node_and_parent_by(
                    root, match_id=id, match_url=url
                )
                if target_node is not None:
                    break
        if target_node is None or parent_node is None:
            return {"status": "error", "message": "Bookmark not found"}

        if dry_run:
            return {"status": "planned", "action": "delete", "id": str(target_node.get("id"))}

        try:
            parent_node.get("children", []).remove(target_node)
        except ValueError:
            return {"status": "error", "message": "Failed to remove bookmark from parent"}

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"status": "success", "deleted": True}
    except PermissionError as e:
        return {"status": "error", "message": f"Failed to write bookmarks: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to delete bookmark: {e}"}
