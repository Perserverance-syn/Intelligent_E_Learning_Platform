# CI Pipeline — SmartLearn AI API

## What this pipeline does

Every pull request targeting `main` must pass two gates before it can be merged:

| Gate | Job | Fail = PR blocked? |
|---|---|---|
| Unit tests pass | `test` | Yes (once branch protection is set) |
| SonarQube Quality Gate | `sonar` | Yes |

SonarQube results (issues, coverage, Quality Gate verdict) are visible directly on the PR via the SonarQube/SonarCloud PR decoration feature.

---

## Files

```
.github/
  workflows/
    ci.yml                ← the pipeline definition
sonar-project.properties  ← tells Sonar what to scan
docs/
  pipeline.md             ← this file
```

---

## One-time setup (do this once, then forget it)

### 1 — Add secrets to the repo

Go to **Settings → Secrets and variables → Actions → New repository secret**.

| Secret name | Value |
|---|---|
| `SONAR_TOKEN` | Token generated in SonarQube: *My Account → Security → Generate Token* |
| `SONAR_HOST_URL` | Your SonarQube server URL, e.g. `http://your-server:9000` |

> **SonarCloud instead of self-hosted?** Set `SONAR_HOST_URL` to `https://sonarcloud.io`, uncomment `sonar.organization` in `sonar-project.properties`, and remove `SONAR_HOST_URL` from the env section of `ci.yml` (SonarCloud infers it).

### 2 — Create the project in SonarQube

In the SonarQube UI: **Create Project → Manually**.  
Set the project key to exactly `Intelligent_E_Learning_Platform` (must match `sonar.projectKey`).  
Select **"Clean as You Code"** as the analysis method — this scopes the Quality Gate to new code only, so old issues don't block every PR.

### 3 — Enable PR decoration (so results show on the PR)

In SonarQube: **Administration → DevOps Platform Integrations → GitHub**.  
Add your GitHub App credentials. After this, Sonar posts a comment and status check directly on each PR.

### 4 — Set branch protection on main

Do this **after** opening one test PR so the checks appear in the dropdown.

Settings → Branches → main → Edit:

- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  - Add: `Run Tests` (the `test` job)
  - Add: `SonarQube Scan` (the `sonar` job)
- ✅ Require branches to be up to date before merging

> ⚠️ Do **not** enable "Require code quality results" — that's GitHub's own CodeQL integration, not SonarQube.

---

## How the Quality Gate works

The pipeline uses SonarQube's **"Clean as You Code"** mode. The gate evaluates **only the lines changed in the PR**, not the entire codebase. This means:

- Pre-existing issues in untouched files → **not gated, won't block your PR**
- New issues introduced in your PR diff → **gated, will block**

Default thresholds (configurable in SonarQube → Quality Gates):

| Metric | Threshold |
|---|---|
| New bugs | 0 |
| New vulnerabilities | 0 |
| New code smells coverage | Warn only |
| New code coverage | ≥ 80% (adjust to taste) |

---

## Extending the pipeline

### Add a new check (e.g. linting)

Add a step inside the `test` job, before pytest:

```yaml
- name: Lint with flake8
  run: |
    pip install flake8
    flake8 . --max-line-length=120 --exclude=migrations,__pycache__
```

### Add SAST (Bandit — Python security linter)

```yaml
- name: Bandit SAST scan
  run: |
    pip install bandit
    bandit -r . -x ./tests -f json -o bandit-report.json || true

- name: Upload Bandit report
  uses: actions/upload-artifact@v4
  with:
    name: bandit-report
    path: bandit-report.json
```

SonarQube can also ingest Bandit output — add to `sonar-project.properties`:
```
sonar.python.bandit.reportPaths=bandit-report.json
```

### Add dependency scanning (SBOM / SCA)

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

### Change Python version

Edit `python-version` in `ci.yml`. Current value: `3.11`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `test` job fails at `pip install` | `requirements.txt` path wrong | Confirm file is at repo root, same level as `ci.yml`'s `working-directory` |
| `sonar` job: "Project not found" | `sonar.projectKey` mismatch | Must match exactly what you created in SonarQube UI |
| Quality Gate never resolves (timeout) | SonarQube server unreachable from GitHub runner | Confirm public URL; check firewall/security group on port 9000 |
| PR shows no Sonar comment | PR decoration not configured | Complete step 3 (DevOps Platform Integration) in SonarQube |
| `coverage.xml` not found by Sonar | pytest produced no output (0 tests) | `|| true` in `ci.yml` prevents failure, but Sonar needs the file — add a trivial test |
| OpenAI import error at test time | `OPENAI_API_KEY` not stubbed | Already handled by the `env` block in `ci.yml`; if adding new keys, add them there |
