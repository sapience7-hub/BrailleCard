# Judge demo hosting

## Decision

Publish a read-only judge demo at `https://braillecard.dorqlabs.com` through
the existing authenticated, outbound-only Dorq Labs Cloudflare Tunnel. This
must not require a new Cloudflare API key or a new tunnel.

The public demo and the private operator workspace are separate processes:

| Service | Exposure | Contents |
| --- | --- | --- |
| Judge demo | Existing Cloudflare Tunnel | A pre-generated sample card, visual preview, source-derived tactile preview, and Braille review artifacts only. |
| Operator workspace | Loopback only | Uploads, future local slicing, and future Moonraker handoff for the Sovol SV07. |

The interactive operator app (`braille_card.web`, the Flask "Local Studio")
remains local-only and is never run as a public service or added to any
tunnel ingress rule.

## Current public state (live)

`braillecard.dorqlabs.com` is routed through the existing `dashboards` tunnel
(`~/.cloudflared/dashboards-config.yml`) to
`braillecard-demo.service` (`deploy/braillecard-demo.service`), a loopback-only
static file server on port 8768 serving `public/demo/`. It is a purely static
page with no forms, no POST routes, and no application code — one
pre-generated sample job's preview-stage artifacts
(`scripts/build_judge_demo.py` regenerates them deterministically from
`examples/heart.svg` + `examples/card.json`), a link to the Braille review
artifact, and an honest "not yet human-reviewed" status block.

The earlier "BrailleCard is resting" placeholder (`public/resting/`,
`deploy/braillecard-resting.service`, port 8767) still runs locally as a
fallback but is no longer in the tunnel's ingress rules.

## Lowest-ceremony implementation (done)

1. Serve a pre-generated example job as static files — no POST route and no
   remote/printer control exists in this service at all.
2. Run that demo process on a new loopback-only port (8768) under a separate
   user service (`braillecard-demo.service`).
3. Point the existing `braillecard.dorqlabs.com` hostname ingress rule in
   `dashboards-config.yml` at the new port and restart the existing Cloudflare
   user service.
4. The normal operator process (`braille_card.web`) stays a manually-run local
   dev process on a different loopback port and is never added to the tunnel
   configuration.

No public uploads are needed for judges. This avoids accounts, quotas,
retention handling, and a public job store while still giving them a working,
read-only artifact review.

## Add later subdomains without dashboard clicks

The existing authenticated `dashboards` tunnel can create a single DNS route
without a Cloudflare API key:

```sh
scripts/add-dorqlabs-hostname.sh example
```

The helper rejects invalid names, never overwrites an existing DNS record, and
does not change tunnel ingress or deploy a service. Add and verify a
hostname-specific ingress rule separately before exposing a real application.

## Required public isolation checks

- Public routes have no upload, slicing, Moonraker, printer-status, upload, or
  print-start controls.
- Public responses reveal no private address, port, credential, job directory,
  or printer configuration.
- The public URL renders the sample card in a fresh browser without accessing
  the private service.
- The private operator process cannot be reached through any tunnel ingress
  hostname.

## Manual Cloudflare step

None was needed: the `braillecard` DNS route already existed (it previously
pointed at the resting placeholder), so only the ingress `service:` target
changed.
