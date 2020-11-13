# MiniGolf Game

import pygame as pg
import sys
import math
import time

# functions for adding, subtracting and multiplying lists
def add_lists(l1, l2):
    added = [l1[0] + l2[0], l1[1] + l2[1]]
    return added


def mul_list(l1,c):
    multiplied = [l1[0] * c, l1[1]*c]
    return multiplied


def sub_lists(l1,l2):
    return add_lists(l1, mul_list(l2, -1))


def move_rect(rect, velocity):
    rect.x += velocity[0]
    rect.y += velocity[1]

# initial variables

ball_width = 10
ball_height = 10

goal_width = 10
goal_height = 10

BROWN_COLOUR = (128, 0, 0)

CLOCK_RATE = 240
NAME_THIS_LATER = 5.0
FRICTION = 0.992

color = (255,255,255)


class Arrow(pg.sprite.Sprite):
    def __init__(self, direction):
        super().__init__()

        # Finding the angle of the wind
        # We have to do the multiplication by -1 because the coordinate system
        # in pygame is (0,0) at top-left corner
        vector = pg.math.Vector2(direction[0], -1 * direction[1])
        r, phi = vector.as_polar()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pg.image.load("arrow.png")
        self.image = pg.transform.scale(self.image, (90, 48))
        self.image = pg.transform.rotate(self.image, phi)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.center = (display_width - 75, 75)


# Ball class
# velocity attribute
class Ball(pg.sprite.Sprite):
    def __init__(self, initial_position):
        super().__init__()
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pg.image.load("ball.png")
        self.image = pg.transform.scale(self.image, (15, 15))

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.center = initial_position
        self.velocity = [0, 0]

        # Pygame only allows for the coordinates of Rects to be integer valued
        # This does not let us use wind and friction because they would affect the coordinates with float amounts
        # To avoid this limitation of Pygame, the ball class maintains a float-valued position
        # To set the coordinate of the rect, at each timestep we round this float-valued position to integers
        self.float_pos = [self.rect.centerx, self.rect.centery]


    def update(self):
        self.velocity = mul_list(self.velocity, FRICTION)
        self.float_pos = add_lists(self.float_pos, self.velocity)
        self.rect.center = (round(self.float_pos[0]), round(self.float_pos[1]))

        # check border collision
        # let's assume I have click pos
        if self.rect.left < 0 or self.rect.right > display_width:
            self.velocity[0] = -self.velocity[0]
        if self.rect.top < 0 or self.rect.bottom > display_height:
            self.velocity[1] = -self.velocity[1]

        move_rect(self.rect, self.velocity)

    def set_velocity(self, velocity):
        self.velocity = velocity


class StationaryObstacle(pg.sprite.Sprite):
    def __init__(self, initial_position, height, width):
        super().__init__()
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pg.Surface([width, height])
        self.image.fill(BROWN_COLOUR)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.center = initial_position


class MovingObstacle(StationaryObstacle):
    def __init__(self, initial_position, height, width, type, speed, boundary):
        super().__init__(initial_position, height, width)

        self.type = type
        self.speed = speed
        self.boundary = boundary

        assert type in ['horizontal', 'vertical'], 'type is not one of the allowable values!'
        if type == 'horizontal':
            assert boundary[0] <= self.rect.centerx <= boundary[1], 'obstacle initialized outside of boundary!'
        elif type == 'vertical':
            assert boundary[0] <= self.rect.centery <= boundary[1], 'obstacle initialized outside of boundary!'

    def update(self):
        if self.type == 'horizontal':
            if not self.boundary[0] <= self.rect.centerx <= self.boundary[1]:
                self.speed *= -1
            self.rect.move_ip(self.speed, 0)
        elif self.type == 'vertical':
            if not self.boundary[0] <= self.rect.centery <= self.boundary[1]:
                self.speed *= -1
            self.rect.move_ip(0, self.speed)


# sprite for goal
class Goal(pg.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.

        self.image = pg.image.load("goal.png")
        self.image = pg.transform.scale(self.image, (100, 100))

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.center = position


# main game loop
    # obtain click
    # check collision with borders and goal
    # update ball position

level_3_obstacles = []
obstacle_width = 20
for t in range(-20,21):
    y_change = math.sin(t * math.pi / 20)
    y_change *= 70
    y_change = int(y_change)
    level_3_obstacles.append(MovingObstacle((500 + t * obstacle_width, 0 + y_change),
                                            600, obstacle_width, 'vertical', 1, [-50 + y_change, 50 + y_change]))
    level_3_obstacles.append(MovingObstacle((500 + t * obstacle_width, 800 + y_change),
                                            600, obstacle_width, 'vertical', 1, [750 + y_change, 850 + y_change]))

# The parameters defining each level
level_dicts = [
    {
        'display_width': 800,
        'display_height': 800,
        'ball_pos': (100, 400),
        'goal_pos': (600, 400),
        'obstacles': [StationaryObstacle((400,350), 550, 50)],
        'wind': [0.003, -0.008]
    },
    {
        'display_width': 800,
        'display_height': 800,
        'ball_pos': (500, 700),
        'goal_pos': (100, 100),
        'obstacles': [
            MovingObstacle((350,300), 40, 200, "horizontal",2, [150, 650]),
            MovingObstacle((350, 500), 40, 200, "horizontal", 1, [200, 600])
        ],
        'wind': [-0.006, -0.001]
    },
    {
        'display_width': 1000,
        'display_height': 800,
        'ball_pos': (55,420),
        'goal_pos': (950,400),
        'obstacles': level_3_obstacles,
        'wind': [-0.003, -0.01]
    }
]

# Main Page

score_counter = 0
bc_color = (50, 205, 50)

pg.init()
display_width = 900
display_height = 600

screen = pg.display.set_mode((display_width, display_height))
main_image = pg.image.load("main.png")
screen.fill(bc_color)
screen.blit(main_image,(-50,0))
not_start_game = True

while not_start_game:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            not_start_game = False
    pg.display.flip()

for level_dict in level_dicts:

    pg.init()
    display_width = level_dict['display_width']
    display_height = level_dict['display_height']

    screen = pg.display.set_mode((display_width, display_height))
    screen.fill(bc_color)

    bounce_sound = pg.mixer.Sound('bounce.wav')
    clap_sound = pg.mixer.Sound('golf clap.wav')

    clock = pg.time.Clock()
    ball_goal_collision_checker = pg.sprite.collide_circle_ratio(0.6)

    ball_group = pg.sprite.Group()
    ball = Ball(level_dict['ball_pos'])
    ball_group.add(ball)

    goal = Goal(level_dict['goal_pos'])
    goal_group = pg.sprite.Group()
    goal_group.add(goal)

    obstacles = level_dict['obstacles']
    obstacle_group = pg.sprite.Group()
    for obstacle in obstacles:
        obstacle_group.add(obstacle)

    shot_ball = False

    wind = level_dict['wind']
    wind_speed = CLOCK_RATE*(wind[0]**2 + wind[1]**2)**0.5
    arrow = Arrow(wind)
    arrow_group = pg.sprite.Group()
    arrow_group.add(arrow)
    pg.font.init()
    pg_font = pg.font.SysFont('Comic Sans MS', 20)
    wind_speed_text = pg_font.render('%.1f px/sec' % wind_speed, False, (0, 0, 0))
    pg1_font = pg.font.SysFont('Comic Sans MS', 50)
    congratulate_text = pg1_font.render('Great Job!', False, (255, 255, 255))

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if not shot_ball:
                    score_counter += 1
                    click_x, click_y = pg.mouse.get_pos()
                    velocity = [(ball.rect.center[0] - click_x)/NAME_THIS_LATER,
                                (ball.rect.center[1] - click_y)/NAME_THIS_LATER]
                    ball.set_velocity(velocity)
                    shot_ball = True
            elif event.type == pg.MOUSEBUTTONUP and event.button == 3:
                ball.velocity = [0,0]
                ball.float_pos = [level_dict['ball_pos'][0], level_dict['ball_pos'][1]]
                ball.rect.center = tuple(ball.float_pos)
                shot_ball = False

        # we update the position of the obstacles before updating the position of the ball so that we avoid problems
        # with intersecting the obstacle again and again
        obstacle_group.update()

        if pg.sprite.spritecollideany(goal,ball_group,collided = ball_goal_collision_checker) != None:
            ball.set_velocity([0, 0])
            screen.blit(congratulate_text, ((display_width/2)- 100, 200))
            pg.display.flip()
            clap_sound.play()
            time.sleep(6)
            break # go to the next level

        # Check for obstacle collisions
        collided_obstacle = pg.sprite.spritecollideany(ball, obstacle_group)
        if collided_obstacle is not None:
            bounce_sound.play()
            ball_x, ball_y = ball.rect.center

            # Check if intersect from top
            if ball_y < collided_obstacle.rect.top:
                # Make sure that the ball won't again intersect the obstacle at the next timestep
                ball.float_pos[1] = collided_obstacle.rect.top - 10
                # The ball should bounce off of the obstacle
                ball.velocity[1] *= -1
                # if the ball hits the obstacle from top and the obstacle if moving vertically upwards, the ball's
                # upward speed after collision should be at least the same as the obstacle's upward speed
                if isinstance(collided_obstacle, MovingObstacle) and \
                        collided_obstacle.type == 'vertical' and \
                        collided_obstacle.speed < 0:
                    ball.velocity[1] = min(collided_obstacle.speed, ball.velocity[1])
            elif ball_y > collided_obstacle.rect.bottom:
                ball.float_pos[1] = collided_obstacle.rect.bottom + 10
                ball.velocity[1] *= -1
                if isinstance(collided_obstacle, MovingObstacle) and \
                        collided_obstacle.type == 'vertical' and \
                        collided_obstacle.speed > 0:
                    ball.velocity[1] = max(collided_obstacle.speed, ball.velocity[1])

            if ball_x < collided_obstacle.rect.left:
                ball.float_pos[0] = collided_obstacle.rect.left - 10
                ball.velocity[0] *= -1
                if isinstance(collided_obstacle, MovingObstacle) and \
                        collided_obstacle.type == 'horizontal' and \
                        collided_obstacle.speed < 0:
                    ball.velocity[0] = min(collided_obstacle.speed, ball.velocity[0])
            elif ball_x > collided_obstacle.rect.right:
                ball.float_pos[0] = collided_obstacle.rect.right + 10
                ball.velocity[0] *= -1
                if isinstance(collided_obstacle, MovingObstacle) and \
                        collided_obstacle.type == 'horizontal' and \
                        collided_obstacle.speed > 0:
                    ball.velocity[0] = max(collided_obstacle.speed, ball.velocity[0])
            ball.float_pos = add_lists(ball.float_pos, ball.velocity)

        if shot_ball:
            ball.velocity[0] += wind[0]
            ball.velocity[1] += wind[1]

        clock.tick(CLOCK_RATE)
        ball_group.update()
        screen.fill(bc_color)
        goal_group.draw(screen)
        ball_group.draw(screen)
        obstacle_group.draw(screen)
        arrow_group.draw(screen)
        screen.blit(wind_speed_text, (display_width - 120, 125))
        score_text = pg_font.render('Score: ' + str(score_counter), False, (0, 0, 0))
        screen.blit(score_text, (50, 10))
        if not shot_ball:
            mouse_x, mouse_y = pg.mouse.get_pos()
            ball_x, ball_y = ball.rect.center
            pg.draw.line(
                screen,
                (0, 0, 255),
                (ball_x, ball_y),
                (
                    ball_x + 3*(ball_x - mouse_x),
                    ball_y + 3*(ball_y - mouse_y)
                ),
                2
            )

        pg.display.flip()

screen.fill(bc_color)
pg.font.init()
pg_font = pg.font.SysFont('Comic Sans MS', 40)
end_text = pg_font.render('Congratulations ! Your Score is: ' + str(score_counter), False, (255, 255, 255))
screen.blit(end_text, (190, 125))
pg.display.flip()
time.sleep(5)

pg.quit()
