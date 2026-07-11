import os
import json
import math
from datetime import datetime
from avatar_to_ascii import download_avatar, image_to_contrib_grid
from github_stats import GitHubStatsFetcher

def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def format_line(y_pos, label, value, label_color="#f97316", dot_color="#4b5563", value_color="#38bdf8", prefix_len=18):
    """
    Formats a single monospace line with dotted alignment.
    """
    dots_count = prefix_len - len(label) - 2
    if dots_count < 1:
        dots_count = 1
    dots = "." * dots_count
    
    # Total right side columns available ~48 characters (to fit x=360 to x=850 at font-size 12)
    max_val_len = 65 - prefix_len - 2
    display_val = str(value)
    if len(display_val) > max_val_len:
        display_val = display_val[:max_val_len - 3] + "..."
        
    return f"""  <text x="360" y="{y_pos}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="12.5" font-weight="500">
    <tspan fill="{label_color}">{label}</tspan>
    <tspan fill="{dot_color}">: {dots} </tspan>
    <tspan fill="{value_color}">{display_val}</tspan>
  </text>"""

def format_section_header(y_pos, title, line_color="#1f2937", text_color="#9ca3af"):
    """
    Formats a terminal section divider, e.g., - Contact -----------------
    """
    title_text = f"─ {title} "
    # Right panel width at font-size 12 is about 60 chars
    remaining_len = 54 - len(title_text)
    if remaining_len < 1:
        remaining_len = 1
    line = "─" * remaining_len
    return f"""  <text x="360" y="{y_pos}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11.5" font-weight="700">
    <tspan fill="{text_color}">{title_text}</tspan>
    <tspan fill="{line_color}">{line}</tspan>
  </text>"""

def generate_svg():
    print("Loading configurations...")
    config = load_config()
    username = config["github_username"]
    
    print(f"Fetching GitHub stats for {username}...")
    stats_fetcher = GitHubStatsFetcher(username)
    stats = stats_fetcher.fetch_all_stats()
    
    print("Generating Contribution Grid avatar...")
    avatar_img = download_avatar(username)
    # Target size: 30 columns x 40 rows for contribution grid
    contrib_grid = image_to_contrib_grid(avatar_img, width=30, height=40)

    # Calculate typing animation widths
    typed_text = f"{username}@macos:~"
    char_width = 7.8  # Approx width of a monospace char at font-size 13
    text_width = len(typed_text) * char_width
    cursor_start_x = 360
    cursor_end_x = 360 + text_width + 4
 
    print("Compiling SVG content...")
    # Header buttons & macOS terminal style
    svg_elements = []
    
    # 1. Left Side Contribution Grid Portrait
    contrib_svg_rects = ["  <!-- Left Side Contribution Grid Portrait -->"]
    tile_size = 7.5
    tile_gap = 1.8
    x_start = 45.5
    y_start_contrib = 86.0
    
    for y_idx, row in enumerate(contrib_grid):
        for x_idx, color in enumerate(row):
            cx = x_start + x_idx * (tile_size + tile_gap)
            cy = y_start_contrib + y_idx * (tile_size + tile_gap)
            contrib_svg_rects.append(
                f'  <rect class="contrib-tile" x="{cx:.2f}" y="{cy:.2f}" width="{tile_size}" height="{tile_size}" rx="1.5" ry="1.5" fill="{color}" />'
            )
            
    contrib_text_block = "\n".join(contrib_svg_rects)
    svg_elements.append(contrib_text_block)

    # 2. Right Side Info Panel
    # Typing username header
    typing_header = f"""  <!-- Typing Header -->
  <g clip-path="url(#type-clip)">
    <text x="360" y="80" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="13.5" font-weight="bold">
      <tspan fill="#34d399">{username}</tspan>
      <tspan fill="#9ca3af">@macos:~</tspan>
    </text>
  </g>
  
  <!-- Typing Cursor -->
  <rect x="{cursor_start_x}" y="66" width="7" height="15" fill="#38bdf8">
    <animate attributeName="x" from="{cursor_start_x}" to="{cursor_end_x}" dur="1.5s" begin="0.5s" fill="freeze" keyTimes="0; 1" keySplines="0.25, 0.1, 0.25, 1.0" calcMode="spline" />
    <animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite" />
  </rect>"""
    svg_elements.append(typing_header)

    # Calculate Y-positions dynamically with explicit margins to prevent overlap
    OS_y = 105
    Host_y = OS_y + 17.5
    Editor_y = Host_y + 17.5
    Location_y = Editor_y + 17.5
    Portfolio_y = Location_y + 17.5
    Email_y = Portfolio_y + 17.5
    
    y_tech_header = Email_y + 24
    Languages_y = y_tech_header + 17.5
    Frameworks_y = Languages_y + 17.5
    Database_y = Frameworks_y + 17.5
    Tools_y = Database_y + 17.5
    
    y_stats_header = Tools_y + 24
    Repos_y = y_stats_header + 17.5
    Followers_y = Repos_y + 17.5
    Activity_y = Followers_y + 17.5
    TopLang_y = Activity_y + 17.5
    bar_y = TopLang_y + 8.5
    
    y_act_header = bar_y + 22 if stats["top_languages"] else TopLang_y + 24
    Act1_y = y_act_header + 17.5
    Act2_y = Act1_y + 17.5
    Act3_y = Act2_y + 17.5
    
    # System Info
    svg_elements.append(format_line(OS_y, "OS", config["os"]))
    svg_elements.append(format_line(Host_y, "Host", "MacBook Pro"))
    svg_elements.append(format_line(Editor_y, "Editor", config["editor"]))
    svg_elements.append(format_line(Location_y, "Location", config["location"]))
    svg_elements.append(format_line(Portfolio_y, "Portfolio", config["portfolio"]))
    svg_elements.append(format_line(Email_y, "Email", config["email"]))
    
    # Technical Profile Section
    svg_elements.append(format_section_header(y_tech_header, "Technical Profile"))
    svg_elements.append(format_line(Languages_y, "Languages", ", ".join(config["languages"])))
    svg_elements.append(format_line(Frameworks_y, "Frameworks", ", ".join(config["frameworks"])))
    svg_elements.append(format_line(Database_y, "Database", ", ".join(config["database"])))
    svg_elements.append(format_line(Tools_y, "Tools", ", ".join(config["tools"])))
    
    # GitHub Stats Section
    svg_elements.append(format_section_header(y_stats_header, "GitHub Stats"))
    svg_elements.append(format_line(Repos_y, "Repos", f"{stats['public_repos']} public repos"))
    svg_elements.append(format_line(Followers_y, "Followers", f"{stats['followers']} | Following: {stats['following']}"))
    
    contrib_str = f"{stats['contributions']} contributions"
    if stats["longest_streak"] > 0:
        contrib_str += f" | Streak: {stats['longest_streak']} days"
    svg_elements.append(format_line(Activity_y, "Activity", contrib_str))
    
    # Top Languages Progress Bar
    if stats["top_languages"]:
        lang_names = [lang["name"] for lang in stats["top_languages"][:3]]
        lang_display = ", ".join(lang_names)
        svg_elements.append(format_line(TopLang_y, "Top Lang", lang_display))
        
        # Render the custom multi-colored progress bar
        progress_bar_g = [f'  <!-- Progress Bar -->']
        progress_bar_g.append(f'  <rect x="495" y="{bar_y}" width="160" height="5" rx="2.5" fill="#1f2937" />')
        
        current_x = 495
        for lang in stats["top_languages"][:4]:
            width = (lang["percentage"] / 100.0) * 160
            color = lang["color"]
            progress_bar_g.append(f'  <rect x="{current_x}" y="{bar_y}" width="{width:.1f}" height="5" rx="1.5" fill="{color}" />')
            current_x += width
            
        svg_elements.append("\n".join(progress_bar_g))

    # Recent Activity Section
    svg_elements.append(format_section_header(y_act_header, "Recent Activity"))
    act_ys = [Act1_y, Act2_y, Act3_y]
    for idx, act in enumerate(stats["recent_activity"][:3]):
        svg_elements.append(format_line(act_ys[idx], f"Act {idx+1}", act, label_color="#60a5fa", value_color="#e5e7eb"))

    # Bottom Update Timestamp
    y_bottom = 495
    svg_elements.append(f"""  <!-- Bottom Timestamp -->
  <text x="360" y="{y_bottom}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">
    Last Updated: {stats['last_updated']} (auto-updated every 12h)
  </text>""")

    # Combine into full SVG template
    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" width="100%" height="auto">
  <defs>
    <!-- Import beautiful Monospace Font -->
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      
      .terminal-window {{
        filter: drop-shadow(0 25px 50px rgba(0, 0, 0, 0.45));
        animation: fadeIn 0.8s ease-out;
      }}
      
      .contrib-tile {{
        transition: transform 0.15s ease, fill 0.15s ease;
        transform-box: fill-box;
        transform-origin: center;
      }}
      
      .contrib-tile:hover {{
        transform: scale(1.3);
        fill: #38bdf8; /* Sky blue highlight on hover */
        cursor: pointer;
      }}
      
      @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
    
    <!-- Typing Animation Clip Path -->
    <clipPath id="type-clip">
      <rect x="360" y="60" width="0" height="30">
        <animate attributeName="width" from="0" to="{cursor_end_x - 360}" dur="1.5s" begin="0.5s" fill="freeze" keyTimes="0; 1" keySplines="0.25, 0.1, 0.25, 1.0" calcMode="spline" />
      </rect>
    </clipPath>
  </defs>

  <g class="terminal-window">
    <!-- Window Background (Premium Deep Dark) -->
    <rect x="0" y="0" width="900" height="520" rx="12" fill="#0b0f19" stroke="#1f2937" stroke-width="1.5" />

    <!-- Window Title Bar -->
    <path d="M 0,12 A 12,12 0 0,1 12,0 L 888,0 A 12,12 0 0,1 900,12 L 900,42 L 0,42 Z" fill="#111827" />
    
    <!-- Window Control Buttons (macOS Style) -->
    <circle cx="25" cy="21" r="6" fill="#ff5f56" />
    <circle cx="45" cy="21" r="6" fill="#ffbd2e" />
    <circle cx="65" cy="21" r="6" fill="#27c93f" />

    <!-- Terminal Title -->
    <text x="450" y="25" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="12" fill="#9ca3af" text-anchor="middle" font-weight="bold">
      {username}@macos: ~
    </text>

    <!-- Title Bar Divider -->
    <line x1="0" y1="42" x2="900" y2="42" stroke="#1f2937" stroke-width="1" />

    <!-- Vertical Separator Line (Dashed, Premium look) -->
    <line x1="335" y1="58" x2="335" y2="502" stroke="#1f2937" stroke-width="1.5" stroke-dasharray="4 4" />

    <!-- Rendered SVG elements -->
{chr(10).join(svg_elements)}
  </g>
</svg>"""

    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "assets"), exist_ok=True)
    svg_output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "terminal.svg")
    
    with open(svg_output_path, "w") as f:
        f.write(svg_template)
        
    print(f"Successfully generated responsive terminal SVG at {svg_output_path}!")
    
    # Run supplementary retro generators
    generate_tree_svg(stats, username)
    generate_retro_badges()

def generate_retro_badges():
    print("Generating retro CLI social badges...")
    badges = {
        "linkedin": ("[ LINKEDIN ]", "#38bdf8"),
        "email": ("[ EMAIL ]", "#f97316"),
        "portfolio": ("[ PORTFOLIO ]", "#34d399")
    }
    
    for name, (label, color) in badges.items():
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="130" height="28" viewBox="0 0 130 28">
  <style>
    .badge-rect {{
      fill: #0b0f19;
      stroke: #1f2937;
      stroke-width: 1.5;
      transition: all 0.2s ease;
    }}
    .badge-rect:hover {{
      fill: #111827;
      stroke: {color};
    }}
    .badge-text {{
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 10.5px;
      font-weight: bold;
      fill: {color};
      text-anchor: middle;
      dominant-baseline: middle;
      transition: fill 0.2s ease;
      cursor: pointer;
    }}
    .badge-rect:hover + .badge-text, .badge-text:hover {{
      fill: #e5e7eb;
    }}
  </style>
  <rect class="badge-rect" x="1.5" y="1.5" width="127" height="25" rx="4" />
  <text class="badge-text" x="65" y="14">{label}</text>
</svg>"""
        output_path = os.path.join(os.path.dirname(__file__), "..", "assets", f"{name}_badge.svg")
        with open(output_path, "w") as f:
            f.write(svg_content)
    print("Generated retro social badges successfully!")

def generate_tree_svg(stats: dict, username: str):
    print("Generating 3D Isometric Contribution Graph SVG...")
    if "contribution_days" not in stats or not stats["contribution_days"]:
        print("No contribution days found in stats! Skipping generation.")
        return
        
    # Find most recent commit
    recent_day = None
    for day in reversed(stats["contribution_days"]):
        if day["contributionCount"] > 0:
            recent_day = day
            break
            
    # Calculate stats
    total_commits = sum(day["contributionCount"] for day in stats["contribution_days"])
    
    busiest_day = max(stats["contribution_days"], key=lambda d: d["contributionCount"])
    busiest_count = busiest_day["contributionCount"]
    busiest_date = datetime.strptime(busiest_day["date"], "%Y-%m-%d").strftime("%b %d, %Y") if busiest_count > 0 else "N/A"
    
    # Calculate streaks
    longest_streak = 0
    temp_streak = 0
    longest_start = None
    longest_end = None
    temp_start = None
    
    for day in stats["contribution_days"]:
        if day["contributionCount"] > 0:
            if temp_streak == 0:
                temp_start = day["date"]
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
                longest_start = temp_start
                longest_end = day["date"]
        else:
            temp_streak = 0
            
    current_streak = 0
    current_start = None
    current_end = None
    for day in reversed(stats["contribution_days"]):
        if day["contributionCount"] > 0:
            if current_streak == 0:
                current_end = day["date"]
            current_streak += 1
            current_start = day["date"]
        else:
            if current_streak > 0:
                break
                
    longest_streak_str = ""
    if longest_streak > 0 and longest_start and longest_end:
        ls_start = datetime.strptime(longest_start, "%Y-%m-%d").strftime("%b %d")
        ls_end = datetime.strptime(longest_end, "%Y-%m-%d").strftime("%b %d")
        longest_streak_str = f"{ls_start} - {ls_end}"
        
    current_streak_str = ""
    if current_streak > 0 and current_start and current_end:
        cs_start = datetime.strptime(current_start, "%Y-%m-%d").strftime("%b %d")
        cs_end = datetime.strptime(current_end, "%Y-%m-%d").strftime("%b %d")
        current_streak_str = f"{cs_start} - {cs_end}"
        
    # Premium 3D Isometric Shading Color Palette
    # Colors: (Top Face, Left Face, Right Face)
    colors_3d = {
        0: ("#161b22", "#11151b", "#0d1115"),  # Level 0
        1: ("#0e4429", "#0b3620", "#082818"),  # Level 1
        2: ("#006d32", "#005728", "#00411e"),  # Level 2
        3: ("#26a641", "#1e8534", "#166327"),  # Level 3
        4: ("#39d353", "#2ea942", "#227e31")   # Level 4
    }
    
    x_origin = 195
    y_origin = 110
    w = 11.5
    h_d = 5.75
    
    svg_elements = []
    recent_marker = ""
    
    # Render all 3D pillars back-to-front
    for idx, day in enumerate(stats["contribution_days"]):
        col = idx // 7
        row = idx % 7
        
        cx = x_origin + col * w - row * w
        cy = y_origin + col * h_d + row * h_d
        
        cnt = day["contributionCount"]
        dt = datetime.strptime(day["date"], "%Y-%m-%d")
        
        # Calculate level 0-4
        if cnt == 0:
            level = 0
            H = 0
        elif cnt <= 2:
            level = 1
            H = 8
        elif cnt <= 5:
            level = 2
            H = 18
        elif cnt <= 8:
            level = 3
            H = 30
        else:
            level = 4
            H = 45
            
        # Add slight additional height scaling for active commits
        if cnt > 0:
            H = min(75, H + (cnt - 1) * 1.8)
            
        top_color, left_color, right_color = colors_3d[level]
        is_recent = (recent_day and day["date"] == recent_day["date"])
        
        pillar_shapes = []
        
        # If H == 0, draw flat floor tile (rhombus only)
        if H == 0:
            pillar_shapes.append(
                f'<polygon points="{cx:.1f},{cy - h_d:.1f} {cx + w:.1f},{cy:.1f} {cx:.1f},{cy + h_d:.1f} {cx - w:.1f},{cy:.1f}" fill="{top_color}" stroke="#0b0f19" stroke-width="0.3" />'
            )
        else:
            # 1. Left face vertical wall
            pillar_shapes.append(
                f'<polygon points="{cx - w:.1f},{cy - H:.1f} {cx:.1f},{cy - H + h_d:.1f} {cx:.1f},{cy + h_d:.1f} {cx - w:.1f},{cy:.1f}" fill="{left_color}" />'
            )
            # 2. Right face vertical wall
            pillar_shapes.append(
                f'<polygon points="{cx:.1f},{cy - H + h_d:.1f} {cx + w:.1f},{cy - H:.1f} {cx + w:.1f},{cy:.1f} {cx:.1f},{cy + h_d:.1f}" fill="{right_color}" />'
            )
            # 3. Top face rhombus
            pillar_shapes.append(
                f'<polygon points="{cx:.1f},{cy - H - h_d:.1f} {cx + w:.1f},{cy - H:.1f} {cx:.1f},{cy - H + h_d:.1f} {cx - w:.1f},{cy - H:.1f}" fill="{top_color}" stroke="{top_color}" stroke-width="0.3" />'
            )
            
        # Hover interactive tooltip
        commit_lbl = f"{cnt} commits" if cnt != 1 else "1 commit"
        if cnt == 0:
            commit_lbl = "No commits"
            
        # Prevent clipping on the right edge of the card
        tx_offset = -140 if col > 44 else 10
            
        tooltip_element = f"""<g class="tooltip" transform="translate({cx + tx_offset:.2f}, {cy - H - 18:.2f})">
        <rect x="0" y="0" width="130" height="18" rx="3" fill="#111827" stroke="{top_color if cnt > 0 else '#1f2937'}" stroke-width="1" opacity="0.95" />
        <text x="65" y="12" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="8.5" fill="#e5e7eb" font-weight="bold" text-anchor="middle">{commit_lbl} ({dt.strftime('%b %d')})</text>
      </g>"""
      
        group_class = "pillar-group recent-pillar" if is_recent else "pillar-group"
        day_url = f"https://github.com/{username}?tab=overview&amp;from={day['date']}&amp;to={day['date']}"
        svg_elements.append(
            f'    <a href="{day_url}" target="_blank">\n      <g class="{group_class}" data-date="{day["date"]}">\n        {" ".join(pillar_shapes)}\n        {tooltip_element}\n      </g>\n    </a>'
        )
        
        if is_recent:
            recent_marker = f"""    <!-- Pulse Halo for Most Recent Commit -->
    <circle cx="{cx:.2f}" cy="{cy - H:.2f}" r="13" fill="none" stroke="#ef4444" stroke-width="1.8">
      <animate attributeName="r" values="8;15;8" dur="1.2s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite" />
    </circle>
    <circle cx="{cx:.2f}" cy="{cy - H:.2f}" r="2.5" fill="#ef4444" />"""

    # Generate month labels along the top-left axis (col axis)
    months_labels = []
    last_month = None
    seen_months = set()
    for idx, day in enumerate(stats["contribution_days"]):
        col = idx // 7
        dt = datetime.strptime(day["date"], "%Y-%m-%d")
        m_name = dt.strftime("%b")
        if m_name != last_month and m_name not in seen_months:
            seen_months.add(m_name)
            last_month = m_name
            
            # Week start baseline at row 0
            cx = x_origin + col * w
            cy = y_origin + col * h_d
            tx = cx - 18
            ty = cy - 25
            months_labels.append(
                f'    <line x1="{tx + 14:.1f}" y1="{ty + 4:.1f}" x2="{cx:.1f}" y2="{cy - 5:.1f}" stroke="#374151" stroke-width="0.8" stroke-dasharray="2 2" />'
                f'\n    <text x="{tx:.1f}" y="{ty:.1f}" font-family="\'JetBrains Mono\', \'Fira Code\', monospace" font-size="9" fill="#9ca3af" text-anchor="end">{m_name}</text>'
            )
            
    # Generate weekday labels along the top-right axis (row axis)
    weekday_labels = []
    for r, label in [(0, "Sun"), (3, "Wed"), (6, "Sat")]:
        cx = x_origin - r * w
        cy = y_origin + r * h_d
        weekday_labels.append(
            f'    <text x="{cx - 15:.1f}" y="{cy + 3:.1f}" font-family="\'JetBrains Mono\', \'Fira Code\', monospace" font-size="9" fill="#4b5563" text-anchor="end">{label}</text>'
        )
        
    # Generate 3D Legend items at bottom-right
    legend_elements = []
    lx_start = 650
    ly_start = 440
    for lvl in range(5):
        lx = lx_start + lvl * 28
        ly = ly_start
        t_col, l_col, r_col = colors_3d[lvl]
        H_leg = lvl * 7
        
        leg_shapes = []
        if H_leg == 0:
            leg_shapes.append(
                f'<polygon points="{lx:.1f},{ly - h_d:.1f} {lx + w:.1f},{ly:.1f} {lx:.1f},{ly + h_d:.1f} {lx - w:.1f},{ly:.1f}" fill="{t_col}" stroke="#0b0f19" stroke-width="0.3" />'
            )
        else:
            leg_shapes.append(
                f'<polygon points="{lx - w:.1f},{ly - H_leg:.1f} {lx:.1f},{ly - H_leg + h_d:.1f} {lx:.1f},{ly + h_d:.1f} {lx - w:.1f},{ly:.1f}" fill="{l_col}" />'
            )
            leg_shapes.append(
                f'<polygon points="{lx:.1f},{ly - H_leg + h_d:.1f} {lx + w:.1f},{ly - H_leg:.1f} {lx + w:.1f},{ly:.1f} {lx:.1f},{ly + h_d:.1f}" fill="{r_col}" />'
            )
            leg_shapes.append(
                f'<polygon points="{lx:.1f},{ly - H_leg - h_d:.1f} {lx + w:.1f},{ly - H_leg:.1f} {lx:.1f},{ly - H_leg + h_d:.1f} {lx - w:.1f},{ly - H_leg:.1f}" fill="{t_col}" stroke="{t_col}" stroke-width="0.3" />'
            )
        legend_elements.append(f'      <g transform="translate(0, 0)">{" ".join(leg_shapes)}</g>')

    # SVG compilation
    svg_tree_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 480" width="100%" height="auto">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      
      .contrib-graph-card {{
        filter: drop-shadow(0 25px 50px rgba(0, 0, 0, 0.45));
        animation: graphFadeIn 0.8s ease-out;
      }}
      
      .pillar-group {{
        transition: transform 0.2s ease;
        cursor: pointer;
        transform-box: fill-box;
        transform-origin: bottom center;
      }}
      
      .pillar-group:hover {{
        transform: translateY(-8px);
      }}
      
      .pillar-group .tooltip {{
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.15s ease, transform 0.15s ease;
        transform: translateY(5px);
        transform-box: fill-box;
      }}
      
      .pillar-group:hover .tooltip {{
        opacity: 1;
        transform: translateY(0);
      }}
      
      @keyframes graphFadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
  </defs>

  <g class="contrib-graph-card">
    <!-- Window Background -->
    <rect x="0" y="0" width="900" height="480" rx="12" fill="#0b0f19" stroke="#1f2937" stroke-width="1.5" />

    <!-- Window Title Bar -->
    <path d="M 0,12 A 12,12 0 0,1 12,0 L 888,0 A 12,12 0 0,1 900,12 L 900,42 L 0,42 Z" fill="#111827" />
    
    <!-- Window Control Buttons (macOS Style) -->
    <circle cx="25" cy="21" r="6" fill="#ff5f56" />
    <circle cx="45" cy="21" r="6" fill="#ffbd2e" />
    <circle cx="65" cy="21" r="6" fill="#27c93f" />

    <!-- Terminal Title -->
    <text x="450" y="25" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="12" fill="#9ca3af" text-anchor="middle" font-weight="bold">
      {username}@macos: ~/isometric-contributions
    </text>

    <!-- Title Bar Divider -->
    <line x1="0" y1="42" x2="900" y2="42" stroke="#1f2937" stroke-width="1" />

    <!-- Header Text -->
    <text x="35" y="70" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="13" fill="#34d399" font-weight="bold">
      &gt; git log --graph --date=relative --all --3d-projection (Past 12 Months)
    </text>

    <!-- Weekday and Month labels -->
{chr(10).join(weekday_labels)}
{chr(10).join(months_labels)}

    <!-- 3D Pillars -->
{chr(10).join(svg_elements)}
{recent_marker}

    <!-- Left Stats Panel -->
    <g transform="translate(45, 340)">
      <text x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">Longest Streak</text>
      <text x="0" y="22" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="20" fill="#34d399" font-weight="bold">{longest_streak} days</text>
      <text x="0" y="38" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#9ca3af">{longest_streak_str}</text>
      
      <text x="0" y="65" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">Current Streak</text>
      <text x="0" y="87" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="20" fill="#34d399" font-weight="bold">{current_streak} days</text>
      <text x="0" y="103" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#9ca3af">{current_streak_str}</text>
    </g>

    <!-- Right Stats Panel -->
    <g transform="translate(620, 95)">
      <text x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">1 Year Total</text>
      <text x="0" y="24" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="22" fill="#34d399" font-weight="bold">{total_commits:,} commits</text>
      <text x="0" y="40" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#9ca3af">Past 365 Days</text>
      
      <text x="0" y="70" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">Busiest Day</text>
      <text x="0" y="92" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="19" fill="#34d399" font-weight="bold">{busiest_count} commits</text>
      <text x="0" y="108" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#9ca3af">{busiest_date}</text>
    </g>

    <!-- Legend -->
    <g transform="translate(0, 0)">
      <text x="590" y="445" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10" fill="#4b5563" font-weight="bold" text-anchor="end">Less</text>
{chr(10).join(legend_elements)}
      <text x="795" y="445" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10" fill="#4b5563" font-weight="bold" text-anchor="start">More</text>
    </g>
  </g>
</svg>"""

    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "contribution_tree.svg")
    with open(output_path, "w") as f: f.write(svg_tree_template)
    print(f"Successfully generated Contribution Tree SVG at {output_path}!")

if __name__ == "__main__":
    generate_svg()
