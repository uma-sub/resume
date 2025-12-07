"""
BS/MD Reddit Scanner - Streamlit App
Scans r/premed and r/bsmd for BS/MD program updates, interviews, and results
Modern UI inspired by ShadCN design system
Uma S, 20 NOV 2025
HOW TO RUN
python -m streamlit run reddit_scanner.py
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(
    page_title="BS/MD Reddit Scanner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS inspired by ShadCN design system
st.markdown("""
    <style>
    /* Main background - Clean light grey */
    .stApp {
        background: #f5f5f5;
    }
    
    /* Header styling - Dark blue/grey gradient */
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
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: #e2e8f0;
        font-size: 1.1rem;
        margin-top: 12px;
        font-weight: 400;
    }
    
    /* Button styling - Bold blue */
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
    
    /* Input fields - Clean white with dark borders */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea textarea {
        border-radius: 6px;
        border: 2px solid #cbd5e1;
        padding: 10px;
        background: white;
        color: #1e293b;
        font-size: 15px;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stTextArea textarea:focus {
        border-color: #2563eb;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        background: white;
        padding: 12px;
        border-radius: 6px;
        border: 2px solid #cbd5e1;
    }
    
    .stCheckbox label {
        color: #1e293b;
        font-weight: 500;
    }
    
    /* Slider - Blue */
    .stSlider>div>div>div {
        background: #2563eb;
    }
    
    /* Expander - White cards with dark text */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 6px;
        border: 2px solid #cbd5e1;
        font-weight: 600;
        color: #1e293b;
    }
    
    /* Metrics - Blue numbers */
    [data-testid="stMetricValue"] {
        color: #2563eb;
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #475569;
        font-weight: 600;
    }
    
    /* Post card styling - White cards with strong borders */
    .post-card {
        background: white;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 16px;
        border: 2px solid #cbd5e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
    }
    
    .post-card:hover {
        box-shadow: 0 4px 12px rgba(37,99,235,0.15);
        border-color: #2563eb;
        transform: translateY(-2px);
    }
    
    .post-title {
        color: #0f172a;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    .post-meta {
        display: flex;
        gap: 16px;
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 12px;
        font-weight: 500;
    }
    
    .post-stats {
        display: inline-flex;
        gap: 8px;
        background: #eff6ff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        color: #2563eb;
        border: 1px solid #bfdbfe;
    }
    
    /* Sidebar - Light grey */
    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 2px solid #cbd5e1;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #0f172a;
        font-weight: 700;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background: #d1fae5;
        color: #065f46;
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stWarning {
        background: #fef3c7;
        color: #92400e;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stError {
        background: #fee2e2;
        color: #991b1b;
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stInfo {
        background: #dbeafe;
        color: #1e40af;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #0f172a !important;
    }
    
    /* Regular text */
    p, div, span {
        color: #334155;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Keywords to look for
KEYWORDS = [
    'bs/md', 'bsmd', 'bs md', 'interview', 'acceptance', 'result', 
    'decision', 'admitted', 'rejected', 'waitlist', 'program',
    'combined degree', '7 year', '8 year', 'early assurance'
]

def scan_subreddit(subreddit_name, days=1):
    """Scan a subreddit for relevant posts using Reddit's JSON API"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://www.reddit.com/r/{subreddit_name}/new.json?limit=100"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return [{'error': f'Failed to fetch from r/{subreddit_name}'}]
        
        data = response.json()
        posts = []
        
        time_filter = datetime.now() - timedelta(days=days)
        
        for post_data in data['data']['children']:
            post = post_data['data']
            post_time = datetime.fromtimestamp(post['created_utc'])
            
            if post_time < time_filter:
                continue
            
            # Check if post contains any keywords
            text_to_search = (post['title'] + " " + post.get('selftext', '')).lower()
            if any(keyword in text_to_search for keyword in KEYWORDS):
                posts.append({
                    'title': post['title'],
                    'author': post['author'],
                    'score': post['score'],
                    'url': f"https://reddit.com{post['permalink']}",
                    'created': post_time.strftime('%b %d, %Y at %I:%M %p'),
                    'preview': post.get('selftext', '')[:300] + '...' if len(post.get('selftext', '')) > 300 else post.get('selftext', ''),
                    'subreddit': subreddit_name,
                    'num_comments': post['num_comments']
                })
        
        return posts
    except Exception as e:
        return [{'error': str(e)}]

# Header
st.markdown("""
    <div class="main-header">
        <h1>🎓 BS/MD Reddit Scanner</h1>
        <p>Stay updated on BS/MD programs • Interviews • Decisions • Results</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Scan Settings")
    
    days = st.slider("📅 Days to look back", min_value=1, max_value=7, value=1, 
                     help="How many days of posts to scan")
    
    st.markdown("---")
    st.markdown("### 📍 Select Subreddits")
    
    scan_premed = st.checkbox("r/premed", value=True, help="Primary subreddit for pre-med students")
    scan_bsmd = st.checkbox("r/bsmd", value=True, help="Dedicated BS/MD subreddit")
    
    st.markdown("---")
    st.markdown("### ➕ Additional Subreddits")
    custom_subreddits = st.text_area(
        "Add more (one per line)",
        placeholder="ApplyingToCollege\ncollegeresults",
        height=100
    )
    
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.markdown("""
    - Run daily for updates
    - Check before deadlines
    - Filter by keywords
    - Save important posts
    """)

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 🔍 Ready to scan?")
    st.markdown("Click the button below to fetch the latest BS/MD updates from Reddit")

with col2:
    scan_button = st.button("🚀 Scan Reddit Now", type="primary", use_container_width=True)

if scan_button:
    if not scan_premed and not scan_bsmd and not custom_subreddits:
        st.error("⚠️ Please select at least one subreddit to scan!")
    else:
        all_posts = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        subreddits_to_scan = []
        if scan_premed:
            subreddits_to_scan.append('premed')
        if scan_bsmd:
            subreddits_to_scan.append('bsmd')
        if custom_subreddits:
            subreddits_to_scan.extend([s.strip() for s in custom_subreddits.split('\n') if s.strip()])
        
        total_subs = len(subreddits_to_scan)
        
        for idx, sub in enumerate(subreddits_to_scan):
            status_text.text(f"Scanning r/{sub}...")
            posts = scan_subreddit(sub, days)
            if posts and 'error' not in posts[0]:
                all_posts.extend(posts)
            progress_bar.progress((idx + 1) / total_subs)
            time.sleep(1)
        
        progress_bar.empty()
        status_text.empty()
        
        # Check for errors
        if any('error' in post for post in all_posts if isinstance(post, dict)):
            st.warning("⚠️ Some subreddits could not be accessed. Showing available results.")
        
        if not all_posts:
            st.warning(f"😕 No BS/MD related posts found in the last {days} day(s)")
            st.info("💡 Try increasing the number of days or checking different subreddits!")
        else:
            # Sort by score (popularity)
            all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Display summary
            st.success(f"✅ Found {len(all_posts)} relevant posts!")
            
            st.markdown("---")
            
            # Stats
            st.markdown("### 📊 Overview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📝 Total Posts", len(all_posts))
            with col2:
                total_comments = sum(p.get('num_comments', 0) for p in all_posts)
                st.metric("💬 Comments", total_comments)
            with col3:
                avg_score = sum(p.get('score', 0) for p in all_posts) // len(all_posts) if all_posts else 0
                st.metric("⭐ Avg Score", avg_score)
            with col4:
                unique_authors = len(set(p.get('author', '') for p in all_posts))
                st.metric("👥 Authors", unique_authors)
            
            st.markdown("---")
            
            # Filter options
            with st.expander("🔧 Filter & Sort Options"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    min_score = st.number_input("Minimum score", min_value=0, value=0)
                with col2:
                    min_comments = st.number_input("Minimum comments", min_value=0, value=0)
                with col3:
                    keyword_filter = st.text_input("Keyword search", placeholder="e.g., interview")
                
                sort_option = st.selectbox(
                    "Sort by",
                    ["Score (High to Low)", "Score (Low to High)", "Comments (Most)", "Date (Newest)"]
                )
            
            # Apply filters
            filtered_posts = all_posts
            if min_score > 0:
                filtered_posts = [p for p in filtered_posts if p.get('score', 0) >= min_score]
            if min_comments > 0:
                filtered_posts = [p for p in filtered_posts if p.get('num_comments', 0) >= min_comments]
            if keyword_filter:
                keyword_lower = keyword_filter.lower()
                filtered_posts = [p for p in filtered_posts if keyword_lower in p['title'].lower() or keyword_lower in p.get('preview', '').lower()]
            
            # Apply sorting
            if sort_option == "Score (Low to High)":
                filtered_posts.sort(key=lambda x: x.get('score', 0))
            elif sort_option == "Comments (Most)":
                filtered_posts.sort(key=lambda x: x.get('num_comments', 0), reverse=True)
            elif sort_option == "Date (Newest)":
                filtered_posts.sort(key=lambda x: x.get('created', ''), reverse=True)
            
            if not filtered_posts:
                st.warning("😔 No posts match your filters. Try adjusting them.")
            else:
                st.markdown(f"### 📋 Results ({len(filtered_posts)} posts)")
                
                # Display posts
                for idx, post in enumerate(filtered_posts, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="post-card">
                            <div class="post-title">{idx}. {post['title']}</div>
                            <div class="post-meta">
                                <span>📍 r/{post['subreddit']}</span>
                                <span>👤 u/{post['author']}</span>
                                <span>🕐 {post['created']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(f"<span class='post-stats'>⬆️ {post['score']} upvotes</span>", unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"<span class='post-stats'>💬 {post['num_comments']} comments</span>", unsafe_allow_html=True)
                        with col3:
                            st.link_button("Read Post", post['url'], use_container_width=True)
                        
                        if post['preview']:
                            with st.expander("📄 Preview"):
                                st.markdown(post['preview'])
                        
                        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Pro Tip:</strong> Run this scanner daily to stay ahead of BS/MD program updates!</p>
    <p style='font-size: 0.9rem;'>Made with ❤️ for BS/MD applicants</p>
</div>
""", unsafe_allow_html=True)
