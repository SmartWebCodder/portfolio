"use client";

import { useEffect } from "react";

/* Framer variant classes on an experience card root. */
const CARD = "framer-9p2kii";
const OPEN = "framer-v-9p2kii";
const CLOSED = "framer-v-1chhkwp";

/**
 * The template's experience cards are an accordion: the "Toggle Button" chevron
 * swaps the card between its Opened and Closed variants, which the stylesheet
 * already knows how to lay out. Framer drove that from its runtime; this does
 * the same class swap, and adds the keyboard/ARIA wiring a button needs.
 */
export default function Accordion() {
  useEffect(() => {
    const cards = Array.from(document.querySelectorAll<HTMLElement>(`.${CARD}`));
    if (!cards.length) return;

    const cleanups: Array<() => void> = [];

    // Cards repeat once per breakpoint variant, so key the open card by the role
    // it shows rather than by index — otherwise each variant opens separately.
    const titleOf = (card: HTMLElement) =>
      card.querySelector("h4")?.textContent?.trim() ?? "";

    const titles: string[] = [];
    for (const card of cards) {
      const t = titleOf(card);
      if (t && !titles.includes(t)) titles.push(t);
    }
    const firstTitle = titles[0];

    const setOpen = (card: HTMLElement, open: boolean) => {
      card.classList.toggle(OPEN, open);
      card.classList.toggle(CLOSED, !open);
      card.setAttribute("aria-expanded", String(open));
      const body = card.querySelector<HTMLElement>(".framer-fmtgiz");
      if (body) body.hidden = false;
    };

    for (const card of cards) {
      setOpen(card, titleOf(card) === firstTitle);

      // the template only made the chevron interactive; the whole row is the
      // sensible target, and the chevron stays as the affordance
      const toggle = card;
      const chevron = card.querySelector<HTMLElement>(".framer-qipdi4");

      toggle.setAttribute("role", "button");
      toggle.setAttribute("tabindex", "0");
      toggle.setAttribute(
        "aria-label",
        `Toggle details for ${titleOf(card) || "this role"}`
      );
      toggle.style.cursor = "pointer";
      if (chevron) chevron.style.pointerEvents = "none";

      const activate = () => {
        const nowOpen = !card.classList.contains(OPEN);
        const title = titleOf(card);
        // keep every breakpoint copy of the same card in sync
        for (const other of cards) {
          if (titleOf(other) === title) setOpen(other, nowOpen);
        }
      };

      const onClick = () => activate();
      const onKey = (e: KeyboardEvent) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      };

      toggle.addEventListener("click", onClick);
      toggle.addEventListener("keydown", onKey);
      cleanups.push(() => {
        toggle.removeEventListener("click", onClick);
        toggle.removeEventListener("keydown", onKey);
      });
    }

    return () => cleanups.forEach((fn) => fn());
  }, []);

  return null;
}
