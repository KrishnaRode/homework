/* =============================================================================
 *  File:        frontend/app/layout.tsx
 *  Description: Root layout: theme bootstrap, metadata, and global site footer.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import type { Metadata } from "next";
import "./globals.css";
import { appConfig } from "@/app.config";
import { SiteFooter } from "@/components/Footer";

export const metadata: Metadata = {
  title: `${appConfig.fullName} — ${appConfig.tagline}`,
  description: appConfig.description,
};

const themeScript = `
(function(){
  try {
    var t = localStorage.getItem('prepwell_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', t);
  } catch(e){}
})();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <div className="flex min-h-screen flex-col">
          <div className="flex-1">{children}</div>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
