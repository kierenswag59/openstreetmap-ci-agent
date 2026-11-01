# Assignment 3 sandbox: CI-failure analyst (deliverables map)

This is a sandbox copy of `openstreetmap/openstreetmap-website`, pinned at upstream commit
`729cdc3d`, with a gh-aw CI-failure analyst added. The upstream README follows below this section.

| Deliverable | File |
|---|---|
| Design document (150 lines or fewer) | [DESIGN.md](DESIGN.md) |
| Agentic workflow (source and compiled) | [ci-failure-analyst.md](.github/workflows/ci-failure-analyst.md), [ci-failure-analyst.lock.yml](.github/workflows/ci-failure-analyst.lock.yml) |
| Repository facts for agents | [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) |
| Skill and scripts | [SKILL.md](.claude/skills/ci-failure-triage/SKILL.md), [scripts/](.claude/skills/ci-failure-triage/scripts/) |
| Contributor policy for the bot | [CONTRIBUTING.md, "Automated CI-failure triage comments"](CONTRIBUTING.md#automated-ci-failure-triage-comments-sandbox-addition) |
| Golden tasks (16 real cases) and reproduction steps | [evals/golden/](evals/golden/), [README](evals/golden/README.md) |
| Adversarial cases (5, incl. "close all stale issues": ADV-01) and the Q1 issue test | [evals/adversarial/](evals/adversarial/), [Q1-issue-injection](evals/adversarial/Q1-issue-injection/actual.md) |
| Scores: live run and dry run | [results.md](evals/golden/results.md), [results-dryrun.md](evals/golden/results-dryrun.md), [RUBRIC.md](evals/golden/RUBRIC.md) |
| Failure analysis and incident | [ANALYSIS.md](evals/golden/ANALYSIS.md) |
| Governance detail, runbook, kill switch | [GOVERNANCE.md](docs/GOVERNANCE.md), [RUNBOOK.md](docs/RUNBOOK.md), [killswitch.log](evals/golden/logs/killswitch.log) |
| Run ledgers and live tool-call digests | [logs/live/](evals/golden/logs/live/), [logs/live/tools/](evals/golden/logs/live/tools/README.md), [logs/ledger.tsv](evals/golden/logs/ledger.tsv) |

---

# openstreetmap-website

[![Lint](https://github.com/openstreetmap/openstreetmap-website/actions/workflows/lint.yml/badge.svg?branch=master&event=push)](https://github.com/openstreetmap/openstreetmap-website/actions/workflows/lint.yml?query=branch%3Amaster+event%3Apush)
[![Tests](https://github.com/openstreetmap/openstreetmap-website/actions/workflows/tests.yml/badge.svg?branch=master&event=push)](https://github.com/openstreetmap/openstreetmap-website/actions/workflows/tests.yml?query=branch%3Amaster+event%3Apush)
[![Coverage Status](https://coveralls.io/repos/openstreetmap/openstreetmap-website/badge.svg?branch=master)](https://coveralls.io/github/openstreetmap/openstreetmap-website?branch=master)

This is `openstreetmap-website`, the [Ruby on Rails](https://rubyonrails.org/)
application that powers the [OpenStreetMap](https://www.openstreetmap.org) website and API.

This repository consists of:

* The web site, including user accounts, diary entries, user-to-user messaging.
* The XML- and JSON-based editing [API](https://wiki.openstreetmap.org/wiki/API_v0.6).
* The Browse pages - a web front-end to the OpenStreetMap data.
* The GPX uploads, browsing and API.

A fully-functional `openstreetmap-website` installation depends on other services, including map tile
servers and geocoding services, that are provided by other software. The default installation
uses publicly-available services to help with development and testing.

# License

This software is licensed under the [GNU General Public License 2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt),
a copy of which can be found in the [LICENSE](LICENSE) file.

# Installation

`openstreetmap-website` is a Ruby on Rails application that uses PostgreSQL as its database, and has a large
number of dependencies for installation. For full details please see [INSTALL.md](doc/INSTALL.md).

# Development

We're always keen to have more developers! Pull requests are very welcome.

* Bugs are recorded in the [issue tracker](https://github.com/openstreetmap/openstreetmap-website/issues).
* Translation is managed by [Translatewiki](https://translatewiki.net/wiki/Translating:OpenStreetMap).
* Local Chapters shown on the Communities page, and their translations, come from [osm-community-index](https://github.com/osmlab/osm-community-index).
* There is a [rails-dev@openstreetmap.org](https://lists.openstreetmap.org/listinfo/rails-dev) mailing list for development discussion.
* IRC - there is the #osm-dev channel on irc.oftc.net.

More details on contributing to the code are in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

# Maintainers

* Tom Hughes [@tomhughes](https://github.com/tomhughes/)
* Andy Allan [@gravitystorm](https://github.com/gravitystorm/)
* Marwin Hochfelsner [@hlfan](https://github.com/hlfan/)
