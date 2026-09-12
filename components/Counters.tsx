"use client";

import { useEffect } from "react";

const DURATION = 1600;

/**
 * Counts the hero metrics up when they scroll into view. Framer drove these
 * from a code component; the lift replaces it with a `data-count` target.
 */
export default function Counters() {
  useEffect(() => {
    const spans = Array.from(
      document.querySelectorAll<HTMLElement>("[data-count]")
    );
    if (!spans.length) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const frames: number[] = [];

    const run = (el: HTMLElement) => {
      const target = Number(el.dataset.count);
      if (!Number.isFinite(target)) return;
      if (reduced) {
        el.textContent = String(target);
        return;
      }
      const started = performance.now();
      const tick = (now: number) => {
        const t = Math.min(1, (now - started) / DURATION);
        el.textContent = String(Math.round(target * (1 - Math.pow(1 - t, 3))));
        if (t < 1) frames.push(requestAnimationFrame(tick));
      };
      frames.push(requestAnimationFrame(tick));
    };

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          io.unobserve(entry.target);
          run(entry.target as HTMLElement);
        }
      },
      { threshold: 0.4 }
    );

    spans.forEach((el) => io.observe(el));
    return () => {
      io.disconnect();
      frames.forEach(cancelAnimationFrame);
    };
  }, []);

  return null;
}
