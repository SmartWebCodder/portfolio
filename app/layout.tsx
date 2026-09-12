import type { Metadata, Viewport } from "next";
import "./base.css";
import "@/styles/devsync.css";
import "@/styles/fastfolio.css";
import "@/styles/overrides.css";
import { profile } from "@/lib/data";

export const metadata: Metadata = {
  metadataBase: new URL("https://akintoyenelson.dev"),
  title: `${profile.fullName} — ${profile.role}`,
  description: profile.intro,
  openGraph: {
    title: `${profile.fullName} — ${profile.role}`,
    description: profile.intro,
    type: "website",
    images: [{ url: profile.photo }],
  },
  twitter: {
    card: "summary_large_image",
    title: `${profile.fullName} — ${profile.role}`,
    description: profile.intro,
  },
};

export const viewport: Viewport = {
  themeColor: "#111111",
  colorScheme: "dark",
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
      </head>
      <body>{children}</body>
    </html>
  );
}
