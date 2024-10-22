# DIY-AI-Assistant

## Getting Started

This project is set up using Python 3.10 and managed with Poetry. Below are the instructions to get started with the
development.

### Prerequisites

- Python 3.10 or higher
- Poetry 1.6.* for dependency management

### Installing Poetry

If you do not have Poetry installed, follow the official installation instructions provided by Poetry:

[Poetry Installation Guide](https://python-poetry.org/docs/#installation)

### Project Setup

Once you have Poetry installed, you can set up the project environment:

```bash
# Clone the repository
git clone git@github.com:wWrongName/DIY-AI-Assistant.git
cd DIY-AI-Assistant

# Install dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell

# Create .env file and adjust environment variables
cp .env.example .env
```

### Start the assistant
1. Run the backend:
```bash
python -m scripts.websocket_bot
```
2. Open in the Browser `index.html`. Tap on `Enable Audio Playback` button and then just `Start Recording`.
