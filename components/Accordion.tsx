"use client";

import { useEffect } from "react";
import { wireAccordion } from "@/lib/accordion";

/**
 * The experience cards are an accordion in the template, driven by Framer's
 * variant system. The stylesheet already knows the Opened and Closed variants;
 * this swaps between them and adds the keyboard and ARIA wiring the template's
 * div-as-button lacked.
 */
export default function Accordion() {
  useEffect(() => {
    const items = Array.from(
      document.querySelectorAll<HTMLElement>(".framer-9p2kii")
    );

    // the template made only the chevron interactive; the whole row is the
    // sensible target, and the chevron stays as the affordance
    items.forEach((item) => {
      const chevron = item.querySelector<HTMLElement>(".framer-qipdi4");
      if (chevron) chevron.style.pointerEvents = "none";
    });

    return wireAccordion({
      items,
      openClass: "framer-v-9p2kii",
      closedClass: "framer-v-1chhkwp",
      headingSelector: "h4",
      labelFor: (title) => `Toggle details for ${title || "this role"}`,
    });
  }, []);

  return null;
}
