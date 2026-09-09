# Cross-Country Flight Planner
### CS 4273 Capstone Design Project - Fall 2026
**Group:** D
***Version:*** This document is updated to the latest date (09/08/2026) to reflect Group D's understanding of the domain, current project scope, identified technologies and tools, key project feature, unit-test examples, goals, and planned development progress for Ticket 2 Artifact.

## Team Members
- Reese Zimmermann — Product Owner
- Avinash Kandadi — Sprint Master 1
- Sahith Gondi — Sprint Master 2
- Sean Ropp — Sprint Master 3
- Elise Alvarado — Sprint Master 4
- Nic Grounds — Mentor / Client

## Project Description

The Flight Planner project is a software-based system designed to assist pilots with cross-country flight planning by replacing the traditional pen-and-paper process used.

Traditionally, pilots use paper navigation logs, aircraft performance information, weather data, route information, and tools such as the 
E6-B flight computer to determine factors including distance, flight time, fuel consumption, headings, waypoints, climb performance, and descent performance.

Beyond serving solely as a planning tool, the system is designed to double as a **learning and practice tool**, helping students and new pilots understand and work through the flight-planning process step-by-step, rather than simply producing a final number.

The goal of this project is to create a system intended to serve two purposes:

1. **Flight-planning assistance** — Help pilots organize the information and calculations involved in preparing a cross-country flight.
2. **Learning and practice** — Allow users to practice and better understand the calculations and decision-making involved in traditional flight planning.

The software is intended to support the pilot's decision-making process rather than replace official aviation resources or pilot judgment.

## Identified Technologies & Tools

| Technology | Purpose |
|---|---|
| **Python** | Primary programming language for implementing mathematical and data-processing logic for calculations involving flight time, fuel consumption, climb and descent performance, waypoint calculations, aircraft performance information, and weather information|
| **AviationWeather.gov / SkyVector.com APIs** | Live aviation weather data  [METAR](https://aviationweather.gov/api/data/metar) and [TAF](https://aviationweather.gov/api/data/taf) endpoints feed real wind, visibility, and forecast data into the planning calculations |
| **Docker** | Containerizes the application for a consistent development and deployment environment across all team members |
| **GitHub Actions** | CI/CD pipeline to runs automated unit tests and checks on every push/PR to catch issues early |
| **Jira** | Project planning and task organization to track team progress |

### Learning Resources
- Python: [learnpython.org](https://www.learnpython.org/)
- GitHub Actions: [docs.github.com/en/actions](https://docs.github.com/en/actions)
- Docker: [Docker 101 Tutorial](https://www.docker.com/101-tutorial/)
- Jira: [Atlassian Jira Getting Started Guide](https://www.atlassian.com/software/jira/guides/getting-started/introduction)
- Aviation weather data: aviationweather.gov / SkyVector.com

## Key Project Feature: Density Altitude Calculation

One of the calculations the system replaces from the E6-B and paper performance charts is **density altitude** the pressure altitude corrected for temperature. It's the single input that nearly every other performance chart in the aircraft's POH depends on: rate of climb, true airspeed, takeoff/landing distance, and range are all plotted against density altitude.

**Inputs:**
- Pressure Altitude (PA) — altitude read off the altimeter when set to 29.92" Hg
- Outside Air Temperature (OAT), in °C

**Output:** Density Altitude (ft) — used downstream by the system to look up expected climb rate, true airspeed, takeoff/landing distance, and fuel range for the planned flight.

**Why this feature matters:** Nearly every aircraft performance figure (climb rate, takeoff roll, landing distance, range) is only accurate once corrected for density altitude. Getting this calculation right is important for the rest of the performance-planning features build on.

## Goals & Progress Plan

**Overall goal:** Deliver a working flight-planning tool by the end of the semester that a pilot or student could realistically use to plan a cross-country flight, with wind, fuel, distance, and waypoint calculations pulling from live aviation weather data.

**Progress plan (tracked via Jira, tickets scoped per sprint):**

1. **Domain understanding & tech setup**  — finalize tech stack, set up Docker environment, connect to aviationweather.gov endpoints, confirm formulas for wind triangle/fuel/distance calculations.
2. **Core calculation engine** — implement and unit-test wind correction angle, ground speed, fuel burn, and distance/waypoint calculations in Python.
3. **Weather data integration** — pull live METAR/TAF data from aviationweather.gov and feed it into the calculation engine.
4. **CI/CD pipeline** — set up GitHub Actions to run the test suite automatically on every push/PR.
5. **User-facing interface** — build a simple UI for entering a route and viewing the full flight plan output.
6. **Practice/learning mode** — add a mode that walks a user through the planning process step-by-step rather than just showing final results.
7. **Review & polish** — incorporate feedback from our mentor, refine documentation and test coverage.

## Repository

**GitHub Repository:**  
https://github.com/OU-CS-4273-Capstone-Grounds/fa26-flightplanner
