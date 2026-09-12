"use client";

import { useEffect } from "react";

const BUTTON = ".framer-13fpnqk";
const SHEET_ID = "site-menu";

const LINKS = [
  { label: "Home", href: "#top" },
  { label: "About", href: "#about-us" },
  { label: "Works", href: "#explore" },
  { label: "Experience", href: "#experience" },
  { label: "Blogs", href: "#blogs" },
  { label: "Contact", href: "#contact" },
];

/**
 * The template's Menu button opens an overlay through Framer's variant system,
 * which is not shipped, so the button did nothing. This builds the sheet and
 * wires the button to it.
 */
export default function Menu() {
  useEffect(() => {
    const buttons = Array.from(document.querySelectorAll<HTMLElement>(BUTTON));
    if (!buttons.length) return;

    const sheet = document.createElement("nav");
    sheet.id = SHEET_ID;
    sheet.className = "site-menu";
    sheet.setAttribute("aria-label", "Site");
    sheet.hidden = true;
    sheet.innerHTML = LINKS.map(
      (l) => `<a class="site-menu__link" href="${l.href}">${l.label}</a>`
    ).join("");
    document.body.appendChild(sheet);

    const setOpen = (open: boolean) => {
      sheet.hidden = !open;
      sheet.style.display = open ? "" : "none";
      sheet.classList.toggle("is-open", open);
      document.body.style.overflow = open ? "hidden" : "";
      buttons.forEach((b) => {
        b.setAttribute("aria-expanded", String(open));
        b.classList.toggle("is-open", open);
      });
    };

    const toggle = (e: Event) => {
      e.preventDefault();
      setOpen(sheet.hidden);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
      if ((e.key === "Enter" || e.key === " ") && buttons.includes(e.target as HTMLElement)) {
        e.preventDefault();
        setOpen(sheet.hidden);
      }
    };

    buttons.forEach((b) => {
      b.setAttribute("role", "button");
      b.setAttribute("aria-controls", SHEET_ID);
      b.setAttribute("aria-expanded", "false");
      b.style.cursor = "pointer";
      b.addEventListener("click", toggle);
    });
    sheet.addEventListener("click", (e) => {
      if ((e.target as HTMLElement).tagName === "A") setOpen(false);
    });
    document.addEventListener("keydown", onKey);

    return () => {
      buttons.forEach((b) => b.removeEventListener("click", toggle));
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
      sheet.remove();
    };
  }, []);

  return null;
}
