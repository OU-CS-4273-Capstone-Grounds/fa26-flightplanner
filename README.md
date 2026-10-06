# Cross-Country Flight Planner
### CS 4273 Capstone Design Project (Fall 2026) - Group D

**Last Updated:** October 6, 2026

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

## Start the CLI

### Run locally

Python 3.13 is recommended. From the repository root, create and activate a virtual environment, install the dependencies, and start the CLI:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main
```

The CLI will prompt you for the four-letter ICAO identifiers of the departure and destination airports.

### Run with Docker

From the repository root, build the image and run it with an interactive terminal:

```bash
docker build -t flight-planner .
docker run --rm -it flight-planner
```

## Identified Technologies & Tools

| Technology | Purpose |
|---|---|
| **Python** | Primary programming language for implementing mathematical and data-processing logic for calculations involving flight time, fuel consumption, climb and descent performance, waypoint calculations, aircraft performance information, and weather information|
| **AviationWeather.gov / SkyVector.com APIs** | Live aviation weather data  [METAR](https://aviationweather.gov/api/data/metar) and [TAF](https://aviationweather.gov/api/data/taf) endpoints feed real wind, visibility, and forecast data into the planning calculations |
| **Docker** | Packages the Python backend and its dependencies into an image for consistent development and deployment |
| **GitHub Actions** | Runs automated tests and Docker build checks on pushes/PRs; planned deployment automation will publish images and trigger hosting updates after successful checks on `main` |
| **GitHub Container Registry (GHCR)** | Will store versioned backend Docker images built by GitHub Actions |
| **Render Web Service** | Will pull the backend image from GHCR and run the Python HTTP API at a public HTTPS URL |
| **GitHub Pages** | Will host the static frontend, which calls the Render backend from the user's browser |
| **Jira** | Project planning and task organization to track team progress |

### Learning Resources
- Python: [learnpython.org](https://www.learnpython.org/)
- GitHub Actions: [docs.github.com/en/actions](https://docs.github.com/en/actions)
- Docker: [Docker 101 Tutorial](https://www.docker.com/101-tutorial/)
- GHCR: [Publishing Docker images with GitHub Actions](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
- Render: [Deploy a prebuilt Docker image](https://render.com/docs/deploying-an-image)
- GitHub Pages: [What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- Jira: [Atlassian Jira Getting Started Guide](https://www.atlassian.com/software/jira/guides/getting-started/introduction)
- Aviation weather data: aviationweather.gov / SkyVector.com

## Planned Hosting and Deployment Workflow

The frontend will be hosted on **GitHub Pages**, and the Python backend will run as a **Render Web Service**. **GitHub Container Registry (GHCR)** will store the backend Docker images. GitHub Actions will connect these services by testing changes, building and publishing images, and triggering deployment.

**Current status:** The repository has a Python CLI and CI jobs for unit tests and Docker builds. The HTTP API, frontend, image publishing, and hosting deployments still need to be implemented. Before deploying to Render, add an API layer (such as FastAPI) around the existing Python modules and change the container startup command to run an HTTP server instead of the interactive CLI.

### Deployment Steps

1. Team members create a feature branch from the latest `main`, push changes to that feature branch, and open a pull request into `main`.
2. GitHub Actions runs the backend checks (Python tests and Docker build) and frontend checks (tests and production build) independently on the pull request.
3. If both sets of checks pass, the pull request is eligible for review and merge. Passing checks do not deploy code from the feature branch.
4. If either set of checks fails, the pull request is blocked from merging. This includes cases where the backend passes but the frontend fails, or the frontend passes but the backend fails. Team members fix the failed check on the same feature branch, and GitHub Actions reruns the checks. Neither component is deployed while the pull request is blocked.
5. After the pull request merges into `main`, GitHub Actions reruns both sets of checks against the merged commit. A shared release gate continues only when both sets pass.
6. After the release gate passes, GitHub Actions publishes the backend image to `ghcr.io/ou-cs-4273-capstone-grounds/fa26-flightplanner`, tagged "latest", and calls a Render deploy hook. Render pulls the image and starts the backend. Publishing a new image alone does not trigger a Render deployment.
7. The same release deploys the successfully built frontend to GitHub Pages. If either check fails on `main`, neither the backend nor frontend is deployed, and the last successful versions remain live.
8. Users open the frontend in their browser. It sends HTTPS requests to the Render API, which performs calculations or fetches aviation weather and returns JSON results.

### Workflow Diagram

```mermaid
flowchart TD
    A["Create feature branch from latest main"] --> B["Push changes and open pull request"]
    B --> C["Backend tests and Docker build"]
    B --> D["Frontend tests and production build"]
    C --> E{"Both checks pass?"}
    D --> E
    E -->|No| F["Block merge; fix failed check; no deployment"]
    F --> B
    E -->|Yes| G["Eligible for review and merge"]
    G --> H["Merge into main and rerun both checks"]
    H --> I{"Both checks pass on main?"}
    I -->|No| J["Keep last successful backend and frontend live"]
    I -->|Yes| K["Release gate opens"]
    K --> L["Publish backend image to GHCR"]
    L --> M["Trigger Render deploy hook"]
    M --> N["Render runs Python API"]
    K --> O["Deploy frontend to GitHub Pages"]
    O --> P["User opens frontend in browser"]
    P <-->|HTTPS requests / JSON results| N
    N <-->|Weather requests / responses| Q["AviationWeather.gov"]
```

### Hosting Configuration

- **Image publishing:** Use the GitHub Actions `GITHUB_TOKEN` with `contents: read` and `packages: write`. Build a `linux/amd64` image for Render and deploy a specific image digest or commit tag so releases are traceable.
- **Render:** Select **Web Service**, then **Existing Image**, and supply the GHCR image URL. If the image is private, configure a registry credential with `read:packages`. Store the Render deploy hook URL as a GitHub Actions secret.
- **Backend:** Listen on `0.0.0.0` and the port configured by Render. Allow the frontend origin, `https://ou-cs-4273-capstone-grounds.github.io`, through CORS.
- **Frontend:** Configure the Render API's HTTPS URL and the GitHub Pages project base path, `/fa26-flightplanner/`. Keep credentials in backend environment variables or GitHub Actions secrets.

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
