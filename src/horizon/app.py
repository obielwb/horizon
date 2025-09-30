#!/usr/bin/env python
import sys
import os
from typing import Dict, List
from dotenv import load_dotenv
load_dotenv() 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horizon.config import Config
from horizon.crew import Horizon
import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime



# Page configuration
st.set_page_config(
    page_title="NVIDIA Horizon - Startup Discovery",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #76b900;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .startup-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #76b900;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'discovery_running' not in st.session_state:
    st.session_state.discovery_running = False
if 'discovery_results' not in st.session_state:
    st.session_state.discovery_results = None

def load_startup_database():
    """Load all discovered startups from the main database and supplement with output files"""
    main_db_path = Path("outputs/startup_database.json")
    
    # Load from main database first
    if main_db_path.exists():
        try:
            with open(main_db_path, 'r', encoding='utf-8') as f:
                main_startups = json.load(f)
        except Exception as e:
            print(f"Error loading main database: {e}")
            main_startups = []
    else:
        main_startups = []
    
    # Also load from individual country discovery files for backward compatibility
    outputs_dir = Path("outputs")
    additional_startups = []
    
    if outputs_dir.exists():
        for json_file in outputs_dir.glob("nvidia_inception_*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    additional_startups.extend(_extract_startups_from_discovery_file(data))
            except Exception as e:
                print(f"Warning: Error loading {json_file.name}: {e}")
    
    # Combine and deduplicate
    all_startups = main_startups + additional_startups
    if not all_startups:
        return pd.DataFrame()
    
    # Deduplicate based on name
    seen_names = set()
    unique_startups = []
    for startup in all_startups:
        name = startup.get('name', '').lower().strip()
        if name and name not in seen_names:
            seen_names.add(name)
            unique_startups.append(startup)
    
    df = pd.DataFrame(unique_startups)
    
    # Standardize column names
    column_mapping = {
        'Company Name': 'name',
        'company_name': 'name',
        'Name': 'name',
        'Website': 'website',
        'website_url': 'website',
        'URL': 'website',
        'Description': 'description',
        'Location': 'location',
        'country': 'location',  # Map country to location for consistency
        'Country': 'location',
        'AI Technology Focus': 'technology',
        'industry': 'technology',
        'Industry': 'technology',
        'Target Market': 'market',
        'market': 'market',
        'Key Milestones': 'milestones',
        'milestones': 'milestones',
        'Founding Year': 'founded',
        'founded': 'founded'
    }
    
    # Apply column mapping
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    return df

def _extract_startups_from_discovery_file(self, data: Dict) -> List[Dict]:
    """Extract startups from discovery result files"""
    startups = []
    
    if 'task_results' in data:
        for task_name, task_result in data['task_results'].items():
            if isinstance(task_result, str):
                try:
                    # Try to parse JSON arrays of startups
                    if task_result.strip().startswith('['):
                        parsed = json.loads(task_result)
                        if isinstance(parsed, list):
                            for item in parsed:
                                if isinstance(item, dict) and item.get('name') or item.get('Company Name'):
                                    startups.append(item)
                except json.JSONDecodeError:
                    # If it's not JSON, skip this task result
                    pass
    
    return startups

def display_startup_card(startup):
    """Display a single startup as a card"""
    with st.container():
        st.markdown('<div class="startup-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {startup.get('name', 'Unknown Company')}")
            if 'description' in startup and startup['description']:
                st.write(startup['description'])
            
            # Display key info
            info_cols = st.columns(4)
            if 'location' in startup and startup['location']:
                info_cols[0].metric("Location", startup['location'])
            if 'technology' in startup and startup['technology']:
                info_cols[1].metric("Technology", startup['technology'])
            if 'market' in startup and startup['market']:
                info_cols[2].metric("Market", startup['market'])
            if 'founded' in startup and startup['founded']:
                info_cols[3].metric("Founded", startup['founded'])
        
        with col2:
            if 'website' in startup and startup['website']:
                st.link_button("Visit Website", startup['website'], use_container_width=True)
        
        # Additional details in expander
        if 'milestones' in startup and startup['milestones']:
            with st.expander("Key Milestones & Investors"):
                st.write(startup['milestones'])
        
        st.markdown('</div>', unsafe_allow_html=True)

def run_discovery(countries, ventures):
    """Run the startup discovery process"""
    st.session_state.discovery_running = True
    
    try:
        with st.spinner(f"🔍 Discovering AI startups in {', '.join(countries)}..."):
            discovery_system = Horizon()
            
            print("Starting discovery with the following parameters:")
            if len(countries) == 1:
                print("Single country mode")
                results = discovery_system.discover_country(
                    countries[0],
                    specific_ventures=ventures if ventures else None
                )
            else:
                specific_ventures_per_country = None
                if ventures:
                    specific_ventures_per_country = {
                        country: ventures for country in countries
                    }
                
                results = discovery_system.discover_multiple_countries(
                    countries,
                    specific_ventures_per_country=specific_ventures_per_country
                )
            
            st.session_state.discovery_results = results
            st.success("✅ Discovery completed successfully!")
            return results
            
    except Exception as e:
        st.error(f"❌ Error during discovery: {str(e)}")
        return None
    finally:
        st.session_state.discovery_running = False

# Main app
def main():
    # Header
    st.markdown('<p class="main-header">🚀 NVIDIA Horizon</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI Startup Discovery System</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.nvidia.com/content/dam/en-zz/Solutions/about-nvidia/logo-and-brand/01-nvidia-logo-vert-500x200-2c50-d@2x.png", width=200)
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "🔍 Run Discovery", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This system discovers and analyzes AI startups across Latin America 
        for the NVIDIA Inception program.
        """)
    
    # Main content based on selected page
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🔍 Run Discovery":
        show_discovery_page()
    else:
        show_settings()

def show_dashboard():
    """Display the dashboard with startup database"""
    st.header("Startup Database")
    
    # Load data
    df = load_startup_database()
    
    if df.empty:
        st.info("No startups in database yet. Run a discovery to populate the database.")
        return
    
    # Metrics - FIXED: Properly handle pandas operations and ensure we get actual numbers
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Startups", len(df))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        # FIX: Extract the actual number value safely
        country_count = 0
        if 'location' in df.columns:
            try:
                # Ensure we're getting a scalar value, not a Series
                country_count = int(df['location'].nunique())
            except (TypeError, ValueError):
                # If nunique() returns a Series, try to extract the value
                country_count = 0
        st.metric("Countries", country_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        # FIX: Extract the actual number value safely
        tech_count = 0
        if 'technology' in df.columns:
            try:
                tech_count = int(df['technology'].nunique())
            except (TypeError, ValueError):
                tech_count = 0
        st.metric("Technologies", tech_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Last Updated", datetime.now().strftime("%Y-%m-%d"))
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        countries = ['All']
        if 'location' in df.columns:
            # FIX: Handle empty or non-string data safely
            location_series = df['location'].dropna()
            if not location_series.empty:
                try:
                    # Convert to string and get unique values
                    unique_locations = location_series.astype(str).unique()
                    countries += sorted(unique_locations.tolist())
                except Exception as e:
                    st.error(f"Error processing locations: {e}")
        selected_country = st.selectbox("Filter by Country", countries)
    
    with col2:
        technologies = ['All']
        if 'technology' in df.columns:
            # FIX: Handle empty or non-string data safely
            tech_series = df['technology'].dropna()
            if not tech_series.empty:
                try:
                    unique_techs = tech_series.astype(str).unique()
                    technologies += sorted(unique_techs.tolist())
                except Exception as e:
                    st.error(f"Error processing technologies: {e}")
        selected_tech = st.selectbox("Filter by Technology", technologies)
    
    with col3:
        search_term = st.text_input("Search by Name", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_country != 'All' and 'location' in filtered_df.columns:
        try:
            filtered_df = filtered_df[filtered_df['location'].astype(str) == selected_country]
        except Exception as e:
            st.error(f"Error filtering by country: {e}")
    
    if selected_tech != 'All' and 'technology' in filtered_df.columns:
        try:
            filtered_df = filtered_df[filtered_df['technology'].astype(str) == selected_tech]
        except Exception as e:
            st.error(f"Error filtering by technology: {e}")
    
    if search_term and 'name' in filtered_df.columns:
        try:
            filtered_df = filtered_df[filtered_df['name'].astype(str).str.contains(search_term, case=False, na=False)]
        except Exception as e:
            st.error(f"Error searching by name: {e}")
    
    st.markdown(f"### Showing {len(filtered_df)} startups")
    
    # Display options
    view_mode = st.radio("View Mode", ["Cards", "Table"], horizontal=True)
    
    if view_mode == "Cards":
        for _, startup in filtered_df.iterrows():
            try:
                display_startup_card(startup.to_dict())
            except Exception as e:
                st.error(f"Error displaying startup card: {e}")
    else:
        # Display as table
        display_columns = ['name', 'location', 'technology', 'market', 'website']
        display_columns = [col for col in display_columns if col in filtered_df.columns]
        try:
            st.dataframe(filtered_df[display_columns], use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying table: {e}")
    
    # Export option
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📥 Export to CSV"):
            try:
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"startups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error exporting CSV: {e}")

def show_discovery_page():
    """Display the discovery configuration and execution page"""
    st.header("Run Startup Discovery")
    
    # Discovery configuration
    st.subheader("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Target Countries")
        countries = st.multiselect(
            "Select countries to search",
            Config.TARGET_COUNTRIES,
            default=["Brazil"]
        )
    
    with col2:
        st.markdown("#### Venture Capitals (Optional)")
        st.markdown("*Leave empty to use default VCs*")
        
        venture_input = st.text_area(
            "Enter venture names (one per line)",
            placeholder="Kaszek Ventures\nMonashees\nMAYA Capital",
            height=100
        )
        
        ventures = [v.strip() for v in venture_input.split('\n') if v.strip()] if venture_input else None
    
    # Display configuration summary
    with st.expander("📋 Configuration Summary"):
        st.markdown(f"**Countries:** {', '.join(countries) if countries else 'None selected'}")
        st.markdown(f"**Venture Capitals:** {', '.join(ventures) if ventures else 'Default VCs will be used'}")
        st.markdown(f"**AI Technologies:** {', '.join(Config.AI_TECHNOLOGIES[:5])}...")
        st.markdown(f"**Market Sectors:** {', '.join(Config.MARKET_SECTORS[:5])}...")
    
    st.markdown("---")
    
    # Run button
    if not countries:
        st.warning("⚠️ Please select at least one country")
    else:
        if st.button("🚀 Start Discovery", type="primary", disabled=st.session_state.discovery_running):
            results = run_discovery(countries, ventures)
            
            if results:
                st.balloons()
                st.success("Discovery completed! Check the Dashboard to see results.")
                
                # Show summary
                with st.expander("📊 Discovery Summary", expanded=True):
                    if isinstance(results, dict):
                        st.json(results)
    
    # Show status if running
    if st.session_state.discovery_running:
        st.info("🔄 Discovery in progress... This may take several minutes.")
        st.progress(0.5)

def show_settings():
    """Display settings and configuration"""
    st.header("Settings")
    
    st.subheader("API Configuration")
    
    # Check API keys
    has_openai = Config.OPENAI_API_KEY != "your-openai-api-key"
    has_resend = Config.RESEND_API_KEY != "your-resend-api-key"
    
    col1, col2 = st.columns(2)
    
    with col1:
        if has_openai:
            st.success("✅ OpenAI API Key: Configured")
        else:
            st.error("❌ OpenAI API Key: Not configured")
            st.info("Set OPENAI_API_KEY environment variable")
    
    with col2:
        if has_resend:
            st.success("✅ Resend API Key: Configured")
        else:
            st.warning("⚠️ Resend API Key: Not configured (optional)")
            st.info("Set RESEND_API_KEY environment variable for email reports")
    
    st.markdown("---")
    
    st.subheader("Default Configuration")
    
    with st.expander("Target Countries"):
        st.write(Config.TARGET_COUNTRIES)
    
    with st.expander("AI Technologies"):
        st.write(Config.AI_TECHNOLOGIES)
    
    with st.expander("Market Sectors"):
        st.write(Config.MARKET_SECTORS)
    
    with st.expander("Latin America VCs"):
        st.write(Config.LATAM_VCS)
    
    st.markdown("---")
    
    st.subheader("Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Database"):
            if st.checkbox("I understand this will delete all startup data"):
                outputs_dir = Path("outputs")
                if outputs_dir.exists():
                    for file in outputs_dir.glob("*.json"):
                        file.unlink()
                    st.success("Database cleared successfully!")
                    st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Database"):
            st.rerun()

if __name__ == "__main__":
    main()