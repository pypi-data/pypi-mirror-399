# Caprazli Priority Provenance for Independent Researchers

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18115235.svg)](https://doi.org/10.5281/zenodo.18115235)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](LICENSE)

**Cryptographic priority claims for independent researchers.**

## The Problem

Independent researchers lack institutional infrastructure for establishing priority. Universities provide witnesses, timestamps, and social proof. Without affiliation, you have none of these.

## The Solution

Dual-Layer Provenance combines two complementary mechanisms:

| Layer | Purpose | Mechanism |
|-------|---------|-----------|
| **Continuous** | Daily work timestamping | Bitcoin blockchain via OpenTimestamps |
| **Formal** | Publication registration | DOI via Zenodo |

## Quick Start

```bash
# Install dependencies
pip install opentimestamps-client

# Timestamp a file
python caprazli_provenance.py stamp myfile.pdf
# Creates: myfile.pdf.ots

# Verify a timestamp (after Bitcoin confirmation)
python caprazli_provenance.py verify myfile.pdf.ots

# Install git hook for automatic timestamping
python caprazli_provenance.py install-hook
```

## How It Works

```
Your file
    │
    ▼
SHA-256 hash
    │
    ▼
OpenTimestamps aggregates with others
    │
    ▼
Merkle root anchored in Bitcoin block
    │
    ▼
Proof stored in .ots file
    │
    ▼
Anyone can verify, forever
```

## Why Bitcoin?

| Property | Benefit |
|----------|---------|
| Most secure blockchain | 15+ years, never compromised |
| Most decentralized | No single point of failure |
| Most likely to exist in 2050 | Long-term proof durability |
| Free via OpenTimestamps | No transaction fees |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the formal specification (T-003).

## Citation

**APA 7th:**
> Caprazli, K. M. (2026). *Caprazli Priority Provenance for Independent Researchers* (Version 1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.18115235

**Chicago (Author-Date):**
> Caprazli, Kafkas M. 2026. "Caprazli Priority Provenance for Independent Researchers." Software, version 1.0.0. Zenodo. https://doi.org/10.5281/zenodo.18115235.

**MLA 9th:**
> Caprazli, Kafkas M. *Caprazli Priority Provenance for Independent Researchers*. Version 1.0.0, Zenodo, 2026, doi:10.5281/zenodo.18115235.

**IEEE:**
> K. M. Caprazli, "Caprazli Priority Provenance for Independent Researchers," version 1.0.0, 2026. [Online]. Available: https://doi.org/10.5281/zenodo.18115235

**BibTeX:**
```bibtex
@software{caprazli_provenance_2026,
  author       = {Caprazli, Kafkas M.},
  title        = {Caprazli Priority Provenance for Independent Researchers},
  year         = 2026,
  version      = {1.0.0},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18115235},
  url          = {https://doi.org/10.5281/zenodo.18115235}
}
```

See [CITATION.cff](CITATION.cff) for machine-readable metadata (Zotero, GitHub, etc.).

## Author

**Kafkas M. Caprazli**
ORCID: [0000-0002-5744-8944](https://orcid.org/0000-0002-5744-8944)

## License

CC-BY-4.0 — Use freely, attribution required. See [LICENSE](LICENSE).
