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
    print("Generating Contribution Tree SVG...")
    if "contribution_days" not in stats or not stats["contribution_days"]:
        print("No contribution days found in stats! Skipping tree generation.")
        return
        
    months_data = {}
    for day in stats["contribution_days"]:
        dt = datetime.strptime(day["date"], "%Y-%m-%d")
        my_key = dt.strftime("%b '%y")
        if my_key not in months_data:
            months_data[my_key] = []
        months_data[my_key].append(day)
        
    month_keys = list(months_data.keys())[-12:]
    
    limbs_paths = []
    branch_paths = []
    twig_paths = []
    ambient_leaves = []
    leaf_rects = []
    month_labels = []
    recent_marker = ""
    
    recent_day = None
    for day in reversed(stats["contribution_days"]):
        if day["contributionCount"] > 0:
            recent_day = day
            break
            
    colors = {
        0: "#13261a",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353"
    }
    
    x_base = 450
    y_base = 560
    y_split = 445
    
    root_paths = [
        f'    <!-- Gnarled roots and flared base -->',
        f'    <path d="M 390 570 Q 420 540, 435 460" fill="none" stroke="#4e342e" stroke-width="26" stroke-linecap="round" />',
        f'    <path d="M 510 570 Q 480 540, 465 460" fill="none" stroke="#4e342e" stroke-width="26" stroke-linecap="round" />',
        f'    <path d="M 450 570 L 450 435" fill="none" stroke="#4e342e" stroke-width="32" stroke-linecap="round" />',
        f'    <path d="M 390 570 Q 350 580, 310 585" fill="none" stroke="#4e342e" stroke-width="12" stroke-linecap="round" />',
        f'    <path d="M 510 570 Q 550 580, 590 585" fill="none" stroke="#4e342e" stroke-width="12" stroke-linecap="round" />',
        f'    <path d="M 450 570 Q 450 585, 450 592" fill="none" stroke="#4e342e" stroke-width="14" stroke-linecap="round" />'
    ]
    
    limbs_paths = [
        f'    <!-- Large Primary Limbs -->',
        f'    <path d="M 435 450 C 410 390, 340 330, 290 280" fill="none" stroke="#4e342e" stroke-width="20" stroke-linecap="round" />',
        f'    <path d="M 450 435 C 450 380, 440 310, 450 220" fill="none" stroke="#4e342e" stroke-width="16" stroke-linecap="round" />',
        f'    <path d="M 465 450 C 490 390, 560 330, 610 280" fill="none" stroke="#4e342e" stroke-width="20" stroke-linecap="round" />'
    ]
    
    for i, key in enumerate(month_keys):
        angle_deg = 173 - i * (166 / 11)
        theta = math.radians(angle_deg)
        
        x_tip = x_base + 210 * math.cos(theta)
        y_tip = 340 - 150 * math.sin(theta)
        
        if i <= 3:
            x_start_branch, y_start_branch = 290, 280
            c1x = 290 + 35 * math.cos(theta)
            c1y = 280 - 25 * math.sin(theta)
        elif i <= 7:
            x_start_branch, y_start_branch = 450, 220
            c1x = 450 + 25 * math.cos(theta)
            c1y = 220 - 25 * math.sin(theta)
        else:
            x_start_branch, y_start_branch = 610, 280
            c1x = 610 + 35 * math.cos(theta)
            c1y = 280 - 25 * math.sin(theta)
            
        branch_paths.append(
            f'    <path d="M {x_start_branch} {y_start_branch} Q {c1x:.1f} {c1y:.1f} {x_tip:.1f} {y_tip:.1f}" fill="none" stroke="#4e342e" stroke-width="5.0" stroke-linecap="round" />'
        )
        
        twig_len1 = 45
        twig_len2 = 55
        twig_len3 = 45
        
        theta1 = theta + 0.60
        theta2 = theta
        theta3 = theta - 0.60
        
        xt1 = x_tip + twig_len1 * math.cos(theta1)
        yt1 = y_tip - twig_len1 * math.sin(theta1)
        xt2 = x_tip + twig_len2 * math.cos(theta2)
        yt2 = y_tip - twig_len2 * math.sin(theta2)
        xt3 = x_tip + twig_len3 * math.cos(theta3)
        yt3 = y_tip - twig_len3 * math.sin(theta3)
        
        twig_paths.append(f'    <path d="M {x_tip:.1f} {y_tip:.1f} L {xt1:.1f} {yt1:.1f}" fill="none" stroke="#4e342e" stroke-width="2.2" stroke-linecap="round" />')
        twig_paths.append(f'    <path d="M {x_tip:.1f} {y_tip:.1f} L {xt2:.1f} {yt2:.1f}" fill="none" stroke="#4e342e" stroke-width="2.2" stroke-linecap="round" />')
        twig_paths.append(f'    <path d="M {x_tip:.1f} {y_tip:.1f} L {xt3:.1f} {yt3:.1f}" fill="none" stroke="#4e342e" stroke-width="2.2" stroke-linecap="round" />')
        
        label_x = x_base + 380 * math.cos(theta)
        label_y = 360 - 270 * math.sin(theta)
        
        branch_paths.append(
            f'    <line x1="{x_tip:.1f}" y1="{y_tip:.1f}" x2="{label_x:.1f}" y2="{label_y:.1f}" stroke="#374151" stroke-width="1" stroke-dasharray="3 3" />'
        )
        
        anchor = "middle"
        if label_x < 420:
            anchor = "end"
            label_x -= 5
        elif label_x > 480:
            anchor = "start"
            label_x += 5
            
        month_labels.append(
            f'    <text x="{label_x:.1f}" y="{label_y + 4:.1f}" font-family="\'JetBrains Mono\', \'Fira Code\', monospace" font-size="10.5" fill="#f97316" font-weight="bold" text-anchor="{anchor}">{key}</text>'
        )
        
        for k in range(25):
            twig_idx = k % 3
            if twig_idx == 0:
                x_start, y_start, x_end, y_end, twig_angle = x_tip, y_tip, xt1, yt1, theta1
            elif twig_idx == 1:
                x_start, y_start, x_end, y_end, twig_angle = x_tip, y_tip, xt2, yt2, theta2
            else:
                x_start, y_start, x_end, y_end, twig_angle = x_tip, y_tip, xt3, yt3, theta3
                
            t = 0.2 + (k // 3) * (0.8 / 8)
            if t > 1.0: t = 1.0
            cx = x_start + (x_end - x_start) * t
            cy = y_start + (y_end - y_start) * t
            
            angle_perp = twig_angle + math.pi / 2
            offset_perp = ((k * 13) % 36) - 18
            offset_para = ((k * 19) % 24) - 12
            cx += offset_perp * math.cos(angle_perp) + offset_para * math.cos(twig_angle)
            cy -= offset_perp * math.sin(angle_perp) + offset_para * math.sin(twig_angle)
            
            ambient_leaves.append(
                f'    <rect class="contrib-leaf-bg" x="{cx - 3.75:.2f}" y="{cy - 3.75:.2f}" width="7.5" height="7.5" rx="1.8" fill="#102217" opacity="0.9" />'
            )
            
        month_days = months_data[key]
        N = len(month_days)
        for j, day in enumerate(month_days):
            twig_idx = j % 3
            if twig_idx == 0:
                x_start, y_start, x_end, y_end, twig_angle = x_tip, y_tip, xt1, yt1, theta1
            elif twig_idx == 1:
                x_start, y_start, x_end, y_end, twig_angle = x_tip, y_tip, xt2, yt2, theta2
            else:
                x_start, y_start, x_end, y_end, twig_angle = x_tip, y_tip, xt3, yt3, theta3
                
            t = 0.15 + (j // 3) * (0.8 / max(1, (N // 3)))
            if t > 1.0: t = 1.0
            
            cx = x_start + (x_end - x_start) * t
            cy = y_start + (y_end - y_start) * t
            
            angle_perp = twig_angle + math.pi / 2
            offset_perp = ((j * 17) % 36) - 18
            offset_para = ((j * 23) % 24) - 12
            cx += offset_perp * math.cos(angle_perp) + offset_para * math.cos(twig_angle)
            cy -= offset_perp * math.sin(angle_perp) + offset_para * math.sin(twig_angle)
            
            cnt = day["contributionCount"]
            if cnt == 0:
                color = colors[0]
            elif cnt <= 1:
                color = colors[1]
            elif cnt <= 3:
                color = colors[2]
            elif cnt <= 6:
                color = colors[3]
            else:
                color = colors[4]
                
            is_recent = (recent_day and day["date"] == recent_day["date"])
            leaf_class = "contrib-leaf recent-leaf" if is_recent else "contrib-leaf"
            
            leaf_rects.append(
                f'    <rect class="{leaf_class}" x="{cx - 3.75:.2f}" y="{cy - 3.75:.2f}" width="7.5" height="7.5" rx="1.8" fill="{color}" />'
            )
            
            if is_recent:
                recent_marker = f"""    <!-- Pulse Halo for Most Recent Commit -->
    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="11" fill="none" stroke="#ef4444" stroke-width="1.8">
      <animate attributeName="r" values="6;14;6" dur="1.2s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite" />
    </circle>
    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="2.5" fill="#ef4444" />
    <!-- Floating details bubble -->
    <g transform="translate({cx + 12:.2f}, {cy - 12:.2f})">
      <rect x="0" y="0" width="185" height="18" rx="3" fill="#111827" stroke="#ef4444" stroke-width="1" opacity="0.95" />
      <text x="7" y="12" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#e5e7eb" font-weight="bold">Recent: {day['date']} ({cnt} commits)</text>
    </g>"""

    svg_tree_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600" width="100%" height="auto">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      
      .contrib-tree-card {{
        filter: drop-shadow(0 25px 50px rgba(0, 0, 0, 0.45));
        animation: treeFadeIn 0.8s ease-out;
      }}
      
      .contrib-leaf {{
        transition: transform 0.15s ease, fill 0.15s ease;
        transform-box: fill-box;
        transform-origin: center;
      }}
      
      .contrib-leaf:hover {{
        transform: scale(1.8);
        fill: #38bdf8;
        cursor: pointer;
      }}
      
      @keyframes treeFadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
  </defs>

  <g class="contrib-tree-card">
    <!-- Window Background -->
    <rect x="0" y="0" width="900" height="600" rx="12" fill="#0b0f19" stroke="#1f2937" stroke-width="1.5" />

    <!-- Window Title Bar -->
    <path d="M 0,12 A 12,12 0 0,1 12,0 L 888,0 A 12,12 0 0,1 900,12 L 900,42 L 0,42 Z" fill="#111827" />
    
    <!-- Window Control Buttons (macOS Style) -->
    <circle cx="25" cy="21" r="6" fill="#ff5f56" />
    <circle cx="45" cy="21" r="6" fill="#ffbd2e" />
    <circle cx="65" cy="21" r="6" fill="#27c93f" />

    <!-- Terminal Title -->
    <text x="450" y="25" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="12" fill="#9ca3af" text-anchor="middle" font-weight="bold">
      {username}@macos: ~/contribution-tree
    </text>

    <!-- Title Bar Divider -->
    <line x1="0" y1="42" x2="900" y2="42" stroke="#1f2937" stroke-width="1" />

    <!-- Header Text -->
    <text x="35" y="70" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="13" fill="#34d399" font-weight="bold">
      &gt; git log --graph --date=relative --all --organic-foliage (Past 12 Months)
    </text>

    <!-- Tree elements -->
{chr(10).join(root_paths)}
{chr(10).join(limbs_paths)}
{chr(10).join(branch_paths)}
{chr(10).join(twig_paths)}
{chr(10).join(ambient_leaves)}
{chr(10).join(leaf_rects)}
{chr(10).join(month_labels)}
{recent_marker}

    <!-- Legend -->
    <g transform="translate(680, 560)">
      <text x="0" y="9" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">Less</text>
      <rect x="35" y="0" width="10" height="10" rx="1.5" fill="{colors[0]}" stroke="#1f2937" stroke-width="0.5" />
      <rect x="48" y="0" width="10" height="10" rx="1.5" fill="{colors[1]}" />
      <rect x="61" y="0" width="10" height="10" rx="1.5" fill="{colors[2]}" />
      <rect x="74" y="0" width="10" height="10" rx="1.5" fill="{colors[3]}" />
      <rect x="87" y="0" width="10" height="10" rx="1.5" fill="{colors[4]}" />
      <text x="103" y="9" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">More</text>
    </g>
  </g>
</svg>"""

    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "contribution_tree.svg")
    with open(output_path, "w") as f:
        f.write(svg_tree_template)
    print(f"Successfully generated Contribution Tree SVG at {output_path}!")

if __name__ == "__main__":
    generate_svg()
