# MarkItDown MCP Advanced

A powerful MCP (Model Context Protocol) server that converts various document formats to Markdown with PaddleOCR support.

## Features

- **Multi-format Support**: PDF, images, Office documents, HTML, CSV
- **OCR Integration**: High-accuracy text recognition via PaddleOCR API
- **URL Support**: Direct processing of remote file URLs
- **MCP Protocol**: Full compliance with MCP standard (STDIO and HTTP modes)
- **Lightweight**: Core features use only Python standard library

## Supported Formats

| Category | Extensions |
|----------|------------|
| PDF | `.pdf` |
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx`, `.xls` (requires extra dependency) |
| Web | `.html`, `.htm` |
| CSV | `.csv` |

## Configuration

Required environment variables:

```bash
export PADDLE_API_URL="your_api_url"
export PADDLE_TOKEN="your_token"
export MARKITDOWN_TEMP_DIR="/path/to/temp"
```


## Usage with Claude Desktop

Add to Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown-mcp",
      "env": {
        "PADDLE_API_URL": "your_api_url",
        "PADDLE_TOKEN": "your_token"
      }
    }
  }
}
```

## Links

- [GitHub Repository](https://github.com/DuanYan007/markitdown)
- [Issue Tracker](https://github.com/DuanYan007/markitdown/issues)

## License

MIT License
