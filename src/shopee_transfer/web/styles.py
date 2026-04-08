"""
Shopee UI/UX Styling Module
Provides Shopee-branded colors, CSS injection, and component wrapper functions.
"""

import streamlit as st

# Shopee Brand Color Palette
SHOPEE_COLORS = {
    # Primary Colors
    "primary_orange": "#EE4D2D",
    "orange_hover": "#D4431F",
    "orange_active": "#C03A1A",
    "orange_light": "#FFF0ED",
    "orange_medium": "#FDDDD7",

    # Secondary Colors
    "navy": "#172B4D",
    "blue": "#0080C6",
    "yellow": "#FCCD34",
    "green": "#2DC258",
    "red": "#F05025",

    # Neutral Colors
    "text_primary": "#1A1A1A",
    "text_secondary": "#555555",
    "text_muted": "#999999",
    "surface_light": "#F7F7F7",
    "surface_lighter": "#F0F0F0",
    "border": "#E8E8E8",
    "white": "#FFFFFF",
}

# Shopee Seller Center URLs per market
SELLER_CENTER_URLS: dict[str, tuple[str, str]] = {
    "my": ("Malaysia",    "https://seller.shopee.com.my/"),
    "sg": ("Singapore",   "https://seller.shopee.sg/"),
    "id": ("Indonesia",   "https://seller.shopee.co.id/"),
    "vn": ("Vietnam",     "https://banhang.shopee.vn/"),
    "ph": ("Philippines", "https://seller.shopee.ph/"),
    "th": ("Thailand",    "https://seller.shopee.co.th/"),
}

# Custom CSS Styles for Shopee Branding
CSS_CUSTOM_STYLES = f"""
<style>
/* ============ GLOBAL STYLES ============ */
:root {{
    --shopee-primary: {SHOPEE_COLORS['primary_orange']};
    --shopee-navy: {SHOPEE_COLORS['navy']};
    --shopee-blue: {SHOPEE_COLORS['blue']};
    --shopee-green: {SHOPEE_COLORS['green']};
    --shopee-yellow: {SHOPEE_COLORS['yellow']};
    --shopee-red: {SHOPEE_COLORS['red']};
    --shopee-text-primary: {SHOPEE_COLORS['text_primary']};
    --shopee-text-secondary: {SHOPEE_COLORS['text_secondary']};
    --shopee-surface: {SHOPEE_COLORS['surface_light']};
    --shopee-border: {SHOPEE_COLORS['border']};
}}

/* Main container padding */
.main {{
    padding: 1rem 2rem;
}}

/* ============ TYPOGRAPHY ============ */
h1 {{
    color: {SHOPEE_COLORS['navy']};
    font-weight: 700;
    font-size: 2rem;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}}

h2 {{
    color: {SHOPEE_COLORS['navy']};
    font-weight: 700;
    font-size: 1.375rem;
    margin-top: 0.25rem;
    margin-bottom: 0.75rem;
    padding-left: 0.75rem;
    border-left: 3px solid {SHOPEE_COLORS['primary_orange']};
}}

h3 {{
    color: {SHOPEE_COLORS['navy']};
    font-weight: 600;
    font-size: 1.125rem;
}}

p {{
    color: {SHOPEE_COLORS['text_primary']};
    line-height: 1.6;
}}

/* Caption text */
.caption {{
    color: {SHOPEE_COLORS['text_secondary']};
    font-size: 0.875rem;
}}

/* ============ BUTTONS ============ */
.stButton > button {{
    background-color: {SHOPEE_COLORS['primary_orange']};
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    width: 100%;
    cursor: pointer;
}}

.stButton > button:hover {{
    background-color: {SHOPEE_COLORS['orange_hover']};
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(238, 77, 45, 0.2);
}}

.stButton > button:active {{
    background-color: {SHOPEE_COLORS['orange_active']};
    transform: translateY(0);
}}

.stButton > button:disabled {{
    opacity: 0.6;
    cursor: not-allowed;
}}

/* ============ INPUT FIELDS ============ */
.stSelectbox [data-baseweb="select"] {{
    border-radius: 4px;
}}

.stSelectbox [data-baseweb="select"] > div {{
    border-color: {SHOPEE_COLORS['border']};
}}

.stSelectbox [data-baseweb="select"]:focus-within > div {{
    border-color: {SHOPEE_COLORS['primary_orange']};
    box-shadow: 0 0 0 2px rgba(238, 77, 45, 0.1);
}}

/* File uploader styling */
.stFileUploader {{
    position: relative;
}}

.stFileUploader section {{
    border: 2px dashed {SHOPEE_COLORS['primary_orange']};
    border-radius: 8px;
    padding: 1.5rem;
    background-color: {SHOPEE_COLORS['orange_light']};
    transition: all 0.2s ease;
}}

.stFileUploader section:hover {{
    background-color: {SHOPEE_COLORS['orange_medium']};
    border-color: {SHOPEE_COLORS['orange_hover']};
}}

/* ============ METRICS ============ */
.stMetric {{
    background: {SHOPEE_COLORS['white']};
    padding: 1.25rem;
    border-radius: 10px;
    border: 1px solid {SHOPEE_COLORS['border']};
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}

.stMetric label {{
    color: {SHOPEE_COLORS['text_secondary']};
    font-weight: 600;
    font-size: 0.8125rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.stMetric [data-testid="stMetricValue"] {{
    color: {SHOPEE_COLORS['navy']};
    font-size: 1.875rem;
    font-weight: 700;
}}

/* ============ DATA FRAMES ============ */
[data-testid="stDataFrame"] {{
    border: 1px solid {SHOPEE_COLORS['border']};
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}

[data-testid="stDataFrame"] thead {{
    background-color: {SHOPEE_COLORS['surface_light']};
    color: {SHOPEE_COLORS['navy']};
    font-weight: 600;
    border-bottom: 2px solid {SHOPEE_COLORS['border']};
}}

[data-testid="stDataFrame"] tbody tr:nth-child(even) {{
    background-color: {SHOPEE_COLORS['surface_light']};
}}

[data-testid="stDataFrame"] tbody tr:hover {{
    background-color: {SHOPEE_COLORS['surface_lighter']};
}}

/* ============ STATUS MESSAGES ============ */
.stAlert {{
    border-radius: 4px;
    border-left: 4px solid;
    padding: 1rem;
}}

.stSuccess {{
    background-color: rgba(45, 194, 88, 0.1);
    border-left-color: {SHOPEE_COLORS['green']};
}}

.stError {{
    background-color: rgba(240, 80, 37, 0.1);
    border-left-color: {SHOPEE_COLORS['red']};
}}

.stWarning {{
    background-color: rgba(252, 205, 52, 0.1);
    border-left-color: {SHOPEE_COLORS['yellow']};
}}

.stInfo {{
    background-color: rgba(0, 128, 198, 0.1);
    border-left-color: {SHOPEE_COLORS['blue']};
}}

/* ============ DIVIDERS ============ */
.stDivider {{
    margin: 2rem 0;
    border-color: {SHOPEE_COLORS['border']};
}}

/* ============ BADGES & PILLS ============ */
.shopee-badge {{
    display: inline-block;
    padding: 0.375rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0.25rem;
}}

.shopee-badge-success {{
    background-color: {SHOPEE_COLORS['green']};
    color: white;
}}

.shopee-badge-pending {{
    background-color: {SHOPEE_COLORS['yellow']};
    color: {SHOPEE_COLORS['text_primary']};
}}

.shopee-badge-error {{
    background-color: {SHOPEE_COLORS['red']};
    color: white;
}}

.shopee-badge-warning {{
    background-color: {SHOPEE_COLORS['primary_orange']};
    color: white;
}}

.shopee-badge-info {{
    background-color: {SHOPEE_COLORS['blue']};
    color: white;
}}

.shopee-badge-default {{
    background-color: {SHOPEE_COLORS['surface_light']};
    color: {SHOPEE_COLORS['text_primary']};
    border: 1px solid {SHOPEE_COLORS['border']};
}}

/* ============ PROGRESS INDICATORS ============ */
.shopee-progress {{
    width: 100%;
    height: 8px;
    background-color: {SHOPEE_COLORS['surface_light']};
    border-radius: 4px;
    overflow: hidden;
    margin: 1rem 0;
}}

.shopee-progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, {SHOPEE_COLORS['primary_orange']}, {SHOPEE_COLORS['orange_hover']});
    border-radius: 4px;
    transition: width 0.3s ease;
}}

.shopee-progress-label {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
}}

.shopee-progress-label-left {{
    color: {SHOPEE_COLORS['navy']};
}}

.shopee-progress-label-right {{
    color: {SHOPEE_COLORS['text_secondary']};
}}

/* ============ STEP INDICATOR ============ */
.shopee-step-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: {SHOPEE_COLORS['orange_light']};
    color: {SHOPEE_COLORS['primary_orange']};
    border: 1px solid {SHOPEE_COLORS['orange_medium']};
    padding: 0.25rem 0.75rem;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    letter-spacing: 0.06em;
}}

.shopee-step-dots {{
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    justify-content: flex-start;
}}

.shopee-step-dot {{
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
    background-color: {SHOPEE_COLORS['surface_light']};
    border: 2px solid {SHOPEE_COLORS['border']};
    transition: all 0.2s ease;
}}

.shopee-step-dot.active {{
    background-color: {SHOPEE_COLORS['primary_orange']};
    border-color: {SHOPEE_COLORS['primary_orange']};
    transform: scale(1.1);
}}

.shopee-step-dot.completed {{
    background-color: {SHOPEE_COLORS['green']};
    border-color: {SHOPEE_COLORS['green']};
}}

/* ============ CARDS ============ */
.shopee-card {{
    background: {SHOPEE_COLORS['white']};
    border: 1px solid {SHOPEE_COLORS['border']};
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s ease;
}}

.shopee-card:hover {{
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}}

.shopee-card-title {{
    color: {SHOPEE_COLORS['navy']};
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}}

.shopee-card-subtitle {{
    color: {SHOPEE_COLORS['text_secondary']};
    font-size: 0.875rem;
    margin-bottom: 1rem;
}}

.shopee-card-content {{
    color: {SHOPEE_COLORS['text_primary']};
    line-height: 1.6;
}}

/* ============ HERO HEADER ============ */
.shopee-hero {{
    padding: 2rem 0 1.5rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid {SHOPEE_COLORS['border']};
}}

.shopee-hero-eyebrow {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: {SHOPEE_COLORS['orange_light']};
    color: {SHOPEE_COLORS['primary_orange']};
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.25rem 0.7rem;
    border-radius: 100px;
    margin-bottom: 0.75rem;
}}

.shopee-hero-title {{
    font-size: 1.875rem;
    font-weight: 700;
    color: {SHOPEE_COLORS['navy']};
    line-height: 1.25;
    margin: 0 0 0.5rem 0;
    border: none;
    padding: 0;
}}

.shopee-hero-sub {{
    color: {SHOPEE_COLORS['text_secondary']};
    font-size: 0.95rem;
    margin: 0;
    line-height: 1.5;
}}

/* ============ PREREQUISITES BOX ============ */
.shopee-prereq-box {{
    background: #FFF8F6;
    border: 1.5px solid #FDDDD7;
    border-left: 4px solid {SHOPEE_COLORS['primary_orange']};
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1.25rem 0 1.5rem 0;
}}

.shopee-prereq-eyebrow {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: {SHOPEE_COLORS['primary_orange']};
    color: #FFFFFF;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.2rem 0.65rem;
    border-radius: 100px;
    margin-bottom: 0.75rem;
}}

.shopee-prereq-title {{
    color: {SHOPEE_COLORS['navy']};
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 0.75rem 0;
    border: none !important;
    padding: 0 !important;
}}

.shopee-prereq-item {{
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid {SHOPEE_COLORS['surface_lighter']};
    font-size: 0.9rem;
    color: {SHOPEE_COLORS['text_primary']};
    line-height: 1.5;
}}

.shopee-prereq-item:last-child {{
    border-bottom: none;
    padding-bottom: 0;
}}

.shopee-prereq-num {{
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: {SHOPEE_COLORS['primary_orange']};
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 0.1rem;
}}

.shopee-prereq-link {{
    color: {SHOPEE_COLORS['blue']};
    text-decoration: none;
    font-weight: 600;
}}

.shopee-prereq-link:hover {{
    text-decoration: underline;
}}

/* ============ STEP 5: SELLER CENTER UPLOAD GUIDE ============ */
.shopee-sc-highlight {{
    background: linear-gradient(135deg, {SHOPEE_COLORS['orange_light']} 0%, {SHOPEE_COLORS['orange_medium']} 100%);
    border: 2px solid {SHOPEE_COLORS['primary_orange']};
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.shopee-sc-highlight-icon {{
    font-size: 2rem;
    flex-shrink: 0;
}}

.shopee-sc-highlight-text {{
    flex: 1;
}}

.shopee-sc-highlight-label {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {SHOPEE_COLORS['primary_orange']};
    margin-bottom: 0.2rem;
}}

.shopee-sc-highlight-market {{
    font-size: 1.25rem;
    font-weight: 700;
    color: {SHOPEE_COLORS['navy']};
}}

.shopee-sc-highlight-link a {{
    color: {SHOPEE_COLORS['blue']};
    font-weight: 600;
    font-size: 0.95rem;
    text-decoration: none;
}}

.shopee-sc-highlight-link a:hover {{
    text-decoration: underline;
}}

.shopee-market-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin: 1rem 0;
}}

.shopee-market-tile {{
    background: {SHOPEE_COLORS['white']};
    border: 1px solid {SHOPEE_COLORS['border']};
    border-radius: 8px;
    padding: 0.75rem 1rem;
    text-align: center;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}

.shopee-market-tile.target-market {{
    border-color: {SHOPEE_COLORS['primary_orange']};
    border-width: 2px;
    background: #FFF8F6;
}}

.shopee-market-tile-code {{
    font-size: 1rem;
    font-weight: 700;
    color: {SHOPEE_COLORS['navy']};
}}

.shopee-market-tile-link a {{
    font-size: 0.78rem;
    color: {SHOPEE_COLORS['blue']};
    text-decoration: none;
}}

.shopee-market-tile-link a:hover {{
    text-decoration: underline;
}}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {{
    .main {{
        padding: 0.5rem 1rem;
    }}

    h1 {{
        font-size: 1.5rem;
    }}

    h2 {{
        font-size: 1.25rem;
    }}

    .stButton > button {{
        padding: 0.65rem 1.25rem;
    }}
}}

</style>
"""


def inject_styles() -> None:
    """Inject custom Shopee CSS styles into the Streamlit app."""
    st.markdown(CSS_CUSTOM_STYLES, unsafe_allow_html=True)


def badge(text: str, status_type: str = "default") -> str:
    """
    Create a styled Shopee badge.

    Args:
        text: Badge text content
        status_type: "success", "pending", "error", "warning", "info", or "default"

    Returns:
        HTML string for the badge
    """
    status_classes = {
        "success": "shopee-badge shopee-badge-success",
        "pending": "shopee-badge shopee-badge-pending",
        "error": "shopee-badge shopee-badge-error",
        "warning": "shopee-badge shopee-badge-warning",
        "info": "shopee-badge shopee-badge-info",
        "default": "shopee-badge shopee-badge-default",
    }

    css_class = status_classes.get(status_type, status_classes["default"])
    return f'<span class="{css_class}">{text}</span>'


def step_badge(step_number: int, total_steps: int = 4) -> str:
    """
    Create a step indicator badge (e.g., "Step 1/4").

    Args:
        step_number: Current step (1-indexed)
        total_steps: Total number of steps

    Returns:
        HTML string for the step badge
    """
    return f'<div class="shopee-step-badge">Step {step_number}/{total_steps}</div>'


def progress_indicator(current: int, total: int, label: str = "Progress") -> str:
    """
    Create a visual progress indicator.

    Args:
        current: Current progress value
        total: Total progress value
        label: Label for the progress indicator

    Returns:
        HTML string for the progress indicator
    """
    percentage = (current / total * 100) if total > 0 else 0

    return f"""
    <div style="margin: 1rem 0;">
        <div class="shopee-progress-label">
            <span class="shopee-progress-label-left">{label}</span>
            <span class="shopee-progress-label-right">{current}/{total}</span>
        </div>
        <div class="shopee-progress">
            <div class="shopee-progress-fill" style="width: {percentage}%"></div>
        </div>
    </div>
    """


def section_divider(title: str = "") -> None:
    """
    Create a styled section divider.

    Args:
        title: Optional section title
    """
    st.divider()
    if title:
        st.markdown(f"### {title}")


def card(title: str, content: str, subtitle: str = "") -> str:
    """
    Create a styled card component.

    Args:
        title: Card title
        content: Card content
        subtitle: Optional card subtitle

    Returns:
        HTML string for the card
    """
    subtitle_html = f'<div class="shopee-card-subtitle">{subtitle}</div>' if subtitle else ""

    return f"""
    <div class="shopee-card">
        <div class="shopee-card-title">{title}</div>
        {subtitle_html}
        <div class="shopee-card-content">{content}</div>
    </div>
    """


def render_summary_box(title: str, items: dict) -> None:
    """
    Render a summary box with key-value pairs using native Streamlit components.

    Args:
        title: Summary box title
        items: Dictionary of label-value pairs
    """
    with st.container(border=True):
        st.markdown(f"**{title}**")
        for label, value in items.items():
            col1, col2 = st.columns([1, 1])
            col1.caption(label)
            col2.markdown(f"**{value}**")


def render_prereq_box(source_market: str, target_market: str) -> str:
    """
    Render the 'Before You Begin' prerequisites box as an HTML string.

    Args:
        source_market: Source market code (e.g. "my")
        target_market: Target market code (e.g. "sg")

    Returns:
        HTML string — caller must pass unsafe_allow_html=True.
    """
    src_key = source_market.lower()
    tgt_key = target_market.lower()
    src_name, src_url = SELLER_CENTER_URLS.get(src_key, (source_market.upper(), "#"))
    tgt_name, tgt_url = SELLER_CENTER_URLS.get(tgt_key, (target_market.upper(), "#"))

    return f"""
    <div class="shopee-prereq-box">
        <div class="shopee-prereq-eyebrow">Before You Begin</div>
        <div class="shopee-prereq-title">Download These Files First</div>

        <div class="shopee-prereq-item">
            <div class="shopee-prereq-num">1</div>
            <div>
                Go to your <strong>{src_name} ({src_key.upper()}) Seller Center</strong>
                — <a class="shopee-prereq-link" href="{src_url}" target="_blank">{src_url}</a>
                — and download all <strong>5 Mass Update export files</strong>:
                Basic Info, Sales Info, Shipping Info, Days-to-Ship, and Media/Images.
                <br><small style="color:#777;">Path in Seller Center: My Products &rarr; Mass Update &rarr; Export</small>
            </div>
        </div>

        <div class="shopee-prereq-item">
            <div class="shopee-prereq-num">2</div>
            <div>
                Go to your <strong>{tgt_name} ({tgt_key.upper()}) Seller Center</strong>
                — <a class="shopee-prereq-link" href="{tgt_url}" target="_blank">{tgt_url}</a>
                — and download the <strong>Mass Upload Basic Template</strong>.
                <br><small style="color:#777;">Path in Seller Center: My Products &rarr; Mass Upload &rarr; Download Template &rarr; Basic Template</small>
            </div>
        </div>
    </div>
    """


def render_step5_upload_guide(source_market: str, target_market: str) -> str:
    """
    Render the Step 5 'Upload to Seller Center' guide as an HTML string.
    Shows only the two markets involved in the current transfer.

    Args:
        source_market: Source market code (e.g. "my")
        target_market: Target market code (e.g. "sg")

    Returns:
        HTML string — caller must pass unsafe_allow_html=True.
    """
    src_key = source_market.lower()
    tgt_key = target_market.lower()
    src_name, src_url = SELLER_CENTER_URLS.get(src_key, (source_market.upper(), "#"))
    tgt_name, tgt_url = SELLER_CENTER_URLS.get(tgt_key, (target_market.upper(), "#"))

    src_tile = f"""
    <div class="shopee-market-tile">
        <div class="shopee-market-tile-code">{src_key.upper()}</div>
        <div style="font-size:0.78rem;color:#555;margin:0.15rem 0;">{src_name} <span style="font-size:0.65rem;background:#E8E8E8;color:#555;padding:0.1rem 0.4rem;border-radius:8px;font-weight:600;">SOURCE</span></div>
        <div class="shopee-market-tile-link"><a href="{src_url}" target="_blank">{src_url}</a></div>
    </div>"""

    tgt_tile = f"""
    <div class="shopee-market-tile target-market">
        <div class="shopee-market-tile-code">{tgt_key.upper()} <span style="font-size:0.65rem;background:#EE4D2D;color:white;padding:0.1rem 0.4rem;border-radius:8px;font-weight:700;">TARGET</span></div>
        <div style="font-size:0.78rem;color:#555;margin:0.15rem 0;">{tgt_name}</div>
        <div class="shopee-market-tile-link"><a href="{tgt_url}" target="_blank">{tgt_url}</a></div>
    </div>"""

    return f"""
    <div class="shopee-sc-highlight">
        <div class="shopee-sc-highlight-icon">🚀</div>
        <div class="shopee-sc-highlight-text">
            <div class="shopee-sc-highlight-label">Upload Destination</div>
            <div class="shopee-sc-highlight-market">{tgt_name} ({tgt_key.upper()}) Seller Center</div>
            <div class="shopee-sc-highlight-link">
                <a href="{tgt_url}" target="_blank">{tgt_url}</a>
            </div>
        </div>
    </div>

    <p style="color:#1A1A1A;font-size:0.9rem;margin:0.75rem 0 0.5rem 0;">
        In your <strong>{tgt_name} Seller Center</strong>, go to
        <strong>My Products &rarr; Mass Upload &rarr; Upload File</strong>
        and select the file you just downloaded. Shopee will validate the rows and queue your listings for review.
    </p>

    <p style="color:#555;font-size:0.875rem;font-weight:600;margin:1rem 0 0.5rem 0;">Seller Center Links for This Transfer</p>
    <div class="shopee-market-grid">
        {src_tile}
        {tgt_tile}
    </div>
    """


def status_text(text: str, status: str = "info") -> str:
    """
    Create styled status text with badge.

    Args:
        text: Status text
        status: Status type ("success", "pending", "error", "warning", "info")

    Returns:
        HTML string combining badge and text
    """
    status_badge = badge(status.upper(), status)
    return f'{status_badge} <span style="margin-left: 0.5rem; color: #1A1A1A;">{text}</span>'
