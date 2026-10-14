# Logotypes.dev

An open-source project that offers a wide range of logos for your projects through an API.

https://logotypes.dev

## Usage

**Random logo**

<img src="https://logotypes.dev/random" height="40" />

```
https://www.logotypes.dev/random
```

**Random logo with defined props**

<img src="https://logotypes.dev/random?variant=glyph" height="40" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://logotypes.dev/random?version=black" height="40" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://logotypes.dev/random?variant=wordmark&version=black" height="40" />

```
https://www.logotypes.dev/random?variant=glyph
https://www.logotypes.dev/random?version=black
https://www.logotypes.dev/random?variant=wordmark&version=black
```

**By logo name**

<img src="https://logotypes.dev/spotify" height="40" />

```
https://www.logotypes.dev/spotify
```

**By logo name with defined props**

<img src="https://logotypes.dev/airbnb?variant=glyph" height="40" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://logotypes.dev/airbnb?variant=wordmark" height="40" />

```
https://www.logotypes.dev/airbnb?variant=wordmark
https://www.logotypes.dev/airbnb?version=black
https://www.logotypes.dev/airbnb?variant=wordmark&version=black
```

## Data

You can also access the raw data in a different ways

**All data**

```
https://www.logotypes.dev/all
```

**Random data**

```
https://www.logotypes.dev/random/data
https://www.logotypes.dev/random/data?variant=wordmark
https://www.logotypes.dev/random/data?version=black
https://www.logotypes.dev/random/data?variant=wordmark&version=black
```

**Specific data**

```
https://www.logotypes.dev/spotify/data
```

## MCP

Logotypes.dev exposes a remote [MCP](https://modelcontextprotocol.io) server (Streamable HTTP, stateless, read-only) so AI assistants can search and fetch logos. No installation or API key is needed.

```
https://www.logotypes.dev/mcp
```

### Setup

**Claude Code**

```
claude mcp add --transport http logotypes https://www.logotypes.dev/mcp
```

**Claude Desktop / claude.ai**

Go to Settings > Connectors > Add custom connector and use the URL above. Alternatively, bridge it with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "logotypes": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://www.logotypes.dev/mcp"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "logotypes": { "url": "https://www.logotypes.dev/mcp" }
  }
}
```

**VS Code** (`.vscode/mcp.json`)

```json
{
  "servers": {
    "logotypes": { "type": "http", "url": "https://www.logotypes.dev/mcp" }
  }
}
```

### Tools

| Tool           | Parameters                                       | Description                                                      |
| -------------- | ------------------------------------------------ | ---------------------------------------------------------------- |
| `search_logos` | `query`, `variant?`, `version?`, `limit?`        | Search brands by name (substring match). Default limit is 20.    |
| `get_logo`     | `name`, `variant?`, `version?`, `include_svg?`   | Get the logo files of one brand. SVG source is off by default.   |
| `random_logo`  | `variant?`, `version?`                           | Get a random logo.                                               |
| `list_logos`   | `variant?`, `version?`                           | List every brand with its available variants and versions.       |

`variant` is `wordmark` or `glyph`. `version` is `color`, `black` or `white`.

### Example prompts

- "Find the Spotify glyph in white and add it to the footer."
- "List the brands available as wordmark in black."
- "Give me a random logo for the placeholder card."

## Contribution

Help me enhance this project by adding brand logotypes. Your contributions to open-source initiative will contribute to a more comprehensive collection of logos. Join it in making this project complete by incorporating logos from various brands. Together, let's create a valuable resource for designers and developers worldwide.

I have tried to conceive this project from pure simplicity, from development to the contribution model.

### Adding new logotypes as a designer

1. The file names must follow a specific structure.

   I have created a naming structure for the files that automatically generates the API.

   `logoName-variant-version.svg`

   variant: `wordmark` / `glyph`  
   version: `color` / `black` / `white`

   For example: `nike-wordmark-black.svg`

2. Simply make a pull request including the logos in the [static/logos](static/logos) folder with the correct naming structure and in .svg format, and you're good to go!

## FAQs

### When to use wordmark or glyph in variants?

|                                 Example                                 | Type     | Description                                         |
| :---------------------------------------------------------------------: | -------- | --------------------------------------------------- |
| <img src="https://logotypes.dev/reddit?variant=wordmark" width="112" /> | Wordmark | a logo format that is made up of a symbol and text. |
|  <img src="https://logotypes.dev/reddit?variant=glyph" height="40" />   | Glyph    | consists of only one symbol or drawing.             |
