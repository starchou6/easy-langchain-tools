#!/usr/bin/env python3
"""
Google Maps Tools Creation Module
"""

from langchain_core.tools import tool
from typing import Optional
import json
from google_maps_client import GoogleMapsClient

# Create Google Maps client
client = GoogleMapsClient()

@tool
async def search_restaurants(area: str, cuisine: Optional[str] = None, 
                           price_level: Optional[str] = None,
                           rating_min: Optional[float] = None, radius: int = 5000) -> str:
    """
    Search for restaurants in a specified area - optimized version to reduce AI processing time
    
    Args:
        area: Area name, such as "Shibuya", "Shinjuku", "Tokyo", "New York", "London"
        cuisine: Cuisine type, such as "sushi", "ramen", "tempura"
        price_level: Price level range, such as "0-2" (budget), "2-3" (mid-range), "3-4" (high-end)
        rating_min: Minimum rating, such as 4.0
        radius: Search radius (meters), such as 1000, 5000, 10000
    
    Returns:
        Optimized restaurant information JSON string
    """
    try:
        # Parse price level
        min_price = None
        max_price = None
        if price_level:
            try:
                min_price, max_price = map(int, price_level.split('-'))
            except:
                pass
        
        # Build search query
        query = f"{cuisine} restaurant" if cuisine else "restaurant"
        query += f" in {area}"
        
        # Directly call Google Maps API, let API handle filtering
        places = await client.search_places_async(
            query=query,
            type="restaurant",
            language="en",
            radius=radius,
            minprice=min_price,
            maxprice=max_price
        )
        
        # Rating filter (Google Maps API doesn't directly support this, so handle here)
        if rating_min:
            places = [place for place in places if place.rating and place.rating >= rating_min]
        
        # Optimize data
        optimized_results = []
        for place in places:
            optimized = {
                "type": "restaurant",
                "name": place.name,
                "address": place.address,
                "rating": place.rating,
                "price_level": place.price_level,
                "cuisine_type": cuisine or "restaurant",
                "phone": place.phone,
                "website": place.website,
                "location": {
                    "lat": place.location.lat,
                    "lng": place.location.lng
                },
                "operating_hours": "Open now" if place.opening_hours and place.opening_hours.get('open_now') else "Closed",
                "opening_hours": {
                    "open_now": place.opening_hours.get('open_now') if place.opening_hours else None,
                    "weekday_text": place.opening_hours.get('weekday_text') if place.opening_hours else None
                },
                "business_status": "Operating",
                "reviews": f"{getattr(place, 'user_ratings_total', 0)} ratings",
                "recommendation_reason": f"Great {cuisine or 'restaurant'} in {area}",
                "place_id": place.location.place_id,
                "types": place.types[:3] if place.types else [],
                "photos": len(place.photos) if place.photos else 0
            }
            optimized_results.append(optimized)
        
        return json.dumps(optimized_results, ensure_ascii=False)
        
    except Exception as e:
        return f"Failed to search restaurants: {str(e)}"

@tool
async def search_attractions(area: str, attraction_type: Optional[str] = None,
                           price_level: Optional[str] = None,
                           rating_min: Optional[float] = None, radius: int = 5000) -> str:
    """
    Search for tourist attractions in a specified area - optimized version
    
    Args:
        area: Area name, such as "Tokyo", "Shibuya", "Asakusa", "New York", "London"
        attraction_type: Attraction type, such as "museum", "temple", "park"
        price_level: Price level range, such as "0-2" (free), "2-3" (paid)
        rating_min: Minimum rating, such as 4.0
        radius: Search radius (meters), such as 1000, 5000, 10000
    
    Returns:
        Optimized attraction information JSON string
    """
    try:
        # Parse price level
        min_price = None
        max_price = None
        if price_level:
            try:
                min_price, max_price = map(int, price_level.split('-'))
            except:
                pass
        
        # Build search query
        query = f"tourist attractions in {area}"
        if attraction_type:
            query += f" {attraction_type}"
        
        # Directly call Google Maps API, let API handle filtering
        places = await client.search_places_async(
            query=query,
            type="tourist_attraction",
            language="en",
            radius=radius,
            minprice=min_price,
            maxprice=max_price
        )
        
        # Rating filter (Google Maps API doesn't directly support this, so handle here)
        if rating_min:
            places = [place for place in places if place.rating and place.rating >= rating_min]
        
        # Optimize data
        optimized_results = []
        for place in places:
            optimized = {
                "type": "attraction",
                "name": place.name,
                "address": place.address,
                "rating": place.rating,
                "price_level": place.price_level,
                "phone": place.phone,
                "website": place.website,
                "location": {
                    "lat": place.location.lat,
                    "lng": place.location.lng
                },
                "opening_hours": "Open now" if place.opening_hours and place.opening_hours.get('open_now') else "Closed",
                "opening_hours": {
                    "open_now": place.opening_hours.get('open_now') if place.opening_hours else None,
                    "weekday_text": place.opening_hours.get('weekday_text') if place.opening_hours else None
                },
                "description": f"Popular {attraction_type or 'attraction'} in {area}",
                "recommendation_reason": f"Highly rated {attraction_type or 'attraction'} in {area}",
                "place_id": place.location.place_id,
                "types": place.types[:3] if place.types else [],
                "photos": len(place.photos) if place.photos else 0
            }
            optimized_results.append(optimized)
        
        return json.dumps(optimized_results, ensure_ascii=False)
        
    except Exception as e:
        return f"Failed to search attractions: {str(e)}"

@tool
async def search_hotels(area: str, hotel_type: Optional[str] = None,
                       price_level: Optional[str] = None, rating_min: Optional[float] = None,
                       radius: int = 5000) -> str:
    """
    Search for hotels in a specified area - optimized version to reduce AI processing time
    
    Args:
        area: Area name, such as "Shibuya", "Shinjuku", "Tokyo", "New York", "London"
        hotel_type: Hotel type, such as "luxury", "budget", "business", "resort"
        price_level: Price level range, such as "0-2" (budget), "2-3" (mid-range), "3-4" (luxury)
        rating_min: Minimum rating, such as 4.0
        radius: Search radius (meters), such as 1000, 5000, 10000
    
    Returns:
        Optimized hotel information JSON string
    """
    try:
        # Parse price level
        min_price = None
        max_price = None
        if price_level:
            try:
                min_price, max_price = map(int, price_level.split('-'))
            except:
                pass
        
        # Build search query
        query = f"hotels in {area}"
        if hotel_type:
            query += f" {hotel_type}"
        
        # Directly call Google Maps API, let API handle filtering
        places = await client.search_places_async(
            query=query,
            type="lodging",
            language="en",
            radius=radius,
            minprice=min_price,
            maxprice=max_price
        )
        
        # Rating filter (Google Maps API doesn't directly support this, so handle here)
        if rating_min:
            places = [place for place in places if place.rating and place.rating >= rating_min]
        
        # Optimize data
        optimized_results = []
        for place in places:
            optimized = {
                "type": "hotel",
                "name": place.name,
                "address": place.address,
                "rating": place.rating,
                "price_level": place.price_level,
                "phone": place.phone,
                "website": place.website,
                "location": {
                    "lat": place.location.lat,
                    "lng": place.location.lng
                },
                "operating_hours": "Open now" if place.opening_hours and place.opening_hours.get('open_now') else "Closed",
                "opening_hours": {
                    "open_now": place.opening_hours.get('open_now') if place.opening_hours else None,
                    "weekday_text": place.opening_hours.get('weekday_text') if place.opening_hours else None
                },
                "business_status": "Operating",
                "reviews": f"{getattr(place, 'user_ratings_total', 0)} ratings",
                "recommendation_reason": f"Great {hotel_type or 'hotel'} in {area}",
                "place_id": place.location.place_id,
                "types": place.types[:3] if place.types else [],
                "photos": len(place.photos) if place.photos else 0
            }
            optimized_results.append(optimized)
        
        return json.dumps(optimized_results, ensure_ascii=False)
        
    except Exception as e:
        return f"Failed to search hotels: {str(e)}"

@tool
async def get_directions(origin: str, destination: str, mode: str = 'transit') -> str:
    """
    Get route planning from origin to destination
    
    Args:
        origin: Starting point, such as "Tokyo Station", "New York Penn Station"
        destination: Destination, such as "Tokyo Tower", "Empire State Building"
        mode: Transportation mode, options: "transit", "driving", "walking", "bicycling"
    
    Returns:
        Route information JSON string
    """
    try:
        route = await client.get_directions_async(origin, destination, mode)
        
        if route:
            result = {
                "origin": {
                    "address": route.origin.address,
                    "lat": route.origin.lat,
                    "lng": route.origin.lng
                },
                "destination": {
                    "address": route.destination.address,
                    "lat": route.destination.lat,
                    "lng": route.destination.lng
                },
                "distance": route.distance,
                "duration": route.duration,
                "steps": route.steps,
                "mode": mode
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": "Unable to get route information"}, ensure_ascii=False)
            
    except Exception as e:
        return f"Failed to get directions: {str(e)}"

@tool
async def get_location_info(address: str) -> str:
    """
    Get detailed information for an address
    
    Args:
        address: Address, such as "Tokyo Tower, Tokyo, Japan", "Empire State Building, New York, USA"
    
    Returns:
        Location information JSON string
    """
    try:
        location = await client.geocode_async(address)
        
        if location:
            result = {
                "address": location.address,
                "lat": location.lat,
                "lng": location.lng,
                "place_id": location.place_id
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": "Unable to find this address"}, ensure_ascii=False)
            
    except Exception as e:
        return f"Failed to get location information: {str(e)}"

def get_maps_tools():
    """
    Get Google Maps tools list
    """
    return [
        search_restaurants,
        search_attractions,
        search_hotels,
        get_directions,
        get_location_info
    ]