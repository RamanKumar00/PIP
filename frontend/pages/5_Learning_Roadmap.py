import streamlit as st
import json
from utils.styles import inject_custom_css, hero_banner
from utils.tech_mapping import get_resolution_map, get_autocomplete_suggestions, DEFAULT_SEARCH_URL_TEMPLATE

# Page Configuration
st.set_page_config(
    page_title="Learning Platform - PlaceMentor AI",
    page_icon="🎯",
    layout="wide",
)

# Apply Custom Design System
inject_custom_css()

# Inject meta viewport tag for mobile browser responsiveness
st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">', unsafe_allow_html=True)

# Auth guard check
if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("Please log in first from the Command Center Home Page.")
    st.stop()

# Header Bar
st.markdown(
    """
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">PORTAL / LEARNING HUB</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">PlaceMentor Learning Hub</h2>
        </div>
        <span class="badge badge-indigo">Direct Redirect System</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hero Banner
hero_banner(
    title="Master Core Technical Skills Instantly",
    subtitle="Search any programming language, framework, database, or development tool. You will be immediately redirected to the best tutorial resources in a new browser tab.",
    eyebrow="GLOBAL LEARNING PORTAL"
)

# Centralized technology mapping variables
resolution_map = get_resolution_map()
suggestions = get_autocomplete_suggestions()

# Custom component HTML structure with embedded JS logic for lookup, normalization, and redirect
# Using template placeholders to avoid python f-string escaping conflicts
html_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  
  body {
    background-color: transparent;
    color: #FAFAFA;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    margin: 0;
    padding: 0;
    overflow: visible;
  }
  .search-container {
    position: relative;
    width: 100%;
    max-width: 650px;
    margin: 10px auto;
  }
  .search-input-wrapper {
    display: flex;
    align-items: center;
    background: #09090B;
    border: 1px solid #27272A;
    border-radius: 10px;
    padding: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
  .search-input-wrapper:focus-within {
    border-color: #FAFAFA;
    box-shadow: 0 0 0 2px rgba(250, 250, 250, 0.1), 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  .search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #FAFAFA;
    font-size: 15px;
    padding: 12px 16px;
    width: 100%;
  }
  .search-input::placeholder {
    color: #71717A;
  }
  .search-button {
    background: #FAFAFA;
    color: #000000;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    padding: 12px 24px;
    cursor: pointer;
    transition: background-color 0.15s ease;
    white-space: nowrap;
  }
  .search-button:hover {
    background: #E4E4E7;
  }
  .suggestions-list {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    right: 0;
    background: #09090B;
    border: 1px solid #27272A;
    border-radius: 8px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 1000;
    display: none;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
  }
  .suggestion-item {
    padding: 12px 18px;
    cursor: pointer;
    font-size: 14px;
    color: #E2E8F0;
    transition: background-color 0.15s ease, color 0.15s ease;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .suggestion-item:hover, .suggestion-item.active {
    background: #18181B;
    color: #FAFAFA;
  }
  .suggestion-item .alias-tag {
    font-size: 11px;
    color: #71717A;
    background: #18181B;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #27272A;
  }
  /* Custom scrollbar */
  .suggestions-list::-webkit-scrollbar {
    width: 6px;
  }
  .suggestions-list::-webkit-scrollbar-track {
    background: transparent;
  }
  .suggestions-list::-webkit-scrollbar-thumb {
    background: #27272A;
    border-radius: 3px;
  }
</style>
</head>
<body>
<div class="search-container">
    <div class="search-input-wrapper">
        <input type="text" id="search-input" class="search-input" placeholder="Search Python, React, Docker, Machine Learning..." autocomplete="off" />
        <button id="search-btn" class="search-button">Search</button>
    </div>
    <div id="suggestions-list" class="suggestions-list"></div>
</div>

<script>
  // Injected variables replaced by python code
  const mapping = __MAPPING__;
  const suggestions = __SUGGESTIONS__;
  const defaultSearchTemplate = __SEARCH_TEMPLATE__;

  const searchInput = document.getElementById('search-input');
  const suggestionsList = document.getElementById('suggestions-list');
  const searchBtn = document.getElementById('search-btn');

  let activeIndex = -1;
  let currentFiltered = [];

  function showSuggestions(val) {
    suggestionsList.innerHTML = '';
    if (!val || val.trim() === '') {
      suggestionsList.style.display = 'none';
      return;
    }
    
    const query = val.toLowerCase().trim();
    
    // Filter display names containing the query
    const matchSet = new Set();
    suggestions.forEach(item => {
      if (item.toLowerCase().includes(query)) {
        matchSet.add(item);
      }
    });
    
    // Check aliases and match primary display name
    for (const [key, value] of Object.entries(mapping)) {
      if (key.includes(query)) {
        // Find Display Name matching this URL in suggestions
        suggestions.forEach(sug => {
          if (mapping[sug.toLowerCase()] === value) {
            matchSet.add(sug);
          }
        });
      }
    }
    
    currentFiltered = Array.from(matchSet);

    if (currentFiltered.length === 0) {
      const div = document.createElement('div');
      div.className = 'suggestion-item';
      div.innerHTML = `<span>Search GeeksforGeeks for "<b>${escapeHtml(val)}</b>"</span><span class="alias-tag">Search</span>`;
      div.addEventListener('click', () => {
        performSearch(val);
      });
      suggestionsList.appendChild(div);
    } else {
      currentFiltered.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.innerHTML = `<span>${item}</span><span class="alias-tag">Tutorial</span>`;
        div.addEventListener('click', () => {
          performSearch(item);
        });
        suggestionsList.appendChild(div);
      });
    }
    
    suggestionsList.style.display = 'block';
    activeIndex = -1;
  }

  function performSearch(query) {
    if (!query || query.trim() === '') return;
    
    // Normalize user input (trim spaces, ignore case, resolve aliases)
    const normalized = query.toLowerCase().trim();
    let targetUrl = mapping[normalized];
    
    if (!targetUrl) {
      // Fallback search URL
      targetUrl = defaultSearchTemplate.replace('{query}', encodeURIComponent(query));
    }
    
    window.open(targetUrl, '_blank');
    searchInput.value = '';
    suggestionsList.style.display = 'none';
  }

  // Event Listeners
  searchInput.addEventListener('input', (e) => {
    showSuggestions(e.target.value);
  });

  searchInput.addEventListener('focus', (e) => {
    showSuggestions(e.target.value);
  });

  searchInput.addEventListener('keydown', (e) => {
    const items = suggestionsList.getElementsByClassName('suggestion-item');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = (activeIndex + 1) % items.length;
      updateActive(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = (activeIndex - 1 + items.length) % items.length;
      updateActive(items);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex > -1 && items[activeIndex]) {
        items[activeIndex].click();
      } else {
        performSearch(searchInput.value);
      }
    } else if (e.key === 'Escape') {
      suggestionsList.style.display = 'none';
    }
  });

  function updateActive(items) {
    for (let i = 0; i < items.length; i++) {
      items[i].classList.remove('active');
    }
    if (activeIndex > -1 && items[activeIndex]) {
      items[activeIndex].classList.add('active');
      items[activeIndex].scrollIntoView({ block: 'nearest' });
    }
  }

  document.addEventListener('click', (e) => {
    if (e.target !== searchInput && !suggestionsList.contains(e.target)) {
      suggestionsList.style.display = 'none';
    }
  });

  searchBtn.addEventListener('click', () => {
    performSearch(searchInput.value);
  });

  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
  }
</script>
</body>
</html>
"""

# Replace placeholders with JSON representation
search_component_html = html_template.replace(
    "__MAPPING__", json.dumps(resolution_map)
).replace(
    "__SUGGESTIONS__", json.dumps(suggestions)
).replace(
    "__SEARCH_TEMPLATE__", json.dumps(DEFAULT_SEARCH_URL_TEMPLATE)
)

# Render custom HTML component with standard height to prevent dropdown clipping
st.components.v1.html(search_component_html, height=270)

# Popular Technologies Section
st.write("")
st.markdown("### 🌟 Popular Technologies & Tutorials")
st.markdown("Click on any of the cards below to immediately open the tutorial in a new tab.")

# Custom CSS for modern interactive hover cards
st.markdown(
    """
    <style>
    .popular-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 16px;
        margin-top: 10px;
    }
    .popular-card {
        background: #09090B !important;
        border: 1px solid #27272A !important;
        border-radius: 12px !important;
        padding: 22px 18px !important;
        text-align: left !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        text-decoration: none !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        min-height: 140px !important;
    }
    .popular-card:hover {
        border-color: #FAFAFA !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(255, 255, 255, 0.04) !important;
    }
    .popular-card-icon {
        font-size: 1.8rem !important;
        margin-bottom: 12px !important;
    }
    .popular-card-title {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #FAFAFA !important;
        margin: 0 0 6px 0 !important;
    }
    .popular-card-desc {
        font-size: 0.82rem !important;
        color: #A1A1AA !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Grid definitions
popular_techs = [
    {
        "name": "Python",
        "icon": "🐍",
        "desc": "Core language concepts, basic syntax, and programming structures.",
        "url": resolution_map["python"]
    },
    {
        "name": "Java",
        "icon": "☕",
        "desc": "Object-oriented paradigm, concurrency, collections framework.",
        "url": resolution_map["java"]
    },
    {
        "name": "C++",
        "icon": "💻",
        "desc": "High performance programming, STL, memory allocation concepts.",
        "url": resolution_map["c++"]
    },
    {
        "name": "JavaScript",
        "icon": "⚡",
        "desc": "Web page interactivity, DOM manipulation, asynchronous patterns.",
        "url": resolution_map["javascript"]
    },
    {
        "name": "React",
        "icon": "⚛️",
        "desc": "Declarative component UI, state orchestration, React Hooks.",
        "url": resolution_map["react"]
    },
    {
        "name": "FastAPI",
        "icon": "🚀",
        "desc": "High performance APIs build out, Pydantic type models.",
        "url": resolution_map["fastapi"]
    },
    {
        "name": "Docker",
        "icon": "🐳",
        "desc": "Container deployments orchestration, multi-stage builds caching.",
        "url": resolution_map["docker"]
    },
    {
        "name": "PostgreSQL",
        "icon": "🐘",
        "desc": "Robust relational queries, triggers execution, index layout design.",
        "url": resolution_map["postgresql"]
    },
    {
        "name": "Machine Learning",
        "icon": "🤖",
        "desc": "Scikit-Learn regression, data fitting models, evaluation indexes.",
        "url": resolution_map["machine learning"]
    },
    {
        "name": "Data Structures & Algorithms",
        "icon": "📊",
        "desc": "Linked lists, search execution trees, graph processing structures.",
        "url": resolution_map.get("data structures & algorithms", "https://www.geeksforgeeks.org/data-structures/")
    },
    {
        "name": "System Design",
        "icon": "🏗️",
        "desc": "Caching architectures design, load balancers scaling configurations.",
        "url": resolution_map.get("system design", "https://www.geeksforgeeks.org/system-design-tutorial/")
    }
]

# Generate and render HTML grid for popular technologies
grid_html = '<div class="popular-grid">'
for tech in popular_techs:
    grid_html += f"""
    <a href="{tech['url']}" target="_blank" class="popular-card">
        <div>
            <div class="popular-card-icon">{tech['icon']}</div>
            <h4 class="popular-card-title">{tech['name']}</h4>
        </div>
        <p class="popular-card-desc">{tech['desc']}</p>
    </a>
    """
grid_html += '</div>'

st.markdown(grid_html, unsafe_allow_html=True)
