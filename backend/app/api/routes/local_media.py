from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from pathlib import Path
import os
import mimetypes

from app.config import settings

router = APIRouter()


def _is_allowed_path(p: Path) -> bool:
    try:
        p = p.resolve()
    except Exception:
        return False
    for allowed in settings.EXTRA_MEDIA_DIRS:
        try:
            if p.is_dir() and str(p).startswith(str(Path(allowed).resolve())):
                return True
            if str(p).startswith(str(Path(allowed).resolve())):
                return True
        except Exception:
            continue
    return False


@router.get("/local-media/list")
async def list_local_dir(path: str = Query(..., description="Absolute path to list (must be under allowed dirs)")):
    """List files and directories under an allowed folder.

    This endpoint is intentionally conservative: it only works when
    `ALLOW_LOCAL_MEDIA` is True and `EXTRA_MEDIA_DIRS` contains the parent
    folder or one of its ancestors.
    """
    if not settings.ALLOW_LOCAL_MEDIA:
        raise HTTPException(
            status_code=403, detail="Local media serving is disabled")

    p = Path(path)
    if not _is_allowed_path(p):
        raise HTTPException(status_code=403, detail="Path not allowed")

    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    items = []
    try:
        for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            items.append({
                "name": child.name,
                "is_dir": child.is_dir(),
                "size": child.stat().st_size if child.is_file() else None,
                "path": str(child.resolve()),
            })
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return JSONResponse(content={"path": str(p.resolve()), "items": items})


@router.get("/local-media/stream")
async def stream_local_file(path: str = Query(..., description="Absolute path to file (must be under allowed dirs)")):
    """Stream a local file if it is under an allowed folder.

    Uses FileResponse which supports range requests via Starlette/ASGI server.
    """
    if not settings.ALLOW_LOCAL_MEDIA:
        raise HTTPException(
            status_code=403, detail="Local media serving is disabled")

    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    if not _is_allowed_path(p):
        raise HTTPException(status_code=403, detail="Path not allowed")

    # Guess mime type
    mime_type, _ = mimetypes.guess_type(str(p))
    return FileResponse(str(p), media_type=mime_type or "application/octet-stream", filename=p.name)
