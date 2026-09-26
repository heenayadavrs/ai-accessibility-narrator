import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Accessibility Narrator",
  description: "Private, local, audio-first visual and web content companion",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
