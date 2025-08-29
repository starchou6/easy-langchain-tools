"""
Google Maps API Client for Tokyo Travel Helper
Provides direct interaction functionality with Google Maps API
"""

import googlemaps
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from decouple import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Location:
    """Location information data class"""
    lat: float
    lng: float
    address: str
    place_id: Optional[str] = None

@dataclass
class PlaceInfo:
    """Place information data class"""
    name: str
    address: str
    location: Location
    rating: Optional[float] = None
    price_level: Optional[int] = None
    types: List[str] = None
    photos: List[str] = None
    opening_hours: Dict = None
    phone: Optional[str] = None
    website: Optional[str] = None

@dataclass
class RouteInfo:
    """Route information data class"""
    origin: Location
    destination: Location
    distance: str
    duration: str
    steps: List[Dict]
    polyline: str

class GoogleMapsClient:
    """Google Maps API Client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Maps client
        
        Args:
            api_key: Google Maps API key, if not provided will read from environment variables
        """
        self.api_key = api_key or config("GOOGLE_MAPS_API_KEY", default=None)
        if not self.api_key:
            raise ValueError("Google Maps API key is required")
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        logger.info("Google Maps client initialized successfully")
    
    async def geocode_async(self, address: str) -> Optional[Location]:
        """
        Asynchronous geocoding
        
        Args:
            address: Address string
            
        Returns:
            Location object or None
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.gmaps.geocode, address
            )
            
            if result:
                location_data = result[0]['geometry']['location']
                return Location(
                    lat=location_data['lat'],
                    lng=location_data['lng'],
                    address=result[0]['formatted_address'],
                    place_id=result[0].get('place_id')
                )
            return None
        except Exception as e:
            logger.error(f"Geocoding failed: {e}")
            return None
    
    async def search_places_async(self, query: str, location: Optional[Location] = None, 
                                 radius: int = 5000, type: Optional[str] = None,
                                 language: Optional[str] = None, minprice: Optional[int] = None,
                                 maxprice: Optional[int] = None, opennow: Optional[bool] = None,
                                 rankby: Optional[str] = None, pagetoken: Optional[str] = None) -> List[PlaceInfo]:
        """
        Asynchronous place search
        
        Args:
            query: Search query
            location: Search center location
            radius: Search radius (meters), cannot be used when rankby=distance
            type: Place type (e.g., 'restaurant', 'hotel', etc.)
            language: Language code for returned results (e.g., 'en', 'ja', 'zh-CN')
            minprice: Minimum price level (0-4)
            maxprice: Maximum price level (0-4)
            opennow: Whether to return only currently open places
            rankby: Sorting method ('prominence' or 'distance')
            pagetoken: Pagination token for getting next page results
            
        Returns:
            List of PlaceInfo objects
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Build search parameters
            search_params = {
                'query': query
            }
            
            if location:
                search_params['location'] = (location.lat, location.lng)
            
            if radius and rankby != 'distance':
                search_params['radius'] = radius
            
            if type:
                search_params['type'] = type
            
            if language:
                search_params['language'] = language
            
            if minprice is not None:
                search_params['minprice'] = minprice
            
            if maxprice is not None:
                search_params['maxprice'] = maxprice
            
            if opennow is not None:
                search_params['opennow'] = opennow
            
            if rankby:
                search_params['rankby'] = rankby
            
            if pagetoken:
                search_params['pagetoken'] = pagetoken
            
            result = await loop.run_in_executor(
                None, lambda: self.gmaps.places(**search_params)
            )
            
            places = []
            for place in result.get('results', []):
                place_info = self._parse_place_result(place)
                if place_info:
                    places.append(place_info)
            
            return places
        except Exception as e:
            logger.error(f"Place search failed: {e}")
            return []
    
    async def get_directions_async(self, origin: str, destination: str, 
                                 mode: str = 'transit') -> Optional[RouteInfo]:
        """
        Asynchronous route planning
        
        Args:
            origin: Starting point
            destination: Destination
            mode: Transportation mode ('driving', 'walking', 'bicycling', 'transit')
            
        Returns:
            RouteInfo object or None
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self.gmaps.directions(origin, destination, mode=mode)
            )
            
            if result:
                route = result[0]
                leg = route['legs'][0]
                
                # Parse origin and destination
                origin_location = Location(
                    lat=leg['start_location']['lat'],
                    lng=leg['start_location']['lng'],
                    address=leg['start_address']
                )
                
                destination_location = Location(
                    lat=leg['end_location']['lat'],
                    lng=leg['end_location']['lng'],
                    address=leg['end_address']
                )
                
                return RouteInfo(
                    origin=origin_location,
                    destination=destination_location,
                    distance=leg['distance']['text'],
                    duration=leg['duration']['text'],
                    steps=leg['steps'],
                    polyline=route['overview_polyline']['points']
                )
            return None
        except Exception as e:
            logger.error(f"Route planning failed: {e}")
            return None
    
    async def get_nearby_places(self, location: Location, 
                               place_type: str = 'restaurant', 
                               radius: int = 1000,
                               price_level: Optional[Tuple[int, int]] = None,
                               rating_min: Optional[float] = None,
                               rankby: str = 'prominence',
                               language: str = "en") -> List[PlaceInfo]:
        """
        Get nearby places
        
        Args:
            location: Center location
            place_type: Place type
            radius: Search radius (cannot be used when rankby=distance)
            price_level: Price range (min_price, max_price), 0-4
            rating_min: Minimum rating
            rankby: Sorting method ('prominence' or 'distance')
            language: Language code for returned results
            
        Returns:
            List of place information
        """
        # Build search parameters
        search_params = {
            'query': place_type,
            'location': location,
            'type': place_type,
            'rankby': rankby,
            'language': language
        }
        
        if radius and rankby != 'distance':
            search_params['radius'] = radius
        
        if price_level:
            min_price, max_price = price_level
            search_params['minprice'] = min_price
            search_params['maxprice'] = max_price
        
        places = await self.search_places_async(**search_params)
        
        # Filter by rating
        if rating_min:
            places = [place for place in places if place.rating and place.rating >= rating_min]
        
        return places
    
    def _parse_place_result(self, place_data: Dict) -> Optional[PlaceInfo]:
        """
        Parse place data
        
        Args:
            place_data: Raw place data
            
        Returns:
            PlaceInfo object or None
        """
        try:
            location = Location(
                lat=place_data['geometry']['location']['lat'],
                lng=place_data['geometry']['location']['lng'],
                address=place_data.get('formatted_address', ''),
                place_id=place_data.get('place_id')
            )
            
            return PlaceInfo(
                name=place_data.get('name', ''),
                address=place_data.get('formatted_address', ''),
                location=location,
                rating=place_data.get('rating'),
                price_level=place_data.get('price_level'),
                types=place_data.get('types', []),
                photos=place_data.get('photos', []),
                opening_hours=place_data.get('opening_hours', {}),
                phone=place_data.get('formatted_phone_number'),
                website=place_data.get('website')
            )
        except Exception as e:
            logger.error(f"Failed to parse place data: {e}")
            return None