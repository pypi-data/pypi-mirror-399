# kageScope

Minimal, scope-safe reconnaissance automation tool for bug bounty and security research.

`kageScope`, gürültüyü minimumda tutarak bir hedef alan (scope) üzerinde **hızlı ve anlamlı recon çıktıları** üretmek için tasarlanmıştır.  
Amaç: **neye bakacağını bilmeni sağlamak**, her şeyi değil doğru şeyi göstermek.

---

## Features

- Subdomain discovery using `subfinder` and `assetfinder`
- Live host detection with HTTP status visibility  
  *(200 / 301 / 302 / 401 / 403)*
- API endpoint checks on predefined paths
- JavaScript file analysis for potential leaks
- Critical port scanning only (low-noise)
- Fast technology detection
- Clean, per-domain output structure
- Interactive UI or silent CLI mode

---

## Installation

### Recommended (isolated & clean)
```bash
pipx install kagescope
