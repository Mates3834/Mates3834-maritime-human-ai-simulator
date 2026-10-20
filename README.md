# Maritime Human–AI Teaming Lab

**Interactive research prototype for explainable AI-assisted maritime traffic decisions.**

A Streamlit dashboard exploring how a human operator can review, accept, reject, or modify a geometric AI-style course suggestion during synthetic vessel encounters. Developed as a portfolio demonstration related to human–AI collaboration in maritime operations.

> **Research/education only — NOT FOR NAVIGATION.** This is not a certified collision-avoidance system, does not implement validated COLREG compliance, and must not be used to make real vessel maneuvering decisions.

## Overview

The prototype combines a radar-style Plotly display with simple relative-motion calculations and a human-in-the-loop decision workflow. It illustrates *interaction design* rather than a trained machine-learning model. The recommendation is a deterministic, geometry-based candidate-heading search, **not** a learned AI policy.

## Features

- **Three synthetic encounters:** crossing (starboard), head-on, and overtaking
- **Radar-style display:** vessel symbols, heading, track history, projected tracks, closest-approach indicator, and candidate route
- **Risk metrics:** distance at closest point of approach (DCPA/CPA) and time to CPA (TCPA)
- **Three modes:** Human Only, AI Only, and Human + AI
- **Operator interaction:** accept, reject, or modify a suggested maneuver
- **Experiment log:** timestamp, scenario, mode, decision, course change, and pre-decision CPA/TCPA; CSV export
- **Adjustable settings:** scenario, step length, and illustrative position uncertainty

## Radar preview

![Illustrative radar preview](assets/radar_preview.png)

**Image provenance:** `assets/radar_preview.png` is an illustrative figure reconstructed from the demo's vessel geometry, **not a screenshot of the running Streamlit interface**. The live radar is generated dynamically with Plotly in `app.py`.

To add an authentic dashboard screenshot:

1. Run `streamlit run app.py` locally.
2. Choose **Human + AI** and **Head-on** in the sidebar.
3. Capture the radar, metrics and decision-support panel.
4. Save the screenshot to `assets/dashboard.png` and add `![Live application screenshot](assets/dashboard.png)` here.

### How to read the radar

| Visual element | Meaning |
| --- | --- |
| Cyan vessel | Own ship and its current heading |
| Orange vessel | Synthetic target vessel |
| Cyan dashed line | Own ship's constant-course projected path |
| Orange dashed line | Target's constant-course projected path |
| Green line | Geometry-based proposed heading, visible in AI modes |
| Red CPA marker/segment | Projected closest-approach location or separation |
| Concentric rings | Relative distance around own ship, in nautical miles |

The radar uses **local East/North coordinates in nautical miles**, not georeferenced nautical charts or live AIS. The ship shapes are symbolic and not to scale. Zoom/pan is supported in the live Plotly view.

### Dashboard panels and controls

- **Current DCPA** — predicted minimum separation assuming constant current velocities.
- **TCPA** — time until that predicted closest approach; nonnegative and displayed in minutes.
- **Risk flag** — `HIGH` when DCPA is below `0.5 NM` **and** TCPA is below `30 min`, otherwise `LOW`. These are demo thresholds, not safety standards.
- **Own heading** — current simulated course clockwise from north.
- **Mode selector** — `Human Only` hides the recommendation; `AI Only` offers a deterministic suggestion to apply; `Human + AI` lets an operator accept, reject or modify it.
- **Scenario selector** — switches between crossing, head-on and overtaking initial conditions.
- **Position uncertainty** — display-only illustrative slider; **does not affect** CPA or recommendations.
- **Simulation step** — sets the amount of simulated time advanced per click.
- **Decision buttons** — change heading instantly, log a decision, but **do not advance time**.
- **Advance simulation** — moves vessels using constant speeds/headings for the selected step.
- **Experiment log** — records decisions; download CSV for analysis.

### Suggested demonstration walkthrough

1. Select **Head-on**, **Human + AI**.
2. Inspect the risk metrics and green suggested course line.
3. Choose **Accept AI** or set a manual alteration and choose **Modify**.
4. Click **Advance simulation** several times to observe projected tracks change.
5. Compare the same starting scenario in **Human Only** and **AI Only** after pressing **Reset scenario**.
6. Download the experiment CSV and inspect the recorded choices.

**Important limitations:** The recommendation is a simplified candidate-heading search, not a trained AI model or a verified COLREG implementation. The prototype does not model turning dynamics, environmental forces, multi-target traffic, probabilistic uncertainty, or actual human-subject performance. The demo log alone cannot substantiate claims that collaboration improves safety.

## Quick start

Requires Python 3.10+.

```bash
# Clone your repository (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/maritime-human-ai-teaming-lab.git
cd maritime-human-ai-teaming-lab

# Optional: create a virtual environment
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints the local URL (normally `http://localhost:8501`).

### Run without Git

Download the repository ZIP, extract it, open a terminal in the folder containing `app.py`, and run the final two commands above.

## Example workflow

1. Choose an encounter scenario in the sidebar.
2. Select **Human + AI** to display the recommended course change and projected DCPA.
3. Inspect the visualized traffic and rationale.
4. **Accept**, **Reject**, or **Modify** the proposal.
5. Advance the simulation by one time step to observe the updated vessel positions.
6. Export the decision log as CSV for later analysis.

**Modes:** Human Only hides AI advice; AI Only provides an apply-AI-action button; Human + AI supports explicit human responses. This is a simplified interaction demonstration, not a controlled human-subject experiment.

## Methods (simplified)

Vessel velocities are represented in an east/north coordinate frame. For relative position **r** and relative velocity **v**, time to closest approach is estimated by

\[
t_{CPA}=\max\left(0,-\frac{\mathbf r\cdot\mathbf v}{\|\mathbf v\|^2}\right)
\]

and closest-approach distance by

\[
DCPA=\|\mathbf r+\mathbf v t_{CPA}\|.
\]

The program compares geometric candidate headings and displays a suggested alteration with a projected DCPA. These calculations assume constant target motion and simplified instantaneous own-ship course changes. **A higher predicted DCPA alone does not establish a safe or COLREG-compliant maneuver.**

## Project structure

```text
maritime-human-ai-teaming-lab/
├── app.py              # Streamlit UI, kinematics, radar and decisions
├── requirements.txt    # Python dependencies
├── README.md           # Project description and usage
├── .gitignore          # Local files excluded from version control
└── assets/             # Add verified screenshots here
```

## Known limitations

- One target vessel and synthetic scenarios only
- Point-mass kinematics; no validated maneuvering dynamics or actuator limits
- No validated COLREG interpretation, route feasibility, or maritime safety assurance
- No real AIS, radar, weather, or sea-state data
- Position-uncertainty slider is displayed but **not** propagated into risk estimates
- Rule/geometry-based recommendation; no trained AI model
- No empirical evidence of improved safety, workload, trust, or decision quality
- Operator logs are for demonstration; no human-subject study has been conducted

## Research roadmap

- [ ] Add reproducible encounter scenario files and automated unit tests
- [ ] Introduce explicit COLREG reasoning with rule-specific test cases
- [ ] Add multi-vessel traffic and ship maneuvering constraints
- [ ] Propagate sensor uncertainty into probabilistic risk estimates
- [ ] Compare explanation styles and operator override behavior
- [ ] Design an ethics-approved user study before making human-performance claims

## Technology

Python · Streamlit · NumPy · Pandas · Plotly

## Attribution and use

This repository is an independent educational research prototype. It is not an official NTNU project or an affiliated maritime navigation product. Add an appropriate license only after deciding how you want others to reuse the code.
