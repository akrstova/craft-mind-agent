
import os
import googlemaps
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from googlemaps.places import places_nearby
from geopy.geocoders import Nominatim



load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps_client = googlemaps.Client(key=API_KEY)

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

@tool
def add(a: float, b: float):
    """Add two numbers."""
    return a + b

@tool
def multiply(a: float, b: float):
    """Multiply two numbers."""
    return a * b

@tool
def divide(a: float, b: float):
    """Divide two numbers."""
    return a / b



def get_lat_long_from_location(location_name: str) -> str:
    """
    Convert a location name into a latitude,longitude string.
    """
    try:
        geolocator = Nominatim(user_agent="craft_mind_agent")
        location = geolocator.geocode(location_name)

        if location:
            return f"{location.latitude},{location.longitude}"
        else:
            return "⚠️ Location not found."
    except Exception as e:
        return f"❌ Error retrieving location: {str(e)}"




def find_craft_shops(location: str, radius: int = 5000, keyword: str = "yarn shop") -> str:
    location_lat_long = get_lat_long_from_location(location)
    try:
        places_result = places_nearby(
            client=gmaps_client,
            location=location_lat_long,
            radius=radius,
            keyword=keyword,
            type="store"
        )
        results = places_result.get("results", [])
        if not results:
            return "No nearby craft or yarn shops found."

        output = "🧶 Here are some nearby yarn/craft shops:\n\n"
        for place in results[:5]:
            name = place.get("name")
            address = place.get("vicinity")
            rating = place.get("rating", "N/A")
            output += f"• {name} ({rating}⭐)\n  📍 {address}\n\n"
        return output
    except Exception as e:
        return f"Error while searching: {e}"



@tool
def search_nearby_craft_shops(location: str, keyword: str) -> str:
    """Search for nearby shops for a given keyword using Google Maps from a given location string or lat,lng."""
    return find_craft_shops(location=location, keyword=keyword)



@tool
def find_products_with_prices(query: str) -> str:
    """Search for products and prices using Tavily. Input should be a product search query."""
    search_tool = TavilySearchResults(k=5)
    results = search_tool.run(query)

    output = []
    for res in results:
        title = res.get("title", "")
        snippet = res.get("content", "")
        link = res.get("url", "")
        output.append(f"🛒 **{title}**\n{snippet}\n🔗 {link}\n")

    return "\n\n".join(output) if output else "No results found."



shopper_agent = create_react_agent(
    model=model,
    tools=[find_products_with_prices, search_nearby_craft_shops, add, divide, multiply],
    prompt=(
        """You are a shopper agent specifically designed for shopping for craft tools and supplies.
        Given a list of supplies (e.g. 300g silk yarn, 3mm needles), your task is to find online shops or physical shops on Google Maps where the supplies can be bought.
        Additionally, you need to calculate the total estimated cost of the craft project based on the needed and available supplies.
        INSTRUCTIONS:
        - For every item in the supplies list, make a Google search to find relevant online shops in the user's location.
        - If possible, infer the item prices in the online shops and calculate the total estimated cost of the project based on the retrieved prices per item and available math tools (add, divide, multiply).
        - If for some products you cannot infer prices, just say you don't know how much the item will cost.
        - In addition, search for physical stores on Google Maps in the user's location and return them as an alternative.
        - Return the list of items with where to buy them, and the total cost of the project.
        """
        
    ),
    name="shopper_agent",
)

if __name__ == "__main__":
    find_craft_shops()
