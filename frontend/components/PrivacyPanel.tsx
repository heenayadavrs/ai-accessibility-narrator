"use client";

import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "@/lib/api";

export function PrivacyPanel() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function check(retries = 3) {
      for (let i = 0; i < retries; i++) {
        try {
          const h = await fetchHealth();
          if (!cancelled) {
            setHealth(h);
            setError(null);
          }
          return;
        } catch {
          if (i < retries - 1) {
            await new Promise((r) => setTimeout(r, 800));
          }
        }
      }
      if (!cancelled) setError("Backend unreachable");
    }

    void check();
    return () => {
      cancelled = true;
    };
  }, []);

  const isLocal = health?.runtime === "local" && health?.privacy_mode === "local";
  const readyCount = health?.models.filter((model) => model.ready).length ?? 0;

  return (
    <section className="privacy-panel" aria-label="Privacy and runtime status">
      <div className="privacy-icon" aria-hidden="true">◇</div>
      {health ? (
        <>
          <div>
            <strong>{isLocal ? "Private by design" : `Runtime: ${health.runtime}`}</strong>
            <span>
              {isLocal
                ? `Your image stays here · ${readyCount}/${health.models.length} engines ready`
                : "Check your runtime configuration"}
            </span>
          </div>
          <span className={isLocal ? "privacy-check ok" : "privacy-check error"} aria-hidden="true">
            {isLocal ? "✓" : "!"}
          </span>
        </>
      ) : (
        <div>
          <strong>{error ? "Backend offline" : "Checking privacy…"}</strong>
          <span>{error || "Confirming the local inference path"}</span>
        </div>
      )}
    </section>
  );
}
