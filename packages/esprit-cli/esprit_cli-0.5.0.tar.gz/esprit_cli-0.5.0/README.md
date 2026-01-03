<p align="center">
  <a href="https://esprit.dev">
    <img src="https://esprit.dev/logo.png" width="150" alt="Esprit Logo">
  </a>
</p>

<h1 align="center">Esprit CLI</h1>

<h2 align="center">AI-Powered Penetration Testing</h2>

<div align="center">

[![Python](https://img.shields.io/pypi/pyversions/esprit-cli?color=3776AB)](https://pypi.org/project/esprit-cli/)
[![PyPI](https://img.shields.io/pypi/v/esprit-cli?color=10b981)](https://pypi.org/project/esprit-cli/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

</div>

---

## Installation

```bash
# Install with pip
pip install esprit-cli

# Or with pipx (recommended)
pipx install esprit-cli
```

## Quick Start

```bash
# 1. Login to Esprit (opens browser)
esprit login

# 2. Run your first scan
esprit scan https://example.com

# 3. Check your usage
esprit status
```

## Commands

| Command | Description |
|---------|-------------|
| `esprit login` | Login via OAuth (GitHub/Google) |
| `esprit logout` | Logout and clear credentials |
| `esprit whoami` | Show current user info |
| `esprit status` | Show account usage and quota |
| `esprit scan <target>` | Run a penetration test |

### Scan Examples

```bash
# Scan a website
esprit scan https://example.com

# Scan a public GitHub repo
esprit scan github.com/user/repo

# Scan with custom instructions
esprit scan https://app.example.com -i "Focus on authentication vulnerabilities"

# Start scan without streaming logs
esprit scan https://example.com --no-stream
```

## Features

- **AI-Powered Scanning** - Autonomous agents that think like real hackers
- **Real Validation** - Proof-of-concept exploits, not false positives
- **GitHub Integration** - Scan repos and create fix PRs automatically
- **Real-time Logs** - Stream scan progress to your terminal
- **Web Dashboard** - View detailed results at [esprit.dev](https://esprit.dev)

## Documentation

Full documentation available at [esprit.dev/docs](https://esprit.dev/docs)

## Support

- [GitHub Issues](https://github.com/esprit-security/esprit/issues)
- Email: support@esprit.dev

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.
