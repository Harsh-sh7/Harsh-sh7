import os
import json
from datetime import datetime
from avatar_to_ascii import download_avatar, image_to_color_ascii
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
    
    print("Generating ASCII avatar...")
    avatar_img = download_avatar(username)
    # Target size: width=60 columns, aspect_ratio=0.5. Height will be around 30 rows.
    ascii_grid = image_to_color_ascii(avatar_img, width=60, aspect_ratio_factor=0.5)
    
    # Pad/truncate ASCII grid to exactly 34 rows and 60 columns
    target_rows = 34
    target_cols = 60
    if len(ascii_grid) < target_rows:
        padding_row = [(" ", "#0b0f19")] * target_cols
        ascii_grid += [padding_row] * (target_rows - len(ascii_grid))
    else:
        ascii_grid = ascii_grid[:target_rows]

    # Calculate typing animation widths
    typed_text = f"{username}@macos:~"
    char_width = 7.8  # Approx width of a monospace char at font-size 13
    text_width = len(typed_text) * char_width
    cursor_start_x = 360
    cursor_end_x = 360 + text_width + 4

    print("Compiling SVG content...")
    # Header buttons & macOS terminal style
    svg_elements = []
    
    # 1. Left Side ASCII portrait (colorized)
    ascii_svg_lines = []
    for y_idx, row in enumerate(ascii_grid):
        dy = "11.5" if y_idx > 0 else "0"
        row_svg = [f'<tspan x="35" dy="{dy}">']
        
        current_color = None
        current_text = []
        for char, color in row:
            char_esc = char.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if color == current_color:
                current_text.append(char_esc)
            else:
                if current_color is not None:
                    text_str = "".join(current_text)
                    row_svg.append(f'<tspan fill="{current_color}">{text_str}</tspan>')
                current_color = color
                current_text = [char_esc]
        if current_text:
            text_str = "".join(current_text)
            row_svg.append(f'<tspan fill="{current_color}">{text_str}</tspan>')
            
        row_svg.append('</tspan>')
        ascii_svg_lines.append("".join(row_svg))
        
    ascii_text_block = f"""  <text x="35" y="98" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="7.5" font-weight="bold" xml:space="preserve">
    {"".join(ascii_svg_lines)}
  </text>"""
    svg_elements.append(ascii_text_block)

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

if __name__ == "__main__":
    generate_svg()
