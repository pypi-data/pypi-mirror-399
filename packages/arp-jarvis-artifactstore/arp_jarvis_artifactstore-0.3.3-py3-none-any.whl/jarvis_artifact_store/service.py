from __future__ import annotations

from typing import Annotated
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse
from arp_standard_model import Health, Status, VersionInfo
from arp_standard_server import AuthSettings
from arp_standard_server.auth import register_auth_middleware
from pydantic import BaseModel

from . import __version__
from .config import ArtifactStoreConfig, artifact_store_config_from_env
from .errors import InvalidArtifactIdError, NotFoundError, StorageFullError
from .filesystem import ArtifactMetadata, FilesystemArtifactStore
from .utils import auth_settings_from_env_or_dev_secure, now


class ArtifactRef(BaseModel):
    artifact_id: str
    uri: str
    content_type: str | None = None
    size_bytes: int
    checksum_sha256: str | None = None
    created_at: str


def create_app(
    config: ArtifactStoreConfig | None = None,
    auth_settings: AuthSettings | None = None,
) -> FastAPI:
    cfg = config or artifact_store_config_from_env()
    store = FilesystemArtifactStore(cfg)

    app = FastAPI(title="JARVIS Artifact Store", version=__version__)
    register_auth_middleware(app, settings=auth_settings or auth_settings_from_env_or_dev_secure())

    @app.get("/v1/health", response_model=Health)
    async def health() -> Health:
        return Health(status=Status.ok, time=datetime.now(timezone.utc))

    @app.get("/v1/version", response_model=VersionInfo)
    async def version() -> VersionInfo:
        return VersionInfo(
            service_name="arp-jarvis-artifactstore",
            service_version=__version__,
            supported_api_versions=["v1"],
        )

    @app.post("/v1/artifacts", response_model=ArtifactRef)
    async def create_artifact(
        request: Request,
        content_type: Annotated[str | None, Header(alias="Content-Type")] = None,
    ) -> ArtifactRef:
        data = await request.body()
        try:
            metadata = store.put(data, content_type=content_type)
        except StorageFullError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        return _to_ref(metadata)

    @app.get("/v1/artifacts/{artifact_id}")
    async def get_artifact(artifact_id: str) -> FileResponse:
        try:
            metadata = store.get_metadata(artifact_id)
            path = store.get_path(artifact_id)
        except InvalidArtifactIdError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return FileResponse(path, media_type=metadata.content_type)

    @app.head("/v1/artifacts/{artifact_id}")
    async def head_artifact(artifact_id: str) -> Response:
        try:
            metadata = store.get_metadata(artifact_id)
        except InvalidArtifactIdError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        headers = {
            "Content-Length": str(metadata.size_bytes),
        }
        if metadata.content_type:
            headers["Content-Type"] = metadata.content_type
        if metadata.checksum_sha256:
            headers["ETag"] = metadata.checksum_sha256
        return Response(status_code=200, headers=headers)

    @app.get("/v1/artifacts/{artifact_id}/metadata", response_model=ArtifactRef)
    async def get_metadata(artifact_id: str) -> ArtifactRef:
        try:
            metadata = store.get_metadata(artifact_id)
        except InvalidArtifactIdError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return _to_ref(metadata)

    return app


def _to_ref(metadata: ArtifactMetadata) -> ArtifactRef:
    return ArtifactRef(
        artifact_id=metadata.artifact_id,
        uri=metadata.uri,
        content_type=metadata.content_type,
        size_bytes=metadata.size_bytes,
        checksum_sha256=metadata.checksum_sha256,
        created_at=metadata.created_at,
    )
