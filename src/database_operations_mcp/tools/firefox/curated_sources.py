"""Curated bookmark sources for profile creation."""

from typing import Any

from database_operations_mcp.config.mcp_config import mcp

# Predefined curated bookmark collections
CURATED_SOURCES = {
    "developer_tools": {
        "name": "Developer Tools",
        "description": "Essential tools for developers",
        "source_type": "custom_list",
        "config": {
            "bookmarks": [
                {"title": "GitHub", "url": "https://github.com"},
                {"title": "Stack Overflow", "url": "https://stackoverflow.com"},
                {"title": "MDN Web Docs", "url": "https://developer.mozilla.org"},
                {"title": "DevDocs", "url": "https://devdocs.io"},
                {"title": "JSON Placeholder", "url": "https://jsonplaceholder.typicode.com"},
                {"title": "Regex101", "url": "https://regex101.com"},
                {"title": "Postman", "url": "https://www.postman.com"},
                {"title": "VS Code", "url": "https://code.visualstudio.com"},
                {"title": "Docker Hub", "url": "https://hub.docker.com"},
                {"title": "npm", "url": "https://www.npmjs.com"},
                {"title": "PyPI", "url": "https://pypi.org"},
                {"title": "Git", "url": "https://git-scm.com"},
                {"title": "Linux Documentation", "url": "https://tldp.org"},
                {"title": "OWASP", "url": "https://owasp.org"},
                {"title": "SSL Labs", "url": "https://www.ssllabs.com/ssltest/"},
            ]
        },
    },
    "ai_ml": {
        "name": "AI & Machine Learning",
        "description": "Resources for AI and machine learning",
        "source_type": "github_awesome",
        "config": {"topic": "ai", "language": "en"},
    },
    "cooking": {
        "name": "Cooking & Recipes",
        "description": "Popular cooking and recipe websites",
        "source_type": "custom_list",
        "config": {
            "bookmarks": [
                {"title": "AllRecipes", "url": "https://www.allrecipes.com"},
                {"title": "Food Network", "url": "https://www.foodnetwork.com"},
                {"title": "Serious Eats", "url": "https://www.seriouseats.com"},
                {"title": "Bon Appétit", "url": "https://www.bonappetit.com"},
                {"title": "The Kitchn", "url": "https://www.thekitchn.com"},
                {"title": "NYT Cooking", "url": "https://cooking.nytimes.com"},
                {"title": "Epicurious", "url": "https://www.epicurious.com"},
                {"title": "Taste of Home", "url": "https://www.tasteofhome.com"},
                {"title": "Simply Recipes", "url": "https://www.simplyrecipes.com"},
                {"title": "Delish", "url": "https://www.delish.com"},
                {"title": "Cooking Light", "url": "https://www.cookinglight.com"},
                {"title": "EatingWell", "url": "https://www.eatingwell.com"},
                {"title": "Martha Stewart", "url": "https://www.marthastewart.com"},
                {"title": "BBC Good Food", "url": "https://www.bbcgoodfood.com"},
                {"title": "Jamie Oliver", "url": "https://www.jamieoliver.com"},
            ]
        },
    },
    "productivity": {
        "name": "Productivity Tools",
        "description": "Tools to boost productivity and organization",
        "source_type": "custom_list",
        "config": {
            "bookmarks": [
                {"title": "Notion", "url": "https://www.notion.so"},
                {"title": "Trello", "url": "https://trello.com"},
                {"title": "Asana", "url": "https://asana.com"},
                {"title": "Todoist", "url": "https://todoist.com"},
                {"title": "Evernote", "url": "https://evernote.com"},
                {"title": "Google Keep", "url": "https://keep.google.com"},
                {"title": "Microsoft To Do", "url": "https://todo.microsoft.com"},
                {"title": "Forest", "url": "https://www.forestapp.cc"},
                {"title": "Focus@Will", "url": "https://www.focusatwill.com"},
                {"title": "RescueTime", "url": "https://www.rescuetime.com"},
                {"title": "Toggl", "url": "https://toggl.com"},
                {"title": "Google Calendar", "url": "https://calendar.google.com"},
                {"title": "Outlook", "url": "https://outlook.com"},
                {"title": "Slack", "url": "https://slack.com"},
                {"title": "Discord", "url": "https://discord.com"},
            ]
        },
    },
    "news_media": {
        "name": "News & Media",
        "description": "Major news outlets and media sources",
        "source_type": "custom_list",
        "config": {
            "bookmarks": [
                {"title": "BBC News", "url": "https://www.bbc.com/news"},
                {"title": "CNN", "url": "https://www.cnn.com"},
                {"title": "The New York Times", "url": "https://www.nytimes.com"},
                {"title": "The Guardian", "url": "https://www.theguardian.com"},
                {"title": "Reuters", "url": "https://www.reuters.com"},
                {"title": "Associated Press", "url": "https://apnews.com"},
                {"title": "NPR", "url": "https://www.npr.org"},
                {"title": "The Washington Post", "url": "https://www.washingtonpost.com"},
                {"title": "The Wall Street Journal", "url": "https://www.wsj.com"},
                {"title": "Bloomberg", "url": "https://www.bloomberg.com"},
                {"title": "Al Jazeera", "url": "https://www.aljazeera.com"},
                {"title": "Reddit", "url": "https://www.reddit.com"},
                {"title": "Hacker News", "url": "https://news.ycombinator.com"},
                {"title": "TechCrunch", "url": "https://techcrunch.com"},
                {"title": "Wired", "url": "https://www.wired.com"},
            ]
        },
    },
    "finance": {
        "name": "Finance & Investing",
        "description": "Financial news, tools, and investment resources",
        "source_type": "custom_list",
        "config": {
            "bookmarks": [
                {"title": "Yahoo Finance", "url": "https://finance.yahoo.com"},
                {"title": "Bloomberg", "url": "https://www.bloomberg.com"},
                {"title": "CNBC", "url": "https://www.cnbc.com"},
                {"title": "Investopedia", "url": "https://www.investopedia.com"},
                {"title": "Seeking Alpha", "url": "https://seekingalpha.com"},
                {"title": "Morningstar", "url": "https://www.morningstar.com"},
                {"title": "Fidelity", "url": "https://www.fidelity.com"},
                {"title": "Vanguard", "url": "https://investor.vanguard.com"},
                {"title": "Charles Schwab", "url": "https://www.schwab.com"},
                {"title": "Robinhood", "url": "https://robinhood.com"},
                {"title": "Coinbase", "url": "https://www.coinbase.com"},
                {"title": "Binance", "url": "https://www.binance.com"},
                {"title": "Kraken", "url": "https://www.kraken.com"},
                {"title": "TradingView", "url": "https://www.tradingview.com"},
                {"title": "StockTwits", "url": "https://stocktwits.com"},
            ]
        },
    },
    "entertainment": {
        "name": "Entertainment",
        "description": "Streaming services, movies, music, and entertainment",
        "source_type": "custom_list",
        "config": {
            "bookmarks": [
                {"title": "Netflix", "url": "https://www.netflix.com"},
                {"title": "YouTube", "url": "https://www.youtube.com"},
                {"title": "Amazon Prime Video", "url": "https://www.amazon.com/primevideo"},
                {"title": "Disney+", "url": "https://www.disneyplus.com"},
                {"title": "HBO Max", "url": "https://www.hbomax.com"},
                {"title": "Hulu", "url": "https://www.hulu.com"},
                {"title": "Spotify", "url": "https://www.spotify.com"},
                {"title": "Apple Music", "url": "https://music.apple.com"},
                {"title": "Pandora", "url": "https://www.pandora.com"},
                {"title": "SoundCloud", "url": "https://soundcloud.com"},
                {"title": "Twitch", "url": "https://www.twitch.tv"},
                {"title": "IMDb", "url": "https://www.imdb.com"},
                {"title": "Rotten Tomatoes", "url": "https://www.rottentomatoes.com"},
                {"title": "Letterboxd", "url": "https://letterboxd.com"},
                {"title": "Goodreads", "url": "https://www.goodreads.com"},
            ]
        },
    },
    "shopping": {
        "name": "Shopping & Deals",
        "description": "Online shopping and deal-finding sites",
        "source_type": "custom_list",
        "config": {
            "bookmarks": [
                {"title": "Amazon", "url": "https://www.amazon.com"},
                {"title": "eBay", "url": "https://www.ebay.com"},
                {"title": "Walmart", "url": "https://www.walmart.com"},
                {"title": "Target", "url": "https://www.target.com"},
                {"title": "Best Buy", "url": "https://www.bestbuy.com"},
                {"title": "Costco", "url": "https://www.costco.com"},
                {"title": "Home Depot", "url": "https://www.homedepot.com"},
                {"title": "IKEA", "url": "https://www.ikea.com"},
                {"title": "Wayfair", "url": "https://www.wayfair.com"},
                {"title": "Etsy", "url": "https://www.etsy.com"},
                {"title": "AliExpress", "url": "https://www.aliexpress.com"},
                {"title": "Craigslist", "url": "https://craigslist.org"},
                {"title": "Facebook Marketplace", "url": "https://www.facebook.com/marketplace"},
                {"title": "OfferUp", "url": "https://offerup.com"},
                {"title": "Poshmark", "url": "https://poshmark.com"},
            ]
        },
    },
}


# DEPRECATED: Use firefox_curated(operation='get_curated_source') instead
def get_curated_source(source_name: str) -> dict[str, Any]:
    """
    Get a predefined curated source by name.

    Args:
        source_name: Name of the curated source to retrieve

    Returns:
        Dict containing the curated source information or None if not found
    """
    return CURATED_SOURCES.get(source_name)


# DEPRECATED: Use firefox_curated(operation='list_curated_sources') instead
def list_curated_sources() -> dict[str, Any]:
    """
    List all available curated sources.

    Returns:
        Dict containing all available curated sources with metadata
    """
    return {
        "sources": {
            name: {
                "name": info["name"],
                "description": info["description"],
                "source_type": info["source_type"],
            }
            for name, info in CURATED_SOURCES.items()
        },
        "count": len(CURATED_SOURCES),
    }
