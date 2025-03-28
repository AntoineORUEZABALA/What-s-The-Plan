import os
from dotenv import load_dotenv
import googlemaps
from db.chroma_config import get_chroma_client, init_collections
import numpy as np
from sklearn.cluster import KMeans

load_dotenv()

PLACE_TYPES = [
    'restaurant', 'museum', 'park', 'night_club', 'bar',
    'shopping_mall', 'art_gallery', 'tourist_attraction'
]

def cluster_places(places_data):
    if not places_data:
        return []
    
    # Créer les vecteurs de caractéristiques
    features = np.array([
        [
            place.get('rating', 0),
            place.get('price_level', 0),
            len(place.get('types', [])),
            place.get('user_ratings_total', 0) / 1000
        ] for place in places_data
    ])
    
    # Appliquer K-means
    n_clusters = min(5, len(features))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features)
    return clusters

def import_places_from_google(location="Paris, France", radius=5000):
    """
    Import places from Google Maps API
    """
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    client = get_chroma_client()
    places_collection = client.get_collection("places")

    # Get location coordinates
    geocode_result = gmaps.geocode(location)
    if not geocode_result:
        return
    
    location_coord = geocode_result[0]['geometry']['location']
    
    all_places = []
    for place_type in PLACE_TYPES:
        places_result = gmaps.places_nearby(
            location=(location_coord['lat'], location_coord['lng']),
            radius=radius,
            type=place_type
        )
        
        places_data = []
        for place in places_result.get('results', []):
            # Get detailed place information
            place_details = gmaps.place(place['place_id'])['result']
            places_data.append(place_details)
        
        # Cluster les lieux
        clusters = cluster_places(places_data)
        
        # Stocker les lieux avec leurs clusters
        for place_details, cluster in zip(places_data, clusters):
            # Create place embedding
            place_features = [
                place_details.get('rating', 0),
                len(place_details.get('types', [])),
                place_details.get('user_ratings_total', 0) / 1000
            ]
            
            # Store place in database
            metadata = {
                'name': place_details['name'],
                'address': place_details.get('formatted_address', ''),
                'latitude': place_details['geometry']['location']['lat'],
                'longitude': place_details['geometry']['location']['lng'],
                'rating': place_details.get('rating', 0),
                'types': ','.join(place_details.get('types', [])),
                'place_type': place_type,
                'cluster': int(cluster),
                'phone': place_details.get('formatted_phone_number', ''),
                'website': place_details.get('website', ''),
                'price_level': place_details.get('price_level', 0),
            }
            
            places_collection.upsert(
                ids=[place_details['place_id']],
                embeddings=[place_features],
                metadatas=[metadata]
            )

def init_database():
    """
    Initialize database with collections and import places
    """
    users_collection, places_collection = init_collections()
    
    # Import places for specific locations
    locations = ["Paris, France", "Lyon, France", "Marseille, France"]
    for location in locations:
        import_places_from_google(location)

if __name__ == "__main__":
    init_database()
