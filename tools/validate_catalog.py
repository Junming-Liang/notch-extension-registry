#!/usr/bin/env python3
"""Static registry validator. Does NOT establish publisher trust or execute assets."""
import argparse, datetime, json, re, sys, urllib.parse
from pathlib import Path
ID = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)+$")
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[a-zA-Z0-9.-]+)?$")
def validate(catalog):
    def require(ok, message):
        if not ok: raise ValueError(message)
    require(catalog.get('schemaVersion') == 1, 'unsupported schemaVersion')
    require(type(catalog.get('catalogVersion')) is int and catalog['catalogVersion'] > 0, 'invalid catalogVersion')
    require(catalog.get('distribution') in ('development', 'production'), 'invalid distribution')
    entries = catalog.get('entries')
    require(isinstance(entries, list) and len(entries) <= 1000, 'invalid entries')
    seen = set()
    for entry in entries:
        identity = entry.get('id', '')
        require(isinstance(identity, str) and bool(ID.fullmatch(identity)), 'invalid id')
        require(identity not in seen, 'duplicate id')
        seen.add(identity)
        require(bool(SEMVER.fullmatch(entry.get('version', ''))), 'invalid version')
        require(entry.get('protocolVersion') == 1, 'unsupported extension protocol')
        require(entry.get('architecture') in ('arm64', 'x86_64', 'universal'), 'unsupported architecture')
        require(bool(SEMVER.fullmatch(entry.get('minHostVersion', ''))), 'invalid minHostVersion')
        require(type(entry.get('size')) is int and 0 < entry['size'] < 2 * 1024**3, 'invalid asset size')
        require(bool(re.fullmatch(r'[0-9a-f]{64}', entry.get('sha256', ''))), 'invalid sha256')
        url = urllib.parse.urlsplit(entry.get('downloadURL', ''))
        require(url.scheme == 'https' and url.hostname == 'github.com' and not url.username and not url.password and url.port in (None,443) and not url.query and not url.fragment, 'asset URL must be fixed HTTPS GitHub release URL')
        require(bool(re.fullmatch(r'/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/releases/download/[^/]+/[^/]+', url.path)), 'asset URL must pin release tag')
        require('/latest/' not in url.path and '%' not in url.path, 'mutable/encoded URL forbidden')
        require(isinstance(entry.get('capabilities'), list) and all(isinstance(x,str) for x in entry['capabilities']), 'invalid capabilities')
        if catalog['distribution'] == 'production':
            require(bool(entry.get('publisherKeyID')) and bool(entry.get('expectedTeamID')), 'missing pinned publisher identity')
            require(bool(entry.get('packageSignature')), 'missing package signature')
    # Deliberately fail closed: structural validation is NOT a signature verifier.
    require(catalog['distribution'] == 'development', 'production publication disabled until reviewed signature verifier and trust roots exist')
    return len(entries)
def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('catalog',type=Path)
    args=parser.parse_args()
    try:
        if args.catalog.stat().st_size > 1024*1024: raise ValueError('catalog exceeds 1 MiB')
        count=validate(json.loads(args.catalog.read_text()))
        print(f'VALID DEVELOPMENT CATALOG: {count} entries; not approved for executable distribution')
    except (ValueError,OSError,TypeError) as exc:
        print(f'INVALID: {exc}',file=sys.stderr); return 1
    return 0
if __name__ == '__main__': sys.exit(main())
