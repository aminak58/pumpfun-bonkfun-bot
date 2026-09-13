"""RugCheck summary lookup with small in-flight dedup cache."""

from __future__ import annotations

import asyncio
import logging

import aiohttp

log = logging.getLogger(__name__)


class RugCheckClient:
    def __init__(self, base_url: str, timeout_s: float = 10.0, concurrency: int = 4) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout_s)
        self._sem = asyncio.Semaphore(concurrency)
        self._session: aiohttp.ClientSession | None = None
        self._inflight: dict[str, asyncio.Task] = {}

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def _fetch(self, mint: str) -> dict | None:
        url = f"{self._base}/tokens/{mint}/report/summary"
        for attempt in (1, 2):
            try:
                session = await self._ensure_session()
                async with self._sem, session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    if resp.status == 429:
                        await asyncio.sleep(2 * attempt)
                        continue
                    log.debug("rugcheck %s -> HTTP %s", mint, resp.status)
                    return None
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.debug("rugcheck %s attempt %s failed: %s", mint, attempt, exc)
                await asyncio.sleep(1)
        return None

    async def summary(self, mint: str) -> dict | None:
        """Fetch the rugcheck summary once per mint, dedup concurrent requests."""
        if mint in self._inflight:
            return await self._inflight[mint]
        task = asyncio.create_task(self._fetch(mint))
        self._inflight[mint] = task
        try:
            return await task
        finally:
            self._inflight.pop(mint, None)

    def is_flagged(self, summary: dict | None, max_score_norm: float) -> bool:
        if summary is None:
            return False
        score_norm = summary.get("score_normalised") or 0
        if score_norm >= max_score_norm:
            return True
        return any(r.get("level") == "danger" for r in (summary.get("risks") or []))

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
