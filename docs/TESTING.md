# Testing

Run backend tests with `pytest` and frontend tests with `npm test`. API changes
also have three independent contract gates:

- `python scripts/export_openapi.py --output docs/api/openapi/openapi.json --check`
  detects unreviewed drift from the generated compatibility baseline.
- `scripts/check_api_compatibility.sh` uses oasdiff 1.21.0 to reject breaking
  changes between a reviewed baseline and a candidate.
- `scripts/run_api_fitness.sh` uses Schemathesis 4.22.1 to generate requests and
  validate safe canonical responses against the live contract.

Install `requirements-dev.txt` for the Schemathesis CLI. Run generative tests
against an ephemeral database when mutation operations are added to the
fitness profile; the committed safe profile exercises read-only discovery and
collection operations.
