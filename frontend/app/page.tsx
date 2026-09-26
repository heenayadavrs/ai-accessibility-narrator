"use client";

import { FormEvent, useMemo, useState } from "react";
import { AskBox } from "@/components/AskBox";
import { DropZone } from "@/components/DropZone";
import { ImpairmentPreview, previewFilterClass, type PreviewMode } from "@/components/ImpairmentPreview";
import { NarrationStage } from "@/components/NarrationStage";
import { PlayerControls } from "@/components/PlayerControls";
import { PrivacyPanel } from "@/components/PrivacyPanel";
import { askImage, narrateImage, narratePage, type Segment } from "@/lib/api";
import { useNarrationPlayer } from "@/lib/useNarrationPlayer";

type Mode = "image" | "webpage";

export default function HomePage() {
  const [mode, setMode] = useState<Mode>("image");
  const [segments, setSegments] = useState<Segment[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<PreviewMode>("original");
  const [pageUrl, setPageUrl] = useState("fixture:simple_article.html");
  const [answer, setAnswer] = useState<string | null>(null);
  const [answerAudio, setAnswerAudio] = useState<string | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [parseStatus, setParseStatus] = useState<string | null>(null);

  const player = useNarrationPlayer(segments);
  const filterClass = useMemo(() => previewFilterClass(previewMode), [previewMode]);

  async function onImage(file: File) {
    setError(null);
    setBusy(true);
    setAnswer(null);
    setAnswerAudio(null);
    setParseStatus(null);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    try {
      const res = await narrateImage(file);
      setSessionId(res.session_id);
      setSegments(res.segments);
      setLatency(res.latency_ms ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Narration failed");
      setSegments([]);
      setSessionId(null);
    } finally {
      setBusy(false);
    }
  }

  async function onAsk(question: string) {
    if (!sessionId) return;
    setError(null);
    const res = await askImage(sessionId, question);
    setAnswer(res.answer);
    setAnswerAudio(res.audio_url);
  }

  async function onReadPage(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    setAnswer(null);
    setAnswerAudio(null);
    setSessionId(null);
    setPreviewUrl(null);
    try {
      const res = await narratePage(pageUrl.trim());
      setSessionId(res.session_id);
      setSegments(res.segments);
      setParseStatus(res.parse_status);
      if (res.warning) setError(res.warning);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Page narration failed");
      setSegments([]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-mark" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
        </div>
        <div className="brand-copy">
          <p className="eyebrow">Local multimodal accessibility</p>
          <h1>Hear what&apos;s in front of you.</h1>
          <p className="lede">
            Turn images and webpages into private, structured narration.
          </p>
        </div>
        <div className="local-badge">
          <span className="status-dot" aria-hidden="true" />
          Runs locally
        </div>
      </header>

      <main id="main">
        <div className="top-rail">
          <div className="mode-tabs" role="tablist" aria-label="Content mode">
            <button
              type="button"
              role="tab"
              aria-selected={mode === "image"}
              className={mode === "image" ? "active" : undefined}
              onClick={() => setMode("image")}
            >
              <span aria-hidden="true">▧</span> Image
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === "webpage"}
              className={mode === "webpage" ? "active" : undefined}
              onClick={() => setMode("webpage")}
            >
              <span aria-hidden="true">↗</span> Webpage
            </button>
          </div>
          <PrivacyPanel />
        </div>

        <div className="workspace">
          <div className="source-column">
            <div className="panel-heading">
              <div>
                <span className="step-label">01 · SOURCE</span>
                <h2>{mode === "image" ? "Your visual" : "Page to narrate"}</h2>
              </div>
              {latency != null && mode === "image" ? (
                <span className="metric">{(latency / 1000).toFixed(1)}s</span>
              ) : null}
            </div>

            {mode === "image" ? (
              <section className="source-panel" aria-label="Image input">
                <DropZone
                  onFile={onImage}
                  previewUrl={previewUrl}
                  previewFilter={filterClass}
                  disabled={busy}
                />
              </section>
            ) : (
              <section className="source-panel webpage-source" aria-label="Webpage input">
                <div className="web-icon" aria-hidden="true">↗</div>
                <h3>Listen to a webpage</h3>
                <p>Paste a public article URL or use one of the local demo pages.</p>
                <form className="url-row" onSubmit={onReadPage}>
                  <label htmlFor="page-url">Webpage address</label>
                  <div className="input-action">
                    <input
                      id="page-url"
                      value={pageUrl}
                      onChange={(e) => setPageUrl(e.target.value)}
                      placeholder="https://example.com/article"
                      disabled={busy}
                    />
                    <button className="primary-button" type="submit" disabled={busy}>
                      {busy ? "Preparing…" : "Narrate"}
                    </button>
                  </div>
                </form>
                <button
                  className="fixture-link"
                  type="button"
                  onClick={() => setPageUrl("fixture:simple_article.html")}
                >
                  Use demo article
                </button>
                {parseStatus ? <p className="parse-chip">Parsed · {parseStatus}</p> : null}
              </section>
            )}
          </div>

          <div className="narration-column">
            <div className="panel-heading">
              <div>
                <span className="step-label">02 · LISTEN</span>
                <h2>Narration</h2>
              </div>
              <span className={`state-pill ${player.playing ? "is-playing" : ""}`}>
                <span aria-hidden="true">{player.playing ? "●" : "○"}</span>
                {busy ? "Processing" : player.playing ? "Speaking" : "Ready"}
              </span>
            </div>

            {error ? (
              <p className="error error-banner" role="alert">
                {error}
              </p>
            ) : null}

            <p className="status-visible" aria-live="polite">
              {busy ? "Understanding your content locally…" : player.statusText}
            </p>
            <div className="status-live" aria-live="polite" aria-atomic="true">
              {busy ? "Processing locally" : player.statusText}
            </div>

            <NarrationStage
              segments={segments}
              currentIndex={player.index}
              title={mode === "webpage" ? "Structured webpage reading" : "Visual description"}
            />

            <PlayerControls
              playing={player.playing}
              canPrev={player.index > 0}
              canNext={player.index < player.total - 1}
              rate={player.rate}
              onToggle={player.toggle}
              onPrev={player.prev}
              onNext={player.next}
              onRate={player.setRate}
              disabled={!segments.length || busy}
            />
          </div>
        </div>

        <div className="secondary-grid">
          {mode === "image" ? (
            <AskBox
              onAsk={onAsk}
              answer={answer}
              answerAudioUrl={answerAudio}
              onPlayAnswer={() => {
                if (answerAudio) void player.playAnswer(answerAudio);
              }}
              disabled={!sessionId || busy}
            />
          ) : (
            <section className="panel feature-card">
              <span className="step-label">03 · EXPLORE</span>
              <h2>Move at your pace</h2>
              <p className="lede">
                Use previous, next, and playback speed to navigate each semantic section.
              </p>
            </section>
          )}
          <ImpairmentPreview mode={previewMode} onChange={setPreviewMode} />
        </div>
      </main>
    </div>
  );
}
