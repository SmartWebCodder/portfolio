"use client";

import { useEffect } from "react";

/**
 * Marks lazily-loaded project screenshots once they have painted, so the card
 * can cross-fade out of its shimmer placeholder.
 */
export default function ImageFade() {
  useEffect(() => {
    const images = Array.from(
      document.querySelectorAll<HTMLImageElement>('img[loading="lazy"]')
    );

    const markLoaded = (img: HTMLImageElement) => img.classList.add("is-loaded");
    const cleanups: Array<() => void> = [];

    for (const img of images) {
      if (img.complete && img.naturalWidth > 0) {
        markLoaded(img);
        continue;
      }
      const onLoad = () => markLoaded(img);
      img.addEventListener("load", onLoad);
      img.addEventListener("error", onLoad);
      cleanups.push(() => {
        img.removeEventListener("load", onLoad);
        img.removeEventListener("error", onLoad);
      });
    }

    return () => cleanups.forEach((fn) => fn());
  }, []);

  return null;
}
