/* =============================================================================
 *  File:        frontend/components/Footer.tsx
 *  Description: Global site footer credit line, mounted in the root layout so it
 *               appears on every page ("Developed by Krishna Rode").
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
// Slim, unobtrusive credit bar. Lives in the root layout (app/layout.tsx) and is
// pushed to the bottom of the viewport via the flex-column wrapper there.
export function SiteFooter() {
  return (
    <footer className="border-t border-border-soft px-5 py-5 text-center text-xs text-text-faint">
      <p>
        Developed by{" "}
        <span className="font-semibold text-text-muted">Krishna Rode</span>
      </p>
    </footer>
  );
}
