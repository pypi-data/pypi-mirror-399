# Shekel MCP

MCP (Model Context Protocol) server for Shekel Mobility vehicle APIs. This package allows AI assistants like Claude to access vehicle price estimation, social media caption generation, and listing optimization tools.

## Installation

```bash
pip install shekel-mcp
```

Or install from source:

```bash
pip install git+https://github.com/shekelmobility/shekel-mcp.git
```

## Requirements

- Python 3.10 or higher
- A Shekel Mobility API key

## Quick Start

### 1. Install the package

```bash
pip install shekel-mcp
```

### 2. Configure Claude Desktop

Add the following to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "shekel-mobility": {
      "command": "shekel-mcp",
      "args": []
    }
  }
}
```

### 3. Restart Claude Desktop

After saving the configuration, restart Claude Desktop to load the MCP server.

### 4. Start using the tools

You can now ask Claude to use the Shekel Mobility tools:

- "Estimate the price of a 2020 Toyota Camry in Nigeria"
- "Generate Instagram captions for a Mercedes C300"
- "Create optimized listing titles for my Honda Accord"

## Available Tools

### estimate_vehicle

Estimate the market price of a vehicle in the African automotive market.

**Required parameters:**
- `api_key`: Your Shekel Mobility API key
- `vehicle_name`: Name of the vehicle (e.g., "Toyota Camry")
- `year`: Year of manufacture
- `condition`: "foreign_used" or "local_used"

**Optional parameters:**
- `region`: Region for pricing (default: "Nigeria")
- `mileage`: Vehicle mileage in kilometers
- `description`: Additional vehicle details
- `source`: "DEFAULT" or "AUCTION"
- `hard_refresh`: Bypass cache for fresh results

### generate_caption

Generate social media captions and hashtags for vehicle listings.

**Required parameters:**
- `api_key`: Your Shekel Mobility API key
- `vehicle_name`: Name of the vehicle
- `year`: Year of manufacture
- `platforms`: List of platforms (facebook, instagram, tiktok, whatsapp)

**Optional parameters:**
- `tone`: professional, casual, urgent, luxury, or budget
- `language`: Language for captions (default: "English")
- `price`: Vehicle price
- `variations_per_platform`: Number of caption variations (1-3)
- `hashtag_count`: Number of hashtags (1-15)
- `context_suggestions`: Additional instructions for the AI

### optimize_listing

Generate optimized listing titles and SEO keywords.

**Required parameters:**
- `api_key`: Your Shekel Mobility API key
- `vehicle_name`: Name of the vehicle
- `year`: Year of manufacture

**Optional parameters:**
- `title_count`: Number of title suggestions (1-5)
- `include_seo_keywords`: Generate SEO keywords (default: true)
- `description`: Vehicle features and details
- `context_suggestions`: Additional instructions for the AI

## CLI Usage

Run the MCP server manually:

```bash
# Use default production API
shekel-mcp

# Use custom API URL (for development)
shekel-mcp --base-url http://localhost:8000

# Check version
shekel-mcp --version
```

## Environment Variables

- `SHEKEL_API_BASE_URL`: Override the API base URL

## Getting an API Key

Contact Shekel Mobility to obtain an API key:
- Website: https://shekelmobility.com
- Email: support@shekelmobility.com

## License

MIT License
