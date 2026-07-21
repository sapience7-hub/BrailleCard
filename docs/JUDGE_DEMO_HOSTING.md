# Judge demo hosting (deferred)

## Decision

When public hosting resumes, publish a read-only judge demo at
`https://braillecard.dorqlabs.com` through the existing authenticated,
outbound-only Dorq Labs Cloudflare Tunnel. This must not require a new
Cloudflare API key or a new tunnel.

The public demo and the private operator workspace are separate processes:

| Service | Exposure | Contents |
| --- | --- | --- |
| Judge demo | Existing Cloudflare Tunnel | A pre-generated sample card, visual preview, source-derived tactile preview, and Braille review artifacts only. |
| Operator workspace | Loopback only | Uploads, future local slicing, and future Moonraker handoff for the Sovol SV07. |

The current app is local-only. This document is a deployment design, not an
authorization to publish it.

## Lowest-ceremony implementation

1. Add a demo mode that serves a pre-generated example job and disables every
   POST route and remote/printer control.
2. Run that demo process on a new loopback-only port under a separate user
   service.
3. Add one explicit hostname ingress rule for `braillecard.dorqlabs.com` to
   the existing Cloudflare Tunnel configuration and restart the existing
   Cloudflare user service.
4. Keep the normal operator process on a different loopback port and omit it
   from the tunnel configuration.

No public uploads are needed for judges. This avoids accounts, quotas,
retention handling, and a public job store while still giving them a working,
interactive artifact review.

## Required public isolation checks

- Public routes have no upload, slicing, Moonraker, printer-status, upload, or
  print-start controls.
- Public responses reveal no private address, port, credential, job directory,
  or printer configuration.
- The public URL renders the sample card in a fresh browser without accessing
  the private service.
- The private operator process cannot be reached through any tunnel ingress
  hostname.

## Possible manual Cloudflare step

No API key is required for the application. If `*.dorqlabs.com` is not already
routed to the existing tunnel, an operator may need to add one DNS CNAME for
`braillecard` in the Cloudflare dashboard. If the wildcard route already
exists, no dashboard change is necessary. This should be checked only when
public hosting is resumed.
