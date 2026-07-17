import os
import json
import math
import random
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
    
    # 1. Left Side Retro Game Loop instead of static contribution grid
    game_loop_elements = """  <!-- Left Side Commit Invaders Retro Game Card -->
  <!-- Game Bounding Box -->
  <rect x="40" y="58" width="288" height="428" rx="8" fill="#0b0f19" stroke="#1f2937" stroke-width="1.5" />
  
  <!-- Starry Space Background (Scrolling Dust) -->
  <circle cx="80" cy="70" r="1.2" fill="#4b5563" opacity="0.5">
    <animate attributeName="cy" from="58" to="486" dur="4s" repeatCount="indefinite" />
  </circle>
  <circle cx="150" cy="150" r="1.5" fill="#34d399" opacity="0.3">
    <animate attributeName="cy" from="58" to="486" dur="6s" repeatCount="indefinite" />
  </circle>
  <circle cx="280" cy="90" r="1.2" fill="#4b5563" opacity="0.4">
    <animate attributeName="cy" from="58" to="486" dur="5s" repeatCount="indefinite" />
  </circle>
  <circle cx="210" cy="220" r="1" fill="#9ca3af" opacity="0.6">
    <animate attributeName="cy" from="58" to="486" dur="3.5s" repeatCount="indefinite" />
  </circle>
  <circle cx="110" cy="300" r="1.5" fill="#26a641" opacity="0.2">
    <animate attributeName="cy" from="58" to="486" dur="7s" repeatCount="indefinite" />
  </circle>
  <circle cx="250" cy="350" r="1" fill="#4b5563" opacity="0.5">
    <animate attributeName="cy" from="58" to="486" dur="4.5s" repeatCount="indefinite" />
  </circle>

  <!-- Game Headers & Scoreboard -->
  <text x="184" y="78" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" fill="#374151" font-weight="800" text-anchor="middle" letter-spacing="1.5">COMMIT INVADERS</text>
  
  <!-- Score Labels -->
  <g transform="translate(50, 80)">
    <text x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="8" fill="#4b5563" font-weight="bold">SCORE</text>
    <text x="0" y="14" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" fill="#34d399" font-weight="bold" class="score-0" opacity="1">0000</text>
    <text x="0" y="14" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" fill="#34d399" font-weight="bold" class="score-1" opacity="0">0100</text>
    <text x="0" y="14" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" fill="#34d399" font-weight="bold" class="score-2" opacity="0">0250</text>
    <text x="0" y="14" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" fill="#34d399" font-weight="bold" class="score-3" opacity="0">0450</text>
    <text x="0" y="14" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" fill="#34d399" font-weight="bold" class="score-4" opacity="0">0700</text>
    <text x="0" y="14" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" fill="#34d399" font-weight="bold" class="score-5" opacity="0">1000</text>
  </g>

  <!-- Lives Indicator -->
  <g transform="translate(260, 80)">
    <text x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="8" fill="#4b5563" font-weight="bold" text-anchor="middle">LIVES</text>
    <text x="0" y="14" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10" fill="#ef4444" text-anchor="middle">💚 💚 💚</text>
  </g>

  <!-- Lasers (aligned with timeline) -->
  <!-- Laser 1 -->
  <g transform="translate(184, 0)">
    <rect class="laser-beam laser-1" x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
  </g>
  <!-- Laser 2 -->
  <g transform="translate(80, 0)">
    <rect class="laser-beam laser-2" x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
  </g>
  <!-- Laser 3 -->
  <g transform="translate(280, 0)">
    <rect class="laser-beam laser-3" x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
  </g>
  <!-- Laser 4 -->
  <g transform="translate(130, 0)">
    <rect class="laser-beam laser-4" x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
  </g>
  <!-- Laser 5 -->
  <g transform="translate(230, 0)">
    <rect class="laser-beam laser-5" x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
  </g>

  <!-- Enemies (falling) -->
  <!-- Enemy 1 at x=184 -->
  <g class="enemy-1" transform="translate(0, 0)">
    <g transform="translate(184, 0)">
      <rect x="-13.05" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-3.75" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="5.55" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-22.35" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="-13.05" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="5.55" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="14.85" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="-22.35" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
      <rect x="14.85" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
    </g>
  </g>

  <!-- Enemy 2 at x=80 -->
  <g class="enemy-2" transform="translate(0, 0)">
    <g transform="translate(80, 0)">
      <rect x="-13.05" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="5.55" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="-13.05" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="5.55" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-3.75" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
    </g>
  </g>

  <!-- Enemy 3 at x=280 -->
  <g class="enemy-3" transform="translate(0, 0)">
    <g transform="translate(280, 0)">
      <rect x="-13.05" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="-3.75" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="5.55" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="-22.35" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
      <rect x="14.85" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
      <rect x="-13.05" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="5.55" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
    </g>
  </g>

  <!-- Enemy 4 at x=130 -->
  <g class="enemy-4" transform="translate(0, 0)">
    <g transform="translate(130, 0)">
      <rect x="-13.05" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="5.55" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="-22.35" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="14.85" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-13.05" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
      <rect x="5.55" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
    </g>
  </g>

  <!-- Enemy 5 at x=230 -->
  <g class="enemy-5" transform="translate(0, 0)">
    <g transform="translate(230, 0)">
      <rect x="-3.75" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-13.05" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="5.55" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="-22.35" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="14.85" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
    </g>
  </g>

  <!-- Explosions (triggered at corresponding hit points) -->
  <!-- Explosion 1 (at x=184, y=210) -->
  <g class="exp-1" transform="translate(184, 210)">
    <rect class="particle p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
    <rect class="particle p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
    <rect class="particle p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
    <rect class="particle p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
  </g>
  <!-- Explosion 2 (at x=80, y=210) -->
  <g class="exp-2" transform="translate(80, 210)">
    <rect class="particle p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
    <rect class="particle p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
    <rect class="particle p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#0e4429" />
    <rect class="particle p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
  </g>
  <!-- Explosion 3 (at x=280, y=210) -->
  <g class="exp-3" transform="translate(280, 210)">
    <rect class="particle p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
    <rect class="particle p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#0e4429" />
    <rect class="particle p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
    <rect class="particle p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
  </g>
  <!-- Explosion 4 (at x=130, y=210) -->
  <g class="exp-4" transform="translate(130, 210)">
    <rect class="particle p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
    <rect class="particle p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
    <rect class="particle p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#0e4429" />
    <rect class="particle p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
  </g>
  <!-- Explosion 5 (at x=230, y=210) -->
  <g class="exp-5" transform="translate(230, 210)">
    <rect class="particle p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
    <rect class="particle p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
    <rect class="particle p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
    <rect class="particle p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
  </g>

  <!-- Player Ship (moving) -->
  <g class="player-ship">
    <!-- Center of the ship is at (0, 0), animated via translate in player-move keyframe -->
    <!-- Row 0 (top tip) -->
    <rect x="-3.75" y="-13.05" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#39d353" />
    <!-- Row 1 -->
    <rect x="-13.05" y="-3.75" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#26a641" />
    <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#39d353" />
    <rect x="5.55" y="-3.75" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#26a641" />
    <!-- Row 2 -->
    <rect x="-22.35" y="5.55" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#006d32" />
    <rect x="-13.05" y="5.55" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#26a641" />
    <rect x="-3.75" y="5.55" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#39d353" />
    <rect x="5.55" y="5.55" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#26a641" />
    <rect x="14.85" y="5.55" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#006d32" />
    <!-- Row 3 (wings) -->
    <rect x="-22.35" y="14.85" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#0e4429" />
    <rect x="14.85" y="14.85" width="7.5" height="7.5" rx="1.5" ry="1.5" fill="#0e4429" />
  </g>"""
    svg_elements.append(game_loop_elements)

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

      /* ======================================================== */
      /* Retro Arcade Commit Invaders Game Styles                  */
      /* ======================================================== */
      
      /* Player Spaceship Movement */
      @keyframes player-move {{
        0%, 10% {{ transform: translate(184px, 420px); }}       /* Center */
        15%, 26.6% {{ transform: translate(80px, 420px); }}      /* Left */
        33.3%, 45% {{ transform: translate(280px, 420px); }}     /* Right */
        51.6%, 63.3% {{ transform: translate(130px, 420px); }}   /* Mid-Left */
        70%, 81.6% {{ transform: translate(230px, 420px); }}     /* Mid-Right */
        90%, 100% {{ transform: translate(184px, 420px); }}      /* Back to Center */
      }}
      
      .player-ship {{
        animation: player-move 6s infinite ease-in-out;
        transform-box: fill-box;
        transform-origin: center;
      }}

      /* Laser Shooting Animation */
      @keyframes shoot-laser {{
        0% {{ transform: translateY(410px); opacity: 0; }}
        0.1% {{ transform: translateY(410px); opacity: 1; }}
        3.3% {{ transform: translateY(210px); opacity: 1; }}
        3.4%, 100% {{ transform: translateY(210px); opacity: 0; }}
      }}

      .laser-beam {{
        animation: shoot-laser 6s infinite linear;
        opacity: 0;
        transform-box: fill-box;
        transform-origin: bottom center;
      }}
      .laser-1 {{ animation-delay: 0.2s; }}
      .laser-2 {{ animation-delay: 1.1s; }}
      .laser-3 {{ animation-delay: 2.2s; }}
      .laser-4 {{ animation-delay: 3.3s; }}
      .laser-5 {{ animation-delay: 4.4s; }}

      /* Enemy Falling Animations - Continuous, Staggered Flow */
      @keyframes fall-e1 {{
        0% {{ transform: translateY(160px); opacity: 1; }}
        6.7% {{ transform: translateY(210px); opacity: 1; }}
        6.8% {{ transform: translateY(210px); opacity: 0; }}
        93.2% {{ transform: translateY(110px); opacity: 0; }}
        93.3% {{ transform: translateY(110px); opacity: 1; }}
        100% {{ transform: translateY(160px); opacity: 1; }}
      }}
      @keyframes fall-e2 {{
        0%, 8.2% {{ transform: translateY(110px); opacity: 0; }}
        8.3% {{ transform: translateY(110px); opacity: 1; }}
        21.7% {{ transform: translateY(210px); opacity: 1; }}
        21.8%, 100% {{ transform: translateY(210px); opacity: 0; }}
      }}
      @keyframes fall-e3 {{
        0%, 26.6% {{ transform: translateY(110px); opacity: 0; }}
        26.7% {{ transform: translateY(110px); opacity: 1; }}
        40.0% {{ transform: translateY(210px); opacity: 1; }}
        40.1%, 100% {{ transform: translateY(210px); opacity: 0; }}
      }}
      @keyframes fall-e4 {{
        0%, 44.9% {{ transform: translateY(110px); opacity: 0; }}
        45.0% {{ transform: translateY(110px); opacity: 1; }}
        58.3% {{ transform: translateY(210px); opacity: 1; }}
        58.4%, 100% {{ transform: translateY(210px); opacity: 0; }}
      }}
      @keyframes fall-e5 {{
        0%, 63.2% {{ transform: translateY(110px); opacity: 0; }}
        63.3% {{ transform: translateY(110px); opacity: 1; }}
        76.7% {{ transform: translateY(210px); opacity: 1; }}
        76.8%, 100% {{ transform: translateY(210px); opacity: 0; }}
      }}

      .enemy-1 {{ animation: fall-e1 6s infinite linear; transform-box: fill-box; transform-origin: center; }}
      .enemy-2 {{ animation: fall-e2 6s infinite linear; transform-box: fill-box; transform-origin: center; }}
      .enemy-3 {{ animation: fall-e3 6s infinite linear; transform-box: fill-box; transform-origin: center; }}
      .enemy-4 {{ animation: fall-e4 6s infinite linear; transform-box: fill-box; transform-origin: center; }}
      .enemy-5 {{ animation: fall-e5 6s infinite linear; transform-box: fill-box; transform-origin: center; }}

      /* Explosion Particle Animations */
      @keyframes part-ul {{
        0% {{ transform: translate(0, 0); opacity: 0; }}
        0.1% {{ transform: translate(0, 0); opacity: 1; }}
        5.0% {{ transform: translate(-15px, -15px); opacity: 0; }}
        100% {{ transform: translate(-15px, -15px); opacity: 0; }}
      }}
      @keyframes part-ur {{
        0% {{ transform: translate(0, 0); opacity: 0; }}
        0.1% {{ transform: translate(0, 0); opacity: 1; }}
        5.0% {{ transform: translate(15px, -15px); opacity: 0; }}
        100% {{ transform: translate(15px, -15px); opacity: 0; }}
      }}
      @keyframes part-dl {{
        0% {{ transform: translate(0, 0); opacity: 0; }}
        0.1% {{ transform: translate(0, 0); opacity: 1; }}
        5.0% {{ transform: translate(-15px, 15px); opacity: 0; }}
        100% {{ transform: translate(-15px, 15px); opacity: 0; }}
      }}
      @keyframes part-dr {{
        0% {{ transform: translate(0, 0); opacity: 0; }}
        0.1% {{ transform: translate(0, 0); opacity: 1; }}
        5.0% {{ transform: translate(15px, 15px); opacity: 0; }}
        100% {{ transform: translate(15px, 15px); opacity: 0; }}
      }}

      .particle {{
        animation-duration: 6s;
        animation-iteration-count: infinite;
        animation-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
      }}
      .p-ul {{ animation-name: part-ul; }}
      .p-ur {{ animation-name: part-ur; }}
      .p-dl {{ animation-name: part-dl; }}
      .p-dr {{ animation-name: part-dr; }}

      .exp-1 .particle {{ animation-delay: 0.4s; }}
      .exp-2 .particle {{ animation-delay: 1.3s; }}
      .exp-3 .particle {{ animation-delay: 2.4s; }}
      .exp-4 .particle {{ animation-delay: 3.5s; }}
      .exp-5 .particle {{ animation-delay: 4.6s; }}

      /* Scoreboard Digital Count Up */
      @keyframes score-0 {{ 0%, 6.7% {{ opacity: 1; }} 6.8%, 100% {{ opacity: 0; }} }}
      @keyframes score-1 {{ 0%, 6.7% {{ opacity: 0; }} 6.8%, 21.7% {{ opacity: 1; }} 21.8%, 100% {{ opacity: 0; }} }}
      @keyframes score-2 {{ 0%, 21.7% {{ opacity: 0; }} 21.8%, 40.0% {{ opacity: 1; }} 40.1%, 100% {{ opacity: 0; }} }}
      @keyframes score-3 {{ 0%, 40.0% {{ opacity: 0; }} 40.1%, 58.3% {{ opacity: 1; }} 58.4%, 100% {{ opacity: 0; }} }}
      @keyframes score-4 {{ 0%, 58.3% {{ opacity: 0; }} 58.4%, 76.7% {{ opacity: 1; }} 76.8%, 100% {{ opacity: 0; }} }}
      @keyframes score-5 {{ 0%, 76.7% {{ opacity: 0; }} 76.8%, 100% {{ opacity: 1; }} }}

      .score-0 {{ animation: score-0 6s infinite step-end; }}
      .score-1 {{ animation: score-1 6s infinite step-end; }}
      .score-2 {{ animation: score-2 6s infinite step-end; }}
      .score-3 {{ animation: score-3 6s infinite step-end; }}
      .score-4 {{ animation: score-4 6s infinite step-end; }}
      .score-5 {{ animation: score-5 6s infinite step-end; }}
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

# Default tree leaf weight constants
DEFAULT_LEAF_WEIGHTS = {1: 0.35, 2: 0.30, 3: 0.20, 4: 0.15}
PALETTE = {
    1: "#9be9a8",
    2: "#40c463",
    3: "#30a14e",
    4: "#216e39",
}
SQUARE = 9
GAP = 3
CORNER_RADIUS = 2

def size_params(commits: int):
    if commits < 10:
        depth, base_len, leaf_cap = 3, 60, 40
    elif commits < 50:
        depth, base_len, leaf_cap = 4, 75, 140
    elif commits < 150:
        depth, base_len, leaf_cap = 5, 90, 320
    elif commits < 350:
        depth, base_len, leaf_cap = 6, 100, 550
    elif commits < 700:
        depth, base_len, leaf_cap = 7, 108, 800
    else:
        depth, base_len, leaf_cap = 8, 115, 1100

    leaves_total = max(6, min(int(commits * 0.9), leaf_cap))
    return depth, base_len, leaves_total

def build_branches(max_depth, base_len, seed=0):
    rng = random.Random(seed)
    branches = []   # (x1, y1, x2, y2, depth)
    tips = []       # endpoints of terminal branches -> canopy anchors

    def recurse(x, y, angle, length, depth):
        x2 = x + length * math.cos(angle)
        y2 = y - length * math.sin(angle)
        branches.append((x, y, x2, y2, depth))

        if depth >= max_depth:
            tips.append((x2, y2, depth))
            return

        n_children = 2 if depth < max_depth - 1 else rng.choice([2, 3])
        for i in range(n_children):
            spread = math.radians(rng.uniform(16, 34))
            direction = -1 if i % 2 == 0 else 1
            child_angle = angle + direction * spread + math.radians(rng.uniform(-4, 4))
            child_len = length * rng.uniform(0.68, 0.78)
            recurse(x2, y2, child_angle, child_len, depth + 1)

    recurse(0, 0, math.pi / 2, base_len, 0)
    return branches, tips

def squares_for_branch(x1, y1, x2, y2, depth, max_depth, rng):
    length = math.hypot(x2 - x1, y2 - y1)
    n = max(1, round(length / (SQUARE + GAP)))
    pts = []
    for i in range(n + 1):
        t = i / n if n else 0
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        jitter = rng.uniform(-1.1, 1.1)
        nx, ny = -(y2 - y1), (x2 - x1)
        norm = math.hypot(nx, ny) or 1
        x += (nx / norm) * jitter
        y += (ny / norm) * jitter
        pts.append((x, y))

    shade_level = max(1, min(4, 4 - round((depth / max_depth) * 3)))
    return pts, shade_level

def leaf_cluster(cx, cy, count, radius, rng):
    pts = []
    for _ in range(count):
        r = radius * math.sqrt(rng.random())
        theta = rng.uniform(0, 2 * math.pi)
        x = cx + r * math.cos(theta)
        y = cy - r * math.sin(theta) * 0.85
        pts.append((x, y))
    return pts

def weighted_leaf_level(weights, rng):
    r = rng.random()
    cum = 0.0
    for level, w in weights.items():
        cum += w
        if r <= cum:
            return level
    return 4

def weights_from_days(contribution_days):
    counts = [day["contributionCount"] for day in contribution_days if isinstance(day["contributionCount"], (int, float))]
    nonzero = sorted(c for c in counts if c > 0)
    if not nonzero:
        return DEFAULT_LEAF_WEIGHTS

    def pct(p):
        idx = min(len(nonzero) - 1, int(len(nonzero) * p))
        return nonzero[idx]

    q1, q2, q3 = pct(0.25), pct(0.5), pct(0.75)
    buckets = {1: 0, 2: 0, 3: 0, 4: 0}
    for c in nonzero:
        if c <= q1:
            buckets[1] += 1
        elif c <= q2:
            buckets[2] += 1
        elif c <= q3:
            buckets[3] += 1
        else:
            buckets[4] += 1

    total = sum(buckets.values()) or 1
    return {k: v / total for k, v in buckets.items()}

def generate_tree_svg(stats: dict, username: str):
    print("Generating Contribution Tree SVG...")
    if "contribution_days" not in stats or not stats["contribution_days"]:
        print("No contribution days found in stats! Skipping generation.")
        return

    # Calculate stats
    total_commits = stats["contributions"]
    
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

    # Calculate tree parameters
    seed = 7
    width = 900
    height = 680
    rng = random.Random(seed)
    
    max_depth, base_len, leaves_total = size_params(total_commits)
    branches, tips = build_branches(max_depth, base_len, seed=seed)
    
    ground_y = height - 80
    origin_x = width / 2
    
    def to_canvas(x, y):
        return origin_x + x, ground_y + y
        
    rects = []
    max_branch_depth = max_depth
    
    # Branches
    for (x1, y1, x2, y2, depth) in branches:
        cx1, cy1 = to_canvas(x1, y1)
        cx2, cy2 = to_canvas(x2, y2)
        pts, shade = squares_for_branch(cx1, cy1, cx2, cy2, depth, max_branch_depth, rng)
        base_delay = depth * 0.12
        for i, (bx, by) in enumerate(pts):
            delay = base_delay + i * 0.01
            rects.append((bx, by, PALETTE[shade], round(delay, 3)))
            
    # Leaves
    weights = weights_from_days(stats["contribution_days"])
    n_tips = max(1, len(tips))
    per_tip = max(2, leaves_total // n_tips)
    leaf_delay_base = max_depth * 0.12 + 0.15
    
    for (tx, ty, depth) in tips:
        cx, cy = to_canvas(tx, ty)
        radius = 22 + max_depth * 2.2
        cluster = leaf_cluster(cx, cy, per_tip, radius, rng)
        for i, (lx, ly) in enumerate(cluster):
            level = weighted_leaf_level(weights, rng)
            delay = leaf_delay_base + rng.uniform(0, 0.9)
            rects.append((lx, ly, PALETTE[level], round(delay, 3)))
            
    # Grass
    grass_rects = []
    grass_span = width * 0.9
    n_grass = int(grass_span / (SQUARE + GAP))
    for i in range(n_grass):
        gx = (width - grass_span) / 2 + i * (SQUARE + GAP) + rng.uniform(-2, 2)
        gy = ground_y + rng.uniform(6, 26)
        level = rng.choice([1, 1, 2, 2, 3])
        delay = leaf_delay_base + 0.9 + rng.uniform(0, 0.6)
        grass_rects.append((gx, gy, PALETTE[level], round(delay, 3)))
        
    all_rects = rects + grass_rects
    
    svg_rects = []
    for (x, y, color, delay) in all_rects:
        svg_rects.append(
            f'<rect class="cell" x="{x - SQUARE/2:.1f}" y="{y - SQUARE/2:.1f}" '
            f'width="{SQUARE}" height="{SQUARE}" rx="{CORNER_RADIUS}" ry="{CORNER_RADIUS}" '
            f'fill="{color}" style="animation-delay:{delay}s" />'
        )

    # Compile the final SVG inside the premium terminal window template
    svg_tree_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 680" width="100%" height="auto">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      
      .contrib-graph-card {{
        filter: drop-shadow(0 25px 50px rgba(0, 0, 0, 0.45));
        animation: graphFadeIn 0.8s ease-out;
      }}
      
      .cell {{
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
        animation: grow 0.5s ease forwards;
      }}
      
      @keyframes grow {{
        from {{ opacity: 0; transform: scale(0.2); }}
        to   {{ opacity: 1; transform: scale(1); }}
      }}
      
      @keyframes graphFadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
  </defs>

  <g class="contrib-graph-card">
    <!-- Window Background -->
    <rect x="0" y="0" width="900" height="680" rx="12" fill="#0b0f19" stroke="#1f2937" stroke-width="1.5" />

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
      &gt; git log --graph --date=relative --all --fractal-tree (Past 12 Months)
    </text>

    <!-- Tree rendering -->
    <g>
      {chr(10).join(svg_rects)}
    </g>

    <!-- Bottom Stats and Info Panel -->
    <!-- Left Stats Panel -->
    <g transform="translate(45, 110)">
      <text x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">Longest Streak</text>
      <text x="0" y="22" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="20" fill="#34d399" font-weight="bold">{longest_streak} days</text>
      <text x="0" y="38" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#9ca3af">{longest_streak_str}</text>
      
      <text x="0" y="65" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">Current Streak</text>
      <text x="0" y="87" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="20" fill="#34d399" font-weight="bold">{current_streak} days</text>
      <text x="0" y="103" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#9ca3af">{current_streak_str}</text>
    </g>

    <!-- Right Stats Panel -->
    <g transform="translate(620, 110)">
      <text x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" fill="#4b5563" font-weight="bold">1 Year Total</text>
      <text x="0" y="24" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="22" fill="#34d399" font-weight="bold">{total_commits:,} commits</text>
      <text x="0" y="40" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9" fill="#9ca3af">Past 365 Days</text>
    </g>

    <!-- Bottom Counter Label -->
    <text x="450" y="{height - 20}" text-anchor="middle" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="12" fill="#9ca3af" opacity="0.85">{total_commits} commits grown 🌱</text>
  </g>
</svg>"""

    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "contribution_tree.svg")
    with open(output_path, "w") as f: f.write(svg_tree_template)
    print(f"Successfully generated Contribution Tree SVG at {output_path}!")

if __name__ == "__main__":
    generate_svg()
