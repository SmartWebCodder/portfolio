/**
 * Framer injects its icon sprite at runtime, so the ids the lifted markup
 * references (`<use href="#…">`) do not exist in the exported HTML. These are
 * stand-ins at the same ids, drawn to match the icons the template used:
 * an arrow for link buttons, a chevron for the experience accordion, and a
 * quote mark for testimonial cards.
 */
export default function Sprite() {
  return (
    <svg
      aria-hidden="true"
      style={{
        position: "absolute",
        width: 0,
        height: 0,
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      <defs>
        {/* link / download arrow */}
        <g
          id="1175957644"
          fill="none"
          stroke="var(--1m973uw, currentColor)"
          strokeWidth="var(--js9iwy, 2)"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M7 17 17 7" />
          <path d="M8 7h9v9" />
        </g>

        {/* accordion chevron */}
        <g
          id="1249959720"
          fill="none"
          stroke="var(--1m973uw, currentColor)"
          strokeWidth="var(--js9iwy, 2)"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m6 9 6 6 6-6" />
        </g>

        {/* quote mark */}
        <g
          id="547985882"
          fill="none"
          stroke="var(--21h8s6, currentColor)"
          strokeWidth="var(--pgex8v, 1.5)"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M10 11H6.5A2.5 2.5 0 0 1 4 8.5v-.75A2.25 2.25 0 0 1 6.25 5.5H7a3 3 0 0 1 3 3Zm0 0c0 4.5-1.75 6.75-4.5 7.5" />
          <path d="M20 11h-3.5A2.5 2.5 0 0 1 14 8.5v-.75a2.25 2.25 0 0 1 2.25-2.25H17a3 3 0 0 1 3 3Zm0 0c0 4.5-1.75 6.75-4.5 7.5" />
        </g>
      </defs>
    </svg>
  );
}
