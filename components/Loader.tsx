"use client";

import { useEffect, useRef, useState } from "react";

const STEPS = [
  "initializing portfolio",
  "loading skills",
  "setting up projects",
  "almost there",
];

const MAX_HOLD = 1600;

/**
 * Holds first paint until the fonts and the hero image are in. The bar tracks
 * real progress: each resolved dependency advances it, so it is not a fixed
 * animation pretending to load.
 */
export default function Loader() {
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);
  const settled = useRef(false);

  useEffect(() => {
    const finish = () => {
      if (settled.current) return;
      settled.current = true;
      setProgress(100);
      setTimeout(() => setDone(true), 360);
    };

    const heroReady = new Promise<void>((resolve) => {
      const hero = document.querySelector<HTMLImageElement>('img[src*="nelson"]');
      if (!hero || hero.complete) return resolve();
      hero.addEventListener("load", () => resolve(), { once: true });
      hero.addEventListener("error", () => resolve(), { once: true });
    });

    const tasks: Array<Promise<unknown>> = [
      document.fonts?.ready ?? Promise.resolve(),
      heroReady,
    ];

    // each dependency that lands moves the bar; the rest is a slow creep so it
    // never sits still while something is genuinely outstanding
    let landed = 0;
    const share = 80 / tasks.length;
    tasks.forEach((task) =>
      task.then(() => {
        landed += 1;
        setProgress((p) => Math.max(p, Math.round(landed * share)));
      })
    );

    const creep = setInterval(
      () => setProgress((p) => (p >= 92 ? p : p + 1)),
      90
    );
    const cap = setTimeout(finish, MAX_HOLD);
    Promise.all(tasks).then(finish);

    return () => {
      clearInterval(creep);
      clearTimeout(cap);
    };
  }, []);

  useEffect(() => {
    document.body.style.overflow = done ? "" : "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [done]);

  const step = STEPS[Math.min(STEPS.length - 1, Math.floor(progress / 25))];

  return (
    <div className={`loader ${done ? "is-done" : ""}`} aria-hidden={done}>
      <div className="loader__inner">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img className="loader__art" src="/loader.webp" alt="" />
        <div className="loader__bar">
          <span style={{ width: `${progress}%` }} />
        </div>
        <p className="loader__status">
          <span className="loader__step">&gt; {step}...</span>
          <span className="loader__pct">{progress}%</span>
        </p>
      </div>
    </div>
  );
}
