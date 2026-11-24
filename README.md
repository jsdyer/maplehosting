# Maple Hosting Index

A dated sample of .ca domains, observed through DNS. Explore the networks and estimated countries behind their public addresses.

Open https://coolcode.ca/maplehosting/

<!-- coolcode:guide -->
Compare the first 100 .ca domains in a dated Tranco ranking. Open a domain for A/AAAA answers, origin ASNs and DB-IP Country Lite country estimates. Multiple networks can serve one domain, so shares may overlap.
<!-- /coolcode:guide -->

## Sources and interpretation

The reproducible sample is the first 100 .ca apex domains by rank in the identified dated Tranco list. A .ca suffix does not prove Canadian ownership, and the sample is not a measure of all Canadian websites.

A and AAAA answers come from Google DNS-over-HTTPS with EDNS client subnet disabled. Every returned public IP is associated with RIPE RIS origin-AS data and RIPEstat DB-IP Country Lite country estimates. Missing answers and unknown geography stay visible.

An apex DNS answer is not proof of where the browser ultimately loads a website. Redirects, CDNs, anycast, resolver location and dynamic answers can all change the observation. IP geography is not evidence of data residency.

Provider groups are labelled by origin ASN and published network holder. A known CDN-capable network does not prove that a particular domain uses its CDN service. Country/provider counts use distinct domains and can overlap.

## Collection and archive

Schedule: **Monthly** (`23 10 3 * *`, UTC). GitHub schedules are best effort. Scheduled and manual runs collect, validate, commit dated snapshots and deploy. A first code push also collects if no saved dataset exists. Other code pushes rebuild the saved dataset offline.

`data/current.json` contains the latest normalized source records and metadata. `archive/YYYY-MM/*.json.gz` retains distinct captured versions; `data/history.json` lists them. Identical data checks update the check time without manufacturing a change. An initial capture is labelled baseline. Archive data is tracked in Git and does not expire with Actions artifacts. The site has snapshot selection, filtering, source detail, CSV export and an RSS change feed.

The default build needs no network. Failed source validation does not replace the published dataset. Optional `HEALTHCHECKS_PING_URL` sends start/success/failure pings for collection runs; no accuracy email is implied.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/collect.py
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

## Privacy

Search and filters are local to the browser; no upstream request is made by filtering. Public data collection runs in GitHub Actions. The shared CoolCode counter records aggregate page opens, without searches or filter values. The explorer and collector run without Cloudflare changes. To enable shared visit counts and private issue reports, add `maplehosting` to the existing `coolcode-visitor-api` Worker’s `toolList` and deploy it, if not already registered. See the [batch setup notes](https://github.com/jsdyer/jsdyer.github.io/blob/main/docs/tier1-tools.md).

## Software and attribution

Application code is MIT licensed; upstream data retains its original licence and attribution. Follow the source links for original records and terms.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
