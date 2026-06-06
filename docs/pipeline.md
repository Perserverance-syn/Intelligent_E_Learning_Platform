# CI Pipeline — SmartLearn AI API

## Overview

Every pull request targeting `main` must pass two gates before merging:

| Gate | Job | Blocks PR |
|---|---|---|
| Unit tests | `test` | Yes |
| SonarQube Quality Gate | `sonar` | Yes |

## Files

```
.github/workflows/ci.yml
sonar-project.properties
docs/pipeline.md
```

## Setup

### Secrets

Add these in Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `SONAR_TOKEN` | Token from SonarCloud: My Account → Security → Generate Token |
| `SONAR_HOST_URL` | `https://sonarcloud.io` |

### Branch protection on main

Settings → Branches → main → Edit:

- Require a pull request before merging
- Require status checks to pass:
  - `Run Tests`
  - `SonarQube Scan`
- Require branches to be up to date before merging

## How the Quality Gate works

Uses SonarCloud's Clean as You Code mode. Only lines changed in the PR are evaluated. Pre-existing issues in untouched files do not block the PR.

## Extending the pipeline

### Add linting

```yaml
- name: Lint with flake8
  run: |
    pip install flake8
    flake8 backend/ --max-line-length=120 --exclude=__pycache__
```

### Add SAST (Bandit)

```yaml
- name: Bandit SAST scan
  run: |
    pip install bandit
    bandit -r backend/ -f json -o bandit-report.json || true
```

Add to sonar-project.properties:
```
sonar.python.bandit.reportPaths=bandit-report.json
```

### Add dependency scanning (Trivy)

```yaml
- name: Trivy SCA scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: fs
    scan-ref: .
    format: sarif
    output: trivy-results.sarif
    severity: HIGH,CRITICAL
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pip install` fails | Check `backend/requirements.txt` exists |
| "Project not found" in Sonar | `sonar.projectKey` must match exactly |
| Quality Gate times out | SonarCloud server unreachable — check token |
| No Sonar comment on PR | Enable PR decoration in SonarCloud project settings |
| OpenAI import error | Add missing env vars to the `env` block in `ci.yml` |
