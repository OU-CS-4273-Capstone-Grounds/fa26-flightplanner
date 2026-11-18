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
  const [powerSetting, setPowerSetting] = useState(savedFlight.powerSetting == null ? "" : String(savedFlight.powerSetting));
  const [usableFuel, setUsableFuel] = useState(savedFlight.usableFuel == null ? "" : String(savedFlight.usableFuel));
  const allowedPowerSettings = ["50", "55", "60", "65", "70", "75"];

  function saveField(field, value) {
    const flight = {
      origin,
      destination,
      altitude: altitude === "" ? "" : Number(altitude),
      powerSetting: powerSetting === "" ? "" : Number(powerSetting),
      usableFuel: usableFuel === "" ? "" : Number(usableFuel),
    };
    const numericFields = ["altitude", "powerSetting", "usableFuel"];
    flight[field] = numericFields.includes(field) && value !== "" ? Number(value) : value;
    localStorage.setItem("fa26-flight", JSON.stringify(flight));
  }

  return (
    <section className="flight-form-card" aria-labelledby="flight-form-title">
      <header className="flight-form-heading">
        <AirplaneMark />
        <div>
          <p className="form-eyebrow">FLIGHT DETAILS</p>
          <h2 id="flight-form-title">Plan your flight</h2>
          <p className="form-intro">Enter your route details below to get started.</p>
        </div>
      </header>
      <form id="flight-form">
        <div className="form-grid">
          <label className="field">
            <span className="field-label">Origin Airport</span>
            <input className="route-input" name="origin" value={origin} onChange={(event) => { const value = event.target.value.toUpperCase().replace(/[^A-Z]/g, ""); setOrigin(value); saveField("origin", value); }} placeholder="e.g. KOUN" maxLength={4} pattern="[A-Z]{4}" title="Enter a 4-letter ICAO code" autoComplete="off" required />
          </label>
          <label className="field">
            <span className="field-label">Destination Airport</span>
            <input className="route-input" name="destination" value={destination} onChange={(event) => { const value = event.target.value.toUpperCase().replace(/[^A-Z]/g, ""); setDestination(value); saveField("destination", value); }} placeholder="e.g. KDAL" maxLength={4} pattern="[A-Z]{4}" title="Enter a 4-letter ICAO code" autoComplete="off" required />
          </label>
          <label className="field">
            <span className="field-label">Cruise Elevation (ft)</span>
            <input className="route-input" name="altitude" type="text" inputMode="numeric" maxLength={5} pattern="(?:[0-5]?[0-9]{1,4}|60000)" title="Enter a number from 0 to 60,000 feet" value={altitude} onChange={(event) => { const value = event.target.value.replace(/\D/g, "").slice(0, 5); setAltitude(value); saveField("altitude", value); }} onBlur={(event) => { const value = event.target.value.replace(/^0+(?=\d)/, ""); setAltitude(value); saveField("altitude", value); }} placeholder="e.g. 10000" required />
          </label>
          <label className="field">
            <span className="field-label">Power Setting (%)</span>
            <input className="route-input" name="powerSetting" type="text" inputMode="numeric" maxLength={2} pattern="(?:50|55|60|65|70|75)" title="Choose 50, 55, 60, 65, 70, or 75 percent" value={powerSetting} onChange={(event) => { const value = event.target.value.replace(/\D/g, "").slice(0, 2); setPowerSetting(value); saveField("powerSetting", value); event.target.setCustomValidity(""); }} onBlur={(event) => { if (event.target.value && !allowedPowerSettings.includes(event.target.value)) event.target.setCustomValidity("Choose 50, 55, 60, 65, 70, or 75 percent."); else event.target.setCustomValidity(""); }} placeholder="e.g. 65" required />
          </label>
          <label className="field">
            <span className="field-label">Usable Fuel (gallons)</span>
            <input className="route-input" name="usableFuel" type="text" inputMode="decimal" pattern="(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)" title="Enter 0 or more gallons" value={usableFuel} onChange={(event) => { const raw = event.target.value; if (raw.includes("-")) return; const cleaned = raw.replace(/[^0-9.]/g, ""); const [whole, ...fractions] = cleaned.split("."); const value = fractions.length ? `${whole}.${fractions.join("")}` : whole; setUsableFuel(value); saveField("usableFuel", value); }} onBlur={(event) => { let value = event.target.value.replace(/^0+(?=\d)/, ""); if (value.startsWith(".")) value = `0${value}`; setUsableFuel(value); saveField("usableFuel", value); }} placeholder="e.g. 50" required />
          </label>
        </div>
        <a className="calculate-button" href="calculations.html" onClick={(event) => { if (!event.currentTarget.closest("form").reportValidity()) event.preventDefault(); }}>
          <span>Calculate Flight</span>
        </a>
      </form>
    </section>
  );
}

function AirplaneMark() {
  return (
    <svg className="heading-plane" viewBox="0 0 340 220" aria-hidden="true">
      <path d="M28 55 C20 51 13 55 17 64 L34 101 C39 112 47 117 61 120 L111 131 L76 172 C70 179 76 185 85 184 L104 183 L191 128 L246 128 C270 128 294 120 300 113 C305 106 289 95 276 88 C266 82 252 80 238 80 L151 80 L81 31 C73 25 63 25 55 27 L51 30 L86 80 L60 80 Z" />
      <path d="M201 128 L232 128" />
      <g>
        <rect x="105" y="91" width="9" height="18" rx="4.5" /><rect x="128" y="91" width="9" height="18" rx="4.5" />
        <rect x="151" y="91" width="9" height="18" rx="4.5" /><rect x="174" y="91" width="9" height="18" rx="4.5" />
        <rect x="197" y="91" width="9" height="18" rx="4.5" /><rect x="220" y="91" width="9" height="18" rx="4.5" />
        <rect x="243" y="91" width="9" height="18" rx="4.5" />
      </g>
    </svg>
  );
}

function HomePage() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="sidebar-brand" href="index.html" aria-label="FA26 Flight Planner home">
          <span className="sidebar-brand-mark" aria-hidden="true">✈</span>
          <span className="sidebar-brand-name"><strong>fa26</strong><small>FLIGHT PLANNER</small></span>
        </a>
        <p className="sidebar-section-label">FLIGHT TOOLS</p>
        <nav className="sidebar-nav" aria-label="Main navigation">
          <a className="sidebar-link" href="map.html"><span className="sidebar-icon" aria-hidden="true">🗺️</span><span>Map</span></a>
          <a className="sidebar-link" href="teach.html"><span className="sidebar-icon" aria-hidden="true">🧑‍🏫</span><span>Learn the Math</span></a>
          <a className="sidebar-link" href="weather.html"><span className="sidebar-icon" aria-hidden="true">☀️</span><span>Return Weather Data</span></a>
        </nav>
      </aside>
      <main className="flight-planner-home">
      <div className="decorative-sun" aria-hidden="true" />
      <div className="decorative-cloud" aria-hidden="true">
        <span className="cloud-middle-puff" />
      </div>
      <h1 id="page-title" className="page-title">fa26-Flightplanner</h1>
      <RouteForm />
    </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<HomePage />);
