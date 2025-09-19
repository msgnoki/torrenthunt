# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TorrentHunt is a Telegram bot for searching torrents across multiple providers (1337x, ThePirateBay, TorrentGalaxy, etc.). It's built with Python using the Pyrogram framework for Telegram API interaction.

## Development Commands

### Code Quality Tools
- **Linting**: `pre-commit run --all-files` (runs isort, black, flake8, bandit, pyupgrade)
- **Format code**: `black .` and `isort . --profile black`
- **Security check**: `bandit -r .`

### Running the Bot
- **Start bot**: `python app/torrenthunt.py`
- **Start without initialization**: `python app/torrenthunt.py --no-init`

### Environment Setup
- Copy `.env.example` to `.env` and configure required environment variables:
  - `API_ID`, `API_HASH`, `BOT_TOKEN` (Telegram)
  - `TORRENTHUNT_API_KEY` (optional)
  - Database configuration for PostgreSQL or SQLite

## Architecture

### Core Structure
- **`app/torrenthunt.py`**: Main entry point, initializes bot and all services
- **`app/plugins/`**: Telegram bot handlers organized by functionality:
  - `commands/`: Bot commands (/start, /help, etc.)
  - `search/`: Search-related handlers
  - `settings/`: User preference handlers
  - `bookmarks/`: Bookmark management
  - `groups/`: Group-specific functionality
- **`app/apis/`**: External API integrations
- **`app/database/`**: SQLAlchemy models and database management
- **`app/langs/`**: Multi-language support (19 languages)

### Key Components
- **Pyrogram Client**: Extended with custom attributes for shared services
- **Plugin System**: Modular handlers auto-loaded from plugins directory
- **Database**: SQLAlchemy with async support (PostgreSQL/SQLite)
- **Torrent APIs**: Multiple provider integrations via dedicated API classes
- **Explicit Content Detection**: ML model for content filtering

### Important Patterns
- All shared services attached to `Client` class (e.g., `Client.DB`, `Client.language`)
- Plugin handlers use decorators for routing
- Async/await throughout for performance
- Environment-based configuration with dotenv
- Error tracking via Sentry integration

## Dependencies

Project uses modern Python (3.12+) with key dependencies:
- `pyrogram`: Telegram MTProto API framework
- `sqlalchemy`: Database ORM with async support
- `uvloop`: High-performance event loop
- `1337x`: Torrent site API wrapper
- `scikit-learn`: For explicit content detection