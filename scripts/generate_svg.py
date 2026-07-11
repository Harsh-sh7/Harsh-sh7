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

    # 1. Save assets/terminal_avatar.svg (Left Side ASCII grid)
    contrib_svg_rects = []
    tile_size = 7.5
    tile_gap = 1.8
    # Center 30 columns of 9.3px width inside a 280px canvas
    x_start = 1.4
    # Center 40 rows of 9.3px height inside a 380px canvas
    y_start_contrib = 4.9
    
    for y_idx, row in enumerate(contrib_grid):
        for x_idx, color in enumerate(row):
            cx = x_start + x_idx * (tile_size + tile_gap)
            cy = y_start_contrib + y_idx * (tile_size + tile_gap)
            contrib_svg_rects.append(
                f'  <rect x="{cx:.2f}" y="{cy:.2f}" width="{tile_size}" height="{tile_size}" rx="1.5" ry="1.5" fill="{color}" />'
            )
            
    avatar_svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 380" width="100%" height="auto">
  <rect x="0" y="0" width="280" height="380" rx="6" fill="#0b0f19" />
{chr(10).join(contrib_svg_rects)}
</svg>"""

    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "assets"), exist_ok=True)
    avatar_output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "terminal_avatar.svg")
    with open(avatar_output_path, "w") as f:
        f.write(avatar_svg_content)
    print(f"Successfully generated ASCII avatar SVG at {avatar_output_path}!")

    # 2. Build the HTML elements for the README.md terminal stats panel
    languages_display = ", ".join(config["languages"])
    frameworks_display = ", ".join(config["frameworks"])
    database_display = ", ".join(config["database"])
    tools_display = ", ".join(config["tools"])
    
    recent_activity_block = ""
    if stats["recent_activity"]:
        recent_activity_block = '<span style="color:#9ca3af">─ Recent Activity ───────────────────────────────────────────</span><br>\n'
        for idx, act in enumerate(stats["recent_activity"][:3]):
            recent_activity_block += f'<span style="color:#60a5fa">Act {idx+1}</span><span style="color:#4b5563"> : .......... </span><a href="https://github.com/{username}?tab=activity" target="_blank" style="color:#e5e7eb; text-decoration:none;">{act}</a><br>\n'

    # Build the full README.md content dynamically
    readme_content = f"""# Hi 👋

<p align="center">
<table width="850" style="border-collapse: collapse; border: 1px solid #1f2937;">
<!-- Terminal Header Bar -->
<tr bgcolor="#111827">
<td colspan="2" style="padding: 8px; border: none;">
<span style="color:#ff5f56; font-size: 14px;">●</span>
<span style="color:#ffbd2e; font-size: 14px;">●</span>
<span style="color:#27c93f; font-size: 14px;">●</span>
&nbsp;&nbsp;&nbsp;&nbsp;
<span style="color:#9ca3af; font-family: monospace; font-size: 12px; font-weight: bold;">{username}@macos: ~</span>
</td>
</tr>
<!-- Terminal Body -->
<tr bgcolor="#0b0f19">
<!-- Left Column: ASCII Portrait SVG -->
<td width="300" valign="top" align="center" style="padding: 20px; border: none;">
<img src="assets/terminal_avatar.svg" width="280" alt="ASCII Portrait" />
</td>
<!-- Right Column: Interactive Monospace Stats -->
<td width="550" valign="top" align="left" style="padding: 20px 20px 20px 0px; border: none;">
<div style="font-family: monospace; font-size: 12.5px; line-height: 1.55;">
<b><span style="color:#34d399">{username}</span></b><span style="color:#9ca3af">@macos:~</span><br>
<span style="color:#f97316">OS</span><span style="color:#4b5563"> : ............ </span><span style="color:#38bdf8">{config['os']}</span><br>
<span style="color:#f97316">Host</span><span style="color:#4b5563"> : .......... </span><span style="color:#38bdf8">MacBook Pro</span><br>
<span style="color:#f97316">Editor</span><span style="color:#4b5563"> : ........ </span><span style="color:#38bdf8">{config['editor']}</span><br>
<span style="color:#f97316">Location</span><span style="color:#4b5563"> : ...... </span><span style="color:#38bdf8">{config['location']}</span><br>
<span style="color:#f97316">Portfolio</span><span style="color:#4b5563"> : ..... </span><a href="{config['portfolio']}" target="_blank" style="color:#38bdf8; text-decoration:none;">{config['portfolio']}</a><br>
<span style="color:#f97316">Email</span><span style="color:#4b5563"> : ......... </span><a href="mailto:{config['email']}" style="color:#38bdf8; text-decoration:none;">{config['email']}</a><br>
<span style="color:#9ca3af">─ Technical Profile ──────────────────────────────────────────</span><br>
<span style="color:#f97316">Languages</span><span style="color:#4b5563"> : ...... </span><span style="color:#38bdf8">{languages_display}</span><br>
<span style="color:#f97316">Frameworks</span><span style="color:#4b5563"> : ...... </span><span style="color:#38bdf8">{frameworks_display}</span><br>
<span style="color:#f97316">Database</span><span style="color:#4b5563"> : ........ </span><span style="color:#38bdf8">{database_display}</span><br>
<span style="color:#f97316">Tools</span><span style="color:#4b5563"> : ........... </span><span style="color:#38bdf8">{tools_display}</span><br>
<span style="color:#9ca3af">─ GitHub Stats ─────────────────────────────────────────────</span><br>
<span style="color:#f97316">Repos</span><span style="color:#4b5563"> : ............ </span><a href="https://github.com/{username}?tab=repositories" target="_blank" style="color:#38bdf8; text-decoration:none;">{stats['public_repos']} public repos</a><br>
<span style="color:#f97316">Followers</span><span style="color:#4b5563"> : ........ </span><a href="https://github.com/{username}/followers" target="_blank" style="color:#38bdf8; text-decoration:none;">{stats['followers']}</a><span style="color:#4b5563"> | Following: </span><a href="https://github.com/{username}/following" target="_blank" style="color:#38bdf8; text-decoration:none;">{stats['following']}</a><br>
<span style="color:#f97316">Activity</span><span style="color:#4b5563"> : ......... </span><span style="color:#38bdf8">{stats['contributions']} contributions | Streak: {stats['longest_streak']} days</span><br>
{recent_activity_block}<span style="color:#4b5563">Last Updated: {stats['last_updated']} (auto-updated every 12h)</span>
</div>
</td>
</tr>
</table>
</p>

<p align="center">
<a href="https://www.linkedin.com/in/harshit-shakya/" target="_blank">
<img src="assets/linkedin_badge.svg" alt="LinkedIn" width="130">
</a>
<a href="mailto:{config['email']}">
<img src="assets/email_badge.svg" alt="Email" width="130">
</a>
<a href="{config['portfolio']}" target="_blank">
<img src="assets/portfolio_badge.svg" alt="Portfolio" width="130">
</a>
</p>

<br>

<p align="center">
<a href="assets/contribution_tree.svg" target="_blank">
<img src="assets/contribution_tree.svg" alt="GitHub Contribution Tree" width="850">
</a>
</p>

<br>

<p align="center">
<img src="https://visitor-badge.laobi.icu/badge?page_id={username}.{username}" alt="Visitors Counter">
</p>
"""

    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, "w") as f:
        f.write(readme_content)
    print(f"Successfully generated dynamic, interactive README.md at {readme_path}!")

    # 3. Generate supplementary assets
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
