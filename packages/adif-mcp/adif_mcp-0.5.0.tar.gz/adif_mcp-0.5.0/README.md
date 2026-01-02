# ADIF-MCP

**Core [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) service for Amateur Radio Logging.**

[![PyPI version](https://img.shields.io/pypi/v/adif-mcp.svg)](https://pypi.org/project/adif-mcp/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/adif-mcp.svg)](https://pypi.org/project/adif-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-ki7mt.io-blue)](https://www.ki7mt.io/adif-mcp/)

---

## Overview

`adif-mcp` is a spec-compliant engine built on the [ADIF 3.1.6 specification](https://adif.org.uk). It provides a unified, schema-driven foundation for Amateur Radio data, enabling safe and typed access for AI agents, logging applications, and web services.

> **Pretty Code • Pretty Output • Iterative Docs**

---

## Features

- **Spec Compliance**: 100% alignment with ADIF 3.1.6 definitions and data types.
- **MCP Native**: Exposes tools for validation, normalization, and record transformation to any MCP-compliant client.
- **Service Ready**: Designed to host adapters for LoTW, eQSL, QRZ, and Clublog.
- **Provenance**: Uses registered Program IDs (`ADIF-MCP`) and `APP_` fields to track record lineage.

---

## Quick Start

### Installation
```bash
uv add adif-mcp
# or
pip install adif-mcp
```

### Usage as an MCP Tool

This package is intended to be run as an MCP server. Configure your client (like Claude Desktop) to point to the server entry point:

```json
{
  "mcpServers": {
    "adif-mcp": {
      "command": "uvx",
      "args": ["adif-mcp"]
    }
  }
}
```

---

## Documentation & Compliance

Full documentation, including API schemas and the Program ID policy, is available at our central hub:
👉 **[https://www.ki7mt.io/adif-mcp/](https://www.google.com/url?sa=E&source=gmail&q=https://www.ki7mt.io/adif-mcp/)**

### Standard Support

* **Current Spec:** 3.1.6 (Released 2025-09-15)
* **Registered Program ID:** `ADIF-MCP`

---

## Community & Support

* **Issues**: Report bugs or request features on our [GitHub Issue Tracker](https://www.google.com/search?q=https://github.com/ki7mt/ki7mt-mcp-hub/issues).
* **Hub**: This project is part of the [KI7MT MCP Hub](https://github.com/ki7mt/ki7mt-mcp-hub).

*Note: ADIF is a trademark of the ADIF Developers Group. This project is an independent implementation.*
