import streamlit as st
import googlemaps
from streamlit_folium import folium_static
import folium
from db.chroma_config import get_chroma_client

def show_map_page():
    st.title("Explore Places")
    
    client = get_chroma_client()
    places_collection = client.get_collection("places")
    
    # Search bar
    search_query = st.text_input("Search for places")
    
    # Initialize map
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    if search_query:
        # Rechercher dans ChromaDB
        results = places_collection.query(
            query_texts=[search_query],
            n_results=10,
            include=['metadatas', 'distances']
        )
        
        for metadata in results['metadatas'][0]:
            location = [metadata['latitude'], metadata['longitude']]
            name = metadata['name']
            
            folium.Marker(
                location,
                popup=f"""
                <b>{name}</b><br>
                {metadata.get('address', '')}<br>
                Rating: {metadata.get('rating', 'N/A')}
                """,
                tooltip=name
            ).add_to(m)
    
    folium_static(m)

def index_place(place_data, gmaps_client):
    """Indexer un nouveau lieu dans ChromaDB"""
    client = get_chroma_client()
    places_collection = client.get_collection("places")
    
    # Créer un embedding simple basé sur les caractéristiques du lieu
    place_features = [
        place_data.get('rating', 0),
        len(place_data.get('types', [])),
        place_data.get('user_ratings_total', 0) / 1000
    ]
    
    places_collection.upsert(
        ids=[place_data['place_id']],
        embeddings=[place_features],
        metadatas=[{
            'name': place_data['name'],
            'address': place_data.get('formatted_address', ''),
            'latitude': place_data['geometry']['location']['lat'],
            'longitude': place_data['geometry']['location']['lng'],
            'rating': place_data.get('rating', 0),
            'types': ','.join(place_data.get('types', []))
        }]
    )
