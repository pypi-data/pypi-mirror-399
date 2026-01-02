import time
import shutil
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.live import Live

try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

console = Console()


def _clear_terminal() -> None:
    """
    Clear the terminal COMPLETELY - no trace left.
    Uses ANSI escape sequences and system commands.
    """
    import os
    import sys
    
    # ANSI escape sequences for complete clear
    sys.stdout.write('\033[H\033[2J\033[3J')
    sys.stdout.flush()
    
    # System clear command
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear -x 2>/dev/null || clear')
    
    # Rich console clear
    console.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE (Professional Blue/Cyan/Red Hacker Theme)
# ═══════════════════════════════════════════════════════════════════════════════
STYLE_BG = "rgb(10,10,10)"              # Deep black background
STYLE_WHITE = "rgb(255,255,255)"        # Pure white
STYLE_RED = "rgb(255,50,50)"            # Vibrant red - accent color
STYLE_RED_BRIGHT = "rgb(255,100,100)"   # Bright red
STYLE_BLUE_DARK = "rgb(0,50,150)"       # Dark blue - top accent
STYLE_BLUE = "rgb(0,100,255)"           # Electric blue - middle
STYLE_CYAN = "rgb(0,240,240)"           # Electric cyan - bottom accent
STYLE_CYAN_BRIGHT = "rgb(0,255,255)"    # Bright cyan


# ═══════════════════════════════════════════════════════════════════════════════
# SKULL LOGO (Recreation of banner.txt - proper size)
# ═══════════════════════════════════════════════════════════════════════════════

# Devil skull with horns - recreated from banner.txt at proper size
SKULL_LOGO = r"""
           ..    ..........        ..               
            .',:;.',''..,:cllllllc;'.    .,'. ....          
            ''lXO,.,,:lx0XWMMMMMMWNKko;..''cxl.....         
           ..,OMWKxdkXMMMMMMMMMMMMMMMMN0ddONMWl..           
            .'OMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNc..           
              ,OWMMMMMMMMMMMMMMMMMMMMMMMMMMMXl'.            
           ....'oXMMMWWWWWWMMMMMMWWWWWWWMMWO;,;'.           
           .'',..lXOccccccclKMMNxcccccccdXNc.',,'..         
             ...'dK:.     ,.dMM0,      ','dO;.,'...          
                .':l,. ..',;cccc:.  ..',lc..'''.            
               .'.oNKdlllodc''..,oollloONO,....             
           ......;xkkkXMMWx,,. ..cXMWMMMMMO'.               
           ........;lxKMMWx,'..''cKMMMMN0xc;,.              
               ...,;;oXMMMWKOOkO0NMMMWOc;,''                
               .',;;,.cXMNk0MMMMXx00dl..,.                  
                 ......cKXclWMMMk;xO;.''..                  
                       .;c,,oxkx:'cl:;.                     
                       .......''''..                  
"""

# Smaller version for small terminals
SKULL_SMALL = r"""
                ..        ..........        ..               
            .',:;.',''..,:cllllllc;'.    .,'. ....          
            ''lXO,.,,:lx0XWMMMMMMWNKko;..''cxl.....         
           ..,OMWKxdkXMMMMMMMMMMMMMMMMN0ddONMWl..           
            .'OMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNc..           
              ,OWMMMMMMMMMMMMMMMMMMMMMMMMMMMXl'.            
           ....'oXMMMWWWWWWMMMMMMWWWWWWWMMWO;,;'.           
           .'',..lXOccccccclKMMNxcccccccdXNc.',,'..         
             ...'dK:      ,.dMM0,     ','dO;.,'...          
                .':l,....',;cccc:. ...',lc..'''.                           .'.oNKdlllodc''..,oollloONO,....             
           ......;xkkkXMMWx,,. ..cXMWMMMMMO'.               
           ........;lxKMMWx,'..''cKMMMMN0xc;,.              
               ...,;;oXMMMWKOOkO0NMMMWOc;,''                
               .',;;,.cXMNk0MMMMXx00dl..,.                  
                 ......cKXclWMMMk;xO;.''..                  
                       .;c,,oxkx:'cl:;.                     
                        .......''''..     
"""


def get_terminal_size() -> tuple:
    """Get current terminal size."""
    size = shutil.get_terminal_size((80, 24))
    return max(size.columns, 60), max(size.lines, 20)


def skull_logo_animation(duration: float = 2.0) -> None:
    """
    Display centered skull logo with fade-in animation.
    Professional intro animation before main splash.
    
    Args:
        duration: Animation duration in seconds
    """
    _clear_terminal()
    
    term_width, term_height = get_terminal_size()
    
    # Get appropriate skull based on terminal size
    if term_width >= 70 and term_height >= 25:
        skull = SKULL_LOGO
    else:
        skull = SKULL_SMALL
    
    skull_lines = skull.strip().split('\n')
    skull_height = len(skull_lines)
    
    # Calculate vertical centering
    top_padding = max(0, (term_height - skull_height) // 2)
    
    # Calculate horizontal centering based on WIDEST line (not per-line)
    max_line_width = max(len(line) for line in skull_lines)
    left_padding = max(0, (term_width - max_line_width) // 2)
    
    # Fade-in animation
    start_time = time.time()
    
    with Live(console=console, refresh_per_second=20, screen=True) as live:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
            
            # Calculate opacity (0.0 to 1.0)
            progress = min(elapsed / duration, 1.0)
            
            output = Text()
            
            # Top padding
            output.append("\n" * top_padding)
            
            # Render skull with gradient and fade
            total_lines = len(skull_lines)
            for i, line in enumerate(skull_lines):
                line_progress = i / max(total_lines - 1, 1)
                
                # Use SAME padding for ALL lines (based on widest line)
                # This keeps the skull aligned as a block
                
                # Apply SMOOTH BLUE → CYAN gradient (professional)
                # Interpolate between Blue and Cyan based on position
                # Top: Deep Blue (0,50,150)
                # Middle: Electric Blue (0,100,255)
                # Bottom: Bright Cyan (0,255,255)
                
                if line_progress < 0.5:
                    # Top half: Deep Blue → Electric Blue
                    progress_in_section = line_progress / 0.5
                    # Interpolate RGB
                    r = 0
                    g = int(50 + (100 - 50) * progress_in_section)
                    b = int(150 + (255 - 150) * progress_in_section)
                    color = f"rgb({r},{g},{b})"
                else:
                    # Bottom half: Electric Blue → Bright Cyan
                    progress_in_section = (line_progress - 0.5) / 0.5
                    # Interpolate RGB
                    r = 0
                    g = int(100 + (255 - 100) * progress_in_section)
                    b = 255
                    color = f"rgb({r},{g},{b})"
                
                # Apply fade effect based on progress
                if progress < 0.3:
                    # Early fade - dim
                    style = f"dim {color}"
                elif progress < 0.7:
                    # Mid fade - normal
                    style = color
                else:
                    # Final - bold
                    style = f"bold {color}"
                
                output.append(" " * left_padding + line + "\n", style=style)
            
            live.update(output)
            time.sleep(0.05)
    
    # Hold final frame briefly
    time.sleep(0.3)
    _clear_terminal()


def get_terminal_size() -> tuple:
    """Get current terminal size."""
    size = shutil.get_terminal_size((80, 24))
    return max(size.columns, 60), max(size.lines, 20)


def get_skull_logo() -> str:
    """Get appropriate skull logo based on terminal size."""
    term_width, term_height = get_terminal_size()
    
    if term_width >= 70 and term_height >= 25:
        return SKULL_LOGO
    else:
        return SKULL_SMALL


def render_skull_text(term_width: int) -> Text:
    """Render skull logo as Rich Text with colors."""
    skull = get_skull_logo()
    lines = skull.strip().split('\n')
    
    result = Text()
    total = len(lines)
    
    for i, line in enumerate(lines):
        progress = i / max(total - 1, 1)
        
        # Center the line
        padding = max(0, (term_width - len(line)) // 2)
        centered_line = " " * padding + line
        
        # Apply gradient: cyan (top) -> white (middle) -> cyan (bottom)
        if progress < 0.3:
            result.append(centered_line + "\n", style=f"bold {STYLE_BLUE_DARK}")
        elif progress < 0.7:
            result.append(centered_line + "\n", style=f"bold {STYLE_WHITE}")
        else:
            result.append(centered_line + "\n", style=f"bold {STYLE_CYAN}")
    
    return result


def render_kr_cli_banner(term_width: int) -> Text:
    """Render KR-CLI text with high-quality custom ASCII."""
    from .display import BANNER_ASCII
    
    # Use the shared banner constant
    # Strip leading newlines but preserve internal relative layout
    lines = [line for line in BANNER_ASCII.split("\n") if line.strip()]
    
    # Calculate dimensions
    max_line_width = max(len(line) for line in lines) if lines else 0
    padding = max(0, (term_width - max_line_width) // 2)
    
    result = Text()
    total_lines = len(lines)
    
    for i, line in enumerate(lines):
        # Apply the SAME global padding to every line to keep them aligned
        centered = " " * padding + line
        
        # Apply strict 3-color gradient
        # Top = Blue
        # Middle = Electric Blue
        # Bottom = Cyan
        if i < total_lines / 3:
            result.append(centered + "\n", style=f"bold {STYLE_BLUE_DARK}")
        elif i < 2 * total_lines / 3:
            result.append(centered + "\n", style=f"bold {STYLE_BLUE}")
        else:
            result.append(centered + "\n", style=f"bold {STYLE_CYAN}")
    
    return result


def create_loading_display(progress_pct: float, term_width: int, status: str) -> Text:
    """Create loading bar display."""
    bar_width = min(50, term_width - 20)
    filled = int(bar_width * progress_pct)
    empty = bar_width - filled
    
    # Build bar
    bar = "█" * filled + "▒" * empty
    pct = f"{int(progress_pct * 100):3d}%"
    
    result = Text()
    
    # Center the loading bar
    line = f"  ⟨ {bar} ⟩  {pct}"
    padding = max(0, (term_width - len(line)) // 2)
    
    result.append(" " * padding)
    result.append("  ⟨ ", style=STYLE_CYAN)
    result.append("█" * filled, style=f"bold {STYLE_BLUE}")
    result.append("▒" * empty, style="dim white")
    result.append(" ⟩  ", style=STYLE_CYAN)
    result.append(pct, style=f"bold {STYLE_WHITE}")
    result.append("\n\n")
    
    # Status text
    status_padding = max(0, (term_width - len(status)) // 2)
    result.append(" " * status_padding)
    result.append(status, style=f"italic {STYLE_CYAN}")
    
    return result


def animated_splash(skip_animation: bool = False, duration: float = 5.0) -> None:
    """
    Enhanced animated splash screen with skull logo intro.
    
    Sequence:
    1. Skull logo fade-in animation (2 seconds)
    2. Banner + loading bar animation
    3. Program starts
    
    Args:
        skip_animation: If True, shows static version
        duration: Duration of loading animation in seconds (default 5)
    """
    # Clear screen first
    _clear_terminal()
    
    if skip_animation:
        _show_static_splash()
        return
    
    # Phase 1: SKULL LOGO INTRO (2 seconds)
    skull_logo_animation(duration=2.0)
    
    # Phase 2: BANNER + LOADING BAR
    # Get terminal size
    term_width, term_height = get_terminal_size()
    
    # Import KR-CLI banner
    from .display import BANNER_ASCII
    kr_lines = [line for line in BANNER_ASCII.split('\n') if line.strip()]
    
    # Subtitle elements
    sub_line = "═" * 50
    title_text = "⚡  DOMINION v3.5 (5.3.45)  ⚡"
    desc_text = "Advanced AI Security Operations"
    
    # Calculate dimensions for centering
    max_banner_width = max(len(line) for line in kr_lines)
    subtitle_width = len(sub_line)
    max_content_width = max(max_banner_width, subtitle_width)
    
    banner_height = len(kr_lines)
    subtitle_height = 4  # Two separator lines + title + description
    loading_height = 4   # Loading bar section
    total_content_height = banner_height + 1 + subtitle_height + 1 + loading_height
    
    # Vertical centering
    top_padding = max(0, (term_height - total_content_height) // 2)
    
    # Horizontal padding
    banner_padding = max(0, (term_width - max_banner_width) // 2)
    subtitle_padding = max(0, (term_width - subtitle_width) // 2)
    
    # Animated loading
    loading_start = time.time()
    loading_duration = duration - 2.0  # Subtract skull animation time
    
    with Live(console=console, refresh_per_second=30, screen=True) as live:
        while True:
            elapsed = time.time() - loading_start
            if elapsed >= loading_duration:
                break
            
            progress = min(elapsed / loading_duration, 1.0)
            
            output = Text()
            
            # Top padding
            output.append("\n" * top_padding)
            
            # === KR-CLI BANNER (with gradient) ===
            kr_total = len(kr_lines)
            for i, line in enumerate(kr_lines):
                line_progress = i / max(kr_total - 1, 1)
                
                # Blue → Cyan gradient
                if line_progress < 0.33:
                    style = STYLE_BLUE_DARK
                elif line_progress < 0.66:
                    style = STYLE_BLUE
                else:
                    style = STYLE_CYAN
                
                output.append(" " * banner_padding + line + "\n", style=f"bold {style}")
            
            output.append("\n")
            
            # === SUBTITLE SECTION ===
            output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
            
            # Title (centered within subtitle)
            title_pad = (subtitle_width - len(title_text)) // 2
            output.append(" " * subtitle_padding, style=STYLE_BLUE)
            output.append(title_text, style=f"bold {STYLE_BLUE}")
            output.append("\n")
            
            # Description
            desc_pad = (subtitle_width - len(desc_text)) // 2
            output.append(" " * (subtitle_padding + desc_pad))
            output.append(desc_text + "\n", style=f"italic {STYLE_CYAN}")
            
            output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
            output.append("\n")
            
            # === LOADING BAR (Responsive) ===
            bar_width = min(40, term_width - 10)
            bar_padding = max(0, (term_width - bar_width) // 2)
            
            filled = int(bar_width * progress)
            empty = bar_width - filled
            
            output.append(" " * bar_padding)
            output.append("║ ", style=STYLE_CYAN)
            output.append("█" * filled, style=f"bold {STYLE_BLUE}")
            output.append("░" * empty, style=f"dim {STYLE_CYAN}")
            output.append(" ║\n", style=STYLE_CYAN)
            
            # Progress percentage
            pct_text = f"{int(progress * 100)}%"
            pct_padding = max(0, (term_width - len(pct_text)) // 2)
            output.append(" " * pct_padding)
            output.append(pct_text, style=f"bold {STYLE_CYAN}")
            output.append("\n\n")
            
            # Status message (various stages)
            if progress < 0.2:
                status_msg = "⚡ Initializing Systems..."
                status_color = STYLE_BLUE_DARK
            elif progress < 0.4:
                status_msg = "🔐 Loading Security Modules..."
                status_color = STYLE_BLUE
            elif progress < 0.6:
                status_msg = "🤖 Activating AI Engine..."
                status_color = STYLE_CYAN
            elif progress < 0.8:
                status_msg = "🔧 Configuring Tools..."
                status_color = STYLE_BLUE
            else:
                status_msg = "✨ Finalizing Setup..."
                status_color = STYLE_CYAN
            
            status_padding = max(0, (term_width - len(status_msg)) // 2)
            output.append(" " * status_padding)
            output.append(status_msg, style=f"bold {status_color}")
            
            live.update(output)
            time.sleep(0.03)
        
        # Show completion briefly
        output = Text()
        output.append("\n" * top_padding)
        
        # Final banner
        for i, line in enumerate(kr_lines):
            line_progress = i / max(kr_total - 1, 1)
            if line_progress < 0.33:
                style = STYLE_BLUE_DARK
            elif line_progress < 0.66:
                style = STYLE_BLUE
            else:
                style = STYLE_CYAN
            output.append(" " * banner_padding + line + "\n", style=f"bold {style}")
        
        output.append("\n")
        output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
        title_pad = (subtitle_width - len(title_text)) // 2
        output.append(" " * subtitle_padding)
        output.append(title_text + "\n", style=f"bold {STYLE_BLUE}")
        desc_pad = (subtitle_width - len(desc_text)) // 2
        output.append(" " * (subtitle_padding + desc_pad))
        output.append(desc_text + "\n", style=f"italic {STYLE_CYAN}")
        output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
        output.append("\n")
        
        # Full bar
        output.append(" " * bar_padding)
        output.append("║ ", style=STYLE_CYAN)
        output.append("█" * bar_width, style=f"bold {STYLE_BLUE}")
        output.append(" ║\n", style=STYLE_CYAN)
        
        output.append(" " * ((term_width - 4) // 2))
        output.append("100%\n\n", style=f"bold {STYLE_CYAN}")
        
        output.append(" " * ((term_width - 12) // 2))
        output.append("✅ Ready!\n", style=f"bold {STYLE_CYAN}")
        
        live.update(output)
        time.sleep(0.5)
    
    _clear_terminal()

def _show_static_splash() -> None:
    """Show static splash without animation - fully centered."""
    _clear_terminal()
    
    term_width, term_height = get_terminal_size()
    
    # Get logo
    skull = get_skull_logo()
    skull_lines = skull.strip().split('\n')
    
    # IMPORT RAW BANNER
    from .display import BANNER_ASCII
    kr_lines = [line for line in BANNER_ASCII.split('\n') if line.strip()]
    
    # Render all elements
    output = Text()
    
    # Calculate vertical centering
    skull_height = len(skull_lines)
    kr_height = len(kr_lines)
    subtitle_height = 4
    total_height = skull_height + 2 + kr_height + 2 + subtitle_height
    top_padding = max(0, (term_height - total_height) // 2)
    
    output.append("\n" * top_padding)
    
    # Skull logo (centered with gradient)
    # Calculate skull padding once
    max_skull_width = max(len(line) for line in skull_lines) if skull_lines else 0
    skull_padding = max(0, (term_width - max_skull_width) // 2)
    
    for i, line in enumerate(skull_lines):
        progress = i / max(len(skull_lines) - 1, 1)
        
        if progress < 0.3:
            style = STYLE_BLUE_DARK
        elif progress < 0.7:
            style = STYLE_WHITE
        else:
            style = STYLE_CYAN
        
        output.append(" " * skull_padding + line + "\n", style=style)
    
    output.append("\n")
    
    # KR-CLI (Block centered logic fixed)
    # Calculate banner padding once
    max_kr_width = max(len(line) for line in kr_lines) if kr_lines else 0
    kr_padding = max(0, (term_width - max_kr_width) // 2)

    for i, line in enumerate(kr_lines):
        line_progress = i / max(len(kr_lines) - 1, 1)
        if line_progress < 0.33:
            style = f"bold {STYLE_BLUE_DARK}"
        elif line_progress < 0.66:
            style = f"bold {STYLE_BLUE}"
        else:
            style = f"bold {STYLE_CYAN}"
            
        output.append(" " * kr_padding + line + "\n", style=style)

    output.append("\n")
    
    # Subtitle
    sub_line = "═" * 50
    title_text = "⚡  DOMINION v3.5 (5.3.45)  ⚡"
    desc_text = "Advanced AI Security Operations"
    
    sub_padding = max(0, (term_width - len(sub_line)) // 2)
    title_padding = max(0, (term_width - len(title_text)) // 2)
    desc_padding = max(0, (term_width - len(desc_text)) // 2)
    
    output.append(" " * sub_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
    output.append(" " * title_padding, style="")
    output.append("⚡  ", style=STYLE_BLUE)
    output.append("DOMINION", style="bold white")
    output.append(" v3.5  ⚡\n", style=STYLE_BLUE)
    output.append(" " * desc_padding + desc_text + "\n", style=f"italic {STYLE_CYAN}")
    output.append(" " * sub_padding + sub_line, style=STYLE_BLUE_DARK)
    
    console.print(output)
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# THEME UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_style_red() -> str:
    return STYLE_BLUE_DARK

def get_style_orange() -> str:
    return STYLE_BLUE

def get_style_cyan() -> str:
    return STYLE_CYAN

def get_style_pink() -> str:
    return STYLE_PINK


# Test
if __name__ == "__main__":
    animated_splash(duration=5.0)
