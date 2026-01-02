# gfxcanvas

**Advanced Python Graphics and Game Engine**

[![PyPI version](https://badge.fury.io/py/gfxcanvas.svg)](https://badge.fury.io/py/gfxcanvas)
[![Python Version](https://img.shields.io/pypi/pyversions/gfxcanvas.svg)](https://pypi.org/project/gfxcanvas/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

gfxcanvas is a powerful, feature-rich graphics and game development library built on top of Tkinter. It provides an intuitive API for creating 2D/3D graphics, animations, physics simulations, and interactive games.

## ✨ Features

- 🎨 **2D Graphics** - Shapes, text, sprites, and custom drawing
- 🎮 **Game Engine** - Entity system, collision detection, state machines
- ⚡ **Physics Engine** - Dynamics, forces, gravity, and collision resolution
- 🎬 **Animation System** - Multiple easing functions, property animations
- 📷 **Camera System** - Viewport control, following, shake effects
- 💡 **Lighting System** - Dynamic lights with falloff and flicker
- 🗺️ **Tilemap Support** - Grid-based level design
- 🎯 **Input Handling** - Keyboard and mouse events
- 📊 **Data Visualization** - Line plots and bar charts
- 🎭 **Layer System** - Parallax scrolling and depth sorting
- 🎥 **Frame Recording** - Export animations as GIF or image sequences
- 🔧 **Performance Metrics** - FPS counter and profiling tools

## 📦 Installation

### From PyPI

```bash
pip install gfxcanvas
```

### From Source

```bash
git clone https://github.com/basitganie/gfxcanvas.git
cd gfxcanvas
pip install -e .
```

## 🚀 Quick Start

```python
from gfxcanvas import GraphicalCanvas

# Create a window
canvas = GraphicalCanvas(800, 600, "My Game", fps=60)

# Draw a circle
circle = canvas.draw_circle(400, 300, 50, fill="#FF0000")

# Animate it
canvas.animate(circle, 'x', 400, 600, duration=2.0)

# Run the application
canvas.run()
```

## 📚 Examples

### Creating Shapes

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600, "Shapes Demo")

# Rectangle
rect = canvas.draw_rectangle(100, 100, 200, 150, fill="#4CAF50", rounded=10)

# Circle
circle = canvas.draw_circle(500, 300, 75, fill="#2196F3", outline="#FFFFFF", outline_width=3)

# Star
star = canvas.draw_star(400, 450, 60, 30, points=5, fill="#FFD700")

# Polygon
points = [(300, 100), (350, 150), (325, 200), (275, 200), (250, 150)]
polygon = canvas.draw_polygon(points, fill="#E91E63", smooth=True)

canvas.run()
```

### Animation with Easing

```python
from gfxcanvas import GraphicalCanvas, AnimationType

canvas = GraphicalCanvas(800, 600, "Animation Demo")

# Create multiple objects
objects = []
easing_types = [
    AnimationType.LINEAR,
    AnimationType.EASE_IN,
    AnimationType.EASE_OUT,
    AnimationType.EASE_IN_OUT,
    AnimationType.BOUNCE,
    AnimationType.ELASTIC
]

for i, easing in enumerate(easing_types):
    y = 50 + i * 80
    obj = canvas.draw_circle(50, y, 20, fill="#FF5722")
    canvas.animate(obj, 'x', 50, 750, duration=2.0, easing=easing)
    canvas.draw_text(easing.value, 400, y, font=("Arial", 12), color="#FFFFFF")

canvas.run()
```

### Physics Simulation

```python
from gfxcanvas import GraphicalCanvas, PhysicsType

canvas = GraphicalCanvas(800, 600, "Physics Demo")
canvas.set_background("#87CEEB")

# Create ground (static)
ground = canvas.create_physics_body(
    0, 550, 800, 50, 
    body_type=PhysicsType.STATIC
)
canvas.draw_rectangle(0, 550, 800, 50, fill="#8B4513")

# Create falling balls
for i in range(5):
    x = 150 + i * 120
    body = canvas.create_physics_body(
        x, 50, 40, 40,
        body_type=PhysicsType.DYNAMIC,
        mass=1.0,
        restitution=0.8
    )
    canvas.draw_circle(x, 50, 20, fill="#FF5722")

canvas.run()
```

### Interactive Game

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600, "Simple Game", fps=60)

# Create player
player = canvas.create_entity(400, 550, 60, 20, color="#2196F3")

# Create ball
ball = canvas.create_entity(400, 100, 30, 30, 
                           sprite_type='circle', 
                           color="#FF5722")
canvas.set_entity_velocity(ball, 200, 200)

# Score
score = 0
score_text = canvas.draw_text(f"Score: {score}", 400, 30, 
                             font=("Arial", 24, "bold"))

def update(dt):
    global score
    
    # Player movement with arrow keys or WASD
    speed = 400
    if canvas.is_key_pressed('Left') or canvas.is_key_pressed('a'):
        canvas.set_entity_velocity(player, -speed, 0)
    elif canvas.is_key_pressed('Right') or canvas.is_key_pressed('d'):
        canvas.set_entity_velocity(player, speed, 0)
    else:
        canvas.set_entity_velocity(player, 0, 0)
    
    # Update entities
    canvas.update_entity(player, dt)
    canvas.update_entity(ball, dt)
    
    # Keep player on screen
    px, py = canvas.get_entity_position(player)
    px = max(0, min(740, px))
    canvas.set_entity_position(player, px, py)
    
    # Ball collision with walls
    bx, by = canvas.get_entity_position(ball)
    vx, vy = canvas.entities[ball]['velocity']
    
    if bx <= 15 or bx >= 785:
        canvas.set_entity_velocity(ball, -vx, vy)
    if by <= 15:
        canvas.set_entity_velocity(ball, vx, -vy)
    
    # Ball collision with player
    if canvas.check_collision(ball, player):
        canvas.set_entity_velocity(ball, vx, -abs(vy))
        score += 1
        canvas.update_text(score_text, f"Score: {score}")
    
    # Game over
    if by >= 600:
        canvas.pause()
        canvas.draw_text("Game Over!", 400, 300, 
                        font=("Arial", 48, "bold"), color="#FF0000")

canvas.start_game_loop(update_callback=update)
canvas.run()
```

### Sprite Animation

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600, "Sprite Animation")

# Load sprite sheet (64x64 frames)
sprite = canvas.load_sprite_sheet(
    "character_spritesheet.png", 
    frame_width=64, 
    frame_height=64
)

# Draw sprite
character = canvas.draw_sprite(sprite, 400, 300, width=128, height=128)

# Play animation (10 frames per second, loop)
canvas.play_sprite_animation(sprite, frame_duration=0.1, loop=True)

canvas.run()
```

### Camera System

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600, "Camera Demo")

# Create world objects
for i in range(20):
    x = i * 100
    canvas.draw_rectangle(x, 250, 50, 50, fill="#4CAF50")

# Create player
player = canvas.create_entity(400, 300, 40, 40, color="#2196F3")

# Camera follows player
canvas.camera_follow(player, smoothness=0.1)

def update(dt):
    speed = 300
    vx = 0
    
    if canvas.is_key_pressed('Left'):
        vx = -speed
    elif canvas.is_key_pressed('Right'):
        vx = speed
    
    canvas.set_entity_velocity(player, vx, 0)
    canvas.update_entity(player, dt)
    
    # Camera shake on spacebar
    if canvas.is_key_just_pressed('space'):
        canvas.camera_shake(intensity=20, duration=0.5)

canvas.start_game_loop(update_callback=update)
canvas.run()
```

### UI Elements

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600, "UI Demo")

# Button
def on_click():
    print("Button clicked!")

canvas.draw_button(300, 100, 200, 60, "Click Me!", 
                  bg_color="#4CAF50",
                  hover_color="#45a049",
                  callback=on_click)

# Progress bar
progress_bar = canvas.draw_progress_bar(250, 200, 300, 40, 
                                        progress=0.0,
                                        fill_color="#2196F3")

# Slider
def on_slider_change(value):
    canvas.update_progress_bar(progress_bar, value / 100)

canvas.draw_slider(250, 300, 300, 40, 0, 100, 50,
                  callback=on_slider_change)

canvas.run()
```

### Lighting System

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600, "Lighting Demo")
canvas.set_background("#000000")

# Enable lighting
canvas.enable_lighting(ambient=0.2)

# Add lights
light1 = canvas.add_light(200, 300, 200, "#FFFF00", intensity=1.0, flicker=True)
light2 = canvas.add_light(600, 300, 200, "#00FFFF", intensity=1.0)

# Create objects
canvas.draw_circle(200, 300, 50, fill="#FF0000")
canvas.draw_rectangle(550, 250, 100, 100, fill="#00FF00")

# Move lights with mouse
def update(dt):
    mx, my = canvas.get_mouse_position()
    canvas.move_light(light1, mx, my)

canvas.start_game_loop(update_callback=update)
canvas.run()
```

### Data Visualization

```python
from gfxcanvas import GraphicalCanvas
import math

canvas = GraphicalCanvas(900, 700, "Data Visualization")
canvas.set_background("#FFFFFF")

# Line plot
x_data = [i for i in range(20)]
y_data = [math.sin(x * 0.5) * 50 + 100 for x in x_data]

canvas.plot_line(
    x_data, y_data,
    x=50, y=50, width=800, height=250,
    line_color="#2196F3",
    point_color="#FF5722",
    title="Sine Wave",
    xlabel="X Values",
    ylabel="Y Values"
)

# Bar chart
labels = ["Jan", "Feb", "Mar", "Apr", "May"]
values = [45, 67, 89, 56, 78]

canvas.plot_bar(
    labels, values,
    x=50, y=400, width=800, height=250,
    bar_color="#4CAF50",
    title="Monthly Data"
)

canvas.run()
```

### 3D Graphics

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600, "3D Demo")

# Create rotating cube
cube = canvas.draw_cube_3d(
    400, 300, 150,
    rotation_x=30, rotation_y=45,
    face_colors=["#FF0000", "#00FF00", "#0000FF", 
                 "#FFFF00", "#FF00FF", "#00FFFF"]
)

# Animate rotation
angle_x = 0
angle_y = 0

def update(dt):
    global angle_x, angle_y
    angle_x += 30 * dt
    angle_y += 45 * dt
    canvas.rotate_cube_3d(cube, angle_x, angle_y)

canvas.start_game_loop(update_callback=update)
canvas.run()
```

### Recording and Export

```python
from gfxcanvas import GraphicalCanvas, AnimationType

canvas = GraphicalCanvas(800, 600, "Recording Demo")

# Create animation
circle = canvas.draw_circle(100, 300, 50, fill="#FF5722")
canvas.animate(circle, 'x', 100, 700, duration=3.0, easing=AnimationType.EASE_IN_OUT)

# Start recording
canvas.start_recording(format="PNG")

def update(dt):
    # Stop after 3 seconds
    if canvas.get_frame_count() > 180:  # 3 seconds at 60 fps
        num_frames = canvas.stop_recording()
        print(f"Recorded {num_frames} frames")
        
        # Export as GIF
        canvas.export_gif("animation.gif", duration=16, loop=0)
        print("Saved animation.gif")
        
        canvas.pause()

canvas.start_game_loop(update_callback=update)
canvas.run()
```

## 📖 API Documentation

### GraphicalCanvas

Main class for creating graphics applications.

**Constructor:**
```python
GraphicalCanvas(
    width=800, 
    height=600, 
    title="Graphics Engine", 
    bg_color="#1a1a1a", 
    fps=60, 
    antialiasing=True, 
    resizable=False
)
```

### Drawing Methods

| Method | Description |
|--------|-------------|
| `draw_rectangle(x, y, width, height, ...)` | Draw a rectangle |
| `draw_circle(x, y, radius, ...)` | Draw a circle |
| `draw_ellipse(x, y, width, height, ...)` | Draw an ellipse |
| `draw_polygon(points, ...)` | Draw a polygon |
| `draw_line(x1, y1, x2, y2, ...)` | Draw a line |
| `draw_arc(x, y, width, height, start, extent, ...)` | Draw an arc |
| `draw_text(text, x, y, ...)` | Draw text |
| `draw_star(x, y, outer_radius, inner_radius, points, ...)` | Draw a star |
| `draw_arrow(x1, y1, x2, y2, ...)` | Draw an arrow |
| `draw_grid(cell_size, ...)` | Draw a grid |
| `draw_bezier_curve(points, ...)` | Draw a Bézier curve |

### Animation Methods

| Method | Description |
|--------|-------------|
| `animate(object_id, property, from_value, to_value, duration, easing, ...)` | Animate object property |
| `stop_animation(object_id)` | Stop all animations for object |

**Animation Types:**
- `AnimationType.LINEAR`
- `AnimationType.EASE_IN`
- `AnimationType.EASE_OUT`
- `AnimationType.EASE_IN_OUT`
- `AnimationType.BOUNCE`
- `AnimationType.ELASTIC`
- `AnimationType.SPRING`
- `AnimationType.CUBIC`
- `AnimationType.BACK`
- `AnimationType.CIRC`

### Physics Methods

| Method | Description |
|--------|-------------|
| `create_physics_body(x, y, width, height, ...)` | Create physics body |
| `apply_force(body_id, fx, fy)` | Apply force to body |
| `apply_impulse(body_id, ix, iy)` | Apply impulse to body |
| `set_physics_velocity(body_id, vx, vy)` | Set body velocity |
| `get_physics_velocity(body_id)` | Get body velocity |

**Physics Types:**
- `PhysicsType.STATIC` - Non-moving objects
- `PhysicsType.DYNAMIC` - Moving objects with physics
- `PhysicsType.KINEMATIC` - Manually controlled moving objects

### Entity Methods

| Method | Description |
|--------|-------------|
| `create_entity(x, y, width, height, ...)` | Create game entity |
| `update_entity(entity_id, dt)` | Update entity physics |
| `set_entity_velocity(entity_id, vx, vy)` | Set entity velocity |
| `set_entity_acceleration(entity_id, ax, ay)` | Set entity acceleration |
| `get_entity_position(entity_id)` | Get entity position |
| `set_entity_position(entity_id, x, y)` | Set entity position |
| `check_collision(entity1_id, entity2_id)` | Check collision between entities |
| `check_collision_group(entity_id, group)` | Check collision with group |
| `delete_entity(entity_id)` | Delete entity |

### Input Methods

| Method | Description |
|--------|-------------|
| `is_key_pressed(key)` | Check if key is currently pressed |
| `is_key_just_pressed(key)` | Check if key was just pressed this frame |
| `is_key_just_released(key)` | Check if key was just released this frame |
| `is_mouse_button_pressed(button)` | Check if mouse button is pressed |
| `is_mouse_button_just_pressed(button)` | Check if mouse button was just pressed |
| `get_mouse_position()` | Get current mouse position |
| `get_mouse_world_position()` | Get mouse position in world coordinates |

### Camera Methods

| Method | Description |
|--------|-------------|
| `set_camera_position(x, y)` | Set camera position |
| `move_camera(dx, dy)` | Move camera by delta |
| `set_camera_zoom(zoom)` | Set camera zoom level |
| `zoom_camera(delta)` | Zoom camera by delta |
| `camera_follow(target_id, smoothness)` | Make camera follow object |
| `camera_shake(intensity, duration)` | Add camera shake effect |
| `world_to_screen(x, y)` | Convert world to screen coordinates |
| `screen_to_world(x, y)` | Convert screen to world coordinates |

### Sprite Methods

| Method | Description |
|--------|-------------|
| `load_sprite(image_path, sprite_id)` | Load sprite from file |
| `load_sprite_sheet(image_path, frame_width, frame_height, ...)` | Load animated sprite sheet |
| `draw_sprite(sprite_id, x, y, ...)` | Draw sprite on canvas |
| `play_sprite_animation(sprite_id, frame_duration, loop)` | Play sprite animation |
| `stop_sprite_animation(sprite_id)` | Stop sprite animation |

### UI Methods

| Method | Description |
|--------|-------------|
| `draw_button(x, y, width, height, text, callback, ...)` | Draw interactive button |
| `draw_progress_bar(x, y, width, height, progress, ...)` | Draw progress bar |
| `update_progress_bar(object_id, progress)` | Update progress bar value |
| `draw_slider(x, y, width, height, min_val, max_val, value, callback, ...)` | Draw interactive slider |

### Layer Methods

| Method | Description |
|--------|-------------|
| `create_layer(name, visible, opacity, parallax_x, parallax_y)` | Create new layer |
| `set_current_layer(name)` | Set current drawing layer |
| `set_layer_opacity(name, opacity)` | Set layer opacity |
| `set_layer_parallax(name, parallax_x, parallax_y)` | Set layer parallax |
| `show_layer(name)` / `hide_layer(name)` | Show/hide layer |

## 🎨 Utility Classes

### Vector2

```python
from gfxcanvas import Vector2

v1 = Vector2(10, 20)
v2 = Vector2(5, 15)

# Operations
v3 = v1 + v2
v4 = v1 * 2
magnitude = v1.magnitude()
normalized = v1.normalize()
distance = v1.distance_to(v2)
angle = v1.angle_to(v2)
rotated = v1.rotate(math.pi / 4)

# Static methods
zero = Vector2.zero()
up = Vector2.up()
right = Vector2.right()
```

### Color

```python
from gfxcanvas import Color

# Create colors
red = Color(255, 0, 0)
green = Color.from_hex("#00FF00")

# Convert
hex_str = red.to_hex()
rgb_tuple = red.to_tuple()

# Interpolate
middle = Color.lerp(red, green, 0.5)

# Presets
blue = Color.blue()
white = Color.white()
```

### Timer

```python
from gfxcanvas import Timer

def on_timer():
    print("Timer finished!")

timer = Timer(duration=3.0, callback=on_timer, repeat=True)

def update(dt):
    timer.update(dt)
    print(f"Progress: {timer.get_progress():.2f}")
```

## 🎮 Game Loop

```python
from gfxcanvas import GraphicalCanvas

canvas = GraphicalCanvas(800, 600)

def update(dt):
    # Update game logic
    # dt is delta time in seconds
    pass

def draw():
    # Custom drawing code
    pass

# Start game loop
canvas.start_game_loop(update_callback=update, draw_callback=draw)
canvas.run()
```

## ⚙️ Configuration

```python
# Set FPS
canvas.set_fps(120)

# Enable/disable physics
canvas.physics_enabled = True

# Set gravity
canvas.gravity = (0, 981)  # pixels/s²

# Enable lighting
canvas.enable_lighting(ambient=0.3)

# Performance
canvas.culling_enabled = True  # Viewport culling
metrics = canvas.get_performance_metrics()
fps = canvas.get_fps()
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Basit Ahmad Ganie**

- GitHub: [@basitganie](https://github.com/basitganie/)
- Email: basitahmed1412.com

## 🙏 Acknowledgments

- Built on top of Python's Tkinter library
- Uses PIL/Pillow for image processing
- Inspired by modern game engines and graphics libraries

## 📝 Changelog

### Version 1.0.0 (2025-01-XX)

**Initial Release**

- 2D/3D graphics rendering
- Physics engine with collision detection
- Animation system with 10 easing functions
- Camera system with following and shake effects
- Sprite and tilemap support
- Lighting system with dynamic lights
- State machine implementation
- Input handling (keyboard/mouse)
- Data visualization (line plots, bar charts)
- Frame recording and GIF export
- Performance profiling tools
- UI elements (buttons, progress bars, sliders)
- Layer system with parallax scrolling
- Comprehensive utility classes (Vector2, Color, Timer)

## 🐛 Known Issues

Please report issues on the [GitHub issue tracker](https://github.com/basitganie/gfxcanvas/issues).

## 💬 Support

If you encounter any issues or have questions:

- 📫 Open an issue on [GitHub](https://github.com/basitganie/gfxcanvas/issues)
- 📧 Email: basitahmad1412@gmail.com
- 📖 Check the [examples](examples/) directory

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

Made with ❤️  by Basit Ahmad Ganie.
