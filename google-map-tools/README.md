# Google Maps Tools for LangChain

A collection of Google Maps API tools for LangChain that provides location-based services including restaurant search, attraction search, hotel search, directions, and geocoding.

## Features

- **Restaurant Search**: Find restaurants by area, cuisine type, price level, and rating
- **Attraction Search**: Discover tourist attractions by area and type
- **Hotel Search**: Locate hotels by area, type, and price range
- **Directions**: Get route planning with multiple transportation modes
- **Geocoding**: Convert addresses to coordinates and vice versa

## Installation

### Dependencies

Install the required packages:

```bash
pip install googlemaps>=4.10.0 python-decouple langchain-core
```

## Configuration

### Environment Variables

Create a `.env` file in your project root with your Google Maps API key:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### Getting a Google Maps API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API
   - Directions API
   - Geocoding API
4. Create credentials (API Key)
5. Restrict the API key to the specific APIs you need for security

## Usage
### Copy files into your project

- `google_maps_tools.py`
- `google_maps_client.py`

### Basic Setup

```python
# Import Google Maps tools
# Note: Adjust the import path based on where you placed the files in your project
from google_maps_tools import get_maps_tools

# Get all available tools
map_tools = get_maps_tools()

# Define LLM with bound tools
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(map_tools)
```

## Support

For issues related to:
- **Google Maps API**: Check the [Google Maps API documentation](https://developers.google.com/maps)
- **LangChain**: Visit the [LangChain documentation](https://python.langchain.com/)
- **This tool**: Check the source code or create an issue in the repository
