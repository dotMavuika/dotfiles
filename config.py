# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from libqtile import hook
import os
import subprocess
from libqtile import widget
from libqtile import bar, layout, qtile, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
import time  # Añadir este para las animaciones
from libqtile.backend.x11.window import Window as XWindow  # Para las animaciones
from qtile_extras import widget as qtile_widgets  # Importar widgets personalizados


mod = "mod4"
terminal = "alacritty"

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    
    # Move windows between left/right columns or move up/down in current stack.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    
    # Mover ventanas con flechas (alternativa)
    Key([mod, "shift"], "Left", lazy.layout.shuffle_left(), desc="Mover ventana a la izquierda"),
    Key([mod, "shift"], "Right", lazy.layout.shuffle_right(), desc="Mover ventana a la derecha"),
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down(), desc="Mover ventana abajo"),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up(), desc="Mover ventana arriba"),
    
    # Grow windows
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    
    # Ajustar tamaño con flechas (alternativa)
    Key([mod, "control"], "Left", lazy.layout.grow_left(), desc="Crecer ventana a la izquierda"),
    Key([mod, "control"], "Right", lazy.layout.grow_right(), desc="Crecer ventana a la derecha"),
    Key([mod, "control"], "Down", lazy.layout.grow_down(), desc="Crecer ventana abajo"),
    Key([mod, "control"], "Up", lazy.layout.grow_up(), desc="Crecer ventana arriba"),
    
    # Reset window sizes
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    
    # Split and terminal
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(), desc="Toggle between split and unsplit sides of stack"),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    
    # Layout and window controls
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen on the focused window"),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "shift"], "f", lazy.window.toggle_floating(), desc="Toggle floating"), # Atajo alternativo
    
    # System controls
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    
    # Atajos personalizados
    Key([mod, "shift"], "t", lazy.spawn("cambiar_idioma_teclado")),
    Key([], "Print", lazy.spawn("screenshot"), desc="Take a screenshot"),
    Key([mod, "shift"], "s", lazy.spawn("sss"), desc="Take a part screenshot"),
    Key([mod], "m", lazy.window.toggle_minimize(), desc="Minimizar ventana activa"),
]

# Add key bindings to switch VTs in Wayland
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )

groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend([
        Key([mod], i.name, lazy.group[i.name].toscreen(),
            desc="Switch to group {}".format(i.name)),
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name, switch_group=True),
            desc="Switch to & move focused window to group {}".format(i.name)),
    ])


# Colores y temas básicos
colors = {
    "border_focus": "#1e90ff",
    "border_normal": "#4c566a",
    "border_focus_stack": "#ff79c6"
}

# Configuración de animaciones
@hook.subscribe.client_new
def slight_delay(window):
    """Añade un pequeño retraso para efecto visual"""
    time.sleep(0.05)

@hook.subscribe.client_focus
def float_to_front(window):
    """Trae las ventanas flotantes al frente al enfocarse"""
    if window.floating:
        window.bring_to_front()

# Modifica los bordes al enfocar una ventana
@hook.subscribe.client_focus
def _client_focus(window):
    for win in window.group.windows:
        if hasattr(win, '_border_normal'):
            if win is window:
                win.set_border(colors["border_focus"])
            else:
                win.set_border(colors["border_normal"])

layouts = [
    # Layout principal: Columnas con separación
#    layout.Columns(
#        border_width=2,
#        margin=8,
 #        border_focus=colors["border_focus"],
 #        border_normal=colors["border_normal"],
  #       border_focus_stack=colors["border_focus_stack"],
    #     border_on_single=True,  # Mantener bordes con una sola ventana
    #     insert_position=1,
     #    border_radius=8,
      #   margin_on_single=True,  # Mantener márgenes con una sola ventana
    # ),
    
    # Diseño Monadtall
    layout.MonadTall(
        border_width=2,
        margin=8,
        border_focus=colors["border_focus"],
        border_normal=colors["border_normal"],
        border_on_single=True,
        ratio=0.6,
        min_ratio=0.30,
        max_ratio=0.70,
        border_radius=8,
        margin_on_single=True,
    ),
    
    # Diseño MonadWide
    layout.MonadWide(
        border_width=2,
        margin=8,
        border_focus=colors["border_focus"],
        border_normal=colors["border_normal"],
        border_on_single=True,
        ratio=0.6,
        border_radius=8,
        margin_on_single=True,
    ),
    
    # Matrix
    layout.Matrix(
        border_width=2,
        margin=8,
        border_focus=colors["border_focus"],
        border_normal=colors["border_normal"],
        border_on_single=True,
        columns=2,
        border_radius=8,
        margin_on_single=True,
    ),
    
    # RatioTile
    layout.RatioTile(
        border_width=2,
        margin=8,
        border_focus=colors["border_focus"],
        border_normal=colors["border_normal"],
        border_on_single=True,
        border_radius=8,
        margin_on_single=True,
    ),
    
    # Floating
    layout.Floating(
        border_width=3,
        margin=8,
        border_focus=colors["border_focus"],
        border_normal=colors["border_normal"],
        border_on_single=True,
        border_radius=8,
        margin_on_single=True,
    ),
    
    layout.Max(
        border_width=2,
        margin=8,
        border_on_single=True,
        margin_on_single=True,
    ),
]

# Configuración de ventanas flotantes
floating_layout = layout.Floating(
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class='confirmreset'),
        Match(wm_class='makebranch'),
        Match(wm_class='maketag'),
        Match(wm_class='ssh-askpass'),
        Match(title='branchdialog'),
        Match(title='pinentry'),
        Match(wm_class='pavucontrol'),
        Match(wm_class='gnome-calculator'),
    ],
    border_width=3,
    margin=8,
    border_focus=colors["border_focus"],
    border_normal=colors["border_normal"],
    border_on_single=True,
    border_radius=8,
    margin_on_single=True,
)

# Función para animar el cambio de tamaño de ventanas
def animate_resize(win, x, y, w, h, steps=10):
    if not isinstance(win, XWindow):
        return
    
    current = win.get_geometry()
    x_step = (x - current.x) / steps
    y_step = (y - current.y) / steps
    w_step = (w - current.width) / steps
    h_step = (h - current.height) / steps
    
    for i in range(steps):
        new_x = int(current.x + x_step * (i + 1))
        new_y = int(current.y + y_step * (i + 1))
        new_w = int(current.width + w_step * (i + 1))
        new_h = int(current.height + h_step * (i + 1))
        win.place(new_x, new_y, new_w, new_h, 0, None)
        time.sleep(0.01)

# Hook para animar el cambio de tamaño
@hook.subscribe.client_managed
def _client_animated_resize(window):
    if not window.floating:
        return
    
    geo = window.get_geometry()
    animate_resize(window, geo.x, geo.y, geo.width, geo.height)

# Colores para barra de tareas

colors=[
    ["#97D59B", "#141417"],  # ACTIVE WORKSPACES 0
    ["#6A6A6A", "#6A6A6A"],  # INACTIVE WORKSPACES 1
    ["#384149", "#384149"],  # background lighter 2
    ["#FF8080", "#FF8080"],  # red 3
    ["#97D59B", "#97D59B"],  # green 4
    ["#FFFE80", "#FFFE80"],  # yellow 5
    ["#80D1FF", "#80D1FF"],  # blue 6
    ["#C780FF", "#C780FF"],  # magenta 7
    ["#80FFE4", "#80FFE4"],  # cyan 8
    ["#D5D5D5", "#D5D5D5"],  # white 9
    ["#4c566a", "#4c566a"],  # grey 10
    ["#d08770", "#d08770"],  # orange 11
    ["#8fbcbb", "#8fbcbb"],  # super cyan12
    ["#181E23", "#0E131A"],  # super blue 13
    ["#181e23", "#181e23"],  # super dark background 14
]

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.Sep(),
           widget.TextBox("Furina", name="user_text"),
           widget.Sep(),
                widget.Prompt(),
                widget.Spacer(),
                widget.Sep(),
                widget.GroupBox(),
                widget.Sep(),
                widget.Spacer(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#2E2E2E", "#2E2E2E"),
                    },
                    
                ),
                widget.TextBox("", name="default"),
                widget.TextBox("", foreground="#d75f5f"),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                widget.Sep(),
                widget.Battery(format='{char} {percent:1.0%}', charge_char='', discharge_char='', full_char='', unknown_char='', empty_char='', show_short_text=False),
                widget.Sep(),
                widget.TextBox(
    text="🔊",
    fontsize=16,
    mouse_callbacks={'Button4': lambda: qtile.cmd_spawn("pactl set-sink-volume @DEFAULT_SINK@ +5%"),
                     'Button5': lambda: qtile.cmd_spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%")},
    name="volume_icon"
),
widget.GenPollText(
    func=lambda: subprocess.check_output("pamixer --get-volume", shell=True).decode("utf-8").strip() + "%",
    update_interval=1
),

                widget.Sep(),
                widget.Systray(),
                widget.Sep(),
                widget.Clock(format="%Y-%m-%d %a %I:%M %p"), # Botón de apagado
                widget.Sep(),
                widget.CurrentLayoutIcon(),
            ],
            24,
            margin=[5, 5, 0, 5],  # Márgenes: [arriba, derecha, abajo, izquierda]
            opacity=0.9,    # Opcional, para darle un aspecto "flotante"
        

            # border_width=[1, 1, 1, 1],  # Draw top and bottom borders
            # border_color=["2E2E2E", "2E2E2E", "2E2E2E", "2E2E2E"]  # Borders are magenta
        ),
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = False

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~/.config/qtile/set_wallpaper.sh')
    subprocess.Popen([home])

@hook.subscribe.startup_once
def autostart():
    subprocess.Popen(['picom'])

