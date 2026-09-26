export type Segment = {
  index: number;
  type: string;
  text: string;
  audio_url: string | null;
  start_ms: number;
  end_ms: number;
  order?: number | null;
};

export type ImageNarrateResponse = {
  session_id: string;
  caption: string;
  segments: Segment[];
  runtime: string;
  latency_ms?: number | null;
};

export type AskResponse = {
  answer: string;
  audio_url: string | null;
  session_id: string;
};

export type PageNarrateResponse = {
  session_id: string;
  segments: Segment[];
  parse_status: string;
  runtime: string;
  warning?: string | null;
};

export type HealthResponse = {
  status: string;
  runtime: string;
  privacy_mode: string;
  models: { name: string; ready: boolean; detail?: string | null }[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function absUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path}`;
}

export function mediaUrl(path: string | null | undefined): string | null {
  return absUrl(path);
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function narrateImage(file: File): Promise<ImageNarrateResponse> {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch(`${API_BASE}/api/narrate/image`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || "Image narration failed");
  }
  const data: ImageNarrateResponse = await res.json();
  return {
    ...data,
    segments: data.segments.map((s) => ({ ...s, audio_url: mediaUrl(s.audio_url) })),
  };
}

export async function askImage(sessionId: string, question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/api/narrate/image/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || "VQA failed");
  }
  const data: AskResponse = await res.json();
  return { ...data, audio_url: mediaUrl(data.audio_url) };
}

export async function narratePage(url: string): Promise<PageNarrateResponse> {
  const res = await fetch(`${API_BASE}/api/narrate/page`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || "Page narration failed");
  }
  const data: PageNarrateResponse = await res.json();
  return {
    ...data,
    segments: data.segments.map((s) => ({ ...s, audio_url: mediaUrl(s.audio_url) })),
  };
}
