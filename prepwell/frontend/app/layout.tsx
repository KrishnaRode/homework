import type { Metadata } from "next";
import "./globals.css";
import { appConfig } from "@/app.config";

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
      <body>{children}</body>
    </html>
  );
}
