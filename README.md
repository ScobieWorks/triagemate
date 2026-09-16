# TriageMate

TriageMate is a lightweight command‑line tool that automates common issue‑triage tasks for GitHub repositories:

* **Label new issues** based on simple keyword detection.
* **Close stale issues** that have not been updated for a configurable period.
* **Generate a triage summary** (open issue count and label distribution).
* **Suggest priority tags** for open issues.

All actions are performed via the GitHub REST API and require only a personal access token.

## Installation

```bash
pip install git+https://github.com/ScobieWorks/triagemate.git
```

Alternatively, clone the repository and run the script directly:

```bash
python -m triagemate.cli --owner yourorg --repo yourrepo
```

## Usage

```bash
triagemate --owner <owner> --repo <repo> [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--label-new` | Detects keywords in issue bodies and applies corresponding labels.
| `--close-stale` | Closes issues that have not been updated for the number of days specified by `--stale-days`.
| `--summary` | Prints a JSON summary of the current issue state.
| `--suggest` | Prints a suggested priority for each open issue.
| `--stale-days` | Number of days after which an issue is considered stale (default: 30).

All actions require the environment variable `GITHUB_TOKEN` to be set with a token that has `repo` scope.

## Testing

The project includes a small test suite that can be run with:

```bash
python -m unittest discover -s tests -v
```

The tests mock the GitHub API and verify the core logic.

## License

MIT


## Support

If this project saved you time, optional support is welcome: https://paypal.me/Damonwill
