# VALCord

The public code for **VALCord**, a VALORANT statistics bot for Discord.

## About

**VALCord** was my first project—and one of the most ambitious ones I've worked on. It started as a simple Discord bot for tracking Valorant stats, but quickly grew into a full-featured tool with match analysis, leaderboards, and performance tracking.

## History

- **Started:** August 21, 2022
- **Ended:** December 2024
- **Peak Usage:**
  - ~1,000 Discord servers
  - ~20,000 unique users in database
  - Top server had over 100,000 members

After launching version 1, I set out to rebuild VALCord from the ground up, focusing on efficiency and scalability with plans to eventually make it profitable. However, by 2024, I had a realization—while VALCord was a valuable learning experience, maintaining it required more time and effort than it could sustain financially.

Ultimately, I made the tough decision to discontinue VALCord, but the process taught me valuable lessons about scaling projects, building for users, and balancing passion with practicality.

## Why This Code is Public

I know this is not the best code, but it was my first project and I wanted to make it public as I no longer maintain it. This repository serves as a snapshot of my early work and learning journey.

## Features

- VALORANT statistics tracking
- Match analysis
- Leaderboards
- Performance tracking
- Server and account management
- Dynamic image generation for statistics
- Riot Games account linking via OAuth
- Real-time match data caching
- Web dashboard integration (via IPC)

## Technical Infrastructure

### Core Technologies
- **Python 3** - Primary programming language
- **Nextcord** (Discord.py fork) - Discord bot framework with slash commands
- **MongoDB** - NoSQL database for user data, match history, and statistics
- **Pillow (PIL)** - Image processing and generation
- **PM2** - Process manager for production deployment

### APIs & External Services
- **Riot Games API** - VALORANT match data, player statistics, and account information
- **Valorant-API.com** - Agent, weapon, and map metadata
- **Discord API** - Bot interactions and slash commands

### Infrastructure Components
- **MongoDB Database** - Multi-database architecture:
  - `valcordDB` - User accounts, guild settings, website analytics
  - `valorantStatsDB` - Match data, matchlists, player statistics
- **IPC (Inter-Process Communication)** - Communication between bot and web dashboard
- **Image Generation System** - Dynamic statistics image creation with custom templates
- **Caching Layer** - Match data and statistics caching to reduce API calls
- **OAuth Integration** - Riot Games account linking system

### Key Technical Achievements
- **Scalability**: Handled 1,000+ servers and 20,000+ users simultaneously
- **Performance Optimization**: Implemented caching strategies to minimize API rate limits
- **Data Processing**: Processed and analyzed thousands of VALORANT matches
- **Image Generation**: Created dynamic, branded statistics images using PIL
- **Multi-Environment Support**: Beta and production environments with PM2 configuration
- **Modular Architecture**: Cog-based system for extensible command management

### Development Tools
- **aiohttp** - Asynchronous HTTP client for API requests
- **valaw** - VALORANT API wrapper library
- **python-Levenshtein** - String matching for fuzzy search
- **psutil** - System monitoring

## Note

This project is no longer maintained or supported. The code is provided as-is for educational and reference purposes.
