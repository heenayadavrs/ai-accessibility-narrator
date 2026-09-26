"use client";

import type { Segment } from "@/lib/api";

type Props = {
  segments: Segment[];
  currentIndex: number;
  title?: string;
};

export function NarrationStage({ segments, currentIndex, title }: Props) {
  if (!segments.length) {
    return (
      <section className="narration-stage narration-empty" aria-label="Narration stage">
        <div className="sound-bars" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <h3>Your narration will appear here</h3>
        <p>Choose a source, then listen as each section is highlighted.</p>
      </section>
    );
  }

  return (
    <section className="narration-stage" aria-label="Narration stage">
      <div className="narration-meta">
        {title ? <span>{title}</span> : null}
        <span aria-hidden="true">
          {String(currentIndex + 1).padStart(2, "0")} / {String(segments.length).padStart(2, "0")}
        </span>
      </div>
      <div className="segment-list" role="list">
        {segments.map((seg, i) => (
          <p
            key={`${seg.index}-${i}`}
            role="listitem"
            className="segment"
            aria-current={i === currentIndex ? "true" : undefined}
            data-type={seg.type}
          >
            <span className="segment-type">{seg.type}</span>
            {seg.text}
          </p>
        ))}
      </div>
    </section>
  );
}
