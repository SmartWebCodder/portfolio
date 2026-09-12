"use client";

import { useEffect } from "react";
import { wireAccordion } from "@/lib/accordion";

/**
 * The services list is an accordion in the template. Framer only shipped a body
 * for whichever item was open; the lift gives every item one, and this swaps
 * the variant classes so exactly one is open at a time.
 */
export default function Services() {
  useEffect(() => {
    return wireAccordion({
      items: Array.from(
        document.querySelectorAll<HTMLElement>(".framer-DsE1D")
      ),
      openClass: "framer-v-ig0c81",
      closedClass: "framer-v-1xjxd8z",
      headingSelector: "h3",
      labelFor: (title) => `Show details for ${title || "this service"}`,
    });
  }, []);

  return null;
}
