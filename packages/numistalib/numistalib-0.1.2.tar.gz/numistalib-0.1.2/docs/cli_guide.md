# CLI Guide

Complete guide to using the numistalib command-line interface.

## Overview

The numistalib CLI provides access to all Numista API endpoints with a rich, user-friendly interface featuring:

- Color-coded output with Rich theming
- Table and panel display modes
- Cache indicators (💾/🌐)
- Consistent short/long option flags
- Helpful error messages

## Global Options

All commands support:

```bash
--help, -h      Show command help
--version       Show version information
```

## Command Structure

```bash
numistalib <command> <subcommand> [options]
```

## Available Commands

### § 1 Configuration Commands

Manage numistalib configuration.

#### List Configuration

```bash
numistalib config list
```

Displays all current settings including API key (masked), cache directory, rate limits, etc.

#### Get Single Value

```bash
numistalib config get <key>
```

Example:

```bash
numistalib config get cache_dir
```

---

### § 2 Types Commands

Search and retrieve coin/banknote/exonumia types.

#### Search Types

```bash
numistalib types search [OPTIONS]
```

**Required**: At least one of `-q`, `--issuer`, `--catalogue`, `--year`, or `--date`

**Options:**

- `-q, --query TEXT`: Search keywords
- `--issuer TEXT`: Issuer code (e.g., "france", "united-states")
- `--category TEXT`: Category filter (`coin`, `banknote`, `exonumia`)
- `--year TEXT`: Year or range (e.g., "2020" or "2000-2010")
- `--catalogue INTEGER`: Catalogue ID
- `--number TEXT`: Catalogue number (requires `--catalogue`)
- `--ruler INTEGER`: Ruler ID
- `--material INTEGER`: Material ID
- `--date TEXT`: Date or range
- `--size TEXT`: Size in mm or range
- `--weight TEXT`: Weight in grams or range
- `--page INTEGER`: Page number (default: 1)
- `--count INTEGER`: Results per page (default: 50, max: 50)
- `--lang TEXT`: Language (`en`, `es`, `fr`)
- `-t, --table`: Display results in table mode

**Examples:**

```bash
# Simple search
numistalib types search -q "dollar"

# Filter by country and year
numistalib types search --issuer france --year 2020

# Search commemorative coins
numistalib types search -q "commemorative" --category coin

# Search by catalogue reference
numistalib types search --catalogue 5 --number "KM#123"

# Table mode for compact display
numistalib types search -q "euro" -t
```

#### Get Type Details

```bash
numistalib types get <type_id> [OPTIONS]
```

**Arguments:**

- `type_id`: Numista type ID (integer)

**Options:**

- `--lang TEXT`: Language (`en`, `es`, `fr`)

**Example:**

```bash
numistalib types get 95420
numistalib types get 95420 --lang fr
```

**Output Examples:**

The command displays detailed specifications organized into sections:

![Physical Specifications](_static/cli_type_physical_specifications.png)

*Physical characteristics including dimensions, weight, composition, and shape.*

![Obverse Specifications](_static/cli_type_obverse_specifications.png)

*Obverse (front) design description and lettering.*

![Reverse Specifications](_static/cli_type_reverse_specifications.png)

*Reverse (back) design description and lettering.*

![Edge Specifications](_static/cli_type_edge_specifications.png)

*Edge type and inscription details.*

---

### § 3 Catalogues Commands

List available reference catalogues.

#### List All Catalogues

```bash
numistalib catalogues [OPTIONS]
```

Alias: `cat`

**Options:**

- `-t, --table`: Display in table mode

**Examples:**

```bash
# Panel mode (default)
numistalib catalogues

# Table mode
numistalib catalogues -t

# Using alias
numistalib cat
```

---

### § 4 Issuers Commands

List countries and entities that issue coins/banknotes.

#### List All Issuers

```bash
numistalib issuers [OPTIONS]
```

Alias: `isr`

**Options:**

- `--lang TEXT`: Language (`en`, `es`, `fr`)
- `-t, --table`: Display in table mode

**Examples:**

```bash
# English (default)
numistalib issuers

# Spanish
numistalib issuers --lang es

# Table mode
numistalib issuers -t

# Using alias
numistalib isr
```

---

### § 5 Issues Commands

Get issues for a specific type.

#### List Type Issues

```bash
numistalib issues <type_id> [OPTIONS]
```

Alias: `isu`

**Arguments:**

- `type_id`: Numista type ID (integer)

**Options:**

- `--lang TEXT`: Language (`en`, `es`, `fr`)
- `-t, --table`: Display in table mode

**Examples:**

```bash
# Get all issues for a type
numistalib issues 95420

# French language
numistalib issues 95420 --lang fr

# Table mode
numistalib issues 95420 -t

# Using alias
numistalib isu 95420
```

---

### § 6 Mints Commands

Manage mint information.

#### List All Mints

```bash
numistalib mints list [OPTIONS]
```

**Options:**

- `--lang TEXT`: Language (`en`, `es`, `fr`)
- `-t, --table`: Display in table mode

**Example:**

```bash
numistalib mints list
numistalib mints list --lang es -t
```

#### Get Mint Details

```bash
numistalib mints get <mint_id> [OPTIONS]
```

**Arguments:**

- `mint_id`: Mint ID (integer)

**Options:**

- `--lang TEXT`: Language (`en`, `es`, `fr`)

**Example:**

```bash
numistalib mints get 42
```

---

### § 7 Collections Commands

Manage user collections (requires OAuth).

#### List Collections

```bash
numistalib collections list <user_id>
```

**Arguments:**

- `user_id`: Numista user ID (integer)

**Example:**

```bash
numistalib collections list 12345
```

#### Get Collection Items

```bash
numistalib collections items <user_id> [OPTIONS]
```

**Arguments:**

- `user_id`: Numista user ID (integer)

**Options:**

- `--category TEXT`: Filter by category
- `--type INTEGER`: Filter by type ID
- `--collection INTEGER`: Filter by collection ID

**Example:**

```bash
numistalib collections items 12345 --category coin
```

---

### § 8 Image Search Commands

Search by coin images (experimental).

#### Search by Image

```bash
numistalib image-search <image_path> [OPTIONS]
```

**Arguments:**

- `image_path`: Path to image file (JPEG/PNG)

**Options:**

- `--category TEXT`: Category (`coin`, `banknote`, `exonumia`)
- `--max-results INTEGER`: Maximum results (default: 100, max: 100)
- `--lang TEXT`: Language (`en`, `es`, `fr`)
- `--experimental`: Enable experimental features (year/grade detection)

**Example:**

```bash
numistalib image-search /path/to/coin.jpg
numistalib image-search coin.jpg --category coin --max-results 20
```

---

### § 9 Literature Commands

Get publication information.

#### Get Publication

```bash
numistalib literature get <publication_id> [OPTIONS]
```

**Arguments:**

- `publication_id`: Publication ID (e.g., "L123456")

**Example:**

```bash
numistalib literature get L123456
```

---

### § 10 Prices Commands

Get price estimates for issues.

#### Get Price Estimates

```bash
numistalib prices get <type_id> <issue_id> [OPTIONS]
```

**Arguments:**

- `type_id`: Type ID (integer)
- `issue_id`: Issue ID (integer)

**Options:**

- `--currency TEXT`: Currency code (ISO 4217, default: EUR)
- `--lang TEXT`: Language (`en`, `es`, `fr`)

**Example:**

```bash
numistalib prices get 95420 1 --currency USD
```

---

### § 11 Users Commands

Get user profile information.

#### Get User Profile

```bash
numistalib users get <user_id> [OPTIONS]
```

**Arguments:**

- `user_id`: User ID (integer)

**Options:**

- `--lang TEXT`: Language (`en`, `es`, `fr`)

**Example:**

```bash
numistalib users get 12345
```

---

## Display Modes

### Panel Mode (Default)

Displays detailed information in Rich panels:

```bash
numistalib types get 95420
```

### Table Mode

Displays compact information in tables:

```bash
numistalib types search -q "dollar" -t
```

Use the `-t` or `--table` flag with any list command.

---

## Cache Indicators

Every response shows a cache indicator:

- **💾** Cached: Served from local cache (fast, no API quota)
- **🌐** Fresh: Fetched from API (counts against quota)

---

## Tips

1. **Use short flags for quick commands:**

   ```bash
   numistalib types search -q "euro" -t
   ```

2. **Combine filters for precise searches:**

   ```bash
   numistalib types search -q "commemorative" --issuer france --year "2010-2020"
   ```

3. **Use aliases for frequently used commands:**

   ```bash
   numistalib cat    # Instead of 'catalogues'
   numistalib isr    # Instead of 'issuers'
   numistalib isu 95420  # Instead of 'issues 95420'
   ```

4. **Check help for any command:**

   ```bash
   numistalib types search --help
   ```

---

## Error Handling

The CLI provides clear error messages:

- **Authentication errors**: Check your API key in `.env`
- **Rate limit errors**: Wait briefly; rate limits reset automatically
- **Invalid parameters**: Use `--help` to see valid options
- **Network errors**: Retried automatically with exponential backoff

---

## Next Steps

- [Python API Guide](python_api_guide.md) - Use the library programmatically
- [Configuration](configuration.md) - Customize behavior
- [Advanced Usage](advanced_usage.md) - Complex scenarios
