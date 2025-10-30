import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="container mx-auto px-4 py-24 text-center">
      <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
      <p className="text-muted-foreground mb-8">The page you are looking for does not exist.</p>
      <Link className="text-primary underline" to="/">Go back home</Link>
    </div>
  );
}


