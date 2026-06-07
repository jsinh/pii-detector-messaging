# pii-detector-messaging

> PII detection where generic tools fail: 160-char SMS, conversational text, partial identifiers, adversarial obfuscation. Hybrid regex + fine-tuned NER + LLM pipeline with compliance-weighted eval (false negatives cost 10x false positives). Open reference implementation.

## Why this exists

Try running Presidio or AWS Comprehend on a 160-character SMS that reads `dm me at j dot sinh, talk soon`. It misses the email reference entirely. So does spaCy's stock NER. So does most off-the-shelf PII tooling - they are optimised for the long-form documents enterprises classified ten years ago, not the conversational, abbreviated, deliberately obfuscated text that flows through messaging today.

That gap matters. Messaging is now where most regulated communication actually happens - SMS, MMS, WhatsApp, email bodies threaded with quoted replies. The PII that needs to be detected, redacted, or flagged in that channel does not look like the PII in a contract or an HR document. It is shorter. It is coded. People typing on phones at 11 PM do not write "my email address is firstname.lastname@example.com." They write "msg me, j at jsinh dot com." Generic detectors trained on legal corpora do not catch that, and retrofitting them with more regex eventually hits a wall.

I have spent years working in real-time communications and compliance-adjacent infrastructure. Every PII tool I have evaluated for messaging use cases has the same shape - built for documents, bolted onto messaging, brittle in the predictable places. So I am building one from the ground up for the messaging case, in the open, with the eval framework I wish those tools had shipped with.

## What this is (and is not)

A reference implementation. The goal is to demonstrate, on a real codebase with a real evaluation framework, how a messaging-aware PII detector should be built end-to-end. Three components:

1. **Regex layer** for the well-formed identifiers - conventionally-formatted emails, phone numbers, structured account references. Fast, cheap, catches the obvious 60-70%.
2. **Fine-tuned NER model** (DistilBERT or RoBERTa-base, depending on what survives the eval) for the patterned-but-context-dependent cases - names inside conversational sentences, partial addresses, indirect references.
3. **LLM fallback** for genuinely ambiguous edges - adversarial obfuscation, multi-turn references, novel patterns the NER has not seen. Slow, expensive, rare.

The interesting work is not in any single layer. It is in the routing logic between them, the compliance-weighted eval that decides whether the routing is correct, and the failure modes when two layers disagree.

This is *not* a production-ready library. Not yet, not by week 12, probably not ever - that is a different project with different priorities. It is not a drop-in Presidio replacement. It is not tied to any specific compliance regime; GDPR, HIPAA, and the EU AI Act all define PII differently, and reconciling that with your specific risk posture is the user's job to plug in on top of detection.

## Getting started

Works on **macOS, Linux, and Windows**. Two ways to run it: a local Python
environment, or Docker (no Python toolchain required).

### Prerequisites

| Tool | Version | Required for | Notes |
|---|---|---|---|
| [Python](https://www.python.org/downloads/) | 3.11+ (developed on 3.13) | Local install | `python3` on macOS/Linux, `python` on Windows |
| [Git](https://git-scm.com/downloads) | any recent | Cloning | |
| [Docker](https://docs.docker.com/get-docker/) | any recent | Container run | Optional — only for the Docker path |
| `make` | any | The `make` shortcuts | Optional. Preinstalled on macOS/Linux. On Windows use WSL, Git Bash, or run the underlying commands shown below |

### 1. Clone

```bash
git clone https://github.com/jsinh/pii-detector-messaging.git
cd pii-detector-messaging
```

### 2. Create and activate a virtual environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
```

> If PowerShell blocks activation with an execution-policy error, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 3. Install

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

This installs the project in **editable** mode from `src/` along with the dev
dependencies (pytest, httpx, ruff). Editable means your source edits are live
without reinstalling. (`make install` runs the second command for you.)

### 4. Run the API

Pick whichever you like — all four serve the same app on port 8000:

| Command | What it is | Binds |
|---|---|---|
| `make dev` | Dev server, auto-reload | `127.0.0.1` |
| `make run` | Production-style server | `0.0.0.0` |
| `pii-detector` | The installed console command (`make run` calls this) | `0.0.0.0` |
| `fastapi dev src/pii_detector/api/app.py` | The raw FastAPI dev command | `127.0.0.1` |

**Not using `make`** (e.g. Windows without WSL)? Run the commands directly:

```bash
fastapi dev src/pii_detector/api/app.py   # development, with auto-reload
pii-detector                              # production-style run
```

### 5. Verify it's up

- Liveness: [http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz)
- Readiness: [http://127.0.0.1:8000/readyz](http://127.0.0.1:8000/readyz)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Try the detect endpoint:

```bash
curl -X POST http://127.0.0.1:8000/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "dm me at j at jsinh dot com"}'
```

(Returns `{"entities":[]}` for now — the detection pipeline is a stub; the API
contract is live so you can integrate against it today.)

## Running with Docker

No local Python needed — just Docker.

```bash
make docker-build        # or: docker build -t pii-detector-messaging:latest .
make docker-run          # or: docker run --rm -p 8000:8000 pii-detector-messaging:latest
```

Then hit [http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz). The image
runs as a non-root user, binds `0.0.0.0:8000`, and ships a built-in healthcheck.

## Configuration

All settings have safe defaults, so the app runs with zero config. Override any
of them with environment variables (prefix `PII_`) or a local `.env` file (copy
[`.env.example`](./.env.example) to `.env`). Common knobs:

| Variable | Default | Purpose |
|---|---|---|
| `PII_HOST` | `0.0.0.0` | Bind address |
| `PII_PORT` | `8000` | Port |
| `PII_ENVIRONMENT` | `development` | `development` enables auto-reload for `pii-detector` |
| `PII_FN_FP_COST_RATIO` | `10` | Eval: cost of a false negative relative to a false positive |

## Development

```bash
make test      # run the test suite (or: pytest)
make lint      # lint with ruff   (or: ruff check src tests)
make format    # auto-format      (or: ruff format src tests)
make eval      # run eval on the sample dataset (or: pii-eval data/eval/sample.jsonl)
make help      # list all available commands
```

## Project layout

```
src/pii_detector/
├── api/            # Web layer (FastAPI). The only place the web framework lives.
│   ├── app.py      #   create_app() factory + the runnable `app` instance
│   ├── schemas.py  #   public request/response models (the wire contract)
│   └── routers/    #   endpoints: health.py (/healthz, /readyz), detect.py (/detect)
├── core/           # Cross-cutting infrastructure
│   └── config.py   #   env-driven settings (PII_* variables)
├── detection/      # THE PRODUCT — pure detection logic, no web framework
│   ├── types.py    #   EntityType + Entity (the domain vocabulary)
│   ├── base.py     #   Detector interface each layer implements
│   └── pipeline.py #   orchestrates regex -> NER -> LLM (currently a stub)
├── eval/           # Compliance-weighted evaluation framework
│   ├── metrics.py  #   per-entity precision/recall + weighted cost
│   ├── datasets.py #   JSONL gold-set loader
│   └── runner.py   #   `pii-eval` command
└── cli.py          # `pii-detector` command (starts the server)

data/eval/          # Evaluation datasets (JSONL)
tests/              # Test suite (pytest), mirrors the package structure
scripts/            # Standalone helper scripts
```

Design rule: `detection/` and `eval/` never import from `api/` — the detection
logic must be callable without a web server (from eval, batch jobs, notebooks).

## The eval framework

The component I am building first, because everything else is meaningless without it.

Precision and recall mean different things in compliance contexts. A false negative on PII in a regulated message is a potential exposure event with regulatory teeth. A false positive is an annoying over-redaction someone in ops complains about on Slack. The asymmetry is roughly 10:1 in favour of recall for most messaging compliance use cases - not always, but often enough that aggregate F1 lies to you about whether a model is fit for purpose.

The eval framework tracks:

- Precision and recall **per entity type**, never aggregated into a single score
- Errors weighted by compliance severity, with configurable cost ratios (10:1 is the default, not the rule)
- Latency budgets and cost per 1,000 messages, because production teams will ask
- A held-out adversarial set with deliberate obfuscation - homoglyphs, leetspeak, deliberate spacing, the kinds of evasion patterns real users employ when they do not want to be detected

## Status

Day 0. The repo exists, the architecture is sketched, the eval set seed is being assembled. I am building this in public over roughly 12 weeks on top of a day job and a side project, so the cadence is *show your work* rather than *polished release schedule*. Expect early commits to be ugly. Expect things to change. Expect honest postmortems when something does not work - those are usually the more useful posts anyway.

The blog series tracking the build will be linked here once the first post is up.

## License

Apache License 2.0. See [LICENSE](./LICENSE).

## Author

[Jaspal Chauhan](https://github.com/jsinh) - engineer working in real-time communications, compliance, and applied ML. This project is independent personal work, not affiliated with any employer or organisation.