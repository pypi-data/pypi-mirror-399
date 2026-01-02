"""
Optimized CSS utilities for UI performance.
Caches CSS to avoid re-injecting on every render.
"""
import streamlit as st

@st.cache_data(show_spinner=False)
def get_tab_styles():
    """
    Get optimized tab styles - cached to avoid re-injection.
    Uses faster transitions and reduced complexity for better performance.
    """
    return """
        <style>
            /* Tab styling - optimized for performance */
            .stTabs [data-baseweb="tab-list"] {
                gap: 6px;
                background: #f8fafc;
                padding: 4px 4px;
                border-radius: 16px;
                margin-bottom: 18px;
                min-height: 22px;
                will-change: contents; /* Optimize for animations */
            }
            /* Tab item styling - reduced transition complexity */
            .stTabs [data-baseweb="tab"] {
                height: 30px;
                min-height: 30px;
                min-width: 46px;
                white-space: pre-wrap;
                background: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
                color: #475569;
                font-weight: 600;
                font-size: var(--pt-font-sm);
                padding: 0 12px;
                transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
                line-height: 1.33;
                will-change: background, border-color, color; /* Optimize for animations */
            }
            /* Tab item hover styling - simplified */
            .stTabs [data-baseweb="tab"]:hover {
                background: #f1f5f9;
                border-color: #dbe3ef;
                color: #1e293b;
            }
            /* Selected tab item styling - optimized */
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border-color: #667eea !important;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.28) !important;
                font-size: var(--pt-font-md) !important;
            }
            /* Tab highlight styling */
            .stTabs [data-baseweb="tab-highlight"] {
                background-color: transparent !important;
            }
        </style>
    """


def inject_tab_styles_once():
    """
    Inject tab styles only once per session to avoid re-rendering.
    Uses session state to track if styles have been injected.
    """
    cache_key = "tab_styles_injected"
    if not st.session_state.get(cache_key, False):
        st.markdown(get_tab_styles(), unsafe_allow_html=True)
        st.session_state[cache_key] = True

