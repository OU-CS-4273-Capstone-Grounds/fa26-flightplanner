import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function readSavedFlight() {
  try {
    const flight = JSON.parse(localStorage.getItem("fa26-flight") || "{}");
    return flight && typeof flight === "object" ? flight : {};
  } catch {
    return {};
  }
}

function RouteForm() {
  const [savedFlight] = useState(readSavedFlight);
  const [origin, setOrigin] = useState(savedFlight.origin || "");
  const [destination, setDestination] = useState(savedFlight.destination || "");
  const [altitude, setAltitude] = useState(savedFlight.altitude == null ? "" : String(savedFlight.altitude));

  function saveField(field, value) {
    const flight = { origin, destination, altitude: altitude ? Number(altitude) : "" };
    flight[field] = field === "altitude" ? (value ? Number(value) : "") : value;
    localStorage.setItem("fa26-flight", JSON.stringify(flight));
  }

  return (
      <form id="flight-form">
        <div className="form-grid">
          <label className="field">
            <span className="input-wrap">
              <input name="origin" value={origin} onChange={(event) => { const value = event.target.value.toUpperCase().replace(/[^A-Z]/g, ""); setOrigin(value); saveField("origin", value); }} placeholder="ENTER ORIGIN HERE" maxLength={4} pattern="[A-Z]{4}" title="Enter a 4-letter ICAO code" autoComplete="off" required />
            </span>
          </label>
          <label className="field">
            <span className="input-wrap">
              <input name="altitude" type="text" inputMode="numeric" maxLength={5} pattern="(?:[0-5]?[0-9]{1,4}|60000)" title="Enter a number from 0 to 60,000 feet" value={altitude} onChange={(event) => { const value = event.target.value.replace(/\D/g, "").slice(0, 5); setAltitude(value); saveField("altitude", value); }} onBlur={(event) => { const value = event.target.value.replace(/^0+(?=\d)/, ""); setAltitude(value); saveField("altitude", value); }} placeholder="Enter Cruise Elevation (ft)" required />
            </span>
          </label>
          <label className="field">
            <span className="input-wrap">
              <input name="destination" value={destination} onChange={(event) => { const value = event.target.value.toUpperCase().replace(/[^A-Z]/g, ""); setDestination(value); saveField("destination", value); }} placeholder="ENTER DESTINATION HERE" maxLength={4} pattern="[A-Z]{4}" title="Enter a 4-letter ICAO code" autoComplete="off" required />
            </span>
          </label>
        </div>
      </form>
  );
}

function HomePage() {
  return (
      <main className="flight-planner-home">
      <div className="decorative-sun" aria-hidden="true" />
      <div className="decorative-cloud" aria-hidden="true">
        <span className="cloud-middle-puff" />
      </div>
      <h1 id="page-title" className="page-title">fa26-Flightplanner</h1>
      <nav className="page-actions" aria-label="Flight planner pages">
        <a href="calculations.html">Display calculations</a>
        <a href="weather.html">Return Weather Data</a>
      </nav>
      <svg className="plane-illustration" viewBox="0 0 340 220" role="img" aria-label="Airplane outline">
        <g fill="none" stroke="#050505" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M28 55 C20 51 13 55 17 64 L34 101 C39 112 47 117 61 120 L111 131 L76 172 C70 179 76 185 85 184 L104 183 L191 128 L246 128 C270 128 294 120 300 113 C305 106 289 95 276 88 C266 82 252 80 238 80 L151 80 L81 31 C73 25 63 25 55 27 L51 30 L86 80 L60 80 Z" />
          <path d="M201 128 L232 128" />
        </g>
        <g fill="#050505">
          <rect x="105" y="91" width="9" height="18" rx="4.5" /><rect x="128" y="91" width="9" height="18" rx="4.5" />
          <rect x="151" y="91" width="9" height="18" rx="4.5" /><rect x="174" y="91" width="9" height="18" rx="4.5" />
          <rect x="197" y="91" width="9" height="18" rx="4.5" /><rect x="220" y="91" width="9" height="18" rx="4.5" />
          <rect x="243" y="91" width="9" height="18" rx="4.5" />
        </g>
      </svg>
      <RouteForm />
    </main>
  );
}

createRoot(document.getElementById("root")).render(<HomePage />);
