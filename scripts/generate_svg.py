#!/usr/bin/env python3
import os
import re
import json
import math
import random
from datetime import datetime
from avatar_to_ascii import download_avatar, image_to_contrib_grid
from github_stats import GitHubStatsFetcher

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

def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def format_stats_line(y_pos, label, value, is_recent_act=False, prefix_len=14, start_x=22):
    """
    Formats a single monospace line with dotted alignment.
    """
    dots_count = prefix_len - len(label) - 2
    if dots_count < 1:
        dots_count = 1
    dots = "." * dots_count
    
    max_val_len = 60 - prefix_len
    display_val = str(value)
    if len(display_val) > max_val_len:
        display_val = display_val[:max_val_len - 3] + "..."
        
    escaped_val = display_val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    escaped_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    lbl_class = "lbl-act" if is_recent_act else "lbl-os"
    val_class = "lbl-act-val" if is_recent_act else "lbl-val"
    
    return f"""  <text x="{start_x}" y="{y_pos}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="14.5" font-weight="600">
    <tspan class="{lbl_class}">{escaped_label}</tspan>
    <tspan class="lbl-dots">: {dots} </tspan>
    <tspan class="{val_class}">{escaped_val}</tspan>
  </text>"""

def format_stats_section_header(y_pos, title, start_x=22):
    """
    Formats a terminal section divider, e.g., - Contact -----------------
    """
    title_text = f"─ {title} "
    remaining_len = 54 - len(title_text)
    if remaining_len < 1:
        remaining_len = 1
    line = "─" * remaining_len
    return f"""  <text x="{start_x}" y="{y_pos}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="14" font-weight="700">
    <tspan class="section-text">{title_text}</tspan>
    <tspan class="section-line">{line}</tspan>
  </text>"""

def generate_stats_svg(stats: dict, config: dict):
    print("Generating Standalone Stats SVG...")
    
    username = stats["name"]
    typed_text = f"{username}@macos:~"
    char_width = 9.0
    text_width = len(typed_text) * char_width
    cursor_start_x = 22
    cursor_end_x = 22 + text_width + 4
    
    svg_elements = []
    
    # Dynamic positions
    OS_y = 52
    Host_y = OS_y + 15
    Location_y = Host_y + 15
    Editor_y = Location_y + 15
    Focus_y = Editor_y + 15
    
    y_tech_header = Focus_y + 19
    Languages_y = y_tech_header + 15
    Frameworks_y = Languages_y + 15
    Database_y = Frameworks_y + 15
    
    y_stats_header = Database_y + 19
    Repos_y = y_stats_header + 15
    Followers_y = Repos_y + 15
    Activity_y = Followers_y + 15
    TopLang_y = Activity_y + 15
    bar_y = TopLang_y + 8
    
    y_act_header = bar_y + 19 if stats["top_languages"] else TopLang_y + 19
    Act1_y = y_act_header + 15
    Act2_y = Act1_y + 15
    
    # System Info
    svg_elements.append(format_stats_line(OS_y, "OS", config["os"]))
    svg_elements.append(format_stats_line(Host_y, "Host", "MacBook Pro"))
    svg_elements.append(format_stats_line(Location_y, "Location", config["location"]))
    svg_elements.append(format_stats_line(Editor_y, "Editor", config["editor"]))
    svg_elements.append(format_stats_line(Focus_y, "Focus", config["current_focus"]))
    
    # Tech Profile
    svg_elements.append(format_stats_section_header(y_tech_header, "Technical Profile"))
    svg_elements.append(format_stats_line(Languages_y, "Languages", ", ".join(config["languages"])))
    svg_elements.append(format_stats_line(Frameworks_y, "Frameworks", ", ".join(config["frameworks"])))
    svg_elements.append(format_stats_line(Database_y, "Database", ", ".join(config["database"])))
    
    # GitHub Stats
    svg_elements.append(format_stats_section_header(y_stats_header, "GitHub Stats"))
    svg_elements.append(format_stats_line(Repos_y, "Repos", f"{stats['public_repos']} public repos"))
    svg_elements.append(format_stats_line(Followers_y, "Followers", f"{stats['followers']} | Following: {stats['following']}"))
    
    contrib_str = f"{stats['contributions']} contributions"
    if stats["longest_streak"] > 0:
        contrib_str += f" | Streak: {stats['longest_streak']}d"
    svg_elements.append(format_stats_line(Activity_y, "Activity", contrib_str))
    
    # Top Languages Progress Bar
    if stats["top_languages"]:
        lang_names = [lang["name"] for lang in stats["top_languages"][:3]]
        lang_display = ", ".join(lang_names)
        svg_elements.append(format_stats_line(TopLang_y, "Top Lang", lang_display))
        
        progress_bar_g = ['  <!-- Progress Bar -->']
        progress_bar_g.append(f'  <rect class="progress-bg" x="145" y="{bar_y}" width="240" height="6" rx="3" />')
        current_x = 145
        for lang in stats["top_languages"][:4]:
            width = (lang["percentage"] / 100.0) * 240
            color = lang["color"]
            progress_bar_g.append(f'  <rect x="{current_x}" y="{bar_y}" width="{width:.1f}" height="6" rx="2" fill="{color}" />')
            current_x += width
        svg_elements.append("\n".join(progress_bar_g))
        
    # Recent Activity
    svg_elements.append(format_stats_section_header(y_act_header, "Recent Activity"))
    act_ys = [Act1_y, Act2_y]
    for idx, act in enumerate(stats["recent_activity"][:2]):
        svg_elements.append(format_stats_line(act_ys[idx], f"Act {idx+1}", act, is_recent_act=True))
        
    # Timestamp
    y_bottom = Act2_y + 18
    svg_elements.append(f"""  <!-- Bottom Timestamp -->
  <text x="22" y="{y_bottom}" class="timestamp-text" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" font-weight="bold">
    Last Updated: {stats['last_updated']} (auto-updated every 12h)
  </text>""")

    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 360" width="100%" height="auto">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      
      .terminal-card {{
        animation: fadeIn 0.8s ease-out;
      }}
      
      @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}

      /* Theme Colors */
      .bg-rect {{
        fill: #0b0f19;
        stroke: #1f2937;
      }}
      .lbl-os {{ fill: #f97316; }}
      .lbl-dots {{ fill: #4b5563; }}
      .lbl-val {{ fill: #38bdf8; }}
      .header-name {{ fill: #34d399; }}
      .header-host {{ fill: #9ca3af; }}
      .header-cursor {{ fill: #38bdf8; }}
      .section-text {{ fill: #9ca3af; }}
      .section-line {{ fill: #1f2937; }}
      .lbl-act {{ fill: #60a5fa; }}
      .lbl-act-val {{ fill: #e5e7eb; }}
      .progress-bg {{ fill: #1f2937; }}
      .timestamp-text {{ fill: #4b5563; }}

      @media (prefers-color-scheme: light) {{
        .bg-rect {{
          fill: #f9fafb;
          stroke: #d1d5db;
        }}
        .lbl-os {{ fill: #ea580c; }}
        .lbl-dots {{ fill: #9ca3af; }}
        .lbl-val {{ fill: #0284c7; }}
        .header-name {{ fill: #059669; }}
        .header-host {{ fill: #4b5563; }}
        .header-cursor {{ fill: #0284c7; }}
        .section-text {{ fill: #4b5563; }}
        .section-line {{ fill: #e5e7eb; }}
        .lbl-act {{ fill: #2563eb; }}
        .lbl-act-val {{ fill: #111827; }}
        .progress-bg {{ fill: #e5e7eb; }}
        .timestamp-text {{ fill: #9ca3af; }}
      }}
    </style>
  </defs>

  <g class="terminal-card">
    <!-- Window Background -->
    <rect class="bg-rect" x="8" y="8" width="524" height="344" rx="10" stroke-width="1.5" />

    <!-- Typing Header -->
    <g>
      <text x="22" y="34" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="14.5" font-weight="bold">
        <tspan class="header-name">{username}</tspan>
        <tspan class="header-host">@macos:~</tspan>
      </text>
    </g>
    
    <!-- Blinking Cursor -->
    <rect class="header-cursor" x="{cursor_end_x}" y="20" width="8" height="16">
      <animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite" />
    </rect>

{chr(10).join(svg_elements)}
  </g>
</svg>"""

    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "terminal.svg")
    with open(output_path, "w") as f:
        f.write(svg_template)
    print(f"Successfully generated standalone Stats SVG at {output_path}!")

def generate_game_svg():
    print("Generating Standalone Game SVG...")
    
    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 230 360" width="100%" height="auto">
  <defs>
    <style>
      .game-card {{
        animation: fadeIn 0.8s ease-out;
      }}
      
      @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}

      /* Player Spaceship Movement (X=115, 55, 175, 85, 145) */
      @keyframes player-move {{
        0%, 10% {{ transform: translate(115px, 290px); }}        /* Center */
        15%, 26.6% {{ transform: translate(55px, 290px); }}       /* Left */
        33.3%, 45% {{ transform: translate(175px, 290px); }}      /* Right */
        51.6%, 63.3% {{ transform: translate(85px, 290px); }}     /* Mid-Left */
        70%, 81.6% {{ transform: translate(145px, 290px); }}      /* Mid-Right */
        90%, 100% {{ transform: translate(115px, 290px); }}       /* Back to Center */
      }}
      
      .player-ship {{
        animation: player-move 6s infinite ease-in-out;
        transform-origin: center;
      }}

      /* Falling Invaders Animations */
      @keyframes fall-alien-1 {{
        0% {{ transform: translate(115px, 55px); opacity: 1; }}
        9.5% {{ transform: translate(115px, 140px); opacity: 1; }}
        10%, 95% {{ transform: translate(115px, 140px); opacity: 0; }}
        100% {{ transform: translate(115px, 55px); opacity: 1; }}
      }}
      @keyframes fall-alien-2 {{
        0%, 15% {{ transform: translate(55px, 55px); opacity: 0; }}
        16.6% {{ transform: translate(55px, 55px); opacity: 1; }}
        29.5% {{ transform: translate(55px, 160px); opacity: 1; }}
        30%, 100% {{ transform: translate(55px, 160px); opacity: 0; }}
      }}
      @keyframes fall-alien-3 {{
        0%, 31% {{ transform: translate(175px, 55px); opacity: 0; }}
        33.3% {{ transform: translate(175px, 55px); opacity: 1; }}
        44.5% {{ transform: translate(175px, 140px); opacity: 1; }}
        45%, 100% {{ transform: translate(175px, 140px); opacity: 0; }}
      }}
      @keyframes fall-alien-4 {{
        0%, 48% {{ transform: translate(85px, 55px); opacity: 0; }}
        50.0% {{ transform: translate(85px, 55px); opacity: 1; }}
        62.5% {{ transform: translate(85px, 160px); opacity: 1; }}
        63%, 100% {{ transform: translate(85px, 160px); opacity: 0; }}
      }}
      @keyframes fall-alien-5 {{
        0%, 65% {{ transform: translate(145px, 55px); opacity: 0; }}
        66.6% {{ transform: translate(145px, 55px); opacity: 1; }}
        79.5% {{ transform: translate(145px, 140px); opacity: 1; }}
        80%, 100% {{ transform: translate(145px, 140px); opacity: 0; }}
      }}

      .enemy-1 {{ animation: fall-alien-1 6s infinite linear; }}
      .enemy-2 {{ animation: fall-alien-2 6s infinite linear; }}
      .enemy-3 {{ animation: fall-alien-3 6s infinite linear; }}
      .enemy-4 {{ animation: fall-alien-4 6s infinite linear; }}
      .enemy-5 {{ animation: fall-alien-5 6s infinite linear; }}

      /* Projectile Lasers Fired by Player */
      @keyframes laser-1 {{
        0%, 5% {{ transform: translate(115px, 280px); opacity: 0; }}
        5.1% {{ transform: translate(115px, 280px); opacity: 1; }}
        9.5% {{ transform: translate(115px, 140px); opacity: 1; }}
        9.6%, 100% {{ opacity: 0; }}
      }}
      
      @keyframes laser-2 {{
        0%, 20% {{ transform: translate(55px, 280px); opacity: 0; }}
        20.1% {{ transform: translate(55px, 280px); opacity: 1; }}
        29.5% {{ transform: translate(55px, 160px); opacity: 1; }}
        29.6%, 100% {{ opacity: 0; }}
      }}

      @keyframes laser-3 {{
        0%, 37% {{ transform: translate(175px, 280px); opacity: 0; }}
        37.1% {{ transform: translate(175px, 280px); opacity: 1; }}
        44.5% {{ transform: translate(175px, 140px); opacity: 1; }}
        44.6%, 100% {{ opacity: 0; }}
      }}

      @keyframes laser-4 {{
        0%, 55% {{ transform: translate(85px, 280px); opacity: 0; }}
        55.1% {{ transform: translate(85px, 280px); opacity: 1; }}
        62.5% {{ transform: translate(85px, 160px); opacity: 1; }}
        62.6%, 100% {{ opacity: 0; }}
      }}

      @keyframes laser-5 {{
        0%, 72% {{ transform: translate(145px, 280px); opacity: 0; }}
        72.1% {{ transform: translate(145px, 280px); opacity: 1; }}
        79.5% {{ transform: translate(145px, 140px); opacity: 1; }}
        79.6%, 100% {{ opacity: 0; }}
      }}

      .laser-1 {{ animation: laser-1 6s infinite linear; }}
      .laser-2 {{ animation: laser-2 6s infinite linear; }}
      .laser-3 {{ animation: laser-3 6s infinite linear; }}
      .laser-4 {{ animation: laser-4 6s infinite linear; }}
      .laser-5 {{ animation: laser-5 6s infinite linear; }}

      /* Explosion Particle Animations */
      @keyframes part-ul {{ 0% {{ transform: translate(0, 0); opacity: 1; }} 100% {{ transform: translate(-14px, -14px); opacity: 0; }} }}
      @keyframes part-ur {{ 0% {{ transform: translate(0, 0); opacity: 1; }} 100% {{ transform: translate(14px, -14px); opacity: 0; }} }}
      @keyframes part-dl {{ 0% {{ transform: translate(0, 0); opacity: 1; }} 100% {{ transform: translate(-14px, 14px); opacity: 0; }} }}
      @keyframes part-dr {{ 0% {{ transform: translate(0, 0); opacity: 1; }} 100% {{ transform: translate(14px, 14px); opacity: 0; }} }}

      .p-ul {{ animation: part-ul 0.4s ease-out forwards; }}
      .p-ur {{ animation: part-ur 0.4s ease-out forwards; }}
      .p-dl {{ animation: part-dl 0.4s ease-out forwards; }}
      .p-dr {{ animation: part-dr 0.4s ease-out forwards; }}

      @keyframes exp-burst-1 {{ 0%, 9.5% {{ opacity: 0; }} 9.6%, 14% {{ opacity: 1; }} 14.1%, 100% {{ opacity: 0; }} }}
      @keyframes exp-burst-2 {{ 0%, 29.5% {{ opacity: 0; }} 29.6%, 34% {{ opacity: 1; }} 34.1%, 100% {{ opacity: 0; }} }}
      @keyframes exp-burst-3 {{ 0%, 44.5% {{ opacity: 0; }} 44.6%, 49% {{ opacity: 1; }} 49.1%, 100% {{ opacity: 0; }} }}
      @keyframes exp-burst-4 {{ 0%, 62.5% {{ opacity: 0; }} 62.6%, 67% {{ opacity: 1; }} 67.1%, 100% {{ opacity: 0; }} }}
      @keyframes exp-burst-5 {{ 0%, 79.5% {{ opacity: 0; }} 79.6%, 84% {{ opacity: 1; }} 84.1%, 100% {{ opacity: 0; }} }}

      .exp-1 {{ animation: exp-burst-1 6s infinite; }}
      .exp-2 {{ animation: exp-burst-2 6s infinite; }}
      .exp-3 {{ animation: exp-burst-3 6s infinite; }}
      .exp-4 {{ animation: exp-burst-4 6s infinite; }}
      .exp-5 {{ animation: exp-burst-5 6s infinite; }}

      /* Scoreboard Digital Count Up */
      @keyframes score-0 {{ 0%, 9.5% {{ opacity: 1; }} 9.6%, 100% {{ opacity: 0; }} }}
      @keyframes score-1 {{ 0%, 9.5% {{ opacity: 0; }} 9.6%, 29.5% {{ opacity: 1; }} 29.6%, 100% {{ opacity: 0; }} }}
      @keyframes score-2 {{ 0%, 29.5% {{ opacity: 0; }} 29.6%, 44.5% {{ opacity: 1; }} 44.6%, 100% {{ opacity: 0; }} }}
      @keyframes score-3 {{ 0%, 44.5% {{ opacity: 0; }} 44.6%, 62.5% {{ opacity: 1; }} 62.6%, 100% {{ opacity: 0; }} }}
      @keyframes score-4 {{ 0%, 62.5% {{ opacity: 0; }} 62.6%, 79.5% {{ opacity: 1; }} 79.6%, 100% {{ opacity: 0; }} }}
      @keyframes score-5 {{ 0%, 79.5% {{ opacity: 0; }} 79.6%, 100% {{ opacity: 1; }} }}

      .score-0 {{ animation: score-0 6s infinite step-end; }}
      .score-1 {{ animation: score-1 6s infinite step-end; }}
      .score-2 {{ animation: score-2 6s infinite step-end; }}
      .score-3 {{ animation: score-3 6s infinite step-end; }}
      .score-4 {{ animation: score-4 6s infinite step-end; }}
      .score-5 {{ animation: score-5 6s infinite step-end; }}

      /* Theme Colors */
      .bg-rect {{
        fill: #0b0f19;
        stroke: #1f2937;
      }}
      .game-title {{
        fill: #374151;
      }}
      .score-label, .lives-label {{
        fill: #4b5563;
      }}
      .score-val {{
        fill: #34d399;
      }}
      .lives-val {{
        fill: #ef4444;
      }}
      .space-star {{
        fill: #4b5563;
        opacity: 0.5;
      }}

      @media (prefers-color-scheme: light) {{
        .bg-rect {{
          fill: #f9fafb;
          stroke: #d1d5db;
        }}
        .game-title {{
          fill: #9ca3af;
        }}
        .score-label, .lives-label {{
          fill: #9ca3af;
        }}
        .score-val {{
          fill: #059669;
        }}
        .lives-val {{
          fill: #ef4444;
        }}
        .space-star {{
          fill: #d1d5db;
          opacity: 0.8;
        }}
      }}
    </style>
  </defs>

  <g class="game-card">
    <!-- Game Window Background -->
    <rect class="bg-rect" x="8" y="8" width="214" height="344" rx="10" stroke-width="1.5" />
    
    <!-- Starry Space Background -->
    <circle class="space-star" cx="40" cy="50" r="1.2">
      <animate attributeName="cy" from="10" to="350" dur="4s" repeatCount="indefinite" />
    </circle>
    <circle class="space-star" cx="70" cy="120" r="1.5">
      <animate attributeName="cy" from="10" to="310" dur="6s" repeatCount="indefinite" />
    </circle>
    <circle class="space-star" cx="160" cy="70" r="1.2">
      <animate attributeName="cy" from="10" to="310" dur="5s" repeatCount="indefinite" />
    </circle>
    <circle class="space-star" cx="100" cy="180" r="1">
      <animate attributeName="cy" from="10" to="310" dur="3.5s" repeatCount="indefinite" />
    </circle>
    <circle class="space-star" cx="50" cy="220" r="1.5">
      <animate attributeName="cy" from="10" to="310" dur="7s" repeatCount="indefinite" />
    </circle>
    <circle class="space-star" cx="130" cy="250" r="1">
      <animate attributeName="cy" from="10" to="310" dur="4.5s" repeatCount="indefinite" />
    </circle>

    <!-- Game Headers and Scoreboard -->
    <text class="game-title" x="115" y="28" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="10" font-weight="800" text-anchor="middle" letter-spacing="1">COMMIT INVADERS</text>
    
    <!-- Score Labels -->
    <g transform="translate(22, 22)">
      <text class="score-label" x="0" y="8" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="7.5" font-weight="bold">SCORE</text>
      <text x="0" y="20" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="11" font-weight="bold" class="score-val score-0" opacity="1">0000</text>
      <text x="0" y="20" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="11" font-weight="bold" class="score-val score-1" opacity="0">0100</text>
      <text x="0" y="20" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="11" font-weight="bold" class="score-val score-2" opacity="0">0250</text>
      <text x="0" y="20" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="11" font-weight="bold" class="score-val score-3" opacity="0">0450</text>
      <text x="0" y="20" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="11" font-weight="bold" class="score-val score-4" opacity="0">0700</text>
      <text x="0" y="20" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="11" font-weight="bold" class="score-val score-5" opacity="0">1000</text>
    </g>

    <!-- Lives Indicator -->
    <g transform="translate(208, 22)">
      <text class="lives-label" x="0" y="8" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="7.5" font-weight="bold" text-anchor="end">LIVES</text>
      <text class="lives-val" x="0" y="20" font-family="ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Monaco, Consolas, 'Fira Code', 'JetBrains Mono', monospace" font-size="9.5" text-anchor="end">💚 💚 💚</text>
    </g>

    <line x1="16" y1="48" x2="214" y2="48" stroke="#1f2937" stroke-dasharray="3 3" />

    <!-- Lasers -->
    <g class="laser-1">
      <rect x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
    </g>
    <g class="laser-2">
      <rect x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
    </g>
    <g class="laser-3">
      <rect x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
    </g>
    <g class="laser-4">
      <rect x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
    </g>
    <g class="laser-5">
      <rect x="-1" y="0" width="2" height="12" fill="#38bdf8" rx="1" />
    </g>

    <!-- Falling Enemies -->
    <g class="enemy-1">
      <g>
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

    <g class="enemy-2">
      <g>
        <rect x="-13.05" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
        <rect x="5.55" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
        <rect x="-13.05" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
        <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
        <rect x="5.55" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
        <rect x="-3.75" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      </g>
    </g>

    <g class="enemy-3">
      <g>
        <rect x="-13.05" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
        <rect x="-3.75" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
        <rect x="5.55" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
        <rect x="-22.35" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
        <rect x="14.85" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
        <rect x="-13.05" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
        <rect x="5.55" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      </g>
    </g>

    <g class="enemy-4">
      <g>
        <rect x="-13.05" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
        <rect x="5.55" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
        <rect x="-22.35" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
        <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
        <rect x="14.85" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
        <rect x="-13.05" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
        <rect x="5.55" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
      </g>
    </g>

    <g class="enemy-5">
      <g>
        <rect x="-3.75" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
        <rect x="-13.05" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
        <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
        <rect x="5.55" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
        <rect x="-22.35" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
        <rect x="14.85" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      </g>
    </g>

    <!-- Explosions -->
    <g class="exp-1" transform="translate(115, 140)">
      <rect class="p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
      <rect class="p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
      <rect class="p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
      <rect class="p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
    </g>
    <g class="exp-2" transform="translate(55, 160)">
      <rect class="p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
      <rect class="p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
      <rect class="p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#0e4429" />
      <rect class="p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
    </g>
    <g class="exp-3" transform="translate(175, 140)">
      <rect class="p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
      <rect class="p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#0e4429" />
      <rect class="p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
      <rect class="p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
    </g>
    <g class="exp-4" transform="translate(85, 160)">
      <rect class="p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
      <rect class="p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
      <rect class="p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#0e4429" />
      <rect class="p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
    </g>
    <g class="exp-5" transform="translate(145, 140)">
      <rect class="p-ul" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
      <rect class="p-ur" x="-2" y="-2" width="4" height="4" rx="1" fill="#39d353" />
      <rect class="p-dl" x="-2" y="-2" width="4" height="4" rx="1" fill="#006d32" />
      <rect class="p-dr" x="-2" y="-2" width="4" height="4" rx="1" fill="#26a641" />
    </g>

    <!-- Player Ship -->
    <g class="player-ship">
      <rect x="-3.75" y="-13.05" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="-13.05" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-3.75" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="5.55" y="-3.75" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-22.35" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="-13.05" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="-3.75" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#39d353" />
      <rect x="5.55" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#26a641" />
      <rect x="14.85" y="5.55" width="7.5" height="7.5" rx="1.5" fill="#006d32" />
      <rect x="-22.35" y="14.85" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
      <rect x="14.85" y="14.85" width="7.5" height="7.5" rx="1.5" fill="#0e4429" />
    </g>
  </g>
</svg>"""

    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "game.svg")
    with open(output_path, "w") as f:
        f.write(svg_template)
    print(f"Successfully generated standalone Game SVG at {output_path}!")

def compute_streaks_for_days(contribution_days):
    longest_streak = 0
    current_streak = 0
    temp_streak = 0
    longest_start = None
    longest_end = None
    temp_start = None
    
    for day in contribution_days:
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
            
    for day in reversed(contribution_days):
        if day["contributionCount"] > 0:
            current_streak += 1
        else:
            break
            
    longest_streak_str = ""
    if longest_streak > 0 and longest_start and longest_end:
        ls_start = datetime.strptime(longest_start, "%Y-%m-%d").strftime("%b %d")
        ls_end = datetime.strptime(longest_end, "%Y-%m-%d").strftime("%b %d")
        longest_streak_str = f"{ls_start} - {ls_end}"
        
    return longest_streak, current_streak, longest_streak_str

def size_params(commits: int):
    if commits < 10:
        depth, base_len, leaf_cap = 3, 50, 40
    elif commits < 50:
        depth, base_len, leaf_cap = 4, 65, 140
    elif commits < 150:
        depth, base_len, leaf_cap = 5, 80, 320
    elif commits < 350:
        depth, base_len, leaf_cap = 6, 90, 550
    elif commits < 700:
        depth, base_len, leaf_cap = 7, 98, 800
    else:
        depth, base_len, leaf_cap = 8, 105, 1100

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
    print("Generating Standalone Contribution Tree SVG...")
    if "yearly_contributions" not in stats or not stats["yearly_contributions"]:
        print("No yearly contributions found in stats! Skipping tree generation.")
        return
        
    yearly_data = stats["yearly_contributions"]
    key = "overall"
    data = yearly_data[key]
    
    width = 900
    height = 500
    ground_y = height - 60
    origin_x = width / 2
    seed = 7
    
    def to_canvas(x, y):
        return origin_x + x, ground_y + y

    commits = data["contributions"]
    days = data["contribution_days"]
    
    # Calculate streaks
    longest, current, streak_str = compute_streaks_for_days(days)
    
    # Build tree elements
    rng = random.Random(seed)
    max_depth, base_len, leaves_total = size_params(commits)
    branches, tips = build_branches(max_depth, base_len, seed=seed)
    
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
    weights = weights_from_days(days)
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
    grass_span = width * 0.85
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
        
    # Compile standalone SVG
    # Compile standalone SVG
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 500" width="100%" height="auto">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      
      .tree-card {{
        animation: cardFadeIn 0.8s ease-out;
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
      
      @keyframes cardFadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}

      /* Theme Colors */
      .bg-rect {{
        fill: #0b0f19;
        stroke: #1f2937;
      }}
      .stats-label {{
        fill: #4b5563;
      }}
      .stats-val {{
        fill: #34d399;
      }}
      .stats-sub {{
        fill: #9ca3af;
      }}
      .commits-grown {{
        fill: #9ca3af;
      }}

      @media (prefers-color-scheme: light) {{
        .bg-rect {{
          fill: #f9fafb;
          stroke: #d1d5db;
        }}
        .stats-label {{
          fill: #9ca3af;
        }}
        .stats-val {{
          fill: #059669;
        }}
        .stats-sub {{
          fill: #4b5563;
        }}
        .commits-grown {{
          fill: #4b5563;
        }}
      }}
    </style>
  </defs>

  <g class="tree-card">
    <!-- Background -->
    <rect class="bg-rect" x="10" y="10" width="880" height="480" rx="12" stroke-width="1.5" />

    <!-- Left Stats Panel -->
    <g transform="translate(45, 60)">
      <text class="stats-label" x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" font-weight="bold">Longest Streak</text>
      <text class="stats-val" x="0" y="20" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="18" font-weight="bold">{longest} days</text>
      <text class="stats-sub" x="0" y="34" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9">{streak_str if streak_str else 'N/A'}</text>
      
      <text class="stats-label" x="0" y="60" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" font-weight="bold">Current Streak</text>
      <text class="stats-val" x="0" y="80" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="18" font-weight="bold">{current} days</text>
    </g>

    <!-- Right Stats Panel -->
    <g transform="translate(670, 60)">
      <text class="stats-label" x="0" y="0" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="10.5" font-weight="bold">All-Time Total</text>
      <text class="stats-val" x="0" y="20" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="18" font-weight="bold">{commits:,} commits</text>
      <text class="stats-sub" x="0" y="34" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="9">Contribution Period</text>
    </g>

    <!-- Tree and Grass rendering -->
    <g>
      {''.join(svg_rects)}
    </g>

    <text class="commits-grown" x="450" y="{height - 35}" text-anchor="middle" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="12" opacity="0.85">{commits} commits grown 🌱</text>
  </g>
</svg>"""

    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "contribution_tree.svg")
    with open(output_path, "w") as f:
        f.write(svg_content)
    print(f"Successfully generated overall Contribution Tree SVG at {output_path}!")

    update_readme_with_trees(["overall"])

def update_readme_with_trees(targets):
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if not os.path.exists(readme_path):
        print(f"README.md not found at {readme_path}. Skipping README tree update.")
        return
        
    with open(readme_path, "r") as f:
        content = f.read()
        
    start_placeholder = "<!-- START_CONTRIBUTION_TREE -->"
    end_placeholder = "<!-- END_CONTRIBUTION_TREE -->"
    
    if start_placeholder not in content or end_placeholder not in content:
        print("Contribution tree placeholders not found in README.md. Skipping update.")
        return
        
    # Just render the single Overall contribution tree card
    markup = f"""<p align="center" style="margin: 10px 0 0 0;">
  <img src="assets/contribution_tree.svg?v=6" alt="GitHub Contribution Tree" width="100%" style="width: 100%; max-width: 100%; height: auto;">
</p>"""
    
    # Replace content between placeholders
    new_content = re.sub(
        f"{re.escape(start_placeholder)}.*?{re.escape(end_placeholder)}",
        f"{start_placeholder}\n{markup}\n{end_placeholder}",
        content,
        flags=re.DOTALL
    )
    
    with open(readme_path, "w") as f:
        f.write(new_content)
    print("Successfully updated README.md with the single overall contribution tree SVG!")

def generate_retro_badges():
    print("Generating retro CLI social badges...")
    badges = {
        "linkedin": ("[ LINKEDIN ]", "#38bdf8"),
        "email": ("[ EMAIL ]", "#f97316"),
        "portfolio": ("[ PORTFOLIO ]", "#34d399")
    }
    
    for name, (label, color) in badges.items():
        light_color = "#0284c7" if name == "linkedin" else ("#ea580c" if name == "email" else "#059669")
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

    @media (prefers-color-scheme: light) {{
      .badge-rect {{
        fill: #f9fafb;
        stroke: #d1d5db;
      }}
      .badge-rect:hover {{
        fill: #f3f4f6;
        stroke: {light_color};
      }}
      .badge-text {{
        fill: {light_color};
      }}
      .badge-rect:hover + .badge-text, .badge-text:hover {{
        fill: #111827;
      }}
    }}
  </style>
  <rect class="badge-rect" x="1.5" y="1.5" width="127" height="25" rx="4" />
  <text class="badge-text" x="65" y="14">{label}</text>
</svg>"""
        output_path = os.path.join(os.path.dirname(__file__), "..", "assets", f"{name}_badge.svg")
        with open(output_path, "w") as f:
            f.write(svg_content)
    print("Generated retro social badges successfully!")

def generate_svg():
    print("Loading configurations...")
    config = load_config()
    username = config["github_username"]
    
    print(f"Fetching GitHub stats for {username}...")
    stats_fetcher = GitHubStatsFetcher(username)
    stats = stats_fetcher.fetch_all_stats()
    
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "assets"), exist_ok=True)
    
    # Generate standalone components
    generate_stats_svg(stats, config)
    generate_game_svg()
    generate_tree_svg(stats, username)
    generate_retro_badges()

if __name__ == "__main__":
    generate_svg()
