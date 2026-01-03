# hostxray

`hostxray` collects a best-effort, privacy-aware machine specification for environment comparison (dev/uat/prod), troubleshooting, and providing LLM context.

- Standard library first
- Optional enrichment via extras (`pip install hostxray[full]`)
- Best-effort collection with graceful degradation (never crash)
- Deterministic, JSON-serializable output
- Safe mode (default) redacts sensitive identifiers

This README is intentionally self-contained for PyPI. The `docs/` folder (on GitHub) has deeper, field-by-field guidance, but you shouldn’t need it to get started.

## Install

```bash
pip install hostxray
# Optional extras
pip install hostxray[full]
```

## Quickstart (CLI)

Collect a standard, safe-by-default spec as JSON:

```bash
hostxray --format json --profile standard
```

Collect a more complete spec (may include identifying values):

```bash
hostxray --format json --profile full --unsafe
```

Targeted redaction (even in unsafe mode):

```bash
hostxray --format json --profile full --unsafe --redact hostname mac ip user serial
```

## Quickstart (Python)

```python
from hostxray import collect_spec

spec = collect_spec(profile="standard")
print(spec.to_json(indent=2))
```

## Key concepts (quick reference)

### Profiles

Profiles control *what to attempt to collect*.

- `standard`: solid baseline for environment comparison (OS, hardware summary, Python, basic network shape)
- `full`: attempts additional enrichment when available (more detailed hardware/network/process-level data)

If a data source is unavailable (missing permissions, missing optional dependency, unsupported platform), `hostxray` skips it and continues.

### Safe mode vs unsafe

By default, `hostxray` runs in safe mode and redacts common identifiers.

- Safe mode (default): returns a useful spec while redacting sensitive identifiers
- Unsafe mode (`--unsafe` / API option): may include identifying values like hostname, usernames, MAC addresses, IPs, serials (depending on platform and availability)

### Redaction controls

You can explicitly redact categories:

- `hostname`
- `user`
- `ip`
- `mac`
- `serial`

(Exact available categories may evolve; the CLI `--help` is the source of truth for your installed version.)

### Output guarantees

- JSON-serializable, deterministic structure
- Designed to be stable for diffing across machines
- Collection is best-effort; missing fields are expected and normal

## Extras (optional enrichment)

`hostxray` works with the standard library alone. Installing extras enables additional collectors.

```bash
pip install hostxray[full]
```

If you’re distributing this in a locked-down environment, you can stay on the base install and still get a useful baseline.

## CLI

```bash
hostxray --help
```

## Documentation

If you’re viewing this on GitHub, deeper references are available:

- [docs/README.md](docs/README.md): field-by-field guidance and sources
- [docs/USAGE.md](docs/USAGE.md): CLI and API usage
- [docs/EXTRAS.md](docs/EXTRAS.md): what `hostxray[full]` improves
