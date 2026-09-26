"use client";

type Props = {
  playing: boolean;
  canPrev: boolean;
  canNext: boolean;
  rate: number;
  onToggle: () => void;
  onPrev: () => void;
  onNext: () => void;
  onRate: (r: number) => void;
  disabled?: boolean;
};

const RATES = [0.8, 1.0, 1.25];

export function PlayerControls({
  playing,
  canPrev,
  canNext,
  rate,
  onToggle,
  onPrev,
  onNext,
  onRate,
  disabled,
}: Props) {
  return (
    <div className="player-deck" role="group" aria-label="Playback controls">
      <button className="icon-button" type="button" onClick={onPrev} disabled={disabled || !canPrev} aria-label="Previous segment">
        <span aria-hidden="true">‹</span>
      </button>
      <button
        className="play-button"
        type="button"
        onClick={onToggle}
        disabled={disabled}
        aria-label={playing ? "Pause narration" : "Play narration"}
      >
        <span aria-hidden="true">{playing ? "Ⅱ" : "▶"}</span>
        {playing ? "Pause" : "Listen"}
      </button>
      <button className="icon-button" type="button" onClick={onNext} disabled={disabled || !canNext} aria-label="Next segment">
        <span aria-hidden="true">›</span>
      </button>
      <div className="speed-group" role="group" aria-label="Playback speed">
        <span id="speed-label">Speed</span>
        {RATES.map((r) => (
          <button
            key={r}
            type="button"
            aria-pressed={rate === r}
            aria-label={`${r} times speed`}
            onClick={() => onRate(r)}
            disabled={disabled}
          >
            {r.toFixed(2).replace(/\.00$/, ".0")}x
          </button>
        ))}
      </div>
    </div>
  );
}
