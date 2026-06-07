# CI Pipeline — SmartLearn AI API

## Overview

Every pull request targeting `main` runs two independent checks, both required to pass before merging:

| Check | Job | What it does | Blocks merge |
|---|---|---|---|
| Unit Tests | `test` | Runs pytest against the backend test suite | Yes — if any test fails |
| SonarQube Scan | `sonar` | Static analysis + security scan, evaluates the Quality Gate | Yes — if the gate fails |

The two jobs run in parallel and report independently, so a test failure and a Quality Gate failure are visible as separate red checks on the PR.

## Scope

- In scope: backend static analysis, security scanning, unit-test execution, merge enforcement.
- Out of scope: API / integration tests. These require the full backend test suite (DB fixtures, auth tokens, mocked external calls) and are the development team's responsibility. The pipeline already runs anything placed in backend/tests/, so adding them later requires no pipeline changes.

## Secrets

| Secret | Value |
|---|---|
| SONAR_TOKEN | Token from SonarCloud → My Account → Security |
| SONAR_HOST_URL | https://sonarcloud.io |

## Branch protection (main)

- Require a pull request before merging
- Require status checks to pass: Unit Tests, SonarQube Scan

## How the Quality Gate works

Uses SonarCloud "Sonar way" in Clean as You Code mode: only lines changed in the PR are evaluated. Pre-existing issues in untouched files do not block a PR.

## Demonstrating the gates

- Test failure: add a failing test in backend/tests/, push → Unit Tests goes red, merge blocked.
- Gate failure: a PR with security issues or low new-code coverage fails SonarQube Scan.
- Pass state: clean, tested code passes both checks and is mergeable.

## Troubleshooting

| Symptom | Fix |
|---|---|
| pytest ModuleNotFoundError | Add the missing dependency, or test isolated modules |
| folder backend/tests does not exist | Ensure the tests folder exists on the branch |
| can't be indexed twice | Exclude the tests path from sources in sonar.exclusions |
| Quality Gate FAILED | Expected — fix flagged issues or adjust the gate |
