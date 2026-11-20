from ursina import *
import math, random, sys

app = Ursina()
window.color = color.rgb(10, 15, 24)
window.fps_counter.enabled = True

scene.fog_color = color.rgb(10, 15, 24)
scene.fog_density = 0.035

ground = Entity(
    model='plane', scale=(200, 1, 200),
    color=color.rgb(223, 232, 255),
    texture='white_cube', texture_scale=(40, 40),
    collider='box'
)

for i in range(8):
    for side in (-8, 8):
        Entity(
            model='cube',
            position=(side, 6, -20 - i * 14),
            scale=(6, 12 + random.random() * 6, 8),
            color=color.rgb(42, 47, 58),
            collider='box'
        )

lamps = []
for i in range(6):
    x = -5 if i % 2 else 5
    Entity(model='cube', position=(x, 2.5, -10 - i * 20),
           scale=(0.15, 5, 0.15), color=color.dark_gray)
    l = PointLight(position=(x, 5, -10 - i * 20),
                   color=color.rgb(255, 170, 85))
    lamps.append(l)

snow = [Entity(model='cube', scale=0.06, color=color.white,
               position=(random.uniform(-60, 60),
                         random.uniform(0, 40),
                         random.uniform(-60, 60)))
        for _ in range(800)]

def update_snow():
    for s in snow:
        s.y -= 3 * time.dt
        s.x += math.sin(time.time() + s.z) * 0.5 * time.dt
        if s.y < 0:
            s.y = 40
            s.x = random.uniform(-60, 60)
            s.z = random.uniform(-60, 60)

player = FirstPersonController(
    position=(0, 1.7, 0),
    speed=4,
    mouse_sensitivity=Vec2(60, 60)
)
player.cursor.visible = False

stamina = 100
running = False
footprints = []

def add_footprint():
    p = Entity(
        model='quad',
        position=(player.x, 0.02, player.z),
        rotation=(90, player.rotation_y, 0),
        scale=(0.22, 0.35),
        color=color.rgba(170, 187, 204, 200),
        texture='circle'
    )
    p.animate_color(color.rgba(170, 187, 204, 0), duration=15)
    footprints.append(p)
    destroy(p, delay=15)
    if len(footprints) > 80:
        footprints.pop(0)

man = Entity(
    model='cube',
    scale=(0.7, 1.9, 0.4),
    color=color.rgb(15, 15, 15),
    position=(0, 1.7, -40)
)
eye_l = Entity(parent=man, model='sphere', scale=0.12,
               position=(-0.15, 0.75, 0.2), color=color.red, unlit=True)
eye_r = Entity(parent=man, model='sphere', scale=0.12,
               position=(0.15, 0.75, 0.2), color=color.red, unlit=True)
man_light = PointLight(parent=man, color=color.red, distance=8)

man_speed = 3.2
caught = False

def update_man():
    global caught
    if caught:
        return
    target = Vec3(player.x, 1.7, player.z)
    d = target - man.position
    d.y = 0
    if d.length() > 0.3:
        d = d.normalized()
        man.position += d * man_speed * time.dt
    man.look_at(Vec3(player.x, man.y, player.z))
    man.rotation_x = 0

    dist = distance(man.position, player.position)
    danger_alpha = clamp(1 - dist / 25, 0, 0.7)
    camera.ui.color = color.rgba(120, 0, 0, danger_alpha)

    if dist < 1.4:
        caught = True
        Text(text="ОН ТЕБЯ ПОЙМАЛ", origin=0, scale=3, color=color.red)

touch_joystick = Entity(
    parent=camera.ui, model='circle',
    color=color.rgba(255, 255, 255, 40),
    position=(-0.7, -0.4), scale=0.25
)
stick = Entity(
    parent=camera.ui, model='circle',
    color=color.rgba(255, 255, 255, 120),
    position=(-0.7, -0.4), scale=0.12
)

btn_run = Button(
    parent=camera.ui, text='БЕГ',
    position=(0.7, -0.4), scale=(0.2, 0.12),
    color=color.rgba(200, 30, 30, 120)
)
btn_freeze = Button(
    parent=camera.ui, text='ЗАМЕРЕТЬ',
    position=(-0.7, 0.45), scale=(0.25, 0.1),
    color=color.rgba(0, 80, 120, 120)
)

frozen = False
joystick_vec = Vec2(0, 0)

def input(key):
    global frozen, running
    if key == 'escape':
        application.quit()

btn_run.on_click = lambda: setattr(sys.modules[__name__], 'running', True)

def update_joystick():
    if held_keys['left mouse']:
        m = mouse.position
        if m.x < 0:
            dx = m.x - touch_joystick.x
            dy = m.y - touch_joystick.y
            v = Vec2(dx, dy)
            if v.length() > 0:
                v = v.normalized() * min(v.length(), 1)
            stick.position = touch_joystick.position + v * 0.1
            joystick_vec = v
        else:
            camera.rotation_y += mouse.velocity[0] * 80
            camera.rotation_x -= mouse.velocity[1] * 80
    else:
        stick.position = touch_joystick.position
        joystick_vec = Vec2(0, 0)

last_print = Vec3(0, 0, 0)

def update():
    global stamina, running, frozen, last_print
    update_snow()
    update_joystick()
    update_man()

    if not frozen:
        move_dir = Vec3(joystick_vec.y, 0, -joystick_vec.x)
        speed = 7 if running and stamina > 0 else 4
        if running and stamina > 0:
            stamina -= 15 * time.dt
        else:
            stamina = min(100, stamina + 8 * time.dt)
        player.position += move_dir * speed * time.dt

        if distance(player.position, last_print) > 0.9:
            last_print = Vec3(player.position)
            add_footprint()

    Text.size = 0.8

app.run()
