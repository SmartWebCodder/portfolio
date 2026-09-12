"use client";

import { useEffect } from "react";

/**
 * Framer's runtime animates elements in on scroll. The lifted markup keeps the
 * same element structure but carries `data-reveal` / `data-char` hooks instead,
 * which this observer switches on. Char spans additionally get an index so the
 * stagger can be expressed as a CSS transition-delay.
 */
export default function Reveal() {
  useEffect(() => {
    const nodes = Array.from(
      document.querySelectorAll<HTMLElement>("[data-reveal], [data-char]")
    );

    // Stagger is per line of split text, so the delay restarts on each parent.
    const seen = new Map<Element, number>();
    for (const el of nodes) {
      if (!el.hasAttribute("data-char")) continue;
      const parent = el.closest("[data-styles-preset], h1, h2, h3, p") ?? el.parentElement;
      if (!parent) continue;
      const i = seen.get(parent) ?? 0;
      el.style.setProperty("--char-i", String(i));
      seen.set(parent, i + 1);
    }

    if (typeof IntersectionObserver === "undefined") {
      nodes.forEach((el) => el.classList.add("is-in"));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.05 }
    );

    nodes.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return null;
}
