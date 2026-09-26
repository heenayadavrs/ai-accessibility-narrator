from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag

from app.config import get_settings


STRIP_TAGS = {"script", "style", "nav", "footer", "aside", "header", "noscript", "svg", "iframe", "form"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


@dataclass
class ExtractedSegment:
    type: str
    text: str
    order: int


@dataclass
class ExtractionResult:
    segments: list[ExtractedSegment]
    parse_status: str  # ok | partial | error
    warning: str | None = None


def is_safe_url(url: str) -> tuple[bool, str]:
    """SSRF guard: http/https only; reject private/loopback/link-local resolved IPs."""
    try:
        parsed = urlparse(url)
    except Exception:  # noqa: BLE001
        return False, "Invalid URL"
    if parsed.scheme not in {"http", "https"}:
        return False, "Only http and https URLs are allowed"
    if not parsed.hostname:
        return False, "URL must include a hostname"
    host = parsed.hostname
    if host in {"localhost", "metadata", "metadata.google.internal"}:
        return False, "Hostname is not allowed"
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False, "Could not resolve hostname"
    for info in infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return False, "Resolved address is not publicly routable"
    return True, "ok"


def extract_from_html(html: str, source_hint: str = "") -> ExtractionResult:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(STRIP_TAGS):
        tag.decompose()
    for tag in soup.find_all(attrs={"hidden": True}):
        tag.decompose()
    for tag in soup.find_all(attrs={"aria-hidden": "true"}):
        tag.decompose()

    root = (
        soup.find("main")
        or soup.find(attrs={"role": "main"})
        or soup.find("article")
        or soup.body
        or soup
    )

    has_landmark = bool(soup.find("main") or soup.find(attrs={"role": "main"}) or soup.find("article"))
    segments: list[ExtractedSegment] = []
    order = 1

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if title:
        segments.append(ExtractedSegment(type="heading", text=title, order=order))
        order += 1

    for node in root.descendants:
        if not isinstance(node, Tag):
            continue
        name = node.name.lower() if node.name else ""
        if name in HEADING_TAGS:
            text = _visible_text(node)
            if text and not _already_has(segments, text):
                segments.append(ExtractedSegment(type="heading", text=text, order=order))
                order += 1
        elif name in {"p", "li"}:
            text = _visible_text(node)
            if text and not _already_has(segments, text):
                segments.append(ExtractedSegment(type="paragraph", text=text, order=order))
                order += 1
        elif name == "a":
            text = _visible_text(node)
            if text and not _already_has(segments, text):
                segments.append(ExtractedSegment(type="link", text=f"Link: {text}", order=order))
                order += 1
        elif name == "button" or node.get("role") == "button":
            text = _visible_text(node)
            if text and not _already_has(segments, text):
                segments.append(ExtractedSegment(type="button", text=f"Button: {text}", order=order))
                order += 1
        elif name == "img":
            alt = (node.get("alt") or "").strip()
            if alt and not _already_has(segments, alt):
                segments.append(ExtractedSegment(type="image_alt", text=f"Image: {alt}", order=order))
                order += 1

    if not segments:
        # Fall back to raw body text for edge cases without structure.
        body_text = _visible_text(root)
        if body_text:
            segments.append(ExtractedSegment(type="paragraph", text=body_text, order=1))
            return ExtractionResult(
                segments=segments,
                parse_status="partial",
                warning="Page has limited semantic structure; extraction may be incomplete.",
            )
        return ExtractionResult(
            segments=[],
            parse_status="error",
            warning="Could not extract readable content from this page.",
        )

    if not has_landmark:
        return ExtractionResult(
            segments=segments,
            parse_status="partial",
            warning="No main landmark found; reading order may be incomplete.",
        )

    return ExtractionResult(segments=segments, parse_status="ok", warning=None)


def extract_from_file(path: Path) -> ExtractionResult:
    html = path.read_text(encoding="utf-8", errors="ignore")
    return extract_from_html(html, source_hint=str(path))


async def fetch_and_extract(url: str) -> ExtractionResult:
    settings = get_settings()

    # Demo helper: allow relative fixture paths under DATA_DIR (before SSRF checks).
    if url.startswith("fixture:"):
        rel = url.removeprefix("fixture:")
        path = settings.data_dir / "webpages" / rel
        if path.exists():
            return extract_from_file(path)
        return ExtractionResult(segments=[], parse_status="error", warning=f"Fixture not found: {rel}")

    # Support local fixture URLs served as file paths for demo
    if url.startswith("file://"):
        path = Path(url.replace("file://", ""))
        if path.exists():
            return extract_from_file(path)
        return ExtractionResult(segments=[], parse_status="error", warning="Local file not found")

    ok, reason = is_safe_url(url)
    if not ok:
        return ExtractionResult(segments=[], parse_status="error", warning=reason)

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.page_fetch_timeout_s,
            headers={"User-Agent": "AIAccessibilityNarrator/0.1 (local demo)"},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content[: settings.max_page_bytes]
            html = content.decode(resp.encoding or "utf-8", errors="ignore")
    except Exception as exc:  # noqa: BLE001
        return ExtractionResult(
            segments=[],
            parse_status="error",
            warning=f"Failed to fetch page: {exc}",
        )

    result = extract_from_html(html, source_hint=url)
    total_chars = sum(len(s.text) for s in result.segments)
    if total_chars < settings.min_static_text_chars:
        rendered = await _playwright_render(url)
        if rendered:
            result = extract_from_html(rendered, source_hint=url)
    return result


async def _playwright_render(url: str) -> str | None:
    try:
        from playwright.async_api import async_playwright
    except Exception:  # noqa: BLE001
        return None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            html = await page.content()
            await browser.close()
            return html
    except Exception:  # noqa: BLE001
        return None


def _visible_text(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return " ".join(str(node).split())
    # Prefer direct meaningful text without nested block duplication for headings/links
    texts = []
    for child in node.children:
        if isinstance(child, NavigableString):
            t = " ".join(str(child).split())
            if t:
                texts.append(t)
        elif isinstance(child, Tag) and child.name not in STRIP_TAGS | HEADING_TAGS | {"p", "li", "div", "section"}:
            t = " ".join(child.stripped_strings)
            if t:
                texts.append(t)
    if texts:
        return " ".join(texts).strip()
    return " ".join(node.stripped_strings).strip()


def _already_has(segments: list[ExtractedSegment], text: str) -> bool:
    return any(s.text == text or s.text.endswith(text) for s in segments)
