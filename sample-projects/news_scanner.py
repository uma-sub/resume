"""
Daily News Scanner - Streamlit App
Scans and displays the latest news from multiple sources
@Uma S, 15-NOV-2025
HOW TO RUN THIS
python -m streamlit run news_scanner.py
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(
    page_title="Daily News Scanner",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: #f5f5f5;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 32px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: #e2e8f0;
        font-size: 1.1rem;
        margin-top: 12px;
    }
    
    /* Button styling */
    .stButton>button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(37,99,235,0.3);
        width: 100%;
    }
    
    .stButton>button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(37,99,235,0.4);
    }
    
    /* News card styling */
    .news-card {
        background: white;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 20px;
        border: 2px solid #cbd5e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
    }
    
    .news-card:hover {
        box-shadow: 0 4px 12px rgba(37,99,235,0.15);
        border-color: #2563eb;
        transform: translateY(-2px);
    }
    
    .news-title {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    .news-source {
        display: inline-block;
        background: #eff6ff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        color: #2563eb;
        border: 1px solid #bfdbfe;
        margin-right: 10px;
    }
    
    .news-time {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #2563eb;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 2px solid #cbd5e1;
    }
    
    [data-testid="stSidebar"] * {
        color: #0f172a !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 700;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 2px solid #cbd5e1;
        padding: 10px;
        background: white;
        color: #1e293b !important;
    }
    
    .stSelectbox>div>div>select {
        border-radius: 6px;
        border: 2px solid #cbd5e1;
        background: white;
        color: #1e293b !important;
    }
    
    /* Make all text dark and readable */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #0f172a !important;
    }
    
    /* Checkbox labels */
    .stCheckbox label {
        color: #0f172a !important;
        font-weight: 500;
    }
    
    /* Slider labels and text */
    .stSlider label, .stSlider div {
        color: #0f172a !important;
    }
    
    /* Expander text */
    .streamlit-expanderHeader p {
        color: #0f172a !important;
    }
    
    /* All paragraph text */
    p, div, span, label {
        color: #0f172a !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# News sources using RSS-to-JSON API
NEWS_SOURCES = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "Hacker News": "https://news.ycombinator.com/rss",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "http://rss.cnn.com/rss/cnn_topstories.rss",
    "Reuters": "https://www.reutersagency.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
}

def fetch_news_from_rss(rss_url, source_name, max_articles=10):
    """Fetch news from RSS feed using rss2json API"""
    try:
        # Using rss2json.com API to parse RSS feeds
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={rss_url}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        if data.get('status') != 'ok':
            return []
        
        articles = []
        items = data.get('items', [])[:max_articles]
        
        for item in items:
            pub_date = item.get('pubDate', '')
            
            # Parse the date
            try:
                if pub_date:
                    # Try parsing different date formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z']:
                        try:
                            parsed_date = datetime.strptime(pub_date.split('+')[0].strip(), fmt)
                            time_str = parsed_date.strftime('%b %d, %Y at %I:%M %p')
                            break
                        except:
                            continue
                    else:
                        time_str = pub_date
                else:
                    time_str = "Recently"
            except:
                time_str = "Recently"
            
            articles.append({
                'title': item.get('title', 'No Title'),
                'link': item.get('link', '#'),
                'description': item.get('description', '')[:300] + '...' if len(item.get('description', '')) > 300 else item.get('description', ''),
                'source': source_name,
                'time': time_str
            })
        
        return articles
    except Exception as e:
        st.error(f"Error fetching from {source_name}: {str(e)}")
        return []

# Header
st.markdown("""
    <div class="main-header">
        <h1>📰 Daily News Scanner</h1>
        <p>Get the latest news from multiple sources in one place</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Source selection
    st.markdown("### 📍 Select News Sources")
    selected_sources = []
    
    for source in NEWS_SOURCES.keys():
        if st.checkbox(source, value=True):
            selected_sources.append(source)
    
    st.markdown("---")
    
    # Articles per source
    articles_per_source = st.slider(
        "Articles per source",
        min_value=5,
        max_value=20,
        value=10,
        help="Number of articles to fetch from each source"
    )
    
    st.markdown("---")
    
    # Filter by keyword
    st.markdown("### 🔍 Filter News")
    keyword_filter = st.text_input(
        "Search keyword (optional)",
        placeholder="e.g., AI, politics, sports"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Select sources you're interested in
    - Use keyword filter to focus on specific topics
    - Click article titles to read more
    - Refresh regularly for updates
    """)

# Main content
current_date = datetime.now().strftime("%A, %B %d, %Y")
st.markdown(f"### 📅 Today: {current_date}")

# Scan button
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("#### Click below to fetch the latest news")
with col2:
    scan_button = st.button("🔄 Scan News Now", type="primary", use_container_width=True)

if scan_button:
    if not selected_sources:
        st.error("⚠️ Please select at least one news source!")
    else:
        all_articles = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_sources = len(selected_sources)
        
        for idx, source in enumerate(selected_sources):
            status_text.text(f"Fetching from {source}...")
            rss_url = NEWS_SOURCES[source]
            articles = fetch_news_from_rss(rss_url, source, articles_per_source)
            all_articles.extend(articles)
            progress_bar.progress((idx + 1) / total_sources)
            time.sleep(0.5)  # Be nice to the API
        
        progress_bar.empty()
        status_text.empty()
        
        # Apply keyword filter
        if keyword_filter:
            keyword_lower = keyword_filter.lower()
            filtered_articles = [
                article for article in all_articles
                if keyword_lower in article['title'].lower() or 
                   keyword_lower in article['description'].lower()
            ]
        else:
            filtered_articles = all_articles
        
        if not filtered_articles:
            st.warning("😕 No articles found matching your criteria")
            st.info("💡 Try adjusting your filters or selecting more sources!")
        else:
            st.success(f"✅ Found {len(filtered_articles)} articles!")
            
            st.markdown("---")
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📰 Total Articles", len(filtered_articles))
            with col2:
                st.metric("📍 Sources", len(set(a['source'] for a in filtered_articles)))
            with col3:
                st.metric("🔄 Last Updated", datetime.now().strftime("%I:%M %p"))
            
            st.markdown("---")
            st.markdown("### 📋 Latest News")
            
            # Display articles
            for idx, article in enumerate(filtered_articles, 1):
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{idx}. {article['title']}</div>
                    <div style="margin-bottom: 12px;">
                        <span class="news-source">📍 {article['source']}</span>
                        <span class="news-time">🕐 {article['time']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if article['description']:
                    with st.expander("📄 Preview"):
                        st.markdown(article['description'])
                
                st.link_button("📖 Read Full Article", article['link'], use_container_width=False)
                st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Pro Tip:</strong> Run this scanner multiple times a day to stay updated!</p>
    <p style='font-size: 0.9rem;'>News aggregated from trusted sources • Updated in real-time</p>
</div>
""", unsafe_allow_html=True)
