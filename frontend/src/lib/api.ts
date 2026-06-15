// Thin client over the Stillframe backend. No business logic lives here.
// In dev, /api is proxied to the backend (vite.config). In Docker, nginx proxies it.
const BASE = import.meta.env.VITE_API_BASE ?? "/api";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export interface ProviderInfo {
  name: string;
  label: string;
  local: boolean;
  available: boolean;
  models: string[];
  default_model: string;
  detail: string;
}

export interface Frame {
  id: string;
  scene_id: string | null;
  title: string;
  captured: string;
  reflection: string;
  reframe: string;
  mood_score: number | null;
  created_at: string;
  updated_at: string;
}

export const api = {
  health: () => json<{ status: string }>("/health"),
  providers: () => json<{ data: ProviderInfo[] }>("/providers"),
  listFrames: () => json<{ data: Frame[] }>("/frames"),
  createFrame: (body: { title: string; captured: string; scene_id?: string }) =>
    json<{ data: Frame }>("/frames", { method: "POST", body: JSON.stringify(body) }),
};

// reflect streams NDJSON: {type:"delta",text} | {type:"safety",...} | {type:"done"}.
export async function* reflect(
  text: string,
  opts: { scene_id?: string; provider?: string; model?: string } = {}
): AsyncGenerator<{ type: string; text?: string; [k: string]: unknown }> {
  const res = await fetch(`${BASE}/reflect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, ...opts }),
  });
  if (!res.body) throw new Error("No response body");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop() ?? "";
    for (const line of lines) {
      if (line.trim()) yield JSON.parse(line);
    }
  }
}
