# Notch Extension Registry — development data

Static catalog repository candidate. `site/catalog-v1.json` intentionally contains no remote packages because no trusted publishers or published repositories have been configured.

```sh
python3 tools/validate_catalog.py site/catalog-v1.json
python3 -m unittest discover -s tests -v
```

The validator checks structural rules, pinned GitHub Release URLs and integrity metadata syntax. It does not authenticate publishers. Production catalogs fail closed until trusted signature verification is added; fake signature strings or SHA digests cannot bypass that gate.

CI validates only. Pages publishing and repository creation require the owner's reviewed remote setup. No token belongs in the client or catalog. Licensed under MIT; see `LICENSE`.
