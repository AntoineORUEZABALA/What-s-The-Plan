import streamlit as st
from db.chroma_config import get_chroma_client

def show_profile_page():
    st.title("My Profile")
    
    client = get_chroma_client()
    users_collection = client.get_collection("users")
    user_id = st.session_state['user_token']
    
    # Récupérer les données utilisateur
    try:
        user_data = users_collection.get(
            ids=[user_id],
            include=['metadatas']
        )
        user_metadata = user_data['metadatas'][0] if user_data['metadatas'] else {}
    except:
        user_metadata = {}
    
    with st.form("profile_form"):
        name = st.text_input("Name", value=user_metadata.get('name', ''))
        
        st.subheader("Preferences")
        
        # Restaurants
        st.subheader("🍽️ Restaurants", divider="rainbow")
        col1, col2 = st.columns(2)
        with col1:
            preferences = {
                "restaurant_gastronomique": st.checkbox("Gastronomique", value=user_metadata.get('pref_restaurant_gastronomique', False)),
                "restaurant_traditionnel": st.checkbox("Traditionnel", value=user_metadata.get('pref_restaurant_traditionnel', False)),
                "restaurant_asiatique": st.checkbox("Asiatique", value=user_metadata.get('pref_restaurant_asiatique', False)),
                "restaurant_italien": st.checkbox("Italien", value=user_metadata.get('pref_restaurant_italien', False)),
            }
        with col2:
            preferences.update({
                "restaurant_vegetarien": st.checkbox("Végétarien/Vegan", value=user_metadata.get('pref_restaurant_vegetarien', False)),
                "restaurant_fastfood": st.checkbox("Fast-food", value=user_metadata.get('pref_restaurant_fastfood', False)),
                "restaurant_fusion": st.checkbox("Fusion", value=user_metadata.get('pref_restaurant_fusion', False)),
                "restaurant_seafood": st.checkbox("Fruits de mer", value=user_metadata.get('pref_restaurant_seafood', False)),
            })

        # Museums
        st.subheader("🏛️ Musées", divider="rainbow")
        col1, col2 = st.columns(2)
        with col1:
            preferences.update({
                "museum_art": st.checkbox("Art", value=user_metadata.get('pref_museum_art', False)),
                "museum_history": st.checkbox("Histoire", value=user_metadata.get('pref_museum_history', False)),
                "museum_science": st.checkbox("Sciences", value=user_metadata.get('pref_museum_science', False)),
            })
        with col2:
            preferences.update({
                "museum_modern": st.checkbox("Art Moderne", value=user_metadata.get('pref_museum_modern', False)),
                "museum_natural": st.checkbox("Histoire Naturelle", value=user_metadata.get('pref_museum_natural', False)),
                "museum_technology": st.checkbox("Technologie", value=user_metadata.get('pref_museum_technology', False)),
            })

        # Parks
        st.subheader("🌳 Parcs", divider="rainbow")
        col1, col2 = st.columns(2)
        with col1:
            preferences.update({
                "park_nature": st.checkbox("Nature/Botanique", value=user_metadata.get('pref_park_nature', False)),
                "park_family": st.checkbox("Familial", value=user_metadata.get('pref_park_family', False)),
                "park_sport": st.checkbox("Sport/Loisirs", value=user_metadata.get('pref_park_sport', False)),
            })
        with col2:
            preferences.update({
                "park_historical": st.checkbox("Historique", value=user_metadata.get('pref_park_historical', False)),
                "park_thematic": st.checkbox("Thématique", value=user_metadata.get('pref_park_thematic', False)),
                "park_animal": st.checkbox("Animalier", value=user_metadata.get('pref_park_animal', False)),
            })

        # Nightlife
        st.subheader("🌙 Vie Nocturne", divider="rainbow")
        col1, col2 = st.columns(2)
        with col1:
            preferences.update({
                "nightlife_bar": st.checkbox("Bars", value=user_metadata.get('pref_nightlife_bar', False)),
                "nightlife_club": st.checkbox("Boîtes de nuit", value=user_metadata.get('pref_nightlife_club', False)),
                "nightlife_pub": st.checkbox("Pubs", value=user_metadata.get('pref_nightlife_pub', False)),
            })
        with col2:
            preferences.update({
                "nightlife_concert": st.checkbox("Salles de concert", value=user_metadata.get('pref_nightlife_concert', False)),
                "nightlife_karaoke": st.checkbox("Karaoké", value=user_metadata.get('pref_nightlife_karaoke', False)),
                "nightlife_comedy": st.checkbox("Comedy Club", value=user_metadata.get('pref_nightlife_comedy', False)),
            })

        # Shopping
        st.subheader("🛍️ Shopping", divider="rainbow")
        col1, col2 = st.columns(2)
        with col1:
            preferences.update({
                "shopping_mall": st.checkbox("Centre Commercial", value=user_metadata.get('pref_shopping_mall', False)),
                "shopping_luxury": st.checkbox("Luxe", value=user_metadata.get('pref_shopping_luxury', False)),
                "shopping_vintage": st.checkbox("Vintage/Seconde main", value=user_metadata.get('pref_shopping_vintage', False)),
            })
        with col2:
            preferences.update({
                "shopping_local": st.checkbox("Boutiques locales", value=user_metadata.get('pref_shopping_local', False)),
                "shopping_market": st.checkbox("Marchés", value=user_metadata.get('pref_shopping_market', False)),
                "shopping_artisan": st.checkbox("Artisanat", value=user_metadata.get('pref_shopping_artisan', False)),
            })

        if st.form_submit_button("Save Profile"):
            # Créer le vecteur d'embedding des préférences
            preference_vector = [int(v) for v in preferences.values()]
            
            # Mettre à jour le profil
            users_collection.upsert(
                ids=[user_id],
                embeddings=[preference_vector],
                metadatas=[{
                    'name': name,
                    **{f"pref_{k}": v for k, v in preferences.items()}
                }]
            )
            st.success("Profile updated successfully!")
