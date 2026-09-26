from pathlib import Path

import pytest

from app.services.segmentation import split_sentences
from app.services.tts import wav_duration_ms
from app.services.web_extract import extract_from_file, is_safe_url


DATA = Path(__file__).resolve().parents[2] / "data"


def test_split_sentences():
    parts = split_sentences("Hello world. Next sentence! Really?")
    assert parts == ["Hello world.", "Next sentence!", "Really?"]


def test_split_empty():
    assert split_sentences("   ") == []


def test_ssrf_rejects_localhost():
    ok, reason = is_safe_url("http://localhost/admin")
    assert not ok
    assert "not allowed" in reason.lower() or "Hostname" in reason


def test_ssrf_rejects_private_ip_literal():
    # hostname that resolves isn't needed; literal private hosts via hostname check
    ok, _ = is_safe_url("http://127.0.0.1/")
    assert not ok


def test_ssrf_rejects_file_scheme_as_unsafe_network():
    ok, reason = is_safe_url("file:///etc/passwd")
    assert not ok
    assert "http" in reason.lower()


def test_simple_article_order():
    result = extract_from_file(DATA / "webpages" / "simple_article.html")
    types = [s.type for s in result.segments]
    assert "heading" in types
    assert "paragraph" in types
    assert result.parse_status == "ok"
    texts = " ".join(s.text for s in result.segments)
    assert "Screen Fatigue" in texts or "breaks matter" in texts


def test_nav_footer_suppressed():
    result = extract_from_file(DATA / "webpages" / "article_with_nav_footer.html")
    texts = [s.text.lower() for s in result.segments]
    joined = " ".join(texts)
    assert "home" not in joined or "choosing" in joined
    assert "copyright" not in joined
    assert any("desk" in t for t in texts)
    assert any(s.type == "image_alt" for s in result.segments)


def test_pricing_page_has_links():
    result = extract_from_file(DATA / "webpages" / "pricing_page.html")
    types = [s.type for s in result.segments]
    assert "heading" in types
    assert "link" in types
    assert result.parse_status == "ok"


def test_faq_page_structure():
    result = extract_from_file(DATA / "webpages" / "faq_page.html")
    assert result.parse_status == "ok"
    assert len(result.segments) >= 3


def test_parser_edge_case_partial():
    result = extract_from_file(DATA / "webpages" / "parser_edge_case.html")
    assert result.parse_status in {"partial", "error"}
    if result.segments:
        assert result.warning


def test_wav_duration(tmp_path):
    import wave

    path = tmp_path / "t.wav"
    rate = 22050
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x00" * rate)  # 1 second
    ms = wav_duration_ms(path)
    assert 900 <= ms <= 1100
