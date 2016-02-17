#http://www.codeskulptor.org/#user40_OjstzK1dBAgQLcT.py
# program template for Spaceship
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
# C - friction constant, A - acceleration constant 
C = 0.03  
A = 0.4
AV = math.pi / 30
keyState = {'up': False,'right': False,'left': False,'space':False}
isStart = False
rock_group = set([])
missile_group = set([])
explosion_group = set([])

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info  = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 40)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(1.0)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def group_collide(group, other_object):
    global explosion_group
    res = False
    for aObj in list(group):
        if aObj.collide(other_object):
            explosion_group.add(Sprite(aObj.get_position(), [0, 0], 0, 0, explosion_image, explosion_info,explosion_sound))
            group.discard(aObj)
            res = True
    return res    

def group_group_collide(missGroup, rockGroup):
    collisions = 0
    for aRock in list(rockGroup):
        if group_collide(missGroup, aRock):
            rockGroup.discard(aRock)
            collisions += 1
    return collisions  
    
def process_sprite_group(canvas):
    global rock_group, missile_group, explosion_group
    for a_rock in list(rock_group):
        a_rock.draw(canvas)
        a_rock.update()
    for a_missile in list(missile_group):
        a_missile.draw(canvas)
        isExpired = a_missile.update()
        if isExpired:
            missile_group.discard(a_missile)
    for aExplosion in list(explosion_group):
        aExplosion.draw(canvas)
        isExpired = aExplosion.update()
        if isExpired:
            explosion_group.discard(aExplosion)    
# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.forward = angle_to_vector(self.angle)
    def reset(self):
        self.angle_vel = 0
        self.vel = [0,0]
        self.thrust = False
        ship_thrust_sound.pause()
    def get_position(self):
        return self.pos
    def get_radius(self):
        return self.radius
    def shoot(self):
        global missile_group,keyState
        if keyState['space']:
            vel = list(self.vel) 
            self.forward = angle_to_vector(self.angle);
            vel[0] += 9 * self.forward[0]
            vel[1] += 9 * self.forward[1] 
            misPos = list(self.pos)
            misPos[0] += self.radius*math.cos(self.angle)
            misPos[1] += self.radius*math.sin(self.angle)
            missile_group.add(Sprite(misPos, vel, 0, 0, missile_image, missile_info, missile_sound))
            keyState['space'] = False;
    def setThrust(self):
        self.thrust = keyState.get('up')
        if self.thrust:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()
    def updateAngleVel(self):
        if not ((keyState['left']) or (keyState['right'])):
            self.angle_vel = 0
        if keyState['left']:
            self.angle_vel = -AV
        if keyState['right']:
            self.angle_vel = AV
        
    def draw(self,canvas):
        imgCenter = list(self.image_center)
        if self.thrust:
            imgCenter[0] = self.image_center[0] + self.image_size[0]
            imgCenter[1] = self.image_center[1]
        
        canvas.draw_image(self.image, imgCenter, self.image_size, self.pos, self.image_size, self.angle)
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        self.vel[0] *= (1 - C)
        self.vel[1] *= (1 - C)
        self.angle  += self.angle_vel
        if self.thrust:
            self.forward = angle_to_vector(self.angle);
            self.vel[0] += A * self.forward[0]
            self.vel[1] += A * self.forward[1]            
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
    def get_position(self):
        return self.pos
    def get_radius(self):
        return self.radius
    def collide(self,other_object):
        res = False
        othPos = other_object.get_position()
        othRad = other_object.get_radius()
        if ( dist(self.pos,othPos) <  (self.radius + othRad) ):
            res = True
        return res
    
    def draw(self, canvas):
        if self.animated:
            ind = self.age
            imgCenter = [ind * (self.image_size[0] / 2) + self.image_center[0], self.image_center[1]]
            canvas.draw_image(self.image, imgCenter, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):  
        if not self.animated:
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]
            self.pos[0] %= WIDTH
            self.pos[1] %= HEIGHT
            self.angle  += self.angle_vel
        self.age += 1
        return self.age > self.lifespan
        

    
def draw(canvas):
    global time, isStart, rock_group, missile_group, explosion_group,lives, score
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    canvas.draw_text('Lives', (100, 50), 30, 'White', 'serif')
    canvas.draw_text(str(lives), (120, 100), 30, 'White', 'serif')
    canvas.draw_text('Score', (WIDTH - 200, 50), 30, 'White', 'serif')
    canvas.draw_text(str(score), (WIDTH - 170, 100), 30, 'White', 'serif')
    # draw ship and sprites
    my_ship.draw(canvas)
    if isStart:
        process_sprite_group(canvas)
        # handle key events
        my_ship.setThrust()
        my_ship.updateAngleVel()
        my_ship.shoot()
        # update ship and sprites
        my_ship.update()
        score += 10*(group_group_collide(missile_group, rock_group))
        isCollision = group_collide(rock_group,my_ship)
        if isCollision:
            lives -= 1
            if lives == 0:
                isStart = False
                rock_group = set([])
                missile_group = set([])
                explosion_group = set([])
                my_ship.reset()
                timer.stop()
                soundtrack.pause()
    else:
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), (WIDTH/2,HEIGHT/2), splash_info.get_size())
        timer.stop()
        
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    if len(rock_group) < 12:
        astrSize = asteroid_info.get_size()
        dist = 0
        while (dist < 400):
            xPos = random.randrange(astrSize[0] // 2, WIDTH - astrSize[0] // 2);
            yPos = random.randrange(astrSize[1] // 2, HEIGHT - astrSize[1] // 2);
            dist = (my_ship.get_position,[xPos,yPos])
        xVel = random.randrange(-120 // 60, 120 // 60)
        yVel = random.randrange(-120 // 60, 120 // 60)
        VF = score // 100
        xVel += 0.2 *  VF
        yVel += 0.2 *  VF
        angVel = random.randrange(-90, 90)
        angVel *= (math.pi / 40) / 60 
        
        rock_group.add(Sprite([xPos, yPos], [xVel, yVel], 0, angVel, asteroid_image, asteroid_info))
def keyPressed(key):
    global keyState;
    for k in keyState:
        if key == simplegui.KEY_MAP[k]:
            keyState[k] = True
    
def keyReleased(key):
    global keyState;
    for k in keyState:
        if key == simplegui.KEY_MAP[k]:
            keyState[k] = False
def mouse_handler(pos):
    global isStart, timer,lives,score
    if not isStart:
        imgSize = splash_info.get_size() 
        cPos = [WIDTH/2,HEIGHT/2]
        xMin = cPos[0] - (imgSize[0] / 2)
        xMax = cPos[0] + (imgSize[0] / 2)
        yMin = cPos[1] - (imgSize[1] / 2)
        yMax = cPos[1] + (imgSize[1] / 2)
        if (xMin  < pos[0] < xMax) and (yMin  < pos[1] < yMax):
            isStart = True
            lives = 3
            score = 0
            soundtrack.rewind()
            soundtrack.play()
            timer.start()
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], math.pi, ship_image, ship_info)
#rock_group.add(Sprite([WIDTH / 3, HEIGHT / 3], [1, -1], 0, 0, asteroid_image, asteroid_info))

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keyPressed)
frame.set_keyup_handler(keyReleased)
frame.set_mouseclick_handler(mouse_handler)
timer = simplegui.create_timer(1000.0, rock_spawner)
# get things rolling
frame.start()
