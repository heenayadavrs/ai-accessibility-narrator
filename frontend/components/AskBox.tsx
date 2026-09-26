"use client";

import { FormEvent, useState } from "react";

type Props = {
  onAsk: (question: string) => Promise<void>;
  answer: string | null;
  answerAudioUrl: string | null;
  onPlayAnswer: () => void;
  disabled?: boolean;
};

export function AskBox({ onAsk, answer, answerAudioUrl, onPlayAnswer, disabled }: Props) {
  const [question, setQuestion] = useState("What color is the shirt?");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!question.trim() || disabled) return;
    setBusy(true);
    try {
      await onAsk(question.trim());
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel feature-card ask-card" aria-label="Ask about this image">
      <span className="step-label">03 · ASK</span>
      <h2>Go beyond the caption</h2>
      <p className="lede">Ask one focused question about the current image.</p>
      <form className="ask-row" onSubmit={submit}>
        <label htmlFor="ask-input" className="status-live">
          Question
        </label>
        <input
          id="ask-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={disabled || busy}
          placeholder="What color is the shirt?"
        />
        <button className="primary-button" type="submit" disabled={disabled || busy}>
          {busy ? "Thinking…" : "Ask"}
        </button>
      </form>
      {answer ? (
        <div className="answer-card">
          <span className="answer-label">Answer</span>
          <p>{answer}</p>
          {answerAudioUrl ? (
            <button className="answer-play" type="button" onClick={onPlayAnswer} aria-label="Play spoken answer">
              <span aria-hidden="true">▶</span> Hear answer
            </button>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
