#!/usr/bin/env bash
# Create one dorqlabs.com DNS route through the existing dashboards tunnel.
# This deliberately does not edit ingress rules or deploy a service.

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <subdomain>" >&2
  exit 64
fi

subdomain=$1
if ! [[ $subdomain =~ ^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$ ]]; then
  echo "Subdomain must use lowercase letters, digits, and internal hyphens." >&2
  exit 64
fi

config_path=/home/tangoren/.cloudflared/dashboards-config.yml
if [ ! -r "$config_path" ]; then
  echo "Existing dashboards tunnel configuration is unavailable: $config_path" >&2
  exit 78
fi

tunnel_id=$(awk '$1 == "tunnel:" {print $2; exit}' "$config_path")
if [ -z "$tunnel_id" ]; then
  echo "No tunnel identifier found in $config_path" >&2
  exit 78
fi

hostname="$subdomain.dorqlabs.com"
cloudflared --config "$config_path" tunnel route dns "$tunnel_id" "$hostname"
echo "Created DNS route for $hostname. Add a hostname-specific ingress rule before serving it."
