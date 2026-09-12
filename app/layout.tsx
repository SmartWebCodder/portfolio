import type { Metadata, Viewport } from "next";
import "./base.css";
import "@/styles/devsync.css";
import "@/styles/fastfolio.css";
import "@/styles/overrides.css";
import { profile } from "@/lib/data";

const SITE = "https://akintoyenelson.com";
const TITLE = `${profile.fullName} — Full Stack Developer`;
const DESCRIPTION =
  "Full stack developer building fast, scalable web applications: React and " +
  "Next.js on the frontend, Node.js, NestJS and PostgreSQL behind them. " +
  "Seven years shipping production systems.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: {
    default: TITLE,
    template: `%s — ${profile.fullName}`,
  },
  description: DESCRIPTION,
  applicationName: profile.fullName,
  authors: [{ name: profile.fullName, url: SITE }],
  creator: profile.fullName,
  keywords: [
    "full stack developer",
    "frontend developer",
    "React developer",
    "Next.js developer",
    "Node.js engineer",
    "NestJS",
    "PostgreSQL",
    "Laravel developer",
    "Lagos Nigeria",
    profile.fullName,
  ],
  alternates: { canonical: SITE },
  openGraph: {
    type: "website",
    url: SITE,
    siteName: profile.fullName,
    title: TITLE,
    description: DESCRIPTION,
    locale: "en_US",
    images: [
      {
        url: "/og.jpg",
        width: 1200,
        height: 630,
        alt: `${profile.fullName}, full stack developer`,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    site: "@_NelsonAyo",
    creator: "@_NelsonAyo",
    title: TITLE,
    description: DESCRIPTION,
    images: ["/og.jpg"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" },
  },
  icons: {
    icon: "/favicon.png",
    apple: "/favicon.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#111111",
  colorScheme: "dark",
};

/** Tells search engines who the site is about. */
const personSchema = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: profile.fullName,
  url: SITE,
  image: `${SITE}/og.jpg`,
  jobTitle: "Full Stack Developer",
  email: `mailto:${profile.email}`,
  telephone: profile.phone,
  address: { "@type": "PostalAddress", addressLocality: "Lagos", addressCountry: "NG" },
  sameAs: [profile.github, profile.linkedin, profile.x],
  knowsAbout: [
    "React", "Next.js", "TypeScript", "Node.js", "NestJS",
    "Laravel", "PostgreSQL", "MongoDB", "Docker", "AWS",
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&family=Fragment+Mono:ital@0;1&family=Inter:wght@100..900&family=Geist+Mono:wght@100..900&display=swap"
          rel="stylesheet"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(personSchema) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
