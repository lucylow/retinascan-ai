import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

export default function Layout() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isActive = (path: string) => location.pathname === path;

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  const links = [
    { to: "/", label: "Home" },
    { to: "/app", label: "App" },
    { to: "/landing", label: "Landing" },
    { to: "/ai-agent", label: "AI Agent" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 bg-primary text-primary-foreground px-3 py-2 rounded">Skip to content</a>
      <header className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="font-bold focus:outline-none focus:ring-2 focus:ring-ring rounded-sm">RetinaScan AI</Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1 text-sm" aria-label="Main navigation">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive: active }) => `px-3 py-2 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-ring ${
                  active ? "text-primary font-medium bg-primary/5" : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                aria-current={isActive(l.to) ? "page" : undefined}
              >
                {l.label}
              </NavLink>
            ))}
          </nav>

          {/* Mobile toggle */}
          <button
            className="md:hidden inline-flex items-center justify-center rounded-md p-2 text-muted-foreground hover:text-foreground hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring"
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((v) => !v)}
          >
            <svg className={`h-5 w-5 ${mobileOpen ? "hidden" : "block"}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="18" x2="21" y2="18" />
            </svg>
            <svg className={`h-5 w-5 ${mobileOpen ? "block" : "hidden"}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Mobile sheet */}
        <div
          className={`md:hidden border-t bg-background/95 backdrop-blur transition-[max-height] duration-300 overflow-hidden ${mobileOpen ? "max-h-96" : "max-h-0"}`}
          role="dialog"
          aria-modal="true"
        >
          <nav className="container mx-auto px-4 py-3 flex flex-col gap-1" aria-label="Mobile navigation">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive: active }) => `px-3 py-2 rounded-md transition-colors ${
                  active ? "text-primary font-medium bg-primary/5" : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main id="main" className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}


