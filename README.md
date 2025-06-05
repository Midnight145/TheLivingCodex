# The Living Codex

## Overview

Codex is a Discord bot designed to allow you to do text-based roleplay "in-character" in online TTRPG campaigns.

It uses webhooks to send messages as characters, allowing for a seamless roleplaying experience. The bot supports importing characters from various platforms as well as creating custom characters for platforms unsupported.

## Features

### Character Management
- **Import Characters**: Import characters from supported platforms using links or files.
  - Currently Supported Platforms:
    - D&DBeyond
      - Character sheet must be public (Edit --> Home --> Character Privacy --> Public)
    - PathBuilder
      - Link obtained via Menu --> Export --> Export JSON --> View JSON
    - Scoundry
      - Link obtained via Export --> Share as URL
    - CompCon
      - File upload, not a link
      - Pilot Options --> Export Pilot --> Export Data File
- **Update Characters**: Fetch the latest information for a character.
  - D&DBeyond characters will automatically update.
  - PathBuilder characters will need to be re-exported before updating.
  - Scoundry Characters will need to have the link supplied
  - CompCon characters will need to have the file supplied
- **Delete Characters**: Remove characters from the database.
- **View Characters**: Display detailed information about a character.
- **List Characters**: Show all characters owned by a user.

### Proxying
- **Proxy Messages**: Send messages as a character in Discord channels.
- **Autoproxy**: Automatically proxy all messages in a channel, except when prefixed by `[` to allow for out-of-character messages.

### Custom Characters
- **Create Custom Characters**: Interactive character creation.
- **Edit Characters**: Modify attributes such as name, race, classes, and backstory.
- **Edit Images**: Update character images.

### Reaction-Based Actions
- **Delete Messages**: Remove proxied messages.
- **Edit Messages**: Modify proxied messages.
- **View Character Info**: Display character details.
- **Help**: Show help information.

## Commands

### General Commands
- `>import [url]` - Import a character from a supported platform.
  - CompCon characters require a file upload instead of a URL
- `>update <id> [link]` - Update a character's information.
  - PathBuilder characters must be re-exported first
  - Scoundry characters require the link to be supplied
  - CompCon characters require the file to be supplied
- `>delete <id>` - Delete a character.
- `>list` - List all characters owned by the user.
- `>view <id>` - View detailed information about a character.

### Proxy Commands
- `>proxy <prefix|id>` - Proxy as a character in the current channel. All messages will be automatically sent as that character unless prefixed with `[` to allow for out-of-character messages.
- `>unproxy` - Disable proxying in the current channel.

### Custom Character Commands
- `>create` - Start interactive character creation.
- `>edit_character <id> key=value key2=value2 ...` - Edit character attributes.
  - Valid keys include: `name`, `race`, `classes`, `backstory`, `image_url`.
- `>edit_image <id> [image_url]` - Update a character's image.
  - Imported characters can also have images changed, not just custom characters.
  - Can also take a file upload instead of a URL.

### Help
- `>help` - Display help information.


## Installation

Requirements:
- Python 3.13 or higher
  - discord.py
  - aiohttp
  - load_dotenv

Clone the repository:
```bash
git clone git@github.com:Midnight145/TheLivingCodex.git
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory with the following variables:
```plaintext
DATABASE_FILE=sqlite_file.db
DISCORD_TOKEN=your_discord_bot_token
```

Run the bot:
```bash
python main.py
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Make your changes with clear commit messages
3. Open a pull request with a description of your changes.

In the case of adding new importers, the following steps should be followed:
1. Create a new package in character with the name of the platform (e.g., `dndbeyond`, `pathbuilder`, etc.)
2. Create a custom CharacterInfo class that inherits from CharacterInfo
3. Create a custom Importer file that implements import_character and update_character
4. Add your module to modules/character/ModuleDefinitions.py