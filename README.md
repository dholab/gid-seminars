# GID Seminars Aggregator

Aggregates seminars and webinars related to Global Infectious Disease research from multiple sources into a unified calendar and webpage.

## Features

- **Multiple Sources**: NIH VideoCast, university calendars (iCal), manual entries
- **Output Formats**: ICS calendar file, filterable HTML page, JSON feed
- **Caching**: SQLite database prevents redundant fetches
- **Automated Updates**: GitHub Actions runs daily
- **LabKey Deployment**: Uploads to WebDAV for hosting

## Quick Start

```bash
# Install dependencies
uv sync

# Run locally (skip upload)
uv run python main.py --skip-upload

# Run with upload to LabKey
export LABKEY_API="your-api-key"
uv run python main.py
```

## Configuration

Configuration files are in `config/`:

- `sources.toml` - Define seminar sources (RSS feeds, iCal URLs)
- `settings.toml` - General settings (time window, output paths)
- `labkey.toml` - LabKey WebDAV deployment settings

## Adding Manual Entries

Edit `data/manual_seminars.toml` to add seminars not available via automated feeds:

```toml
[[seminar]]
title = "Special Lecture on Emerging Pathogens"
start_datetime = "2025-02-15T14:00:00"
timezone = "America/New_York"
url = "https://example.org/event"
location = "Online"
organizer = "GID Research Group"
```

## Project Structure

```
gid-seminars/
├── src/
│   ├── core/           # Models, database, exceptions
│   ├── sources/        # Source collectors (RSS, iCal, manual)
│   ├── generators/     # Output generators (ICS, HTML, JSON)
│   └── deploy/         # LabKey WebDAV uploader
├── config/             # TOML configuration files
├── data/               # SQLite database, manual entries
├── local-outputs/      # Generated files
└── main.py             # Entry point
```

## License

Internal use - Wisconsin National Primate Research Center
