# Slingship Game

import turtle
import time
import numpy as np
from time import sleep

TIME_STEP = 0.001
G = 10
FRICTION = 0.999

# setting an image as background of program
screen = turtle.Screen()
screen.bgpic("bg.png")


def distance(obj1, obj2):
    return (
               (obj1.cor[0] - obj2.cor[0]) ** 2 +
               (obj1.cor[1] - obj2.cor[1]) ** 2
           ) ** 0.5


class Ball():
    # class used for creation of the ball that we are trying
    # to get to a destination
    def __init__(self, position):
        self.sprite = turtle.Turtle()
        self.sprite.penup()
        self.sprite.shape("circle")
        self.sprite.color("white")
        self.sprite.shapesize(0.4)
        self.sprite.setposition(position[0],position[1])
        self.sprite.pendown()
        self.mass = 1
        self.cor = [position[0], position[1]]
        self.velocity = [0, 0]
        self.acceleration = [0, 0]

        self.contact_counter = 0
        self.is_shot = False
        self.reached_goal = False

    def compute_acc_from_planet(self, planet):
        d_squared = (self.cor[1] - planet.cor[1]) ** 2 + (self.cor[0]
                                                          - planet.cor[0]) ** 2

        if self.contact_counter > 0:
            self.contact_counter -= 1
            a = 0
        elif d_squared < (10 * planet.radius) ** 2:
            # Formulas derived from
            # https: // math.stackexchange.com / questions / 525082 / reflection - across - a - line
            a = 0
            v = np.array([[-self.velocity[0]], [-self.velocity[1]]])

            p_x = planet.cor[0] - self.cor[0]
            p_y = planet.cor[1] - self.cor[1]
            m = p_y / p_x

            T = (1 / (1 + m ** 2)) * np.array([[1 - m ** 2, 2 * m], [2 * m, m ** 2 - 1]])
            new_v = np.dot(T, v)
            self.velocity[0], self.velocity[1] = new_v[0, 0], new_v[1, 0]

            self.contact_counter = 3

        else:
            a = G * planet.mass / d_squared
        direction = [planet.cor[0] - self.cor[0], planet.cor[1] - self.cor[1]]
        distance = d_squared ** 0.5
        direction[0] /= distance
        direction[1] /= distance

        acc = direction
        acc[0] *= a
        acc[1] *= a

        return acc

    def update_acceleration(self, planets):
        self.acceleration = [0, 0]
        for planet in planets:
            acc = self.compute_acc_from_planet(planet)
            self.acceleration[0] += acc[0]
            self.acceleration[1] += acc[1]

    def update_pos(self, planets, powerups):
        if self.is_shot:
            self.update_acceleration(planets)

            self.velocity[0] += self.acceleration[0] * TIME_STEP
            self.velocity[1] += self.acceleration[1] * TIME_STEP

            self.velocity[0] *= FRICTION
            self.velocity[1] *= FRICTION

            self.cor[0] += self.velocity[0] * TIME_STEP
            self.cor[1] += self.velocity[1] * TIME_STEP

            # Check powerups
            for p in powerups:
                if distance(self, p) < 10 * p.radius:
                    # Check powerup type
                    if p.type == 'goal':
                        self.reached_goal = True
                    elif p.type == 'speed' and not p.used:
                        self.velocity[0] *= 1.5
                        self.velocity[1] *= 1.5
                        p.used = True

                        p.sprite.hideturtle()

            self.sprite.setposition(self.cor[0], self.cor[1])

    # function for shooting
    def shoot(self, x, y):

        c = 3200  # A number to maintain velocity
        # to maintain velocity in a reasonable range

        self.velocity[0] = x - self.cor[0]
        self.velocity[1] = y - self.cor[1]

        norm = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5

        self.velocity[0] *= c / norm
        self.velocity[1] *= c / norm

        self.is_shot = True

# class created for planets with necessary parameters that
# affect it's gravitational force


class Planet():
    def __init__(self, mass, position, radius):
        self.sprite = turtle.Turtle()
        self.sprite.penup()
        self.sprite.color("purple")
        self.mass = mass
        self.cor = position
        self.radius = radius
        self.sprite.shape("circle")
        self.sprite.shapesize(radius)
        self.sprite.setposition(position[0], position[1])


# class used to put a goal or other powerups

class PowerUp():
    def __init__(self, position, type):
        self.type = type

        # Change the color
        self.sprite = turtle.Turtle()
        self.sprite.penup()

        if self.type == 'goal':
            self.sprite.fillcolor('violet')
        elif self.type == 'speed':
            self.sprite.fillcolor('cyan')
            self.used = False

        self.cor = position
        self.radius = 2
        self.sprite.shape("circle")
        self.sprite.shapesize(self.radius)
        self.sprite.setposition(position[0], position[1])

# The levels

level_1 = {
    'planets': [
        {'mass':1.3*1e8, 'position':[-100, 0], 'radius':5},
        {'mass':3.5* 1e8, 'position':[300, 0], 'radius':9}
    ],
    'speedups': [],
    'goal': [400, 225],
    'ball_cor': [-550, 0]
}


level_2 = {
    'planets': [
        {'mass': 3 *1e8, 'position':[-250, 100], 'radius':7},
        {'mass': 6 * 1e8, 'position':[100, -50], 'radius':9},
        {'mass': 2 *1e8, 'position':[80, 220], 'radius':5}
    ],
    'speedups': [[-250, -165], [-210,-295], [-330,-70], [-410,-10]],
    'goal': [220, 40],
    'ball_cor': [-370, -210]
}

level_3 = {
    'planets': [
        {'mass':3.0*1e8, 'position':[-250, 190], 'radius':7},
        {'mass':3.4 * 1e8, 'position':[90, -200], 'radius':4},
        {'mass':2.0* 1e8, 'position':[420, -200], 'radius':10}
    ],
    'speedups': [[10,-190]],
    'goal': [-320, 310],
    'ball_cor': [120, -10]
}

level_4 = {
    'planets': [
        {'mass':1.3*1e8, 'position':[-100, -100], 'radius':7},
        {'mass':0.5 * 1e8, 'position':[-400, -50], 'radius':4},
        {'mass':3.5* 1e8, 'position':[300, -30], 'radius':10},
        {'mass':0.5*1e8, 'position':[-100, 100], 'radius':4},
        {'mass':0.5*1e8, 'position':[180, -250], 'radius':4}
    ],
    'speedups': [
        [20,-50] ],
    'goal': [600, -90],
    'ball_cor': [-550, 0]
}

levels = [level_1, level_2, level_3, level_4]

# function that runs each level based on the descriptions of each level written above

def load_level(level_dict):
    # set up planets
    planet_descriptions = level_dict['planets']
    planets = []
    for description in planet_descriptions:
        planets.append(Planet(description["mass"],description["position"], description["radius"]))

    # set up powerups
    speed_descriptions = level_dict['speedups']
    powerups = []
    for description in speed_descriptions:
        powerups.append(PowerUp(description, "speed"))

    powerups.append(PowerUp(level_dict["goal"], "goal"))

    # set up ball
    ball = Ball(level_dict["ball_cor"])

    return ball, powerups, planets

# for writing messages after the completion of each level

screen = turtle.Screen()
writer = turtle.Turtle()
writer.setposition(0, 300)
writer.color("white")
writer.ht()
writer.penup()

cur_level = 0
ball, powerups, planets = load_level(levels[cur_level])
reset_flag = False

# function used for transition between two levels and reset capability

def clear_level(ball, planets, powerups, writer):
    ball.sprite.hideturtle()
    ball.sprite.clear()
    for p in planets:
        p.sprite.hideturtle()
    for p in powerups:
        p.sprite.hideturtle()
    writer.clear()

# function that shoots ball into direction of click

def click_handler(x, y):
    global ball, powerups, planets, cur_level, levels, reset_flag
    if not ball.is_shot:
        ball.shoot(x, y)
    while not ball.reached_goal and not reset_flag:
        ball.update_pos(planets, powerups)
        sleep(TIME_STEP)
    if reset_flag:
        reset_flag = False
    else:
        if cur_level == len(levels)-1:
            writer.write("GAME COMPLETE!", False, align="center", font =("Arial", 80, "bold"))
        else:
            writer.write("GREAT JOB!", False, align="center", font =("Arial", 80, "bold"))
        time.sleep(5)

        cur_level += 1

    clear_level(ball, planets, powerups, writer)

    if cur_level < len(levels):
        ball, powerups, planets = load_level(levels[cur_level])

def reset_handler(x, y):
    global reset_flag
    reset_flag = True

# left click shoots ball
screen.onclick(click_handler)

# right click resets level
screen.onclick(reset_handler, 2)

turtle.done()
