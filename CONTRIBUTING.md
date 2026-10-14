# Contributing

Thanks for contributing to Dynamic UNL Scoring!

We welcome contributions from the community. Whether it's a bug fix, new feature, or documentation improvement, your help is greatly appreciated.

## Getting Started

### Prerequisites

- Python 3.12+ ([python.org](https://www.python.org) or [pyenv](https://github.com/pyenv/pyenv))
- Docker and Docker Compose

### Setup

1. Fork the repository at [github.com/postfiatorg/dynamic-unl-scoring](https://github.com/postfiatorg/dynamic-unl-scoring)
2. Clone your fork:

```bash
git clone git@github.com:YOUR_USERNAME/dynamic-unl-scoring.git
cd dynamic-unl-scoring
git remote add upstream git@github.com:postfiatorg/dynamic-unl-scoring.git
```

3. Install dependencies and configure environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

4. Start the scoring service with PostgreSQL:

```bash
docker compose up
```

5. Verify:

```bash
curl http://localhost:8001/health
```

### Working on a Feature or Fix

```bash
git fetch upstream main
git checkout -b your-branch-name upstream/main
```

When ready to submit, push your branch and open a pull request against `main`.

## Before You Start

Open an issue first and wait for a maintainer go-ahead before writing code. This keeps effort on changes the project actually needs and avoids duplicate work.

Defensive or hardening changes are accepted only with evidence that the bad input actually occurs in a deployed environment: a log excerpt, a captured response, or a failed round. Guards against inputs that have never been observed are closed.

## Pull Request Requirements

Before submitting a PR:

- Run `pytest` and fix any failures
- Run `docker compose build` to confirm the Docker build succeeds
- Mark your PR as a [draft](https://github.blog/2019-02-14-introducing-draft-pull-requests/) until it's ready for review
- Fill in the PR template with a clear description of your changes
- Keep PRs focused — one feature or fix per PR
- Link the approved issue in the PR description

### Hash-pinned scoring modules

The validator sidecars pin these files by content hash and fail closed on any change:

- `scoring_service/services/response_parser.py`
- `scoring_service/services/unl_selector.py`
- `scoring_service/services/score_formula.py`
- `scoring_service/services/diversity_formula.py`
- `scoring_service/services/commit_reveal.py`

Changing a single byte of them forces every validator operator to upgrade their sidecar before the next round. These files only change together with a planned behavioral change and a coordinated sidecar release. Open an issue and wait for a maintainer go-ahead before starting a PR that touches them; unsolicited PRs against these files are closed.

## Repository Layout

- `scoring_service/` — FastAPI scoring service (main application)
- `migrations/` — PostgreSQL schema migrations
- `tests/` — Test suite (pytest)
- `scripts/` — Standalone CLI tools (scoring, data fetching, ASN lookup)
- `infra/` — Modal LLM deployment
- `prompts/` — Scoring prompt templates
- `data/` — Validator snapshots and ASN data
- `phase0/` — Phase 0 archival (benchmarks, results, documentation)
- `docs/` — Active roadmap

## Code Style

- Follow existing patterns in the codebase
- Type hints for function signatures
- Pydantic models for structured data
