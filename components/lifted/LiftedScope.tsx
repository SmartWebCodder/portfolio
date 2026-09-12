import type { ReactNode } from "react";

/**
 * The template's typography presets are scoped under page-level class names
 * that Framer puts on the page root (`.framer-mR5Jm .framer-styles-preset-wj1llc`,
 * and so on). The lifted sections carry most of them already; this wrapper
 * supplies the full set so every preset resolves the way it does on the original.
 */
const SCOPES = [
  "framer-2nqUY",
  "framer-Au8L7",
  "framer-DxOX8",
  "framer-GVdQe",
  "framer-GxEnY",
  "framer-NU0Pm",
  "framer-OLJCl",
  "framer-UMIy9",
  "framer-bt7oY",
  "framer-mR5Jm",
  "framer-ou6pr",
  "framer-sEkee",
].join(" ");

export default function LiftedScope({ children }: { children: ReactNode }) {
  return <div className={`lifted ${SCOPES}`}>{children}</div>;
}
