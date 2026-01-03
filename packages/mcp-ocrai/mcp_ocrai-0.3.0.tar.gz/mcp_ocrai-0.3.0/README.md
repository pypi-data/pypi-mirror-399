# MCP OCR AI

## Introduction

This repository contains an application that allows performing OCR (Optical Character Recognition) on various types of documents and images using the Mistral AI API. The application is designed to process files in formats such as PDF, Word, PowerPoint, images (JPEG, PNG, etc.), and other document formats.

### Main Features:
- Support for multiple document and image formats.
- Use of the Mistral AI API for OCR processing.
- Caching of results to improve performance.

## How to Set Up
1. Add the key to the environment variable:
```txt .profile
export MISTRAL_API_KEY="your_api_key_here"
```

2. Configure the MCP server on ZED:

```json
{
  /// The name of your MCP server
  "ocrai": {
    /// The command which runs the MCP server
    "command": "uvx",
    /// The arguments to pass to the MCP server
    "args": ["mcp_ocrai"],
    /// The environment variables to set
    "env": {}
  }
}

2. Alternatively, you can pass the API key directly via the command line:
```sh
mcp-ocrai --api-key "your_api_key_here"
```
