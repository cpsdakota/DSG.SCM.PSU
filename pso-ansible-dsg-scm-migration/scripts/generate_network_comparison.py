#!/usr/bin/env python3
"""
Network Pre/Post Comparison Report Generator for Palo Alto Firewalls.

Compares: ARP Table, Interface Status, Static Routes
Generates a styled HTML report.

Usage:
  python3 generate_network_comparison.py \
    --pre  snapshots/pre_network_fw01.json \
    --post snapshots/post_network_fw01.json \
    --output reports/network_comparison_fw01.html
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from html import escape

try:
    import xmltodict
    HAS_XMLTODICT = True
except ImportError:
    HAS_XMLTODICT = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_list(val):
    """Wrap single dict in a list; return empty list for None."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def s(val):
    """Safely convert any value to stripped string."""
    if val is None:
        return ""
    return str(val).strip()


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_arp_table(xml_str):
    """
    Parse 'show arp all' XML response.
    Returns dict keyed by IP address.
    """
    result = {}
    if not xml_str:
        return result
    try:
        data = xmltodict.parse(xml_str)
        entries = (data.get("response", {})
                       .get("result", {})
                       .get("entries", {})
                       .get("entry"))
        for e in ensure_list(entries):
            ip = s(e.get("ip"))
            if not ip:
                continue
            result[ip] = {
                "ip":        ip,
                "mac":       s(e.get("hw")),
                "port":      s(e.get("port")),
                "interface": s(e.get("interface")),
                "ttl":       s(e.get("ttl")),
                "status":    s(e.get("status")),
            }
    except Exception:
        pass
    return result


def parse_interfaces(xml_str):
    """
    Parse 'show interface all' XML response.
    Returns dict keyed by interface name using the hw (hardware) section
    for physical state, and enriches with IP/zone from ifnet section.
    """
    result = {}
    if not xml_str:
        return result
    try:
        data = xmltodict.parse(xml_str)
        res = data.get("response", {}).get("result", {})

        # Logical interface info (IP, zone, VR)
        logical = {}
        for e in ensure_list(res.get("ifnet", {}).get("entry")):
            name = s(e.get("name"))
            if name:
                logical[name] = {
                    "ip":   s(e.get("ip")),
                    "zone": s(e.get("zone")),
                    "vsys": s(e.get("vsys")),
                }

        # Hardware interface info (state, speed, duplex)
        for e in ensure_list(res.get("hw", {}).get("entry")):
            name = s(e.get("name"))
            if not name:
                continue
            logi = logical.get(name, {})
            result[name] = {
                "name":      name,
                "state":     s(e.get("state")),
                "speed":     s(e.get("speed")),
                "duplex":    s(e.get("duplex")),
                "mac":       s(e.get("mac")),
                "st":        s(e.get("st")),
                "ip":        logi.get("ip", ""),
                "zone":      logi.get("zone", ""),
                "vsys":      logi.get("vsys", ""),
            }
    except Exception:
        pass
    return result


def parse_static_routes(xml_str):
    """
    Parse 'show routing route type static' XML response.
    Returns dict keyed by destination prefix.
    """
    result = {}
    if not xml_str:
        return result
    try:
        data = xmltodict.parse(xml_str)
        entries = (data.get("response", {})
                       .get("result", {})
                       .get("entry"))
        for e in ensure_list(entries):
            dst = s(e.get("dst"))
            if not dst:
                continue
            result[dst] = {
                "dst":         dst,
                "nexthop":     s(e.get("nexthop")),
                "metric":      s(e.get("metric")),
                "interface":   s(e.get("interface")),
                "flags":       s(e.get("flags")),
                "route_table": s(e.get("route-table")),
                "virtual_router": s(e.get("virtual-router")),
            }
    except Exception:
        pass
    return result


# ---------------------------------------------------------------------------
# Comparison logic
# ---------------------------------------------------------------------------

def compare_dicts(pre, post, compare_fields):
    """
    Compare two {key: dict} maps.
    Returns (added, removed, changed, unchanged_count).
    """
    added    = {k: post[k] for k in post if k not in pre}
    removed  = {k: pre[k]  for k in pre  if k not in post}
    changed  = {}
    unchanged = 0

    for k in pre:
        if k not in post:
            continue
        diffs = {}
        for f in compare_fields:
            pv, pov = s(pre[k].get(f)), s(post[k].get(f))
            if pv != pov:
                diffs[f] = {"pre": pv, "post": pov}
        if diffs:
            changed[k] = {"pre": pre[k], "post": post[k], "changes": diffs}
        else:
            unchanged += 1

    return added, removed, changed, unchanged


# ---------------------------------------------------------------------------
# HTML rendering helpers
# ---------------------------------------------------------------------------

CSS = """
body { font-family: Arial, sans-serif; margin: 30px; background: #f4f6f8; color: #333; }
h1   { color: #2c3e50; border-bottom: 3px solid #2c3e50; padding-bottom: 8px; }
h2   { color: #34495e; margin-top: 0; margin-bottom: 8px;
       display: flex; align-items: center; gap: 12px; }
h3   { color: #555; font-size: 14px; margin: 20px 0 6px 0; }
p.meta     { color: #666; font-size: 13px; }
p.no-change { color: #155724; background: #d4edda; padding: 10px 14px;
              border-radius: 4px; border-left: 4px solid #28a745;
              font-size: 13px; margin: 8px 0 0 0; }
.section   { background: #fff; border-radius: 6px; padding: 20px 24px;
             box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 28px; }
.summary-box { background: #fff; border-radius: 6px; padding: 20px 24px;
               box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 28px; }
table  { border-collapse: collapse; width: 100%; background: #fff;
         box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 12px;
         border-radius: 4px; overflow: hidden; }
th { background: #2c3e50; color: #fff; padding: 10px 14px;
     text-align: left; font-size: 13px; white-space: nowrap; }
td { padding: 9px 14px; border-bottom: 1px solid #e0e0e0; font-size: 13px; }
tr:last-child td { border-bottom: none; }
tr:hover td     { background: #f7f9fc; }
.row-removed td { background: #fff5f5; }
.row-removed:hover td { background: #ffe8e8; }
.row-added td   { background: #f0fff4; }
.row-added:hover td { background: #e0ffe8; }
.row-changed td { background: #fffbf0; }
.row-changed:hover td { background: #fff3d0; }
.val-pre  { color: #c0392b; font-family: monospace; font-weight: bold; }
.val-post { color: #27ae60; font-family: monospace; font-weight: bold; }
.badge { display: inline-block; border-radius: 4px; padding: 3px 9px;
         font-size: 12px; font-weight: bold; white-space: nowrap; }
.badge-pass    { background: #d4edda; color: #155724; }
.badge-changed { background: #fff3cd; color: #856404; }
.badge-added   { background: #cce5ff; color: #004085; }
.badge-removed { background: #f8d7da; color: #721c24; }
.section-badge { font-size: 13px; padding: 4px 12px; border-radius: 12px;
                 font-weight: normal; }
.dot-up   { color: #28a745; font-weight: bold; }
.dot-down { color: #dc3545; font-weight: bold; }
"""


def badge(css_class, text):
    return f'<span class="badge {css_class}">{escape(text)}</span>'


def section_summary(added, removed, changed):
    if not added and not removed and not changed:
        return "PASS", "No Changes"
    parts = []
    if added:   parts.append(f"+{len(added)} added")
    if removed: parts.append(f"-{len(removed)} removed")
    if changed: parts.append(f"{len(changed)} changed")
    return "CHANGED", ", ".join(parts)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_arp(pre_arp, post_arp):
    added, removed, changed, unchanged = compare_dicts(
        pre_arp, post_arp, ["mac", "port", "interface"]
    )
    status, summary = section_summary(added, removed, changed)
    sbadge_cls = "badge-pass" if status == "PASS" else "badge-changed"

    h = f'<div class="section">\n  <h2>ARP Table <span class="section-badge {sbadge_cls}">{summary}</span></h2>\n'

    if not added and not removed and not changed:
        total = len(pre_arp)
        h += f'<p class="no-change">&#10003; ARP table unchanged &mdash; {total} entr{"y" if total == 1 else "ies"} identical pre and post.</p>\n'
    else:
        # Removed
        if removed:
            h += f'<h3>&#x2716; Removed Entries ({len(removed)})</h3>\n'
            h += '<table><thead><tr><th>IP Address</th><th>MAC</th><th>Port</th><th>Interface</th><th>TTL</th></tr></thead><tbody>\n'
            for ip, e in sorted(removed.items()):
                h += f'<tr class="row-removed"><td><strong>{escape(ip)}</strong></td><td>{escape(e["mac"])}</td><td>{escape(e["port"])}</td><td>{escape(e["interface"])}</td><td>{escape(e["ttl"])}</td></tr>\n'
            h += '</tbody></table>\n'

        # Added
        if added:
            h += f'<h3>&#x2795; Added Entries ({len(added)})</h3>\n'
            h += '<table><thead><tr><th>IP Address</th><th>MAC</th><th>Port</th><th>Interface</th><th>TTL</th></tr></thead><tbody>\n'
            for ip, e in sorted(added.items()):
                h += f'<tr class="row-added"><td><strong>{escape(ip)}</strong></td><td>{escape(e["mac"])}</td><td>{escape(e["port"])}</td><td>{escape(e["interface"])}</td><td>{escape(e["ttl"])}</td></tr>\n'
            h += '</tbody></table>\n'

        # Changed
        if changed:
            h += f'<h3>&#x21BB; Changed Entries ({len(changed)})</h3>\n'
            h += '<table><thead><tr><th>IP Address</th><th>Field</th><th>Before</th><th>After</th></tr></thead><tbody>\n'
            for ip, info in sorted(changed.items()):
                for field, vals in info["changes"].items():
                    h += f'<tr class="row-changed"><td><strong>{escape(ip)}</strong></td><td>{escape(field)}</td><td class="val-pre">{escape(vals["pre"])}</td><td class="val-post">{escape(vals["post"])}</td></tr>\n'
            h += '</tbody></table>\n'

        # Unchanged summary
        if unchanged:
            h += f'<p style="font-size:12px;color:#666;margin:4px 0 0 0">+ {unchanged} entr{"y" if unchanged == 1 else "ies"} unchanged (not shown)</p>\n'

    h += '</div>\n'
    return h, status


def render_interfaces(pre_intf, post_intf):
    added, removed, changed, unchanged = compare_dicts(
        pre_intf, post_intf, ["state", "speed", "duplex"]
    )
    status, summary = section_summary(added, removed, changed)
    sbadge_cls = "badge-pass" if status == "PASS" else "badge-changed"

    h = f'<div class="section">\n  <h2>Interface Status <span class="section-badge {sbadge_cls}">{summary}</span></h2>\n'

    # Full comparison table — all interfaces from either snapshot
    all_names = sorted(set(list(pre_intf.keys()) + list(post_intf.keys())))

    if not all_names:
        h += '<p class="no-change">No interface data available.</p>\n'
    else:
        h += '<table>\n<thead><tr><th>Interface</th><th>IP Address</th><th>Zone</th>'
        h += '<th>State (Before)</th><th>Speed (Before)</th>'
        h += '<th>State (After)</th><th>Speed (After)</th><th>Result</th></tr></thead>\n<tbody>\n'

        for name in all_names:
            pre_e = pre_intf.get(name)
            post_e = post_intf.get(name)

            if pre_e and post_e:
                # Both snapshots have the interface
                state_changed = pre_e["state"] != post_e["state"]
                speed_changed = pre_e["speed"] != post_e["speed"]
                any_change = state_changed or speed_changed
                row_cls = "row-changed" if any_change else ""
                result_badge = badge("badge-changed", "CHANGED") if any_change else badge("badge-pass", "OK")
                pre_state_disp = f'<span class="dot-{"up" if pre_e["state"] == "up" else "down"}">{escape(pre_e["state"] or "—")}</span>'
                post_state_disp = f'<span class="dot-{"up" if post_e["state"] == "up" else "down"}">{escape(post_e["state"] or "—")}</span>'
                ip_disp = escape(post_e.get("ip") or pre_e.get("ip") or "")
                zone_disp = escape(post_e.get("zone") or pre_e.get("zone") or "")
                pre_speed  = escape(pre_e["speed"]  or "—")
                post_speed = escape(post_e["speed"] or "—")
                h += f'<tr class="{row_cls}"><td><strong>{escape(name)}</strong></td><td>{ip_disp}</td><td>{zone_disp}</td>'
                h += f'<td>{pre_state_disp}</td><td>{pre_speed}</td>'
                h += f'<td>{post_state_disp}</td><td>{post_speed}</td><td>{result_badge}</td></tr>\n'

            elif pre_e and not post_e:
                # Interface disappeared
                pre_state_disp = f'<span class="dot-{"up" if pre_e["state"] == "up" else "down"}">{escape(pre_e["state"] or "—")}</span>'
                h += f'<tr class="row-removed"><td><strong>{escape(name)}</strong></td>'
                h += f'<td>{escape(pre_e.get("ip",""))}</td><td>{escape(pre_e.get("zone",""))}</td>'
                h += f'<td>{pre_state_disp}</td><td>{escape(pre_e["speed"] or "—")}</td>'
                h += f'<td><em>not present</em></td><td>—</td><td>{badge("badge-removed", "REMOVED")}</td></tr>\n'

            elif not pre_e and post_e:
                # New interface appeared
                post_state_disp = f'<span class="dot-{"up" if post_e["state"] == "up" else "down"}">{escape(post_e["state"] or "—")}</span>'
                h += f'<tr class="row-added"><td><strong>{escape(name)}</strong></td>'
                h += f'<td>{escape(post_e.get("ip",""))}</td><td>{escape(post_e.get("zone",""))}</td>'
                h += f'<td><em>not present</em></td><td>—</td>'
                h += f'<td>{post_state_disp}</td><td>{escape(post_e["speed"] or "—")}</td>'
                h += f'<td>{badge("badge-added", "NEW")}</td></tr>\n'

        h += '</tbody></table>\n'

    h += '</div>\n'
    return h, status


def render_routes(pre_routes, post_routes):
    added, removed, changed, unchanged = compare_dicts(
        pre_routes, post_routes, ["nexthop", "metric", "interface"]
    )
    status, summary = section_summary(added, removed, changed)
    sbadge_cls = "badge-pass" if status == "PASS" else "badge-changed"

    h = f'<div class="section">\n  <h2>Static Routes <span class="section-badge {sbadge_cls}">{summary}</span></h2>\n'

    all_dsts = sorted(set(list(pre_routes.keys()) + list(post_routes.keys())))

    if not all_dsts:
        h += '<p class="no-change">No static route data available.</p>\n'
    else:
        h += '<table>\n<thead><tr><th>Destination</th><th>Next Hop (Before)</th><th>Interface (Before)</th><th>Metric (Before)</th>'
        h += '<th>Next Hop (After)</th><th>Interface (After)</th><th>Metric (After)</th><th>Result</th></tr></thead>\n<tbody>\n'

        for dst in all_dsts:
            pre_r  = pre_routes.get(dst)
            post_r = post_routes.get(dst)

            if pre_r and post_r:
                diffs = {}
                for f in ["nexthop", "metric", "interface"]:
                    if s(pre_r.get(f)) != s(post_r.get(f)):
                        diffs[f] = True
                any_change = bool(diffs)
                row_cls = "row-changed" if any_change else ""
                result_badge = badge("badge-changed", "CHANGED") if any_change else badge("badge-pass", "OK")

                def cell(pre_val, post_val, field):
                    pv, pov = escape(s(pre_val)), escape(s(post_val))
                    return (f'<td class="val-pre">{pv}</td>', f'<td class="val-post">{pov}</td>') if field in diffs else (f'<td>{pv}</td>', f'<td>{pov}</td>')

                nh_pre, nh_post   = cell(pre_r["nexthop"],   post_r["nexthop"],   "nexthop")
                if_pre, if_post   = cell(pre_r["interface"], post_r["interface"], "interface")
                mt_pre, mt_post   = cell(pre_r["metric"],    post_r["metric"],    "metric")

                h += f'<tr class="{row_cls}"><td><strong>{escape(dst)}</strong></td>'
                h += f'{nh_pre}{if_pre}{mt_pre}'
                h += f'{nh_post}{if_post}{mt_post}'
                h += f'<td>{result_badge}</td></tr>\n'

            elif pre_r and not post_r:
                h += f'<tr class="row-removed"><td><strong>{escape(dst)}</strong></td>'
                h += f'<td>{escape(pre_r["nexthop"])}</td><td>{escape(pre_r["interface"])}</td><td>{escape(pre_r["metric"])}</td>'
                h += f'<td colspan="3"><em>route removed</em></td>'
                h += f'<td>{badge("badge-removed", "REMOVED")}</td></tr>\n'

            elif not pre_r and post_r:
                h += f'<tr class="row-added"><td><strong>{escape(dst)}</strong></td>'
                h += f'<td colspan="3"><em>route not present</em></td>'
                h += f'<td>{escape(post_r["nexthop"])}</td><td>{escape(post_r["interface"])}</td><td>{escape(post_r["metric"])}</td>'
                h += f'<td>{badge("badge-added", "NEW")}</td></tr>\n'

        h += '</tbody></table>\n'

    h += '</div>\n'
    return h, status


# ---------------------------------------------------------------------------
# Main report generator
# ---------------------------------------------------------------------------

def generate_report(pre_data, post_data):
    if not HAS_XMLTODICT:
        print("ERROR: xmltodict is required. Install with: pip install xmltodict", file=sys.stderr)
        sys.exit(1)

    device         = pre_data.get("device", "unknown")
    ip             = pre_data.get("ip", "")
    pre_timestamp  = pre_data.get("timestamp", "unknown")
    post_timestamp = post_data.get("timestamp", "unknown")
    generated_at   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pre_arp    = parse_arp_table(pre_data.get("arp_xml", ""))
    post_arp   = parse_arp_table(post_data.get("arp_xml", ""))
    pre_intf   = parse_interfaces(pre_data.get("interfaces_xml", ""))
    post_intf  = parse_interfaces(post_data.get("interfaces_xml", ""))
    pre_routes = parse_static_routes(pre_data.get("routes_xml", ""))
    post_routes= parse_static_routes(post_data.get("routes_xml", ""))

    arp_html,   arp_status   = render_arp(pre_arp, post_arp)
    intf_html,  intf_status  = render_interfaces(pre_intf, post_intf)
    route_html, route_status = render_routes(pre_routes, post_routes)

    all_pass     = all(st == "PASS" for st in [arp_status, intf_status, route_status])
    overall_cls  = "badge-pass" if all_pass else "badge-changed"
    overall_text = "ALL CHECKS PASSED" if all_pass else "CHANGES DETECTED"

    arp_bc   = "badge-pass" if arp_status   == "PASS" else "badge-changed"
    intf_bc  = "badge-pass" if intf_status  == "PASS" else "badge-changed"
    route_bc = "badge-pass" if route_status == "PASS" else "badge-changed"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Network Pre/Post Comparison &mdash; {escape(device)}</title>
  <style>{CSS}</style>
</head>
<body>

  <h1>Network Pre/Post Comparison Report</h1>
  <p class="meta">
    Device: <strong>{escape(device)}</strong> &nbsp;|&nbsp;
    IP: {escape(ip)} &nbsp;|&nbsp;
    Generated: {escape(generated_at)}
  </p>
  <p class="meta">
    Pre-snapshot: {escape(pre_timestamp)} &nbsp;|&nbsp;
    Post-snapshot: {escape(post_timestamp)}
  </p>

  <div class="summary-box">
    <h2 style="margin-top:0">
      Overall Result
      <span class="section-badge {overall_cls}">{overall_text}</span>
    </h2>
    <table>
      <thead>
        <tr><th>Check Area</th><th>Pre Entries</th><th>Post Entries</th><th>Result</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>ARP Table</td>
          <td>{len(pre_arp)}</td>
          <td>{len(post_arp)}</td>
          <td><span class="badge {arp_bc}">{arp_status}</span></td>
        </tr>
        <tr>
          <td>Interface Status</td>
          <td>{len(pre_intf)}</td>
          <td>{len(post_intf)}</td>
          <td><span class="badge {intf_bc}">{intf_status}</span></td>
        </tr>
        <tr>
          <td>Static Routes</td>
          <td>{len(pre_routes)}</td>
          <td>{len(post_routes)}</td>
          <td><span class="badge {route_bc}">{route_status}</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  {arp_html}
  {intf_html}
  {route_html}

</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML network pre/post comparison report for PAN-OS firewalls."
    )
    parser.add_argument("--pre",    required=True, help="Pre-snapshot JSON file path")
    parser.add_argument("--post",   required=True, help="Post-snapshot JSON file path")
    parser.add_argument("--output", required=True, help="Output HTML report file path")
    args = parser.parse_args()

    try:
        with open(args.pre) as f:
            pre_data = json.load(f)
    except Exception as e:
        print(f"ERROR reading pre-snapshot file '{args.pre}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.post) as f:
            post_data = json.load(f)
    except Exception as e:
        print(f"ERROR reading post-snapshot file '{args.post}': {e}", file=sys.stderr)
        sys.exit(1)

    html = generate_report(pre_data, post_data)

    try:
        with open(args.output, "w") as f:
            f.write(html)
        print(f"Report saved to: {args.output}")
    except Exception as e:
        print(f"ERROR writing report to '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
