from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import get_settings
from .models import AuditRecord, Base
from .providers import ProviderError, humanize_page
from .schemas import AuditRequest, AuditResponse

settings = get_settings()
engine = create_async_engine(settings.async_database_url, pool_pre_ping=True) if settings.database_url else None
session_factory = async_sessionmaker(engine, expire_on_commit=False) if engine else None


@asynccontextmanager
async def lifespan(_: FastAPI):
    if engine:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    yield
    if engine:
        await engine.dispose()


app = FastAPI(title="Humanize API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_origin_regex=r"chrome-extension://.*", allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.middleware("http")
async def reject_oversized_audits(request: Request, call_next):
    body_length = request.headers.get("content-length")
    if request.url.path == "/api/audits" and request.method == "POST" and body_length:
        try:
            too_large = int(body_length) > settings.max_request_bytes
        except ValueError:
            too_large = False
        if too_large:
            return JSONResponse(status_code=413, content={"detail": "This page capture is too large. Try a simpler page."})
    return await call_next(request)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


def _result_response(record: AuditRecord) -> AuditResponse:
    return AuditResponse(id=record.id, url=record.url, created_at=record.created_at, **record.result)


@app.post("/api/audits", response_model=AuditResponse)
async def create_audit(payload: AuditRequest, request: Request) -> AuditResponse:
    body_length = request.headers.get("content-length")
    if body_length and int(body_length) > settings.max_request_bytes:
        raise HTTPException(status_code=413, detail="This page capture is too large. Try a simpler page.")
    try:
        result = await humanize_page(payload.context, payload.screenshot, settings)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="The model response could not be validated.") from exc

    now = datetime.now(timezone.utc)
    audit_id = str(uuid4())
    if session_factory:
        async with session_factory() as session:
            record = AuditRecord(id=audit_id, url=str(payload.context.url), title=payload.context.title, score=result.score, result=result.model_dump(mode="json"))
            session.add(record)
            await session.commit()
            audit_id = record.id
    return AuditResponse(id=audit_id, url=str(payload.context.url), created_at=now, **result.model_dump())


@app.get("/api/audits/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: str) -> AuditResponse:
    if session_factory is None:
        raise HTTPException(status_code=503, detail="Audit history is unavailable until DATABASE_URL is configured.")
    try:
        normalized_id = str(UUID(audit_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Audit not found.") from exc
    async with session_factory() as session:
        record = await session.scalar(select(AuditRecord).where(AuditRecord.id == normalized_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return _result_response(record)
