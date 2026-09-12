"use client";

import { useEffect } from "react";

const ITEM = ".framer-DsE1D";
const OPEN = "framer-v-ig0c81";
const CLOSED = "framer-v-1xjxd8z";

/**
 * The services list is an accordion in the template, driven by Framer's
 * variant system. The lift gives every item a body; this swaps the variant
 * classes so one is open at a time.
 */
export default function Services() {
  useEffect(() => {
    const items = Array.from(document.querySelectorAll<HTMLElement>(ITEM));
    if (!items.length) return;

    const titleOf = (el: HTMLElement) =>
      el.querySelector("h3")?.textContent?.trim() ?? "";

    const setOpen = (el: HTMLElement, open: boolean) => {
      el.classList.toggle(OPEN, open);
      el.classList.toggle(CLOSED, !open);
      el.setAttribute("aria-expanded", String(open));
    };

    const cleanups: Array<() => void> = [];

    for (const item of items) {
      item.setAttribute("role", "button");
      item.setAttribute("tabindex", "0");
      item.style.cursor = "pointer";

      const activate = () => {
        const title = titleOf(item);
        const opening = !item.classList.contains(OPEN);
        for (const other of items) {
          // keep every breakpoint copy of the same service in sync
          setOpen(other, opening && titleOf(other) === title);
        }
      };

      const onClick = () => activate();
      const onKey = (e: KeyboardEvent) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      };

      item.addEventListener("click", onClick);
      item.addEventListener("keydown", onKey);
      cleanups.push(() => {
        item.removeEventListener("click", onClick);
        item.removeEventListener("keydown", onKey);
      });
    }

    return () => cleanups.forEach((fn) => fn());
  }, []);

  return null;
}
