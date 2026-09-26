"use client";

export type PreviewMode = "original" | "blur" | "reduced" | "contrast";

type Props = {
  mode: PreviewMode;
  onChange: (mode: PreviewMode) => void;
};

export function ImpairmentPreview({ mode, onChange }: Props) {
  const options: { id: PreviewMode; label: string }[] = [
    { id: "original", label: "Original" },
    { id: "blur", label: "Blur" },
    { id: "reduced", label: "Reduced Color" },
    { id: "contrast", label: "High Contrast" },
  ];

  return (
    <section className="panel feature-card preview-card" aria-label="Visual impairment preview">
      <span className="step-label">04 · PERSPECTIVE</span>
      <h2>Explore another view</h2>
      <p className="lede">Apply an educational approximation to the visual.</p>
      <div className="filter-grid" role="group" aria-label="Preview filters">
        {options.map((o) => (
          <button
            key={o.id}
            type="button"
            aria-pressed={mode === o.id}
            onClick={() => onChange(o.id)}
          >
            {o.label}
          </button>
        ))}
      </div>
      <p className="disclaimer">
        Educational approximation only — not a clinical simulation.
      </p>
    </section>
  );
}

export function previewFilterClass(mode: PreviewMode): string {
  switch (mode) {
    case "blur":
      return "filter-blur";
    case "reduced":
      return "filter-reduced";
    case "contrast":
      return "filter-contrast";
    default:
      return "";
  }
}
