import React from "react";
import { createRoot } from "react-dom/client";
import "./weather.css";

// Placeholder conditions until the weather API is connected.
const sampleWeather = {
  KOUN: { city: "Norman, OK", temperature: 22, dewPoint: 16, wind: 180, windSpeed: 10, windGust: 15, visibility: 10, altimeter: "29.92", flightCategory: "VFR" },
  KLAW: { city: "Lawton, OK", temperature: 24, dewPoint: 17, wind: 190, windSpeed: 12, windGust: 18, visibility: 10, altimeter: "29.91", flightCategory: "VFR" },
};

function getSavedFlight() {
  try {
    return JSON.parse(localStorage.getItem("fa26-flight") || "{}") || {};
  } catch {
    return {};
  }
}

function WeatherCard({ label, airportCode }) {
  const data = sampleWeather[airportCode] || sampleWeather[label === "Origin" ? "KOUN" : "KLAW"];
  return (
    <section className="weather-column" aria-label={`${label} weather`}>
      <header className="airport-heading">
        <div><strong><u>{label}:</u></strong> {airportCode}</div>
        <div>{sampleWeather[airportCode]?.city || "Airport location unavailable"}</div>
      </header>
      <div className="conditions-card">
        <h2><u>Current Conditions</u></h2>
        <div className="condition-group">
          <p><strong>Temperature:</strong> {data.temperature}°C</p>
          <p><strong>Dew Point:</strong> {data.dewPoint}°C</p>
        </div>
        <div className="condition-group">
          <p><strong>Wind:</strong> {data.wind}°</p>
          <p><strong>Wind Speed:</strong> {data.windSpeed} kt</p>
          <p><strong>Wind Gust:</strong> {data.windGust} kt</p>
        </div>
        <div className="condition-group">
          <p><strong>Visibility:</strong> {data.visibility} SM</p>
          <p><strong>Altimeter:</strong> {data.altimeter} inHg</p>
        </div>
        <div className="condition-group">
          <p><strong>Flight Category:</strong> {data.flightCategory}</p>
        </div>
      </div>
    </section>
  );
}

function WeatherPage() {
  const saved = getSavedFlight();
  const origin = saved.origin || "KOUN";
  const destination = saved.destination || "KLAW";
  return (
    <main className="weather-page">
      <div className="weather-panel">
        <div className="weather-grid">
          <WeatherCard label="Origin" airportCode={origin} />
          <WeatherCard label="Destination" airportCode={destination} />
        </div>
      </div>
      <a className="back-button" href="index.html">Back</a>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<WeatherPage />);
