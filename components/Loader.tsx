"use client";

import { useEffect, useState } from "react";

/**
 * The page ships a large amount of lifted markup, so first paint lands before
 * fonts and the hero image do. This holds a brief cover over that gap rather
 * than showing a half-drawn page.
 */
export default function Loader() {
  const [done, setDone] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const finish = () => {
      if (!cancelled) setDone(true);
    };

    const heroReady = new Promise<void>((resolve) => {
      const hero = document.querySelector<HTMLImageElement>(
        'img[src*="nelson"]'
      );
      if (!hero || hero.complete) return resolve();
      hero.addEventListener("load", () => resolve(), { once: true });
      hero.addEventListener("error", () => resolve(), { once: true });
    });

    const ready = Promise.all([
      document.fonts?.ready ?? Promise.resolve(),
      heroReady,
    ]);

    // never hold the page longer than this, whatever is still loading
    const timeout = setTimeout(finish, 1800);
    ready.then(() => {
      clearTimeout(timeout);
      finish();
    });

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, []);

  useEffect(() => {
    document.body.style.overflow = done ? "" : "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [done]);

  return (
    <div className={`loader ${done ? "is-done" : ""}`} aria-hidden={done}>
      <span className="loader__mark">AN</span>
      <span className="loader__bar" />
    </div>
  );
}
