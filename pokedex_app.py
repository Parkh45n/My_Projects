import streamlit as st
import requests

BASE_URL = "https://pokeapi.co/api/v2/"

def get_pokemon_info(name):
    try:
        response = requests.get(f"{BASE_URL}pokemon/{name.lower()}")
        response.raise_for_status()
        return response.json()
    except:
        return None

def get_species_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return None

def get_evolution_chain(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return parse_evolution_chain(data['chain'])
    except:
        return []

def parse_evolution_chain(chain):
    evolution = []
    current = chain
    while current:
        evolution.append(current['species']['name'])
        if current['evolves_to']:
            current = current['evolves_to'][0]
        else:
            break
    return evolution

def get_sprite_for(name, shiny=False, form=None):
    data = get_pokemon_info(name)
    if not data:
        return None
    
    if form:
        for form_entry in data.get('forms', []):
            if form_entry['name'].lower() == form.lower():
                form_data = requests.get(form_entry['url']).json()
                return form_data['sprites']['front_shiny'] if shiny else form_data['sprites']['front_default']
    
    return data['sprites']['front_shiny'] if shiny else data['sprites']['front_default']

def get_flavor_text(species_data):
    for entry in species_data['flavor_text_entries']:
        if entry['language']['name'] == 'en':
            return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
    return "No description available."

def get_ability_description(ability_url):
    try:
        response = requests.get(ability_url)
        response.raise_for_status()
        data = response.json()
        for entry in data['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
        return "No description available."
    except:
        return "No description available."

def get_move_description(move_url):
    try:
        response = requests.get(move_url)
        response.raise_for_status()
        data = response.json()
        for entry in data['flavor_text_entries']:
            if entry['language']['name'] == 'en' and entry['version_group']['name'] in ['sword-shield', 'sun-moon', 'x-y']:
                return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
        return "No description available."
    except:
        return "No description available."

def get_pokemon_forms(pokemon_name):
    try:
        pokemon_data = get_pokemon_info(pokemon_name)
        if not pokemon_data:
            return []
        
        forms = []
        for form in pokemon_data.get('forms', []):
            form_data = requests.get(form['url']).json()
            form_name = form_data['form_name']
            if form_name not in [f['form_name'] for f in forms]:
                forms.append({
                    'form_name': form_name,
                    'is_mega': 'mega' in form_name.lower(),
                    'is_gigantamax': 'gigantamax' in form_name.lower(),
                    'is_default': form_data['is_default'],
                    'sprites': form_data['sprites']
                })
        return forms
    except:
        return []

def get_all_forms_from_species(pokemon_name):
    try:
        species_url = f"{BASE_URL}pokemon-species/{pokemon_name.lower()}"
        species_res = requests.get(species_url)
        if species_res.status_code != 200:
            return []
        
        species_data = species_res.json()
        forms = []
        
        for variety in species_data["varieties"]:
            form_name = variety['pokemon']['name']
            form_data = get_pokemon_info(form_name)
            if form_data:
                forms.append({
                    'form_name': form_name,
                    'is_default': variety['is_default'],
                    'sprites': form_data['sprites']
                })
        return forms
    except:
        return []

# --- Streamlit UI ---
st.set_page_config(page_title="Pokédex", page_icon="🔍", layout="centered")
st.title("🔍 Pokédex - Search Any Pokémon")

pokemon_name = st.text_input("Enter Pokémon name", "").strip()
shiny_toggle = st.checkbox("Show shiny version")

if pokemon_name:
    pokemon_data = get_pokemon_info(pokemon_name)
    if pokemon_data:
        species_data = get_species_info(pokemon_data['species']['url'])
        
        if species_data:
            evolution_names = get_evolution_chain(species_data['evolution_chain']['url'])
            flavor_text = get_flavor_text(species_data)
            forms = get_all_forms_from_species(pokemon_name)  # Using the new function to get all forms
            has_alternate_forms = len(forms) > 1  # Check if multiple forms exist
            
            # Layout
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_form = None
                if len(forms) > 1:  # Show form selector if multiple forms exist
                    form_names = [f['form_name'].replace('-', ' ').title() for f in forms]
                    selected_form_name = st.selectbox(
                        "Select Form",
                        form_names,
                        index=0
                    )
                    selected_form = [f for f in forms if f['form_name'].replace('-', ' ').title() == selected_form_name][0]
                    sprite_url = selected_form['sprites']['front_shiny'] if shiny_toggle else selected_form['sprites']['front_default']
                else:
                    sprite_url = pokemon_data['sprites']['front_shiny'] if shiny_toggle else pokemon_data['sprites']['front_default']
                
                if sprite_url:
                    st.image(sprite_url, caption=f"{pokemon_data['name'].title()} ({'Shiny' if shiny_toggle else 'Normal'})", use_container_width=True)
                else:
                    st.warning("No sprite available.")

            with col2:
                st.subheader(f"{pokemon_data['name'].title()} (ID: {pokemon_data['id']})")
                
                # Legendary/Mythical status
                if species_data['is_legendary']:
                    st.markdown("**🔱 Legendary Pokémon**")
                if species_data['is_mythical']:
                    st.markdown("**✨ Mythical Pokémon**")
                
                st.write(f"**Height:** {pokemon_data['height'] / 10:.1f} m")
                st.write(f"**Weight:** {pokemon_data['weight'] / 10:.1f} kg")
                
                types = ', '.join([t['type']['name'].title() for t in pokemon_data['types']])
                st.write(f"**Type(s):** {types}")
                
                # Abilities with descriptions
                st.markdown("**🧠 Abilities:**")
                for ability in pokemon_data['abilities']:
                    ability_name = ability['ability']['name'].replace('-', ' ').title()
                    is_hidden = "(Hidden Ability)" if ability['is_hidden'] else ""
                    with st.expander(f"{ability_name} {is_hidden}"):
                        st.write(get_ability_description(ability['ability']['url']))
                
                st.markdown(f"📖 **Description:** _{flavor_text}_")

            # Base Stats
            st.subheader("📊 Base Stats")
            for stat in pokemon_data['stats']:
                stat_name = stat['stat']['name'].replace('-', ' ').title()
                st.write(f"- **{stat_name}**: {stat['base_stat']}")

            # Moves Section (Top 5)
            st.subheader("⚔️ Top 5 Moves")
            moves = pokemon_data['moves'][:5]  # Only show first 5 moves
            if moves:
                for move in moves:
                    move_name = move['move']['name'].replace('-', ' ').title()
                    with st.expander(move_name):
                        st.write(get_move_description(move['move']['url']))
            else:
                st.write("This Pokémon has no moves.")

            # Evolution Chain
            st.subheader("🌱 Evolution Chain")
            if evolution_names:
                evo_cols = st.columns(len(evolution_names))
                for idx, name in enumerate(evolution_names):
                    sprite = get_sprite_for(name, shiny_toggle)
                    with evo_cols[idx]:
                        if sprite:
                            st.image(sprite, caption=name.title(), use_container_width=True)
                        else:
                            st.text(name.title())
            else:
                st.write("No evolution data available.")

            # All Forms Section - Enhanced from the second code
            if has_alternate_forms:
                st.subheader("🌟 All Available Forms")
                st.markdown("""
                <style>
                .x-factor {
                    padding: 10px;
                    border-radius: 10px;
                    background: linear-gradient(90deg, #ff9a9e 0%, #fad0c4 100%);
                    color: black;
                    margin-bottom: 20px;
                }
                </style>
                <div class="x-factor">
                    This Pokémon has multiple forms! See them all below.
                </div>
                """, unsafe_allow_html=True)
                
                # Display all forms in columns
                form_cols = st.columns(min(4, len(forms)))
                for idx, form in enumerate(forms):
                    with form_cols[idx % len(form_cols)]:
                        form_name_display = form['form_name'].replace('-', ' ').title()
                        sprite = form['sprites']['front_shiny'] if shiny_toggle else form['sprites']['front_default']
                        if sprite:
                            st.image(sprite, caption=form_name_display, use_container_width=True)
                        else:
                            st.text(form_name_display)
                        if form['is_default']:
                            st.markdown("**⭐ Default Form**")
        else:
            st.error("Failed to load species data.")
    else:
        st.error("Pokémon not found.")
else:
    st.info("Enter a Pokémon name to begin (e.g., Pikachu, Charizard, Mewtwo).")