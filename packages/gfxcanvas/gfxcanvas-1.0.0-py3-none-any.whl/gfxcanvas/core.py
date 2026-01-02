"""
gfxcanvas - Advanced Python Graphics and Game Engine
Author: Basit Ahmad Ganie
Version: 1.0.0
Features: 2D/3D graphics, physics, lighting, shaders, sprites, tilemap, state machine, audio
"""

import tkinter as tk
from tkinter import filedialog
import math
import time
import random
from typing import List, Dict, Tuple, Optional, Callable, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import json
from PIL import Image, ImageDraw, ImageTk, ImageGrab, ImageFilter, ImageEnhance
import io


class AnimationType(Enum):
    """Animation easing types"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    SPRING = "spring"
    CUBIC = "cubic"
    BACK = "back"
    CIRC = "circ"


class BlendMode(Enum):
    """Blend modes for compositing"""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    ADD = "add"
    SCREEN = "screen"
    OVERLAY = "overlay"


class PhysicsType(Enum):
    """Physics body types"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    KINEMATIC = "kinematic"


class CollisionShape(Enum):
    """Collision shape types"""
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    POLYGON = "polygon"


@dataclass
class Transform:
    """2D transformation matrix"""
    x: float = 0
    y: float = 0
    rotation: float = 0
    scale_x: float = 1
    scale_y: float = 1
    opacity: float = 1.0
    z_index: int = 0


@dataclass
class Camera:
    """Camera for viewport control"""
    x: float = 0
    y: float = 0
    zoom: float = 1.0
    rotation: float = 0
    shake_intensity: float = 0
    shake_duration: float = 0
    follow_target: Optional[str] = None
    follow_smoothness: float = 0.1


@dataclass
class Layer:
    """Layer for organizing objects"""
    name: str
    visible: bool = True
    opacity: float = 1.0
    parallax_x: float = 1.0
    parallax_y: float = 1.0
    objects: List[str] = field(default_factory=list)


@dataclass
class Light:
    """Dynamic lighting source"""
    x: float
    y: float
    radius: float
    color: str
    intensity: float = 1.0
    flicker: bool = False


@dataclass
class Sprite:
    """Sprite with animation support"""
    image: Any
    frames: List[Any] = field(default_factory=list)
    current_frame: int = 0
    frame_duration: float = 0.1
    frame_timer: float = 0
    playing: bool = False
    loop: bool = True


class GraphicalCanvas:
    """Advanced graphics and game engine"""
    
    COLOR_PRESETS = {
        "forest_green": "#228B22", "sky_blue": "#87CEEB", "coral": "#FF7F50",
        "gold": "#FFD700", "lavender": "#E6E6FA", "tomato": "#FF6347",
        "teal": "#008080", "salmon": "#FA8072", "violet": "#EE82EE",
        "khaki": "#F0E68C", "turquoise": "#40E0D0", "firebrick": "#B22222",
        "navy": "#000080", "steel_blue": "#4682B4", "olive": "#808000",
        "spring_green": "#00FF7F", "crimson": "#DC143C", "chocolate": "#D2691E",
        "midnight_blue": "#191970", "orchid": "#DA70D6", "lime": "#00FF00",
        "cyan": "#00FFFF", "magenta": "#FF00FF", "orange": "#FFA500",
        "pink": "#FFC0CB", "purple": "#800080", "indigo": "#4B0082",
        "maroon": "#800000", "aquamarine": "#7FFFD4", "peach": "#FFDAB9",
    }
    
    def __init__(self, width=800, height=600, title="Graphics Engine", 
                 bg_color="#1a1a1a", fps=60, antialiasing=True, resizable=False):
        """Initialize the graphics engine"""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(resizable, resizable)
        
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fps = fps
        self.frame_delay = 1000 // fps
        self.antialiasing = antialiasing
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Core systems
        self.animations = []
        self.objects = {}
        self.object_id_counter = 0
        self.is_running = False
        self._last_time = time.time()
        self._frame_count = 0
        self._fps_counter = 0
        self._fps_time = time.time()
        self._actual_fps = 0
        self._delta_time = 0
        
        # Layers
        self.layers = {"default": Layer("default")}
        self.current_layer = "default"
        
        # Camera
        self.camera = Camera()
        
        # Lighting system
        self.lights = {}
        self.ambient_light = 1.0
        self.lighting_enabled = False
        
        # Physics system
        self.physics_enabled = True
        self.gravity = (0, 981)  # pixels/s²
        self.physics_bodies = {}
        
        # Sprite system
        self.sprites = {}
        self.sprite_batches = {}
        
        # Tilemap system
        self.tilemaps = {}
        
        # Input handling
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = {1: False, 2: False, 3: False}
        self.mouse_just_pressed = {1: False, 2: False, 3: False}
        self.mouse_just_released = {1: False, 2: False, 3: False}
        self._setup_input_handlers()
        
        # Game entities
        self.entities = {}
        self.collision_groups = {}
        
        # State machine
        self.state_machines = {}
        
        # Frame capture
        self.recording = False
        self.recorded_frames = []
        self.frame_format = "PNG"
        
        # Post-processing effects
        self.post_effects = []
        
        # Performance metrics
        self.performance_metrics = {
            'draw_calls': 0,
            'objects': 0,
            'entities': 0,
            'frame_time': 0,
            'physics_time': 0,
            'render_time': 0
        }
        
        # Update callbacks
        self.update_callbacks = []
        self.draw_callbacks = []
        
        # Viewport culling
        self.culling_enabled = True
        self.culling_margin = 100
    
    def _setup_input_handlers(self):
        """Setup keyboard and mouse input handlers"""
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Button-1>', lambda e: self._on_mouse_button(e, 1, True))
        self.canvas.bind('<ButtonRelease-1>', lambda e: self._on_mouse_button(e, 1, False))
        self.canvas.bind('<Button-2>', lambda e: self._on_mouse_button(e, 2, True))
        self.canvas.bind('<ButtonRelease-2>', lambda e: self._on_mouse_button(e, 2, False))
        self.canvas.bind('<Button-3>', lambda e: self._on_mouse_button(e, 3, True))
        self.canvas.bind('<ButtonRelease-3>', lambda e: self._on_mouse_button(e, 3, False))
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
    
    def _on_key_press(self, event):
        """Handle key press"""
        if event.keysym not in self.keys_pressed:
            self.keys_just_pressed.add(event.keysym)
        self.keys_pressed.add(event.keysym)
    
    def _on_key_release(self, event):
        """Handle key release"""
        self.keys_pressed.discard(event.keysym)
        self.keys_just_released.add(event.keysym)
    
    def _on_mouse_move(self, event):
        """Handle mouse movement"""
        self.mouse_pos = (event.x, event.y)
    
    def _on_mouse_button(self, event, button, pressed):
        """Handle mouse button"""
        if pressed and not self.mouse_buttons[button]:
            self.mouse_just_pressed[button] = True
        elif not pressed and self.mouse_buttons[button]:
            self.mouse_just_released[button] = True
        self.mouse_buttons[button] = pressed
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel"""
        if event.delta > 0:
            self.zoom_camera(0.1)
        else:
            self.zoom_camera(-0.1)
    
    def _clear_input_buffers(self):
        """Clear just pressed/released buffers"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_pressed = {1: False, 2: False, 3: False}
        self.mouse_just_released = {1: False, 2: False, 3: False}
    
    # ==================== INPUT METHODS ====================
    
    def is_key_pressed(self, key):
        """Check if a key is currently pressed"""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key):
        """Check if a key was just pressed this frame"""
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key):
        """Check if a key was just released this frame"""
        return key in self.keys_just_released
    
    def is_mouse_button_pressed(self, button=1):
        """Check if mouse button is pressed"""
        return self.mouse_buttons.get(button, False)
    
    def is_mouse_button_just_pressed(self, button=1):
        """Check if mouse button was just pressed"""
        return self.mouse_just_pressed.get(button, False)
    
    def is_mouse_button_just_released(self, button=1):
        """Check if mouse button was just released"""
        return self.mouse_just_released.get(button, False)
    
    def get_mouse_position(self):
        """Get current mouse position"""
        return self.mouse_pos
    
    def get_mouse_world_position(self):
        """Get mouse position in world coordinates"""
        return self.screen_to_world(self.mouse_pos[0], self.mouse_pos[1])
    
    # ==================== UTILITY METHODS ====================
    
    def _get_next_id(self):
        """Get next unique object ID"""
        self.object_id_counter += 1
        return f"obj_{self.object_id_counter}"
    
    def rgb_to_hex(self, r, g, b):
        """Convert RGB to hex color"""
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
    
    def hex_to_rgb(self, hex_color):
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def gradient_color(self, color1, color2, ratio):
        """Interpolate between two colors"""
        r1, g1, b1 = self.hex_to_rgb(color1)
        r2, g2, b2 = self.hex_to_rgb(color2)
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        return self.rgb_to_hex(r, g, b)
    
    def lerp(self, a, b, t):
        """Linear interpolation"""
        return a + (b - a) * t
    
    def clamp(self, value, min_val, max_val):
        """Clamp value between min and max"""
        return max(min_val, min(max_val, value))
    
    def distance(self, x1, y1, x2, y2):
        """Calculate distance between two points"""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def angle_between(self, x1, y1, x2, y2):
        """Calculate angle between two points in radians"""
        return math.atan2(y2 - y1, x2 - x1)
    
    def normalize_angle(self, angle):
        """Normalize angle to -π to π"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
    
    def point_in_rect(self, px, py, x, y, width, height):
        """Check if point is inside rectangle"""
        return x <= px <= x + width and y <= py <= y + height
    
    def point_in_circle(self, px, py, cx, cy, radius):
        """Check if point is inside circle"""
        return self.distance(px, py, cx, cy) <= radius
    
    def rect_intersects_rect(self, x1, y1, w1, h1, x2, y2, w2, h2):
        """Check if two rectangles intersect"""
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)
    
    def circle_intersects_circle(self, x1, y1, r1, x2, y2, r2):
        """Check if two circles intersect"""
        return self.distance(x1, y1, x2, y2) < r1 + r2
    
    # ==================== LAYER MANAGEMENT ====================
    
    def create_layer(self, name, visible=True, opacity=1.0, parallax_x=1.0, parallax_y=1.0):
        """Create a new layer with parallax support"""
        self.layers[name] = Layer(name, visible, opacity, parallax_x, parallax_y)
        return name
    
    def set_current_layer(self, name):
        """Set the current drawing layer"""
        if name in self.layers:
            self.current_layer = name
    
    def get_layer(self, name):
        """Get layer by name"""
        return self.layers.get(name)
    
    def delete_layer(self, name):
        """Delete a layer and all its objects"""
        if name in self.layers and name != "default":
            for obj_id in self.layers[name].objects[:]:
                self.delete_object(obj_id)
            del self.layers[name]
    
    def set_layer_opacity(self, name, opacity):
        """Set layer opacity"""
        if name in self.layers:
            self.layers[name].opacity = self.clamp(opacity, 0, 1)
    
    def set_layer_parallax(self, name, parallax_x, parallax_y):
        """Set layer parallax factors"""
        if name in self.layers:
            self.layers[name].parallax_x = parallax_x
            self.layers[name].parallax_y = parallax_y
    
    def toggle_layer_visibility(self, name):
        """Toggle layer visibility"""
        if name in self.layers:
            self.layers[name].visible = not self.layers[name].visible
            self._update_layer_visibility(name)
    
    def show_layer(self, name):
        """Show layer"""
        if name in self.layers:
            self.layers[name].visible = True
            self._update_layer_visibility(name)
    
    def hide_layer(self, name):
        """Hide layer"""
        if name in self.layers:
            self.layers[name].visible = False
            self._update_layer_visibility(name)
    
    def _update_layer_visibility(self, layer_name):
        """Update visibility of all objects in a layer"""
        layer = self.layers[layer_name]
        state = tk.NORMAL if layer.visible else tk.HIDDEN
        
        for obj_id in layer.objects:
            if obj_id in self.objects:
                obj = self.objects[obj_id]
                if 'canvas_id' in obj:
                    self.canvas.itemconfig(obj['canvas_id'], state=state)
                elif 'canvas_ids' in obj:
                    for cid in obj['canvas_ids']:
                        if cid:
                            self.canvas.itemconfig(cid, state=state)
    
    # ==================== CAMERA CONTROL ====================
    
    def set_camera_position(self, x, y):
        """Set camera position"""
        self.camera.x = x
        self.camera.y = y
    
    def move_camera(self, dx, dy):
        """Move camera by delta"""
        self.camera.x += dx
        self.camera.y += dy
    
    def set_camera_zoom(self, zoom):
        """Set camera zoom level"""
        self.camera.zoom = max(0.1, zoom)
    
    def zoom_camera(self, delta):
        """Zoom camera by delta"""
        self.camera.zoom = max(0.1, self.camera.zoom + delta)
    
    def set_camera_rotation(self, angle):
        """Set camera rotation in radians"""
        self.camera.rotation = angle
    
    def rotate_camera(self, delta):
        """Rotate camera by delta"""
        self.camera.rotation += delta
    
    def camera_follow(self, target_id, smoothness=0.1):
        """Make camera follow an object"""
        self.camera.follow_target = target_id
        self.camera.follow_smoothness = smoothness
    
    def camera_unfollow(self):
        """Stop camera following"""
        self.camera.follow_target = None
    
    def camera_shake(self, intensity=10, duration=0.5):
        """Add camera shake effect"""
        self.camera.shake_intensity = intensity
        self.camera.shake_duration = duration
    
    def _update_camera(self, dt):
        """Update camera (follow, shake, etc.)"""
        # Follow target
        if self.camera.follow_target and self.camera.follow_target in self.objects:
            target = self.objects[self.camera.follow_target]
            target_x = target['transform'].x
            target_y = target['transform'].y
            
            self.camera.x = self.lerp(self.camera.x, target_x, self.camera.follow_smoothness)
            self.camera.y = self.lerp(self.camera.y, target_y, self.camera.follow_smoothness)
        
        # Camera shake
        if self.camera.shake_duration > 0:
            self.camera.shake_duration -= dt
            if self.camera.shake_duration <= 0:
                self.camera.shake_intensity = 0
    
    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        # Apply camera shake
        shake_x = random.uniform(-self.camera.shake_intensity, self.camera.shake_intensity) if self.camera.shake_intensity > 0 else 0
        shake_y = random.uniform(-self.camera.shake_intensity, self.camera.shake_intensity) if self.camera.shake_intensity > 0 else 0
        
        screen_x = (x - self.camera.x) * self.camera.zoom + self.width / 2 + shake_x
        screen_y = (y - self.camera.y) * self.camera.zoom + self.height / 2 + shake_y
        return screen_x, screen_y
    
    def screen_to_world(self, x, y):
        """Convert screen coordinates to world coordinates"""
        world_x = (x - self.width / 2) / self.camera.zoom + self.camera.x
        world_y = (y - self.height / 2) / self.camera.zoom + self.camera.y
        return world_x, world_y
    
    def is_on_screen(self, x, y, margin=0):
        """Check if world coordinates are visible on screen"""
        screen_x, screen_y = self.world_to_screen(x, y)
        return (-margin <= screen_x <= self.width + margin and
                -margin <= screen_y <= self.height + margin)
    
    # ==================== LIGHTING SYSTEM ====================
    
    def enable_lighting(self, ambient=0.3):
        """Enable dynamic lighting system"""
        self.lighting_enabled = True
        self.ambient_light = ambient
    
    def disable_lighting(self):
        """Disable lighting system"""
        self.lighting_enabled = False
    
    def add_light(self, x, y, radius, color="#FFFF00", intensity=1.0, flicker=False, light_id=None):
        """Add a light source"""
        if light_id is None:
            light_id = self._get_next_id()
        
        self.lights[light_id] = Light(x, y, radius, color, intensity, flicker)
        return light_id
    
    def remove_light(self, light_id):
        """Remove a light source"""
        if light_id in self.lights:
            del self.lights[light_id]
    
    def move_light(self, light_id, x, y):
        """Move a light source"""
        if light_id in self.lights:
            self.lights[light_id].x = x
            self.lights[light_id].y = y
    
    def set_light_intensity(self, light_id, intensity):
        """Set light intensity"""
        if light_id in self.lights:
            self.lights[light_id].intensity = intensity
    
    def _calculate_lighting(self, x, y):
        """Calculate lighting at a point"""
        if not self.lighting_enabled:
            return 1.0
        
        total_light = self.ambient_light
        
        for light in self.lights.values():
            dist = self.distance(x, y, light.x, light.y)
            if dist < light.radius:
                # Inverse square falloff
                falloff = 1.0 - (dist / light.radius)
                intensity = light.intensity * falloff
                
                # Flicker effect
                if light.flicker:
                    intensity *= random.uniform(0.8, 1.0)
                
                total_light += intensity
        
        return min(1.0, total_light)
    
    # ==================== SPRITE SYSTEM ====================
    
    def load_sprite(self, image_path, sprite_id=None):
        """Load a sprite from file"""
        if sprite_id is None:
            sprite_id = self._get_next_id()
        
        try:
            img = Image.open(image_path)
            if self.antialiasing:
                img.thumbnail((img.width, img.height), Image.LANCZOS)
            
            self.sprites[sprite_id] = Sprite(img)
            return sprite_id
        except Exception as e:
            print(f"Error loading sprite: {e}")
            return None
    
    def load_sprite_sheet(self, image_path, frame_width, frame_height, sprite_id=None):
        """Load animated sprite from sprite sheet"""
        if sprite_id is None:
            sprite_id = self._get_next_id()
        
        try:
            img = Image.open(image_path)
            frames = []
            
            cols = img.width // frame_width
            rows = img.height // frame_height
            
            for row in range(rows):
                for col in range(cols):
                    x = col * frame_width
                    y = row * frame_height
                    frame = img.crop((x, y, x + frame_width, y + frame_height))
                    frames.append(frame)
            
            self.sprites[sprite_id] = Sprite(frames[0] if frames else img, frames)
            return sprite_id
        except Exception as e:
            print(f"Error loading sprite sheet: {e}")
            return None
    
    def draw_sprite(self, sprite_id, x, y, width=None, height=None, 
                   rotation=0, flip_h=False, flip_v=False, object_id=None):
        """Draw a sprite on canvas"""
        if sprite_id not in self.sprites:
            return None
        
        if object_id is None:
            object_id = self._get_next_id()
        
        sprite = self.sprites[sprite_id]
        img = sprite.image
        
        # Resize if dimensions provided
        if width and height:
            img = img.resize((int(width), int(height)), Image.LANCZOS if self.antialiasing else Image.NEAREST)
        
        # Flip
        if flip_h:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_v:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        # Rotate
        if rotation != 0:
            img = img.rotate(-math.degrees(rotation), expand=True)
        
        photo = ImageTk.PhotoImage(img)
        canvas_id = self.canvas.create_image(x, y, image=photo, anchor=tk.CENTER)
        
        self.objects[object_id] = {
            'type': 'sprite',
            'canvas_id': canvas_id,
            'transform': Transform(x, y, rotation),
            'sprite_id': sprite_id,
            'photo': photo,  # Keep reference
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def play_sprite_animation(self, sprite_id, frame_duration=0.1, loop=True):
        """Play sprite animation"""
        if sprite_id in self.sprites:
            sprite = self.sprites[sprite_id]
            sprite.playing = True
            sprite.loop = loop
            sprite.frame_duration = frame_duration
            sprite.current_frame = 0
            sprite.frame_timer = 0
    
    def stop_sprite_animation(self, sprite_id):
        """Stop sprite animation"""
        if sprite_id in self.sprites:
            self.sprites[sprite_id].playing = False
    
    def _update_sprites(self, dt):
        """Update all sprite animations"""
        for sprite in self.sprites.values():
            if sprite.playing and sprite.frames:
                sprite.frame_timer += dt
                
                if sprite.frame_timer >= sprite.frame_duration:
                    sprite.frame_timer = 0
                    sprite.current_frame += 1
                    
                    if sprite.current_frame >= len(sprite.frames):
                        if sprite.loop:
                            sprite.current_frame = 0
                        else:
                            sprite.playing = False
                            sprite.current_frame = len(sprite.frames) - 1
                    
                    sprite.image = sprite.frames[sprite.current_frame]
    
    # ==================== TILEMAP SYSTEM ====================
    
    def create_tilemap(self, tile_width, tile_height, map_width, map_height, tilemap_id=None):
        """Create a tilemap"""
        if tilemap_id is None:
            tilemap_id = self._get_next_id()
        
        self.tilemaps[tilemap_id] = {
            'tile_width': tile_width,
            'tile_height': tile_height,
            'map_width': map_width,
            'map_height': map_height,
            'tiles': [[None for _ in range(map_width)] for _ in range(map_height)],
            'tileset': {},
            'canvas_ids': []
        }
        
        return tilemap_id
    
    def set_tilemap_tile(self, tilemap_id, row, col, tile_id):
        """Set a tile in the tilemap"""
        if tilemap_id in self.tilemaps:
            tilemap = self.tilemaps[tilemap_id]
            if 0 <= row < tilemap['map_height'] and 0 <= col < tilemap['map_width']:
                tilemap['tiles'][row][col] = tile_id
    
    def add_tileset_tile(self, tilemap_id, tile_id, color):
        """Add a tile type to tileset"""
        if tilemap_id in self.tilemaps:
            self.tilemaps[tilemap_id]['tileset'][tile_id] = color
    
    def render_tilemap(self, tilemap_id, x=0, y=0):
        """Render the tilemap"""
        if tilemap_id not in self.tilemaps:
            return
        
        tilemap = self.tilemaps[tilemap_id]
        
        # Clear previous render
        for cid in tilemap['canvas_ids']:
            self.canvas.delete(cid)
        tilemap['canvas_ids'].clear()
        
        # Render tiles
        for row in range(tilemap['map_height']):
            for col in range(tilemap['map_width']):
                tile_id = tilemap['tiles'][row][col]
                if tile_id and tile_id in tilemap['tileset']:
                    tx = x + col * tilemap['tile_width']
                    ty = y + row * tilemap['tile_height']
                    
                    canvas_id = self.canvas.create_rectangle(
                        tx, ty,
                        tx + tilemap['tile_width'],
                        ty + tilemap['tile_height'],
                        fill=tilemap['tileset'][tile_id],
                        outline=""
                    )
                    tilemap['canvas_ids'].append(canvas_id)
    
    def get_tile_at_position(self, tilemap_id, world_x, world_y):
        """Get tile ID at world position"""
        if tilemap_id not in self.tilemaps:
            return None
        
        tilemap = self.tilemaps[tilemap_id]
        col = int(world_x // tilemap['tile_width'])
        row = int(world_y // tilemap['tile_height'])
        
        if 0 <= row < tilemap['map_height'] and 0 <= col < tilemap['map_width']:
            return tilemap['tiles'][row][col]
        return None
    
    # ==================== PHYSICS SYSTEM ====================
    
    def create_physics_body(self, x, y, width, height, body_type=PhysicsType.DYNAMIC,
                           mass=1.0, restitution=0.5, friction=0.3, body_id=None):
        """Create a physics body"""
        if body_id is None:
            body_id = self._get_next_id()
        
        self.physics_bodies[body_id] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'velocity_x': 0,
            'velocity_y': 0,
            'force_x': 0,
            'force_y': 0,
            'mass': mass,
            'type': body_type,
            'restitution': restitution,
            'friction': friction,
            'rotation': 0,
            'angular_velocity': 0,
            'shape': CollisionShape.RECTANGLE
        }
        
        return body_id
    
    def apply_force(self, body_id, fx, fy):
        """Apply force to physics body"""
        if body_id in self.physics_bodies:
            body = self.physics_bodies[body_id]
            body['force_x'] += fx
            body['force_y'] += fy
    
    def apply_impulse(self, body_id, ix, iy):
        """Apply impulse to physics body"""
        if body_id in self.physics_bodies:
            body = self.physics_bodies[body_id]
            if body['type'] == PhysicsType.DYNAMIC:
                body['velocity_x'] += ix / body['mass']
                body['velocity_y'] += iy / body['mass']
    
    def set_physics_velocity(self, body_id, vx, vy):
        """Set physics body velocity"""
        if body_id in self.physics_bodies:
            body = self.physics_bodies[body_id]
            body['velocity_x'] = vx
            body['velocity_y'] = vy
    
    def get_physics_velocity(self, body_id):
        """Get physics body velocity"""
        if body_id in self.physics_bodies:
            body = self.physics_bodies[body_id]
            return (body['velocity_x'], body['velocity_y'])
        return (0, 0)
    
    def _update_physics(self, dt):
        """Update physics simulation"""
        if not self.physics_enabled:
            return
        
        # Apply forces and integrate
        for body_id, body in self.physics_bodies.items():
            if body['type'] != PhysicsType.DYNAMIC:
                continue
            
            # Apply gravity
            body['force_y'] += body['mass'] * self.gravity[1] * dt
            
            # Calculate acceleration
            ax = body['force_x'] / body['mass']
            ay = body['force_y'] / body['mass']
            
            # Update velocity
            body['velocity_x'] += ax * dt
            body['velocity_y'] += ay * dt
            
            # Apply friction
            body['velocity_x'] *= (1 - body['friction'] * dt)
            body['velocity_y'] *= (1 - body['friction'] * dt)
            
            # Update position
            body['x'] += body['velocity_x'] * dt
            body['y'] += body['velocity_y'] * dt
            
            # Update rotation
            body['rotation'] += body['angular_velocity'] * dt
            
            # Reset forces
            body['force_x'] = 0
            body['force_y'] = 0
        
        # Collision detection and resolution
        self._resolve_physics_collisions()
    
    def _resolve_physics_collisions(self):
        """Resolve collisions between physics bodies"""
        bodies = list(self.physics_bodies.items())
        
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                id1, body1 = bodies[i]
                id2, body2 = bodies[j]
                
                # Skip if both are static
                if body1['type'] == PhysicsType.STATIC and body2['type'] == PhysicsType.STATIC:
                    continue
                
                # AABB collision detection
                if self.rect_intersects_rect(
                    body1['x'], body1['y'], body1['width'], body1['height'],
                    body2['x'], body2['y'], body2['width'], body2['height']
                ):
                    # Calculate overlap
                    overlap_x = min(
                        body1['x'] + body1['width'] - body2['x'],
                        body2['x'] + body2['width'] - body1['x']
                    )
                    overlap_y = min(
                        body1['y'] + body1['height'] - body2['y'],
                        body2['y'] + body2['height'] - body1['y']
                    )
                    
                    # Resolve collision
                    if overlap_x < overlap_y:
                        # Horizontal collision
                        if body1['x'] < body2['x']:
                            if body1['type'] == PhysicsType.DYNAMIC:
                                body1['x'] -= overlap_x / 2
                            if body2['type'] == PhysicsType.DYNAMIC:
                                body2['x'] += overlap_x / 2
                        else:
                            if body1['type'] == PhysicsType.DYNAMIC:
                                body1['x'] += overlap_x / 2
                            if body2['type'] == PhysicsType.DYNAMIC:
                                body2['x'] -= overlap_x / 2
                        
                        # Apply restitution
                        restitution = (body1['restitution'] + body2['restitution']) / 2
                        if body1['type'] == PhysicsType.DYNAMIC:
                            body1['velocity_x'] *= -restitution
                        if body2['type'] == PhysicsType.DYNAMIC:
                            body2['velocity_x'] *= -restitution
                    else:
                        # Vertical collision
                        if body1['y'] < body2['y']:
                            if body1['type'] == PhysicsType.DYNAMIC:
                                body1['y'] -= overlap_y / 2
                            if body2['type'] == PhysicsType.DYNAMIC:
                                body2['y'] += overlap_y / 2
                        else:
                            if body1['type'] == PhysicsType.DYNAMIC:
                                body1['y'] += overlap_y / 2
                            if body2['type'] == PhysicsType.DYNAMIC:
                                body2['y'] -= overlap_y / 2
                        
                        # Apply restitution
                        restitution = (body1['restitution'] + body2['restitution']) / 2
                        if body1['type'] == PhysicsType.DYNAMIC:
                            body1['velocity_y'] *= -restitution
                        if body2['type'] == PhysicsType.DYNAMIC:
                            body2['velocity_y'] *= -restitution
    
    # ==================== STATE MACHINE ====================
    
    def create_state_machine(self, initial_state, machine_id=None):
        """Create a state machine"""
        if machine_id is None:
            machine_id = self._get_next_id()
        
        self.state_machines[machine_id] = {
            'current_state': initial_state,
            'states': {},
            'transitions': {}
        }
        
        return machine_id
    
    def add_state(self, machine_id, state_name, enter_callback=None, 
                 update_callback=None, exit_callback=None):
        """Add a state to state machine"""
        if machine_id in self.state_machines:
            self.state_machines[machine_id]['states'][state_name] = {
                'enter': enter_callback,
                'update': update_callback,
                'exit': exit_callback
            }
    
    def add_transition(self, machine_id, from_state, to_state, condition):
        """Add a transition between states"""
        if machine_id in self.state_machines:
            key = f"{from_state}->{to_state}"
            self.state_machines[machine_id]['transitions'][key] = condition
    
    def change_state(self, machine_id, new_state):
        """Manually change state"""
        if machine_id not in self.state_machines:
            return
        
        machine = self.state_machines[machine_id]
        old_state = machine['current_state']
        
        # Exit old state
        if old_state in machine['states'] and machine['states'][old_state]['exit']:
            machine['states'][old_state]['exit']()
        
        # Enter new state
        machine['current_state'] = new_state
        if new_state in machine['states'] and machine['states'][new_state]['enter']:
            machine['states'][new_state]['enter']()
    
    def _update_state_machines(self, dt):
        """Update all state machines"""
        for machine_id, machine in self.state_machines.items():
            current = machine['current_state']
            
            # Update current state
            if current in machine['states'] and machine['states'][current]['update']:
                machine['states'][current]['update'](dt)
            
            # Check transitions
            for key, condition in machine['transitions'].items():
                from_state, to_state = key.split('->')
                if from_state == current and condition():
                    self.change_state(machine_id, to_state)
                    break
    
    # ==================== TEXT DRAWING ====================
    
    def draw_text(self, text, x, y, font=("Arial", 20), color="#FFFFFF",
                  anchor="center", angle=0, object_id=None):
        """Draw text on canvas"""
        if object_id is None:
            object_id = self._get_next_id()
        
        text_id = self.canvas.create_text(
            x, y, text=text, font=font, fill=color, anchor=anchor, angle=angle
        )
        
        self.objects[object_id] = {
            'type': 'text',
            'canvas_id': text_id,
            'transform': Transform(x, y),
            'text': text,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def update_text(self, object_id, new_text):
        """Update text content"""
        if object_id in self.objects and self.objects[object_id]['type'] == 'text':
            obj = self.objects[object_id]
            obj['text'] = new_text
            self.canvas.itemconfig(obj['canvas_id'], text=new_text)
    
    def draw_rainbow_text(self, text, x, y, font=("Arial", 20), 
                         spacing=2, object_id=None):
        """Draw text with rainbow colors"""
        colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", 
                 "#0000FF", "#4B0082", "#9400D3"]
        
        if object_id is None:
            object_id = self._get_next_id()
        
        text_ids = []
        current_x = x
        
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            
            char_id = self.canvas.create_text(
                current_x, y,
                text=char,
                font=font,
                fill=color,
                anchor="w"
            )
            text_ids.append(char_id)
            
            bbox = self.canvas.bbox(char_id)
            if bbox:
                current_x += (bbox[2] - bbox[0]) + spacing
        
        self.objects[object_id] = {
            'type': 'rainbow_text',
            'canvas_ids': text_ids,
            'transform': Transform(x, y),
            'text': text,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id

    def draw_gradient_text(self, text, x, y, start_color, end_color, 
                          font=("Arial", 20), spacing=2, object_id=None):
        """Draw text with gradient effect"""
        if object_id is None:
            object_id = self._get_next_id()
        
        text_ids = []
        total_chars = len(text)
        current_x = x
        
        for i, char in enumerate(text):
            ratio = i / max(1, total_chars - 1)
            color = self.gradient_color(start_color, end_color, ratio)
            
            char_id = self.canvas.create_text(
                current_x, y, text=char, font=font, fill=color, anchor="w"
            )
            text_ids.append(char_id)
            
            bbox = self.canvas.bbox(char_id)
            if bbox:
                current_x += (bbox[2] - bbox[0]) + spacing
        
        self.objects[object_id] = {
            'type': 'gradient_text',
            'canvas_ids': text_ids,
            'transform': Transform(x, y),
            'text': text,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    # ==================== 2D SHAPES ====================
    
    def draw_rectangle(self, x, y, width, height, fill="#FFFFFF",
                      outline="#000000", outline_width=1, rounded=0, object_id=None):
        """Draw a rectangle"""
        if object_id is None:
            object_id = self._get_next_id()
        
        if rounded > 0:
            rect_id = self._create_rounded_rectangle(
                x, y, x + width, y + height, rounded, fill, outline, outline_width
            )
        else:
            rect_id = self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill, outline=outline, width=outline_width
            )
        
        self.objects[object_id] = {
            'type': 'rectangle',
            'canvas_id': rect_id,
            'transform': Transform(x, y),
            'width': width,
            'height': height,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, fill, outline, width):
        """Helper to create rounded rectangle"""
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1,
            x2, y1 + radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2, x1, y2,
            x1, y2 - radius, x1, y1 + radius, x1, y1
        ]
        
        return self.canvas.create_polygon(
            points, smooth=True, fill=fill, outline=outline, width=width
        )
    
    def draw_circle(self, x, y, radius, fill="#FFFFFF",
                   outline="#000000", outline_width=1, object_id=None):
        """Draw a circle"""
        if object_id is None:
            object_id = self._get_next_id()
        
        circle_id = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill, outline=outline, width=outline_width
        )
        
        self.objects[object_id] = {
            'type': 'circle',
            'canvas_id': circle_id,
            'transform': Transform(x, y),
            'radius': radius,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def draw_ellipse(self, x, y, width, height, fill="#FFFFFF",
                    outline="#000000", outline_width=1, object_id=None):
        """Draw an ellipse"""
        if object_id is None:
            object_id = self._get_next_id()
        
        ellipse_id = self.canvas.create_oval(
            x - width/2, y - height/2, x + width/2, y + height/2,
            fill=fill, outline=outline, width=outline_width
        )
        
        self.objects[object_id] = {
            'type': 'ellipse',
            'canvas_id': ellipse_id,
            'transform': Transform(x, y),
            'width': width,
            'height': height,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def draw_polygon(self, points, fill="#FFFFFF", outline="#000000",
                    outline_width=1, smooth=False, object_id=None):
        """Draw a polygon from list of points"""
        if object_id is None:
            object_id = self._get_next_id()
        
        flat_points = [coord for point in points for coord in point]
        
        poly_id = self.canvas.create_polygon(
            flat_points, fill=fill, outline=outline, width=outline_width, smooth=smooth
        )
        
        self.objects[object_id] = {
            'type': 'polygon',
            'canvas_id': poly_id,
            'transform': Transform(points[0][0] if points else 0, points[0][1] if points else 0),
            'points': points,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def draw_line(self, x1, y1, x2, y2, color="#FFFFFF",
                 width=2, smooth=False, arrow=None, dash=None, object_id=None):
        """Draw a line"""
        if object_id is None:
            object_id = self._get_next_id()
        
        line_id = self.canvas.create_line(
            x1, y1, x2, y2, fill=color, width=width, smooth=smooth, 
            arrow=arrow, dash=dash
        )
        
        self.objects[object_id] = {
            'type': 'line',
            'canvas_id': line_id,
            'transform': Transform(x1, y1),
            'end_x': x2,
            'end_y': y2,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def draw_arc(self, x, y, width, height, start, extent, 
                fill="#FFFFFF", outline="#000000", width_line=2, 
                style=tk.PIESLICE, object_id=None):
        """Draw an arc"""
        if object_id is None:
            object_id = self._get_next_id()
        
        arc_id = self.canvas.create_arc(
            x - width/2, y - height/2, x + width/2, y + height/2,
            start=start, extent=extent, fill=fill, outline=outline, 
            width=width_line, style=style
        )
        
        self.objects[object_id] = {
            'type': 'arc',
            'canvas_id': arc_id,
            'transform': Transform(x, y),
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    # ==================== ADVANCED SHAPES ====================
    
    def draw_star(self, x, y, outer_radius, inner_radius, points=5,
                 fill="#FFFF00", outline="#000000", outline_width=2, object_id=None):
        """Draw a star shape"""
        if object_id is None:
            object_id = self._get_next_id()
        
        star_points = []
        angle_step = 2 * math.pi / points
        
        for i in range(points * 2):
            angle = i * angle_step / 2 - math.pi / 2
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            star_points.append((px, py))
        
        return self.draw_polygon(star_points, fill, outline, outline_width, 
                                smooth=False, object_id=object_id)
    
    def draw_arrow(self, x1, y1, x2, y2, color="#FFFFFF", width=2,
                  head_width=10, head_length=15, object_id=None):
        """Draw an arrow"""
        if object_id is None:
            object_id = self._get_next_id()
        
        # Calculate angle
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Arrow head points
        head_points = [
            (x2, y2),
            (x2 - head_length * math.cos(angle - math.pi/6), 
             y2 - head_length * math.sin(angle - math.pi/6)),
            (x2 - head_length * math.cos(angle + math.pi/6), 
             y2 - head_length * math.sin(angle + math.pi/6))
        ]
        
        # Draw line
        line_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
        
        # Draw head
        flat_head = [coord for point in head_points for coord in point]
        head_id = self.canvas.create_polygon(flat_head, fill=color, outline=color)
        
        self.objects[object_id] = {
            'type': 'arrow',
            'canvas_ids': [line_id, head_id],
            'transform': Transform(x1, y1),
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def draw_grid(self, cell_size=50, color="#333333", width=1, object_id=None):
        """Draw a grid"""
        if object_id is None:
            object_id = self._get_next_id()
        
        line_ids = []
        
        # Vertical lines
        for x in range(0, self.width + 1, cell_size):
            lid = self.canvas.create_line(x, 0, x, self.height, fill=color, width=width)
            line_ids.append(lid)
        
        # Horizontal lines
        for y in range(0, self.height + 1, cell_size):
            lid = self.canvas.create_line(0, y, self.width, y, fill=color, width=width)
            line_ids.append(lid)
        
        self.objects[object_id] = {
            'type': 'grid',
            'canvas_ids': line_ids,
            'transform': Transform(0, 0),
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def draw_bezier_curve(self, points, color="#FFFFFF", width=2, steps=50, object_id=None):
        """Draw a Bezier curve"""
        if len(points) < 2:
            return None
        
        if object_id is None:
            object_id = self._get_next_id()
        
        # Calculate curve points
        curve_points = []
        for i in range(steps + 1):
            t = i / steps
            x, y = self._bezier_point(points, t)
            curve_points.append((x, y))
        
        # Draw curve as connected lines
        line_ids = []
        for i in range(len(curve_points) - 1):
            lid = self.canvas.create_line(
                curve_points[i][0], curve_points[i][1],
                curve_points[i+1][0], curve_points[i+1][1],
                fill=color, width=width, smooth=True
            )
            line_ids.append(lid)
        
        self.objects[object_id] = {
            'type': 'bezier',
            'canvas_ids': line_ids,
            'transform': Transform(points[0][0], points[0][1]),
            'points': points,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def _bezier_point(self, points, t):
        """Calculate point on Bezier curve"""
        n = len(points) - 1
        x = y = 0
        
        for i, (px, py) in enumerate(points):
            # Binomial coefficient
            binomial = math.comb(n, i)
            # Bernstein polynomial
            bernstein = binomial * (t ** i) * ((1 - t) ** (n - i))
            x += px * bernstein
            y += py * bernstein
        
        return x, y
    
    # ==================== UI ELEMENTS ====================
    
    def draw_button(self, x, y, width, height, text, 
                   bg_color="#4CAF50", text_color="#FFFFFF",
                   hover_color="#45a049", font=("Arial", 14),
                   rounded=5, callback=None, object_id=None):
        """Draw an interactive button"""
        if object_id is None:
            object_id = self._get_next_id()
        
        # Background
        bg_id = self._create_rounded_rectangle(
            x, y, x + width, y + height, rounded, bg_color, "", 0
        )
        
        # Text
        text_id = self.canvas.create_text(
            x + width/2, y + height/2,
            text=text, font=font, fill=text_color
        )
        
        # Store button state
        button_state = {
            'bg_color': bg_color,
            'hover_color': hover_color,
            'hovering': False
        }
        
        # Hover handlers
        def on_enter(event):
            button_state['hovering'] = True
            self.canvas.itemconfig(bg_id, fill=hover_color)
        
        def on_leave(event):
            button_state['hovering'] = False
            self.canvas.itemconfig(bg_id, fill=bg_color)
        
        def on_click(event):
            if callback:
                callback()
        
        self.canvas.tag_bind(bg_id, '<Enter>', on_enter)
        self.canvas.tag_bind(bg_id, '<Leave>', on_leave)
        self.canvas.tag_bind(bg_id, '<Button-1>', on_click)
        self.canvas.tag_bind(text_id, '<Enter>', on_enter)
        self.canvas.tag_bind(text_id, '<Leave>', on_leave)
        self.canvas.tag_bind(text_id, '<Button-1>', on_click)
        
        self.objects[object_id] = {
            'type': 'button',
            'canvas_ids': [bg_id, text_id],
            'transform': Transform(x, y),
            'width': width,
            'height': height,
            'state': button_state,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def draw_progress_bar(self, x, y, width, height, progress,
                         bg_color="#333333", fill_color="#4CAF50",
                         border_color="#FFFFFF", border_width=2,
                         rounded=5, show_text=True, object_id=None):
        """Draw a progress bar"""
        if object_id is None:
            object_id = self._get_next_id()
        
        progress = self.clamp(progress, 0, 1)
        
        # Background
        bg_id = self._create_rounded_rectangle(
            x, y, x + width, y + height,
            rounded, bg_color, border_color, border_width
        )
        
        # Fill
        fill_width = (width - 4) * progress
        fill_id = None
        if fill_width > 0:
            fill_id = self._create_rounded_rectangle(
                x + 2, y + 2,
                x + 2 + fill_width, y + height - 2,
                max(0, rounded - 1), fill_color, "", 0
            )
        
        # Text
        text_id = None
        if show_text:
            text_id = self.canvas.create_text(
                x + width / 2, y + height / 2,
                text=f"{int(progress * 100)}%",
                font=("Arial", int(height * 0.5), "bold"),
                fill="#FFFFFF"
            )
        
        self.objects[object_id] = {
            'type': 'progress_bar',
            'canvas_ids': [bg_id, fill_id, text_id],
            'transform': Transform(x, y),
            'progress': progress,
            'width': width,
            'height': height,
            'fill_color': fill_color,
            'rounded': rounded,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def update_progress_bar(self, object_id, progress):
        """Update progress bar value"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        if obj['type'] != 'progress_bar':
            return
        
        progress = self.clamp(progress, 0, 1)
        obj['progress'] = progress
        
        # Delete old fill
        if obj['canvas_ids'][1]:
            self.canvas.delete(obj['canvas_ids'][1])
        
        # Redraw fill
        x = obj['transform'].x
        y = obj['transform'].y
        width = obj['width']
        height = obj['height']
        fill_width = (width - 4) * progress
        
        if fill_width > 0:
            fill_id = self._create_rounded_rectangle(
                x + 2, y + 2,
                x + 2 + fill_width, y + height - 2,
                max(0, obj['rounded'] - 1), obj['fill_color'], "", 0
            )
            obj['canvas_ids'][1] = fill_id
        
        # Update text
        if obj['canvas_ids'][2]:
            self.canvas.itemconfig(obj['canvas_ids'][2], text=f"{int(progress * 100)}%")
    
    def draw_slider(self, x, y, width, height, min_val, max_val, value,
                   bg_color="#333333", handle_color="#4CAF50",
                   callback=None, object_id=None):
        """Draw an interactive slider"""
        if object_id is None:
            object_id = self._get_next_id()
        
        value = self.clamp(value, min_val, max_val)
        
        # Track background
        track_id = self.canvas.create_rectangle(
            x, y + height//2 - 3,
            x + width, y + height//2 + 3,
            fill=bg_color, outline=""
        )
        
        # Handle position
        ratio = (value - min_val) / (max_val - min_val)
        handle_x = x + ratio * width
        
        # Handle
        handle_id = self.canvas.create_oval(
            handle_x - height//2, y,
            handle_x + height//2, y + height,
            fill=handle_color, outline="#FFFFFF", width=2
        )
        
        # Slider state
        slider_state = {
            'dragging': False,
            'min_val': min_val,
            'max_val': max_val,
            'value': value,
            'callback': callback
        }
        
        def on_drag(event):
            if slider_state['dragging']:
                # Calculate new value
                ratio = self.clamp((event.x - x) / width, 0, 1)
                new_value = min_val + ratio * (max_val - min_val)
                slider_state['value'] = new_value
                
                # Update handle position
                handle_x = x + ratio * width
                self.canvas.coords(
                    handle_id,
                    handle_x - height//2, y,
                    handle_x + height//2, y + height
                )
                
                if callback:
                    callback(new_value)
        
        def on_press(event):
            slider_state['dragging'] = True
            on_drag(event)
        
        def on_release(event):
            slider_state['dragging'] = False
        
        self.canvas.tag_bind(handle_id, '<Button-1>', on_press)
        self.canvas.tag_bind(handle_id, '<B1-Motion>', on_drag)
        self.canvas.tag_bind(handle_id, '<ButtonRelease-1>', on_release)
        
        self.objects[object_id] = {
            'type': 'slider',
            'canvas_ids': [track_id, handle_id],
            'transform': Transform(x, y),
            'state': slider_state,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    # ==================== GAME ENTITIES ====================
    
    def create_entity(self, x, y, width, height, sprite_type='rectangle',
                     color="#FFFFFF", velocity=(0, 0), collision_group=None,
                     entity_id=None):
        """Create a game entity with physics"""
        if entity_id is None:
            entity_id = self._get_next_id()
        
        # Draw sprite
        if sprite_type == 'rectangle':
            sprite_id = self.draw_rectangle(x, y, width, height, fill=color)
        elif sprite_type == 'circle':
            sprite_id = self.draw_circle(x, y, width/2, fill=color)
        else:
            sprite_id = self.draw_rectangle(x, y, width, height, fill=color)
        
        entity = {
            'id': entity_id,
            'sprite_id': sprite_id,
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'velocity': list(velocity),
            'acceleration': [0, 0],
            'collision_group': collision_group,
            'colliding': False,
            'active': True,
            'tags': set()
        }
        
        self.entities[entity_id] = entity
        
        if collision_group:
            if collision_group not in self.collision_groups:
                self.collision_groups[collision_group] = []
            self.collision_groups[collision_group].append(entity_id)
        
        return entity_id
    
    def update_entity(self, entity_id, dt):
        """Update entity physics"""
        if entity_id not in self.entities:
            return
        
        entity = self.entities[entity_id]
        if not entity['active']:
            return
        
        # Update velocity
        entity['velocity'][0] += entity['acceleration'][0] * dt
        entity['velocity'][1] += entity['acceleration'][1] * dt
        
        # Update position
        dx = entity['velocity'][0] * dt
        dy = entity['velocity'][1] * dt
        
        entity['x'] += dx
        entity['y'] += dy
        
        # Move sprite
        if entity['sprite_id'] in self.objects:
            obj = self.objects[entity['sprite_id']]
            if 'canvas_id' in obj:
                self.canvas.move(obj['canvas_id'], dx, dy)
                obj['transform'].x = entity['x']
                obj['transform'].y = entity['y']
    
    def set_entity_velocity(self, entity_id, vx, vy):
        """Set entity velocity"""
        if entity_id in self.entities:
            self.entities[entity_id]['velocity'] = [vx, vy]
    
    def set_entity_acceleration(self, entity_id, ax, ay):
        """Set entity acceleration"""
        if entity_id in self.entities:
            self.entities[entity_id]['acceleration'] = [ax, ay]
    
    def get_entity_position(self, entity_id):
        """Get entity position"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            return (entity['x'], entity['y'])
        return None
    
    def set_entity_position(self, entity_id, x, y):
        """Set entity position"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            dx = x - entity['x']
            dy = y - entity['y']
            entity['x'] = x
            entity['y'] = y
            
            if entity['sprite_id'] in self.objects:
                obj = self.objects[entity['sprite_id']]
                if 'canvas_id' in obj:
                    self.canvas.move(obj['canvas_id'], dx, dy)
                    obj['transform'].x = x
                    obj['transform'].y = y
    
    def add_entity_tag(self, entity_id, tag):
        """Add tag to entity"""
        if entity_id in self.entities:
            self.entities[entity_id]['tags'].add(tag)
    
    def remove_entity_tag(self, entity_id, tag):
        """Remove tag from entity"""
        if entity_id in self.entities:
            self.entities[entity_id]['tags'].discard(tag)
    
    def has_entity_tag(self, entity_id, tag):
        """Check if entity has tag"""
        if entity_id in self.entities:
            return tag in self.entities[entity_id]['tags']
        return False
    
    def find_entities_with_tag(self, tag):
        """Find all entities with specific tag"""
        return [eid for eid, entity in self.entities.items() if tag in entity['tags']]
    
    def check_collision(self, entity1_id, entity2_id):
        """Check collision between two entities (AABB)"""
        if entity1_id not in self.entities or entity2_id not in self.entities:
            return False
        
        e1 = self.entities[entity1_id]
        e2 = self.entities[entity2_id]
        
        return (e1['x'] < e2['x'] + e2['width'] and
                e1['x'] + e1['width'] > e2['x'] and
                e1['y'] < e2['y'] + e2['height'] and
                e1['y'] + e1['height'] > e2['y'])
    
    def check_collision_group(self, entity_id, group):
        """Check collision with all entities in a group"""
        if group not in self.collision_groups:
            return []
        
        collisions = []
        for other_id in self.collision_groups[group]:
            if other_id != entity_id and self.check_collision(entity_id, other_id):
                collisions.append(other_id)
        
        return collisions
    
    def check_collision_point(self, entity_id, x, y):
        """Check if point is inside entity"""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        return self.point_in_rect(x, y, entity['x'], entity['y'], 
                                  entity['width'], entity['height'])
    
    def apply_gravity(self, entity_id, gravity=500):
        """Apply gravity to entity"""
        if entity_id in self.entities:
            self.entities[entity_id]['acceleration'][1] = gravity
    
    def delete_entity(self, entity_id):
        """Delete an entity"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            
            # Remove from collision group
            if entity['collision_group'] in self.collision_groups:
                if entity_id in self.collision_groups[entity['collision_group']]:
                    self.collision_groups[entity['collision_group']].remove(entity_id)
            
            # Delete sprite
            if entity['sprite_id'] in self.objects:
                self.delete_object(entity['sprite_id'])
            
            del self.entities[entity_id]
    
    # ==================== ANIMATIONS ====================
    
    def animate(self, object_id, property_name, from_value, to_value,
               duration=1.0, easing=AnimationType.LINEAR, delay=0, callback=None):
        """Animate an object property"""
        animation = {
            'object_id': object_id,
            'property': property_name,
            'from': from_value,
            'to': to_value,
            'duration': duration,
            'elapsed': 0,
            'delay': delay,
            'easing': easing,
            'callback': callback,
            'started': False
        }
        
        self.animations.append(animation)
        
        if not self.is_running:
            self._start_main_loop()
    
    def stop_animation(self, object_id):
        """Stop all animations for an object"""
        self.animations = [anim for anim in self.animations 
                          if anim['object_id'] != object_id]
    
    def _apply_easing(self, t, easing_type):
        """Apply easing function to time value (0-1)"""
        if easing_type == AnimationType.LINEAR:
            return t
        elif easing_type == AnimationType.EASE_IN:
            return t * t
        elif easing_type == AnimationType.EASE_OUT:
            return t * (2 - t)
        elif easing_type == AnimationType.EASE_IN_OUT:
            return t * t * (3 - 2 * t)
        elif easing_type == AnimationType.BOUNCE:
            if t < 0.5:
                return 8 * t * t * t * t
            else:
                t = t - 1
                return 1 - 8 * t * t * t * t
        elif easing_type == AnimationType.ELASTIC:
            return math.sin(13 * math.pi / 2 * t) * math.pow(2, -10 * t)
        elif easing_type == AnimationType.SPRING:
            return 1 + (-math.exp(-6 * t) * math.cos(20 * t))
        elif easing_type == AnimationType.CUBIC:
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - math.pow(-2 * t + 2, 3) / 2
        elif easing_type == AnimationType.BACK:
            c1 = 1.70158
            c3 = c1 + 1
            return c3 * t * t * t - c1 * t * t
        elif easing_type == AnimationType.CIRC:
            return 1 - math.sqrt(1 - t * t)
        return t
    
    def _update_animations(self, dt):
        """Update all active animations"""
        for anim in self.animations[:]:
            # Handle delay
            if anim['delay'] > 0:
                anim['delay'] -= dt
                continue
            
            if not anim['started']:
                anim['started'] = True
            
            anim['elapsed'] += dt
            
            if anim['elapsed'] >= anim['duration']:
                t = 1.0
                anim['elapsed'] = anim['duration']
                self.animations.remove(anim)
            else:
                t = anim['elapsed'] / anim['duration']
            
            t = self._apply_easing(t, anim['easing'])
            
            from_val = anim['from']
            to_val = anim['to']
            current_val = from_val + (to_val - from_val) * t
            
            obj_id = anim['object_id']
            if obj_id in self.objects:
                obj = self.objects[obj_id]
                
                if anim['property'] == 'x':
                    dx = current_val - obj['transform'].x
                    obj['transform'].x = current_val
                    if 'canvas_id' in obj:
                        self.canvas.move(obj['canvas_id'], dx, 0)
                    elif 'canvas_ids' in obj:
                        for cid in obj['canvas_ids']:
                            if cid:
                                self.canvas.move(cid, dx, 0)
                
                elif anim['property'] == 'y':
                    dy = current_val - obj['transform'].y
                    obj['transform'].y = current_val
                    if 'canvas_id' in obj:
                        self.canvas.move(obj['canvas_id'], 0, dy)
                    elif 'canvas_ids' in obj:
                        for cid in obj['canvas_ids']:
                            if cid:
                                self.canvas.move(cid, 0, dy)
                
                elif anim['property'] == 'opacity':
                    obj['transform'].opacity = current_val
                
                elif anim['property'] == 'rotation':
                    obj['transform'].rotation = current_val
                
                elif anim['property'] == 'scale':
                    obj['transform'].scale_x = current_val
                    obj['transform'].scale_y = current_val
            
            if t >= 1.0 and anim['callback']:
                anim['callback']()
    
    # ==================== PLOTTING ====================
    
    def plot_line(self, x_data, y_data, x=50, y=50, width=700, height=400,
                 line_color="#00FF00", point_color="#FF0000", show_points=True,
                 show_grid=True, title="", xlabel="", ylabel="", object_id=None):
        """Plot a line graph"""
        if object_id is None:
            object_id = self._get_next_id()
        
        plot_ids = []
        
        # Background
        bg_id = self.canvas.create_rectangle(
            x, y, x + width, y + height, fill="#FFFFFF", outline="#000000", width=2
        )
        plot_ids.append(bg_id)
        
        # Grid
        if show_grid:
            grid_color = "#E0E0E0"
            for i in range(5):
                gx = x + (width * i / 4)
                gy = y + (height * i / 4)
                plot_ids.append(self.canvas.create_line(gx, y, gx, y + height, fill=grid_color))
                plot_ids.append(self.canvas.create_line(x, gy, x + width, gy, fill=grid_color))
        
        if not x_data or not y_data:
            return object_id
        
        # Scale data
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        # Convert to plot coordinates
        plot_points = []
        for xd, yd in zip(x_data, y_data):
            px = x + ((xd - x_min) / x_range) * width
            py = y + height - ((yd - y_min) / y_range) * height
            plot_points.append((px, py))
        
        # Draw line
        for i in range(len(plot_points) - 1):
            lid = self.canvas.create_line(
                plot_points[i][0], plot_points[i][1],
                plot_points[i+1][0], plot_points[i+1][1],
                fill=line_color, width=2
            )
            plot_ids.append(lid)
        
        # Draw points
        if show_points:
            for px, py in plot_points:
                pid = self.canvas.create_oval(
                    px - 3, py - 3, px + 3, py + 3,
                    fill=point_color, outline=point_color
                )
                plot_ids.append(pid)
        
        # Title and labels
        if title:
            tid = self.canvas.create_text(
                x + width/2, y - 20, text=title,
                font=("Arial", 14, "bold"), fill="#000000"
            )
            plot_ids.append(tid)
        
        if xlabel:
            xlid = self.canvas.create_text(
                x + width/2, y + height + 30, text=xlabel,
                font=("Arial", 10), fill="#000000"
            )
            plot_ids.append(xlid)
        
        if ylabel:
            ylid = self.canvas.create_text(
                x - 30, y + height/2, text=ylabel,
                font=("Arial", 10), fill="#000000", angle=90
            )
            plot_ids.append(ylid)
        
        self.objects[object_id] = {
            'type': 'plot',
            'canvas_ids': plot_ids,
            'transform': Transform(x, y),
            'data': {'x': x_data, 'y': y_data},
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def plot_bar(self, labels, values, x=50, y=50, width=700, height=400,
                bar_color="#4CAF50", title="", object_id=None):
        """Plot a bar chart"""
        if object_id is None:
            object_id = self._get_next_id()
        
        plot_ids = []
        
        # Background
        bg_id = self.canvas.create_rectangle(
            x, y, x + width, y + height, fill="#FFFFFF", outline="#000000", width=2
        )
        plot_ids.append(bg_id)
        
        if not labels or not values:
            return object_id
        
        # Calculate bar dimensions
        num_bars = len(labels)
        bar_width = (width * 0.8) / num_bars
        spacing = (width * 0.2) / (num_bars + 1)
        max_val = max(values) if values else 1
        
        # Draw bars
        for i, (label, value) in enumerate(zip(labels, values)):
            bar_height = (value / max_val) * (height * 0.8)
            bar_x = x + spacing + i * (bar_width + spacing)
            bar_y = y + height - bar_height - 40
            
            # Bar
            bid = self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + bar_width, y + height - 40,
                fill=bar_color, outline="#000000"
            )
            plot_ids.append(bid)
            
            # Label
            lid = self.canvas.create_text(
                bar_x + bar_width/2, y + height - 20,
                text=str(label), font=("Arial", 8), fill="#000000"
            )
            plot_ids.append(lid)
            
            # Value
            vid = self.canvas.create_text(
                bar_x + bar_width/2, bar_y - 10,
                text=str(value), font=("Arial", 8, "bold"), fill="#000000"
            )
            plot_ids.append(vid)
        
        # Title
        if title:
            tid = self.canvas.create_text(
                x + width/2, y + 20, text=title,
                font=("Arial", 14, "bold"), fill="#000000"
            )
            plot_ids.append(tid)
        
        self.objects[object_id] = {
            'type': 'bar_chart',
            'canvas_ids': plot_ids,
            'transform': Transform(x, y),
            'data': {'labels': labels, 'values': values},
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    # ==================== 3D RENDERING ====================
    
    def draw_cube_3d(self, x, y, size, rotation_x=0, rotation_y=0,
                    face_colors=None, object_id=None):
        """Draw a pseudo-3D cube"""
        if object_id is None:
            object_id = self._get_next_id()
        
        if face_colors is None:
            face_colors = ["#FF0000", "#00FF00", "#0000FF", 
                          "#FFFF00", "#FF00FF", "#00FFFF"]
        
        # Cube vertices
        s = size / 2
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
        ]
        
        # Apply rotation
        rx, ry = math.radians(rotation_x), math.radians(rotation_y)
        
        rotated = []
        for vx, vy, vz in vertices:
            # Rotate Y
            x_rot = vx * math.cos(ry) - vz * math.sin(ry)
            z_rot = vx * math.sin(ry) + vz * math.cos(ry)
            
            # Rotate X
            y_rot = vy * math.cos(rx) - z_rot * math.sin(rx)
            z_final = vy * math.sin(rx) + z_rot * math.cos(rx)
            
            # Project to 2D
            scale = 200 / (200 + z_final)
            x_proj = x + x_rot * scale
            y_proj = y + y_rot * scale
            
            rotated.append((x_proj, y_proj, z_final))
        
        # Define faces
        faces = [
            ([0, 1, 2, 3], 0), ([4, 5, 6, 7], 1),
            ([0, 1, 5, 4], 2), ([2, 3, 7, 6], 3),
            ([0, 3, 7, 4], 4), ([1, 2, 6, 5], 5),
        ]
        
        # Sort by depth
        face_data = []
        for face_indices, color_idx in faces:
            avg_z = sum(rotated[i][2] for i in face_indices) / len(face_indices)
            face_data.append((avg_z, face_indices, color_idx))
        
        face_data.sort(key=lambda f: f[0])
        
        # Draw faces
        face_ids = []
        for _, face_indices, color_idx in face_data:
            points = [rotated[i][:2] for i in face_indices]
            flat_points = [coord for point in points for coord in point]
            
            face_id = self.canvas.create_polygon(
                flat_points,
                fill=face_colors[color_idx],
                outline="#000000",
                width=2
            )
            face_ids.append(face_id)
        
        self.objects[object_id] = {
            'type': 'cube_3d',
            'canvas_ids': face_ids,
            'transform': Transform(x, y, 0),
            'size': size,
            'rotation_x': rotation_x,
            'rotation_y': rotation_y,
            'face_colors': face_colors,
            'layer': self.current_layer
        }
        self.layers[self.current_layer].objects.append(object_id)
        
        return object_id
    
    def rotate_cube_3d(self, object_id, rotation_x, rotation_y):
        """Update 3D cube rotation"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        if obj['type'] != 'cube_3d':
            return
        
        # Delete old faces
        for cid in obj['canvas_ids']:
            self.canvas.delete(cid)
        
        # Redraw with new rotation
        x, y = obj['transform'].x, obj['transform'].y
        size = obj['size']
        face_colors = obj['face_colors']
        
        # Same logic as draw_cube_3d
        s = size / 2
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
        ]
        
        rx, ry = math.radians(rotation_x), math.radians(rotation_y)
        
        rotated = []
        for vx, vy, vz in vertices:
            x_rot = vx * math.cos(ry) - vz * math.sin(ry)
            z_rot = vx * math.sin(ry) + vz * math.cos(ry)
            
            y_rot = vy * math.cos(rx) - z_rot * math.sin(rx)
            z_final = vy * math.sin(rx) + z_rot * math.cos(rx)
            
            scale = 200 / (200 + z_final)
            x_proj = x + x_rot * scale
            y_proj = y + y_rot * scale
            
            rotated.append((x_proj, y_proj, z_final))
        
        faces = [
            ([0, 1, 2, 3], 0), ([4, 5, 6, 7], 1),
            ([0, 1, 5, 4], 2), ([2, 3, 7, 6], 3),
            ([0, 3, 7, 4], 4), ([1, 2, 6, 5], 5),
        ]
        
        face_data = []
        for face_indices, color_idx in faces:
            avg_z = sum(rotated[i][2] for i in face_indices) / len(face_indices)
            face_data.append((avg_z, face_indices, color_idx))
        
        face_data.sort(key=lambda f: f[0])
        
        face_ids = []
        for _, face_indices, color_idx in face_data:
            points = [rotated[i][:2] for i in face_indices]
            flat_points = [coord for point in points for coord in point]
            
            face_id = self.canvas.create_polygon(
                flat_points,
                fill=face_colors[color_idx],
                outline="#000000",
                width=2
            )
            face_ids.append(face_id)
        
        obj['canvas_ids'] = face_ids
        obj['rotation_x'] = rotation_x
        obj['rotation_y'] = rotation_y
    
    # ==================== FRAME CAPTURE ====================
    
    def start_recording(self, format="PNG"):
        """Start recording frames"""
        self.recording = True
        self.recorded_frames = []
        self.frame_format = format.upper()
    
    def stop_recording(self):
        """Stop recording frames"""
        self.recording = False
        return len(self.recorded_frames)
    
    def capture_frame(self):
        """Capture current frame"""
        if not self.recording:
            return None
        
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        
        img = ImageGrab.grab(bbox=(x, y, x + self.width, y + self.height))
        self.recorded_frames.append(img)
        
        return img
    
    def save_frames(self, directory="frames", prefix="frame_"):
        """Save all recorded frames"""
        import os
        os.makedirs(directory, exist_ok=True)
        
        for i, frame in enumerate(self.recorded_frames):
            filename = f"{directory}/{prefix}{i:05d}.{self.frame_format.lower()}"
            frame.save(filename, self.frame_format)
        
        return len(self.recorded_frames)
    
    def export_gif(self, filename="animation.gif", duration=50, loop=0):
        """Export frames as GIF"""
        if not self.recorded_frames:
            return False
        
        self.recorded_frames[0].save(
            filename,
            save_all=True,
            append_images=self.recorded_frames[1:],
            duration=duration,
            loop=loop
        )
        
        return True
    
    # ==================== OBJECT MANAGEMENT ====================
    
    def delete_object(self, object_id):
        """Delete an object from canvas"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        
        if 'canvas_id' in obj:
            self.canvas.delete(obj['canvas_id'])
        elif 'canvas_ids' in obj:
            for cid in obj['canvas_ids']:
                if cid:
                    self.canvas.delete(cid)
        
        # Remove from layer
        if 'layer' in obj and obj['layer'] in self.layers:
            if object_id in self.layers[obj['layer']].objects:
                self.layers[obj['layer']].objects.remove(object_id)
        
        del self.objects[object_id]
    
    def clear(self):
        """Clear entire canvas"""
        self.canvas.delete("all")
        self.objects.clear()
        self.animations.clear()
        self.entities.clear()
        self.collision_groups.clear()
        self.lights.clear()
        self.sprites.clear()
        self.tilemaps.clear()
        self.physics_bodies.clear()
        self.state_machines.clear()
        
        for layer in self.layers.values():
            layer.objects.clear()
    
    def get_object(self, object_id):
        """Get object by ID"""
        return self.objects.get(object_id)
    
    def get_object_bounds(self, object_id):
        """Get bounding box of object"""
        if object_id not in self.objects:
            return None
        
        obj = self.objects[object_id]
        
        if 'canvas_id' in obj:
            return self.canvas.bbox(obj['canvas_id'])
        elif 'canvas_ids' in obj and obj['canvas_ids']:
            all_bounds = [self.canvas.bbox(cid) for cid in obj['canvas_ids'] if cid]
            if not all_bounds:
                return None
            
            all_bounds = [b for b in all_bounds if b]
            if not all_bounds:
                return None
            
            x1 = min(b[0] for b in all_bounds)
            y1 = min(b[1] for b in all_bounds)
            x2 = max(b[2] for b in all_bounds)
            y2 = max(b[3] for b in all_bounds)
            
            return (x1, y1, x2, y2)
        
        return None
    
    def move_object(self, object_id, dx, dy):
        """Move object by delta"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        obj['transform'].x += dx
        obj['transform'].y += dy
        
        if 'canvas_id' in obj:
            self.canvas.move(obj['canvas_id'], dx, dy)
        elif 'canvas_ids' in obj:
            for cid in obj['canvas_ids']:
                if cid:
                    self.canvas.move(cid, dx, dy)
    
    def set_object_position(self, object_id, x, y):
        """Set object position"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        dx = x - obj['transform'].x
        dy = y - obj['transform'].y
        self.move_object(object_id, dx, dy)
    
    def hide_object(self, object_id):
        """Hide object"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        if 'canvas_id' in obj:
            self.canvas.itemconfig(obj['canvas_id'], state=tk.HIDDEN)
        elif 'canvas_ids' in obj:
            for cid in obj['canvas_ids']:
                if cid:
                    self.canvas.itemconfig(cid, state=tk.HIDDEN)
    
    def show_object(self, object_id):
        """Show object"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        if 'canvas_id' in obj:
            self.canvas.itemconfig(obj['canvas_id'], state=tk.NORMAL)
        elif 'canvas_ids' in obj:
            for cid in obj['canvas_ids']:
                if cid:
                    self.canvas.itemconfig(cid, state=tk.NORMAL)
    
    def set_object_color(self, object_id, color):
        """Set object fill color"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        if 'canvas_id' in obj:
            self.canvas.itemconfig(obj['canvas_id'], fill=color)
    
    def set_background(self, color):
        """Set canvas background color"""
        self.bg_color = color
        self.canvas.configure(bg=color)
    
    def set_background_image(self, image_path):
        """Set background image"""
        try:
            img = Image.open(image_path)
            img = img.resize((self.width, self.height), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)
        except Exception as e:
            print(f"Error loading background image: {e}")
    
    # ==================== EVENT HANDLING ====================
    
    def on_click(self, object_id, callback):
        """Add click event handler to object"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        
        def handle_click(event):
            callback(event)
        
        if 'canvas_id' in obj:
            self.canvas.tag_bind(obj['canvas_id'], '<Button-1>', handle_click)
        elif 'canvas_ids' in obj:
            for cid in obj['canvas_ids']:
                if cid:
                    self.canvas.tag_bind(cid, '<Button-1>', handle_click)
    
    def on_hover(self, object_id, enter_callback, leave_callback=None):
        """Add hover event handlers to object"""
        if object_id not in self.objects:
            return
        
        obj = self.objects[object_id]
        
        def handle_enter(event):
            enter_callback(event)
        
        def handle_leave(event):
            if leave_callback:
                leave_callback(event)
        
        if 'canvas_id' in obj:
            self.canvas.tag_bind(obj['canvas_id'], '<Enter>', handle_enter)
            self.canvas.tag_bind(obj['canvas_id'], '<Leave>', handle_leave)
        elif 'canvas_ids' in obj:
            for cid in obj['canvas_ids']:
                if cid:
                    self.canvas.tag_bind(cid, '<Enter>', handle_enter)
                    self.canvas.tag_bind(cid, '<Leave>', handle_leave)
    
    def add_update_callback(self, callback):
        """Add update callback to game loop"""
        self.update_callbacks.append(callback)
    
    def remove_update_callback(self, callback):
        """Remove update callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
    
    def add_draw_callback(self, callback):
        """Add draw callback to game loop"""
        self.draw_callbacks.append(callback)
    
    def remove_draw_callback(self, callback):
        """Remove draw callback"""
        if callback in self.draw_callbacks:
            self.draw_callbacks.remove(callback)
    
    # ==================== PERFORMANCE ====================
    
    def get_performance_metrics(self):
        """Get performance metrics"""
        self.performance_metrics['objects'] = len(self.objects)
        self.performance_metrics['entities'] = len(self.entities)
        return self.performance_metrics.copy()
    
    def draw_fps_counter(self, x=10, y=10, object_id=None):
        """Draw FPS counter"""
        if object_id is None:
            object_id = "_fps_counter"
        
        if object_id in self.objects:
            self.delete_object(object_id)
        
        fps_text = f"FPS: {self._actual_fps}"
        return self.draw_text(fps_text, x, y, font=("Arial", 12, "bold"),
                            color="#00FF00", anchor="nw", object_id=object_id)
    
    def enable_vsync(self):
        """Enable VSync (frame limiting)"""
        self.frame_delay = 1000 // self.fps
    
    def disable_vsync(self):
        """Disable VSync"""
        self.frame_delay = 0
    
    def set_fps(self, fps):
        """Set target FPS"""
        self.fps = fps
        self.frame_delay = 1000 // fps
    
    def get_fps(self):
        """Get current FPS"""
        return self._actual_fps
    
    def get_delta_time(self):
        """Get delta time since last frame"""
        return self._delta_time
    
    def get_frame_count(self):
        """Get total frame count"""
        return self._frame_count
    
    # ==================== FILE I/O ====================
    
    def save_scene(self, filename):
        """Save scene to JSON file"""
        scene_data = {
            'width': self.width,
            'height': self.height,
            'bg_color': self.bg_color,
            'camera': {
                'x': self.camera.x,
                'y': self.camera.y,
                'zoom': self.camera.zoom,
                'rotation': self.camera.rotation
            },
            'layers': {},
            'objects': {}
        }
        
        # Save layers
        for name, layer in self.layers.items():
            scene_data['layers'][name] = {
                'visible': layer.visible,
                'opacity': layer.opacity,
                'parallax_x': layer.parallax_x,
                'parallax_y': layer.parallax_y
            }
        
        with open(filename, 'w') as f:
            json.dump(scene_data, f, indent=2)
    
    def save_as_image(self, filename, format="PNG"):
        """Save canvas as image"""
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        
        img = ImageGrab.grab(bbox=(x, y, x + self.width, y + self.height))
        img.save(filename, format)
    
    # ==================== MAIN LOOP ====================
    
    def start_game_loop(self, update_callback=None, draw_callback=None):
        """Start game loop"""
        if update_callback:
            self.add_update_callback(update_callback)
        if draw_callback:
            self.add_draw_callback(draw_callback)
        
        self.is_running = True
        self._last_time = time.time()
        self._main_loop()
    
    def _start_main_loop(self):
        """Start main loop (internal)"""
        if not self.is_running:
            self.is_running = True
            self._last_time = time.time()
            self._main_loop()
    
    def _main_loop(self):
        """Main game loop"""
        if not self.is_running:
            return
        
        current_time = time.time()
        dt = current_time - self._last_time
        self._delta_time = dt
        self._last_time = current_time
        
        # Update FPS counter
        self._fps_counter += 1
        if current_time - self._fps_time >= 1.0:
            self._actual_fps = self._fps_counter
            self._fps_counter = 0
            self._fps_time = current_time
        
        # Update camera
        self._update_camera(dt)
        
        # Update sprites
        self._update_sprites(dt)
        
        # Update physics
        if self.physics_enabled:
            physics_start = time.time()
            self._update_physics(dt)
            self.performance_metrics['physics_time'] = time.time() - physics_start
        
        # Update entities
        for entity_id in list(self.entities.keys()):
            self.update_entity(entity_id, dt)
        
        # Update animations
        self._update_animations(dt)
        
        # Update state machines
        self._update_state_machines(dt)
        
        # Call user update callbacks
        for callback in self.update_callbacks:
            callback(dt)
        
        # Call user draw callbacks
        for callback in self.draw_callbacks:
            callback()
        
        # Capture frame if recording
        if self.recording:
            self.capture_frame()
        
        # Clear input buffers
        self._clear_input_buffers()
        
        # Update frame count
        self._frame_count += 1
        
        # Update performance metrics
        self.performance_metrics['frame_time'] = time.time() - current_time
        
        # Schedule next frame
        if self.is_running:
            self.root.after(max(1, self.frame_delay), self._main_loop)
    
    def stop(self):
        """Stop the game loop"""
        self.is_running = False
    
    def pause(self):
        """Pause the game loop"""
        self.is_running = False
    
    def resume(self):
        """Resume the game loop"""
        if not self.is_running:
            self.is_running = True
            self._last_time = time.time()
            self._main_loop()
    
    def run(self):
        """Start the main event loop"""
        if not self.is_running:
            self._start_main_loop()
        self.root.mainloop()
    
    def quit(self):
        """Quit the application"""
        self.is_running = False
        self.root.quit()
        self.root.destroy()


# ==================== UTILITY CLASSES ====================

class Vector2:
    """2D Vector class for game development"""
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
    def magnitude(self):
        """Get vector magnitude"""
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        """Get normalized vector"""
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2(0, 0)
    
    def dot(self, other):
        """Dot product"""
        return self.x * other.x + self.y * other.y
    
    def cross(self, other):
        """Cross product (2D returns scalar)"""
        return self.x * other.y - self.y * other.x
    
    def distance_to(self, other):
        """Distance to another vector"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def angle_to(self, other):
        """Angle to another vector"""
        return math.atan2(other.y - self.y, other.x - self.x)
    
    def rotate(self, angle):
        """Rotate vector by angle (radians)"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def lerp(self, other, t):
        """Linear interpolation"""
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def to_tuple(self):
        """Convert to tuple"""
        return (self.x, self.y)
    
    @staticmethod
    def from_angle(angle, length=1):
        """Create vector from angle and length"""
        return Vector2(math.cos(angle) * length, math.sin(angle) * length)
    
    @staticmethod
    def zero():
        """Zero vector"""
        return Vector2(0, 0)
    
    @staticmethod
    def one():
        """One vector"""
        return Vector2(1, 1)
    
    @staticmethod
    def up():
        """Up vector"""
        return Vector2(0, -1)
    
    @staticmethod
    def down():
        """Down vector"""
        return Vector2(0, 1)
    
    @staticmethod
    def left():
        """Left vector"""
        return Vector2(-1, 0)
    
    @staticmethod
    def right():
        """Right vector"""
        return Vector2(1, 0)


class Color:
    """Color utility class"""
    
    def __init__(self, r, g, b, a=255):
        self.r = max(0, min(255, int(r)))
        self.g = max(0, min(255, int(g)))
        self.b = max(0, min(255, int(b)))
        self.a = max(0, min(255, int(a)))
    
    def to_hex(self):
        """Convert to hex string"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def to_tuple(self):
        """Convert to RGBA tuple"""
        return (self.r, self.g, self.b, self.a)
    
    def to_tuple_normalized(self):
        """Convert to normalized RGBA tuple (0-1)"""
        return (self.r/255, self.g/255, self.b/255, self.a/255)
    
    @staticmethod
    def from_hex(hex_str):
        """Create color from hex string"""
        hex_str = hex_str.lstrip('#')
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return Color(r, g, b)
    
    @staticmethod
    def lerp(color1, color2, t):
        """Linear interpolation between colors"""
        r = int(color1.r + (color2.r - color1.r) * t)
        g = int(color1.g + (color2.g - color1.g) * t)
        b = int(color1.b + (color2.b - color1.b) * t)
        a = int(color1.a + (color2.a - color1.a) * t)
        return Color(r, g, b, a)
    
    # Color constants
    @staticmethod
    def red(): return Color(255, 0, 0)
    
    @staticmethod
    def green(): return Color(0, 255, 0)
    
    @staticmethod
    def blue(): return Color(0, 0, 255)
    
    @staticmethod
    def white(): return Color(255, 255, 255)
    
    @staticmethod
    def black(): return Color(0, 0, 0)
    
    @staticmethod
    def yellow(): return Color(255, 255, 0)
    
    @staticmethod
    def cyan(): return Color(0, 255, 255)
    
    @staticmethod
    def magenta(): return Color(255, 0, 255)
    
    @staticmethod
    def orange(): return Color(255, 165, 0)
    
    @staticmethod
    def purple(): return Color(128, 0, 128)
    
    @staticmethod
    def gray(): return Color(128, 128, 128)


class Timer:
    """Timer utility for game development"""
    
    def __init__(self, duration, callback, repeat=False, auto_start=True):
        self.duration = duration
        self.callback = callback
        self.repeat = repeat
        self.elapsed = 0
        self.active = auto_start
    
    def update(self, dt):
        """Update timer"""
        if not self.active:
            return
        
        self.elapsed += dt
        
        if self.elapsed >= self.duration:
            if self.callback:
                self.callback()
            
            if self.repeat:
                self.elapsed = 0
            else:
                self.active = False
    
    def reset(self):
        """Reset timer"""
        self.elapsed = 0
    
    def start(self):
        """Start timer"""
        self.active = True
    
    def stop(self):
        """Stop timer"""
        self.active = False
    
    def restart(self):
        """Restart timer"""
        self.elapsed = 0
        self.active = True
    
    def get_progress(self):
        """Get progress (0-1)"""
        return min(1.0, self.elapsed / self.duration)
    
    def get_remaining(self):
        """Get remaining time"""
        return max(0, self.duration - self.elapsed)
    
    def is_finished(self):
        """Check if timer is finished"""
        return self.elapsed >= self.duration


class Easing:
    """Easing functions collection"""
    
    @staticmethod
    def linear(t): return t
    
    @staticmethod
    def ease_in_quad(t): return t * t
    
    @staticmethod
    def ease_out_quad(t): return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t):
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t): return t * t * t
    
    @staticmethod
    def ease_out_cubic(t):
        t -= 1
        return t * t * t + 1
    
    @staticmethod
    def ease_in_out_cubic(t):
        return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_in_quart(t): return t * t * t * t
    
    @staticmethod
    def ease_out_quart(t):
        t -= 1
        return 1 - t * t * t * t
    
    @staticmethod
    def ease_in_out_quart(t):
        return 8 * t * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 4) / 2
    
    @staticmethod
    def bounce_out(t):
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    
    @staticmethod
    def elastic_out(t):
        c4 = (2 * math.pi) / 3
        return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


# Quick start helper
def create_window(width=800, height=600, title="Graphics Engine", bg_color="#1a1a1a", fps=60):
    """Quick helper to create a graphics window"""
    return GraphicalCanvas(width, height, title, bg_color, fps)


if __name__ == "__main__":
    canvas = GraphicalCanvas(800, 600, "Graphics Engine")
    canvas.draw_text("gfxcanvas v1.0.0", 400, 300, font=("Arial", 32, "bold"))
    canvas.run()
