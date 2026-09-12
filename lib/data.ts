export const profile = {
  name: "Akintoye Nelson",
  fullName: "Akintoye Ayomide Nelson",
  role: "Full Stack Developer",
  email: "akintoyenelson@gmail.com",
  phone: "+234 813 841 2167",
  location: "Lagos, Nigeria",
  github: "https://github.com/SmartWebCodder",
  linkedin: "https://www.linkedin.com/in/akintoye-ayomide-nelson/",
  x: "https://x.com/_NelsonAyo",
  photo: "/nelson.webp",
  intro:
    "I craft fast, scalable, and user-friendly web applications with modern JavaScript frameworks — combining React and Next.js on the frontend with robust server-side systems in Node.js, NestJS and PostgreSQL.",
  about:
    "I thrive on solving real-world problems, turning ideas into clean, maintainable code, and learning through experimentation. You'll find me building side projects, diving into new tech stacks, or simply exploring what's next in the world of web development.",
};

export const socials = [
  { label: "GitHub", href: profile.github },
  { label: "LinkedIn", href: profile.linkedin },
  { label: "X", href: profile.x },
  { label: "Email", href: `mailto:${profile.email}` },
];

export const stats = [
  { value: 7, suffix: "+", label: "Years in Experience" },
  { value: 8, suffix: "+", label: "Teams Worldwide" },
  { value: 50, suffix: "+", label: "Completed Projects" },
];

export const skillGroups = [
  {
    title: "Frontend",
    items: ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS"],
  },
  {
    title: "Server-side development",
    items: ["Node.js", "NestJS", "Express.js", "PostgreSQL", "MongoDB", "Redis", "Kafka"],
  },
  {
    title: "Tools",
    items: ["Git", "GitHub", "Docker", "Kubernetes", "AWS", "Prisma", "GitHub Actions"],
  },
];

export const projects = [
  {
    title: "PlantRight AI",
    description:
      "A full-stack spatial AI platform for reforestation — intelligent site selection, design and monitoring, with ArcGIS/QGIS integration that cut manual work for forestry teams by 65–80%.",
    tags: ["Next.js & React", "NestJS", "PostgreSQL"],
    href: "https://github.com/SmartWebCodder/plantright-ai",
  },
  {
    title: "Selar Clone",
    description:
      "A production-ready commerce platform for African digital creators, supporting digital product sales, memberships, bundles and creator analytics end to end.",
    tags: ["TypeScript", "Express & NestJS", "Prisma"],
    href: "https://github.com/SmartWebCodder/selar-clone",
  },
  {
    title: "Unispend",
    description:
      "A campus payments ecosystem with real-time student wallet top-ups, QR-code payments and transaction tracking, plus analytics dashboards for revenue-sharing models.",
    tags: ["React", "NestJS", "MongoDB"],
    href: profile.github,
  },
  {
    title: "ChopExpress",
    description:
      "A multi-tenant food delivery platform handling high-concurrency rider, business and order workflows — transaction lookups cut by 50–60% through query optimisation.",
    tags: ["Node.js", "PostgreSQL", "Prisma"],
    href: profile.github,
  },
  {
    title: "FastPay Webhooks",
    description:
      "A real-time webhook system for payment notifications with delivery guarantees, reducing manual reconciliation by 40% across high-volume payment traffic.",
    tags: ["Express", "PostgreSQL", "AWS"],
    href: profile.github,
  },
  {
    title: "Pandar Data Pipelines",
    description:
      "API integrations and data pipelines rebuilt around efficient connection pooling and query optimisation, bringing average response times down by 60%.",
    tags: ["TypeScript", "NestJS", "MongoDB"],
    href: profile.github,
  },
];

export const services = [
  {
    n: "(01)",
    title: "Custom Web Development",
    body: "Build complete web applications from scratch — frontend to backend — optimized for speed, security, and scalability.",
  },
  {
    n: "(02)",
    title: "Frontend Engineering",
    body: "Accessible, responsive interfaces in React and Next.js, built on clean component systems that stay maintainable as the product grows.",
  },
  {
    n: "(03)",
    title: "Server logic & API Development",
    body: "Event-driven services, REST APIs and data pipelines in Node.js and NestJS, tuned for throughput, caching and fault tolerance.",
  },
  {
    n: "(04)",
    title: "Full Stack Application Development",
    body: "End-to-end ownership — schema design, API, interface and deployment — shipped with CI/CD, observability and room to scale.",
  },
];

export const process = [
  {
    n: "01",
    title: "Plan & Architect",
    body: "Before writing a single line of code, I dive deep into understanding the project goals, user needs, and technical constraints.",
  },
  {
    n: "02",
    title: "Build & Develop",
    body: "Build pixel-perfect user interfaces and robust backend systems in parallel. I ensure that every component—UI or API—is maintainable.",
  },
  {
    n: "03",
    title: "Launch & Support",
    body: "I also provide post-launch monitoring, performance optimization, and ongoing iteration support to keep your product growing.",
  },
];

export const clients = [
  "Pandar Resources",
  "ODJTech Multimedia",
  "Unispend",
  "ChopExpress",
  "FastPay Tech",
  "PPLELabs",
  "Taskimony",
  "NTech Info System",
];
