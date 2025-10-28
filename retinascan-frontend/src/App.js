// App.js with improved UI/UX for a modern, professional look.

import React from 'react';
import './App.css';

function App() {
  const apiEndpoint = 'http://localhost:8000/predict'; // Update to your API deployment URL

  return (
    <div className="App">
      <div className="App-container">
        <header className="App-header">
          <h1>RetinaScan AI Client</h1>
          <p>
            This is the **Lovable-Compatible** frontend scaffolding for the RetinaScan AI project. It is designed to connect to the improved, high-performance Python backend.
          </p>
        </header>

        <section className="improvements">
          <h2>Backend Improvements Applied</h2>
          <ul className="feature-list">
            <li>**Improved Code Structure:** Core logic moved to a dedicated Service Layer for better modularity and testing.</li>
            <li>**Performance Enhancements:** Implemented asynchronous file reading and non-blocking model inference for high throughput.</li>
            <li>**Image Quality Assessment (IQA):** Added a pre-processing step to automatically reject poor-quality (blurry/out-of-focus) images, ensuring reliable results.</li>
            <li>**Enhanced Real-World Impact:** API response now includes **Structured Recommendations** (Urgency, Action, Follow-up) for clinical use.</li>
          </ul>
        </section>

        <section className="next-steps">
          <p>
            To begin development, run the Python backend and then start this React client.
          </p>
          <a
            className="App-link"
            href={apiEndpoint}
            target="_blank"
            rel="noopener noreferrer"
          >
            Test API Endpoint
          </a>
        </section>
      </div>
    </div>
  );
}

export default App;
