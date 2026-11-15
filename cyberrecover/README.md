# CyberRecover – Cyberattack Disaster Recovery Toolkit

Hackathon topic: **Disaster Recovery** (cyberattack variant: phishing, tech support scams, ransomware).

## Run it (no install, no build)
- **Easiest:** double-click `index.html`.
- **Or serve locally:** `python -m http.server 8000` in this folder, then open http://localhost:8000
- **Host free:** push to GitHub, then Settings → Pages → Deploy from branch `main` / root. Or drag the folder onto https://app.netlify.com/drop

## Judge walkthrough (about 2 minutes)
1. **Start here:** click "Files are locked / ransom note" to open the ransomware playbook with the incident clock running.
2. **Phishing checker:** click *Load sample*, then *Analyze*. It flags urgency, a lookalike link, a remote-access request and a risky attachment.
3. **Response playbook:** tick steps, watch progress, click *Export incident log*.
4. **Readiness score:** tick what you have. The score and "fix these first" list update live.
5. **Community alert:** generate a ready-to-send warning for staff, family or neighbours.

## Disaster recovery coverage
| Phase | Feature |
|---|---|
| Preparedness / continuity | Readiness score (offline backups, restore tests, MFA, RTO, plan) |
| Prevention / detection | Phishing and scam checker |
| Rapid response / recovery | Timed playbooks: Contain, Assess, Eradicate, Recover, Learn |
| Data protection | Backup-focused steps and checks (3-2-1-1-0) |
| Community support | Alert generator and reporting resources |

## Notes
- Pure HTML/CSS/JS. Everything runs client-side; progress is saved in `localStorage` only, and no data leaves the browser.
- The phishing checker uses rule-based heuristics. It is a guide, not a guarantee.
- Reporting links are US examples; swap in your country's agencies.
