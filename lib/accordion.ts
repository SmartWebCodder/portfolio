/**
 * Shared behaviour for the two accordions lifted from the templates.
 *
 * Both render each item once per breakpoint, so items are grouped by their
 * heading: opening one has to open every copy of it and close everything else.
 */
export type AccordionOptions = {
  items: HTMLElement[];
  openClass: string;
  closedClass: string;
  headingSelector: string;
  labelFor?: (title: string) => string;
};

/** Framer's entrance states never clear inside a collapsed item, because it has
 *  no area for an IntersectionObserver to see. Opening one settles them. */
function settleReveals(item: HTMLElement) {
  item
    .querySelectorAll("[data-reveal], [data-char]")
    .forEach((el) => el.classList.add("is-in"));
}

export function wireAccordion({
  items,
  openClass,
  closedClass,
  headingSelector,
  labelFor,
}: AccordionOptions): () => void {
  if (!items.length) return () => {};

  const titleOf = (el: HTMLElement) =>
    el.querySelector(headingSelector)?.textContent?.trim() ?? "";

  const setOpen = (el: HTMLElement, open: boolean) => {
    el.classList.toggle(openClass, open);
    el.classList.toggle(closedClass, !open);
    el.setAttribute("aria-expanded", String(open));
    if (open) settleReveals(el);
  };

  const firstTitle = titleOf(items[0]);
  const cleanups: Array<() => void> = [];

  for (const item of items) {
    setOpen(item, titleOf(item) === firstTitle);

    item.setAttribute("role", "button");
    item.setAttribute("tabindex", "0");
    item.style.cursor = "pointer";
    if (labelFor) item.setAttribute("aria-label", labelFor(titleOf(item)));

    const activate = () => {
      const opening = !item.classList.contains(openClass);
      const title = titleOf(item);
      // one open at a time, across every breakpoint copy
      for (const other of items) {
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
}
