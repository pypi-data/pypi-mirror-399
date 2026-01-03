"""
MCP Tool definitions for Shekel Mobility APIs.

This module defines the MCP tools that expose the Shekel Mobility APIs
to AI assistants like Claude.
"""

import json
import logging
import os
import sys
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from .client import ShekelAPIClient

# Configure logging - use stderr to avoid corrupting stdio transport
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    "shekel-mobility",
    description="Shekel Mobility AI Vehicle Estimation APIs for the African automotive market",
)

# Base URL - can be overridden via environment variable or CLI
_base_url: str | None = None


def get_base_url() -> str:
    """Get the API base URL."""
    global _base_url
    if _base_url:
        return _base_url
    return os.environ.get(
        "SHEKEL_API_BASE_URL",
        "https://shekel-ai-estimator-4e9f4efc9094.herokuapp.com"
    )


def set_base_url(url: str):
    """Set the API base URL."""
    global _base_url
    _base_url = url


def format_result(result: dict) -> str:
    """Format API result as a readable string."""
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def estimate_vehicle(
    api_key: Annotated[str, "Your Shekel Mobility API key for authentication"],
    vehicle_name: Annotated[str, "Name of the vehicle (e.g., 'Toyota Camry', 'Honda Accord')"],
    year: Annotated[int, "Year of manufacture (e.g., 2019, 2020)"],
    condition: Annotated[str, "Vehicle condition: 'foreign_used' (Tokunbo/imported) or 'local_used' (Nigerian used)"],
    region: Annotated[str, "Region/country for pricing (default: 'Nigeria')"] = "Nigeria",
    mileage: Annotated[int | None, "Vehicle mileage in kilometers (optional but improves accuracy)"] = None,
    description: Annotated[str | None, "Additional details like 'Automatic, Leather seats, Navigation' (optional)"] = None,
    source: Annotated[str, "Source type: 'DEFAULT' for regular listings, 'AUCTION' for auction vehicles"] = "DEFAULT",
    hard_refresh: Annotated[bool, "Set to true to bypass cache and get fresh results"] = False,
) -> str:
    """
    Estimate the market price of a vehicle in the African automotive market.

    This tool searches multiple Nigerian automotive marketplaces (Jiji, Cars45, etc.),
    analyzes comparable listings, and provides three price estimates:
    - LLM estimate: Pure AI-driven analysis
    - Calculated estimate: Statistical weighted average
    - Hybrid estimate: Combination of both approaches

    Returns detailed results including confidence score, comparable vehicles found,
    and AI reasoning for the price estimate.

    Example usage:
    - estimate_vehicle(api_key="your-key", vehicle_name="Toyota Camry", year=2019, condition="foreign_used")
    - estimate_vehicle(api_key="your-key", vehicle_name="Honda Accord", year=2020, condition="local_used", mileage=85000)
    """
    try:
        client = ShekelAPIClient(get_base_url(), api_key)
        result = await client.estimate_vehicle(
            vehicle_name=vehicle_name,
            year=year,
            condition=condition,
            region=region,
            mileage=mileage,
            description=description,
            source=source,
            hard_refresh=hard_refresh,
        )
        await client.close()

        # Check for errors
        if result.get("status", "").upper() == "FAILED":
            return f"Estimation failed: {result.get('error_message', 'Unknown error')}"

        # Check for timeout
        if result.get("_timeout"):
            return f"Request timed out. {result.get('_message', '')} Current status: {result.get('status')}"

        return format_result(result)

    except Exception as e:
        logger.error(f"Error estimating vehicle: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def generate_caption(
    api_key: Annotated[str, "Your Shekel Mobility API key for authentication"],
    vehicle_name: Annotated[str, "Name of the vehicle (e.g., 'Toyota Camry XLE')"],
    year: Annotated[int, "Year of manufacture"],
    platforms: Annotated[list[str], "List of platforms: 'facebook', 'instagram', 'tiktok', 'whatsapp'"],
    tone: Annotated[str, "Caption tone: 'professional', 'casual', 'urgent', 'luxury', or 'budget'"] = "professional",
    language: Annotated[str, "Language for captions (e.g., 'English', 'Pidgin')"] = "English",
    make: Annotated[str | None, "Vehicle make (e.g., 'Toyota')"] = None,
    model: Annotated[str | None, "Vehicle model (e.g., 'Camry')"] = None,
    condition: Annotated[str | None, "Vehicle condition: 'foreign_used' or 'local_used'"] = None,
    price: Annotated[float | None, "Vehicle price (optional)"] = None,
    currency: Annotated[str, "Currency code (default: 'NGN' for Nigerian Naira)"] = "NGN",
    variations_per_platform: Annotated[int, "Number of caption variations per platform (1-3)"] = 1,
    hashtag_count: Annotated[int, "Number of hashtags to generate (1-15)"] = 5,
    context_suggestions: Annotated[str | None, "Additional instructions for caption generation (e.g., 'Focus on luxury features')"] = None,
    hard_refresh: Annotated[bool, "Set to true to bypass cache and get fresh results"] = False,
) -> str:
    """
    Generate optimized social media captions and hashtags for vehicle listings.

    Creates platform-specific captions tailored for Facebook, Instagram, TikTok,
    and WhatsApp. Each platform gets captions optimized for its character limits
    and audience expectations.

    Tone options:
    - professional: Business-like, trustworthy
    - casual: Friendly, conversational
    - urgent: Sales-focused, create urgency
    - luxury: Premium, exclusive feel
    - budget: Value-focused, affordable

    Returns captions per platform and relevant hashtags for maximum engagement.

    Example usage:
    - generate_caption(api_key="key", vehicle_name="Toyota Camry", year=2020, platforms=["instagram", "facebook"])
    - generate_caption(api_key="key", vehicle_name="Mercedes C300", year=2021, platforms=["instagram"], tone="luxury", price=25000000)
    """
    try:
        client = ShekelAPIClient(get_base_url(), api_key)
        result = await client.generate_caption(
            vehicle_name=vehicle_name,
            year=year,
            platforms=platforms,
            tone=tone,
            language=language,
            make=make,
            model=model,
            condition=condition,
            price=price,
            currency=currency,
            variations_per_platform=variations_per_platform,
            hashtag_count=hashtag_count,
            context_suggestions=context_suggestions,
            hard_refresh=hard_refresh,
        )
        await client.close()

        # Check for errors
        if result.get("status", "").upper() == "FAILED":
            return f"Caption generation failed: {result.get('error_message', 'Unknown error')}"

        # Check for timeout
        if result.get("_timeout"):
            return f"Request timed out. {result.get('_message', '')} Current status: {result.get('status')}"

        return format_result(result)

    except Exception as e:
        logger.error(f"Error generating captions: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def optimize_listing(
    api_key: Annotated[str, "Your Shekel Mobility API key for authentication"],
    vehicle_name: Annotated[str, "Name of the vehicle (e.g., 'Toyota Camry XLE')"],
    year: Annotated[int, "Year of manufacture"],
    title_count: Annotated[int, "Number of title suggestions to generate (1-5)"] = 3,
    include_seo_keywords: Annotated[bool, "Whether to generate SEO keywords"] = True,
    language: Annotated[str, "Language for content (e.g., 'English')"] = "English",
    make: Annotated[str | None, "Vehicle make (e.g., 'Toyota')"] = None,
    model: Annotated[str | None, "Vehicle model (e.g., 'Camry')"] = None,
    condition: Annotated[str | None, "Vehicle condition: 'foreign_used' or 'local_used'"] = None,
    price: Annotated[float | None, "Vehicle price (optional)"] = None,
    currency: Annotated[str, "Currency code (default: 'NGN')"] = "NGN",
    description: Annotated[str | None, "Vehicle description with features (e.g., 'Leather seats, sunroof, navigation')"] = None,
    context_suggestions: Annotated[str | None, "Additional instructions (e.g., 'Target young professionals')"] = None,
    hard_refresh: Annotated[bool, "Set to true to bypass cache and get fresh results"] = False,
) -> str:
    """
    Optimize a vehicle listing with AI-generated titles and SEO keywords.

    Generates multiple title variations optimized for marketplace listings,
    plus SEO keywords to improve search visibility.

    Note: Image analysis is not available via MCP. For full image quality
    analysis and composition suggestions, use the REST API directly with
    image uploads.

    Returns:
    - Multiple title suggestions ranked by effectiveness
    - SEO keywords for search optimization
    - Rationale for each title suggestion

    Example usage:
    - optimize_listing(api_key="key", vehicle_name="Toyota Camry", year=2020, title_count=5)
    - optimize_listing(api_key="key", vehicle_name="Honda Accord", year=2019, description="Leather, Navigation, Sunroof", include_seo_keywords=True)
    """
    try:
        client = ShekelAPIClient(get_base_url(), api_key)
        result = await client.optimize_listing(
            vehicle_name=vehicle_name,
            year=year,
            title_count=title_count,
            include_seo_keywords=include_seo_keywords,
            language=language,
            make=make,
            model=model,
            condition=condition,
            price=price,
            currency=currency,
            description=description,
            context_suggestions=context_suggestions,
            hard_refresh=hard_refresh,
        )
        await client.close()

        # Check for errors
        if result.get("status", "").upper() == "FAILED":
            return f"Listing optimization failed: {result.get('error_message', 'Unknown error')}"

        # Check for timeout
        if result.get("_timeout"):
            return f"Request timed out. {result.get('_message', '')} Current status: {result.get('status')}"

        return format_result(result)

    except Exception as e:
        logger.error(f"Error optimizing listing: {e}")
        return f"Error: {str(e)}"


def run_server():
    """Run the MCP server with stdio transport."""
    mcp.run(transport="stdio")
