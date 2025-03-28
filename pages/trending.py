import streamlit as st
import numpy as np
from sklearn.cluster import KMeans
from db.chroma_config import get_chroma_client
import folium
from streamlit_folium import folium_static

def get_user_cluster(users_collection, current_user_id):
    """Détermine le cluster de l'utilisateur actuel"""
    users_data = users_collection.get(
        include=['embeddings', 'metadatas']
    )
    
    if not users_data['embeddings']:
        return None, None
    
    # Préparer les données pour le clustering
    embeddings = np.array(users_data['embeddings'])
    
    # Appliquer K-means
    n_clusters = min(3, len(embeddings))  # Ajuster le nombre de clusters selon les données
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    
    # Trouver le cluster de l'utilisateur actuel
    user_index = users_data['ids'].index(current_user_id)
    user_cluster = clusters[user_index]
    
    # Retourner le cluster et les données complètes pour utilisation ultérieure
    return user_cluster, (embeddings, clusters)

def get_recommended_places(places_collection, user_preferences, n_recommendations=10):
    """Trouve les lieux recommandés basés sur les préférences utilisateur"""
    # Convertir les préférences en vecteur de requête
    query_vector = user_preferences
    
    # Rechercher les lieux similaires
    results = places_collection.query(
        query_embeddings=[query_vector],
        n_results=n_recommendations,
        include=['metadatas', 'distances']
    )
    
    return results['metadatas'][0], results['distances'][0]

def show_trending_page():
    st.title("Trending Places 🔥")
    
    client = get_chroma_client()
    users_collection = client.get_collection("users")
    places_collection = client.get_collection("places")
    
    # Récupérer l'utilisateur actuel et ses préférences
    current_user_id = st.session_state['user_token']
    user_data = users_collection.get(
        ids=[current_user_id],
        include=['embeddings', 'metadatas']
    )
    
    if not user_data['embeddings']:
        st.warning("Please complete your profile first to get personalized recommendations!")
        return
    
    # Obtenir le cluster de l'utilisateur
    user_cluster, cluster_data = get_user_cluster(users_collection, current_user_id)
    
    if user_cluster is None:
        st.warning("Not enough user data for recommendations yet.")
        return
    
    # Afficher les recommandations
    st.subheader("Places you might like")
    
    # Obtenir les recommandations
    recommended_places, scores = get_recommended_places(places_collection, user_data['embeddings'][0])
    
    # Créer la carte
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Afficher les recommandations dans un grid moderne
    cols = st.columns(2)
    for idx, (place, score) in enumerate(zip(recommended_places, scores)):
        col = cols[idx % 2]
        with col:
            with st.container():
                st.markdown(f"""
                <div style='padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 242, 255, 0.3); margin-bottom: 10px;'>
                    <h4>{place['name']}</h4>
                    <p>📍 {place['address']}</p>
                    {'⭐ ' + str(place['rating']) if 'rating' in place else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # Ajouter le marqueur sur la carte
                folium.Marker(
                    [place['latitude'], place['longitude']],
                    popup=f"""
                    <b>{place['name']}</b><br>
                    {place['address']}<br>
                    Rating: {place.get('rating', 'N/A')}
                    """,
                    tooltip=place['name']
                ).add_to(m)
    
    # Afficher la carte
    st.subheader("Map View")
    folium_static(m)
    
    # Statistiques du cluster
    st.subheader("Your Taste Profile")
    if cluster_data:
        embeddings, clusters = cluster_data
        cluster_size = sum(clusters == user_cluster)
        st.info(f"You are in a group with {cluster_size-1} other users who share similar interests!")
