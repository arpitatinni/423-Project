from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import math




SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600




CAR_WIDTH = 50
CAR_HEIGHT = 80
TRACK_WIDTH = 600
TRACK_LEFT_BOUNDARY = SCREEN_WIDTH // 2 - TRACK_WIDTH // 2
TRACK_RIGHT_BOUNDARY = SCREEN_WIDTH // 2 + TRACK_WIDTH // 2




MENU = 0
PLAYING = 1




PAUSED = False




BUTTON_SIZE = 30
BUTTON_Y = SCREEN_HEIGHT - 40
RESTART_X = SCREEN_WIDTH // 2 - 50
PAUSE_X = SCREEN_WIDTH // 2
EXIT_X = SCREEN_WIDTH // 2 + 50




SPECIAL_CAR_SPEED = 10
SPECIAL_CAR_SPAWN_RATE = 200




DIFFICULTIES = {
   'EASY': {'speed': 3, 'spawn_rate': 45, 'enemy_speed': 1, 'max_collisions': 7},
   'MEDIUM': {'speed': 5, 'spawn_rate': 30, 'enemy_speed': 2, 'max_collisions': 5},
   'HARD': {'speed': 7, 'spawn_rate': 20, 'enemy_speed': 3, 'max_collisions': 3}
}








class CarRacingGame:
   def __init__(self):
       self.flag_game_over = False
       glutInit()
       glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
       glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
       glutCreateWindow(b"OpenGL Car Racing")




       glClearColor(0.4, 0.7, 0.2, 1.0)
       glMatrixMode(GL_PROJECTION)
       glLoadIdentity()
       gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
       glMatrixMode(GL_MODELVIEW)




       self.menu_buttons = {
           'EASY': {
               'x': SCREEN_WIDTH // 2 - 150,
               'y': SCREEN_HEIGHT // 2,
               'color': (0.0, 1.0, 0.0),
               'width': 100
           },
           'MEDIUM': {
               'x': SCREEN_WIDTH // 2 - 50,
               'y': SCREEN_HEIGHT // 2,
               'color': (1.0, 1.0, 0.0),
               'width': 100
           },
           'HARD': {
               'x': SCREEN_WIDTH // 2 + 50,
               'y': SCREEN_HEIGHT // 2,
               'color': (1.0, 0.0, 0.0),
               'width': 100
           }
       }




       self.game_state = MENU
       self.paused = False
       self.difficulty = None
       self.car_x = SCREEN_WIDTH // 2
       self.car_y = 50
       self.enemy_cars = []
       self.special_car = None
       self.special_car_timer = 0
       self.score = 0
       self.game_over = False
       self.collisions = 0
       self.spawn_timer = 0
       self.passed_cars = set()
       self.move_speed = 7
       self.keys = {}
       self.grass_points = self.generate_grass_points()
       self.side_lines = self.generate_side_lines()




   def draw_control_buttons(self):
       def draw_filled_triangle(x1, y1, x2, y2, x3, y3):
           min_x, max_x = int(min(x1, x2, x3)), int(max(x1, x2, x3))
           min_y, max_y = int(min(y1, y2, y3)), int(max(y1, y2, y3))




           def is_inside_triangle(px, py):
               def sign(x1, y1, x2, y2, x3, y3):
                   return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)




               d1 = sign(px, py, x1, y1, x2, y2)
               d2 = sign(px, py, x2, y2, x3, y3)
               d3 = sign(px, py, x3, y3, x1, y1)
               has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
               has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
               return not (has_neg and has_pos)




           glBegin(GL_POINTS)
           for x in range(min_x, max_x + 1):
               for y in range(min_y, max_y + 1):
                   if is_inside_triangle(x, y):
                       glVertex2f(x, y)
           glEnd()




       def draw_filled_rect(x1, y1, x2, y2):
           glBegin(GL_POINTS)
           for x in range(int(min(x1, x2)), int(max(x1, x2)) + 1):
               for y in range(int(min(y1, y2)), int(max(y1, y2)) + 1):
                   glVertex2f(x, y)
           glEnd()




       # Restart button (green triangle)
       glColor3f(0.0, 0.7, 0.0)
       draw_filled_triangle(
           RESTART_X - 15, BUTTON_Y + 15,
           RESTART_X + 5, BUTTON_Y + 25,
           RESTART_X + 5, BUTTON_Y + 5
       )




       # Pause/Play button (yellow)
       glColor3f(1.0, 0.75, 0.0)
       if self.paused:
           draw_filled_triangle(
               PAUSE_X - 10, BUTTON_Y + 5,
               PAUSE_X - 10, BUTTON_Y + 25,
               PAUSE_X + 10, BUTTON_Y + 15
           )
       else:
           draw_filled_rect(PAUSE_X - 10, BUTTON_Y + 5, PAUSE_X - 5, BUTTON_Y + 25)
           draw_filled_rect(PAUSE_X + 5, BUTTON_Y + 5, PAUSE_X + 10, BUTTON_Y + 25)




       # Exit button (red X)
       glColor3f(1.0, 0.0, 0.0)
       glPointSize(2.0)
       glBegin(GL_POINTS)
       for t in range(0, 101, 2):
           t = t / 100
           x = EXIT_X - 10 + t * 20
           y = BUTTON_Y + 5 + t * 20
           glVertex2f(x, y)
           y2 = BUTTON_Y + 25 - t * 20
           glVertex2f(x, y2)
       glEnd()




   def handle_button_click(self, x, y):
       y = SCREEN_HEIGHT - y




       if BUTTON_Y <= y <= BUTTON_Y + BUTTON_SIZE:
           if RESTART_X - 15 <= x <= RESTART_X + 5:
               print("Restarting Game")
               self.game_state = MENU
               return True




           elif PAUSE_X - 10 <= x <= PAUSE_X + 10:
               self.paused = not self.paused
               return True




           elif EXIT_X - 10 <= x <= EXIT_X + 10:
               print(f"Goodbye! Final Score: {self.score}")
               glutLeaveMainLoop()
               return True
       return False




   def draw_text(self, x, y, text, color=(1.0, 1.0, 1.0)):
       glColor3f(*color)
       glRasterPos2f(x, y)
       for char in text:
           glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))




   def draw_menu(self):
       self.draw_text(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50,
                      "Select Difficulty:", (1.0, 1.0, 1.0))




       for difficulty, button in self.menu_buttons.items():
           self.draw_text(button['x'], button['y'],
                          difficulty.capitalize(), button['color'])




   def handle_menu_click(self, x, y):
       y = SCREEN_HEIGHT - y




       menu_y = SCREEN_HEIGHT // 2
       if menu_y - 10 <= y <= menu_y + 10:
           for difficulty, button in self.menu_buttons.items():
               if button['x'] <= x <= button['x'] + button['width']:
                   self.start_game(difficulty)
                   return




   def start_game(self, difficulty):
       self.difficulty = difficulty
       self.game_state = PLAYING
       self.score = 0
       self.collisions = 0
       self.game_over = False
       self.enemy_cars = []
       self.special_car = None
       self.special_car_timer = 0
       self.car_x = SCREEN_WIDTH // 2
       self.car_y = 50
       self.passed_cars = set()
       self.paused = False




   def generate_grass_points(self):
       grass_points = []
       for _ in range(2000):
           x = random.randint(0, SCREEN_WIDTH)
           y = random.randint(0, SCREEN_HEIGHT)
           grass_points.append((x, y))
       return grass_points




   def generate_side_lines(self):
       side_lines = []
       for y in range(0, SCREEN_HEIGHT, 30):
           side_lines.append((TRACK_LEFT_BOUNDARY - 10, y))
           side_lines.append((TRACK_RIGHT_BOUNDARY + 10, y))
       return side_lines




   def draw_background(self):
       glColor3f(0.3, 0.6, 0.2)
       glPointSize(1)
       glBegin(GL_POINTS)
       for x, y in self.grass_points:
           glVertex2f(x, y)
       glEnd()




   def draw_car(self, x, y, color):
       glColor3f(*color)
       glPointSize(3)
       glBegin(GL_POINTS)




       for x_point in range(int(x - CAR_WIDTH / 2), int(x + CAR_WIDTH / 2)):
           for y_point in range(int(y), int(y + CAR_HEIGHT * 0.2)):
               glVertex2f(x_point, y_point)




       for x_point in range(int(x - CAR_WIDTH / 3), int(x + CAR_WIDTH / 3)):
           for y_point in range(int(y + CAR_HEIGHT * 0.2), int(y + CAR_HEIGHT * 0.7)):
               glVertex2f(x_point, y_point)




       for x_point in range(int(x - CAR_WIDTH / 4), int(x + CAR_WIDTH / 4)):
           for y_point in range(int(y + CAR_HEIGHT * 0.7), int(y + CAR_HEIGHT)):
               glVertex2f(x_point, y_point)




       glColor3f(0.7, 0.9, 1.0)
       for x_point in range(int(x - CAR_WIDTH / 6), int(x + CAR_WIDTH / 6)):
           for y_point in range(int(y + CAR_HEIGHT * 0.8), int(y + CAR_HEIGHT * 0.9)):
               glVertex2f(x_point, y_point)




       glColor3f(0.2, 0.2, 0.2)
       for wheel_x in [x - CAR_WIDTH / 3, x + CAR_WIDTH / 3]:
           for angle in range(0, 360, 10):
               wheel_radius = 5
               wx = int(wheel_x + wheel_radius * math.cos(math.radians(angle)))
               wy = int(y + wheel_radius * math.sin(math.radians(angle)))
               glVertex2f(wx, wy)




       glEnd()




   def draw_track(self):
       glColor3f(0.3, 0.3, 0.3)
       glPointSize(2)
       glBegin(GL_POINTS)
       for y in range(0, SCREEN_HEIGHT):
           glVertex2f(TRACK_LEFT_BOUNDARY, y)
           glVertex2f(TRACK_RIGHT_BOUNDARY, y)
       glEnd()




   def is_car_overlap(self, new_x):
       for car in self.enemy_cars:
           if abs(new_x - car['x']) < CAR_WIDTH:
               return True
       return False




   def spawn_enemy_car(self):
       self.spawn_timer += 1




       if self.spawn_timer >= DIFFICULTIES[self.difficulty]['spawn_rate']:
           attempts = 0
           while attempts < 10:
               x = random.randint(
                   TRACK_LEFT_BOUNDARY + 20,
                   TRACK_RIGHT_BOUNDARY - 20
               )




               if not self.is_car_overlap(x):
                   car_id = random.randint(0, 1000000)
                   color = (random.random(), random.random(), random.random())
                   self.enemy_cars.append({
                       'id': car_id,
                       'x': x,
                       'y': SCREEN_HEIGHT,
                       'color': color,
                       'direction': random.choice([-1, 1]),
                       'passed': False
                   })
                   break
               attempts += 1
           self.spawn_timer = 0




   def spawn_special_car(self):
       if self.special_car is None:
           self.special_car_timer += 1
           if self.special_car_timer >= SPECIAL_CAR_SPAWN_RATE:
               self.special_car_timer = 0
               x = random.randint(
                   TRACK_LEFT_BOUNDARY + 20,
                   TRACK_RIGHT_BOUNDARY - 20
               )
               self.special_car = {
                   'x': x,
                   'y': SCREEN_HEIGHT,
                   'color': (1.0, 0.8, 0.0),
                   'passed': False,
                   'is_special': True,
                   'direction': random.choice([-1, 1])
               }




   def check_collision(self, car):
       return (abs(car['x'] - self.car_x) < CAR_WIDTH and
               abs(car['y'] - self.car_y) < CAR_HEIGHT)




   def check_car_passed(self, car):
       return (car['y'] < self.car_y and
               not car['passed'] and
               not self.check_collision(car))




   def draw_enemy_cars(self):
       if self.paused:
           for car in self.enemy_cars:
               self.draw_car(car['x'], car['y'], car['color'])
           return




       new_enemy_cars = []
       enemy_speed = DIFFICULTIES[self.difficulty]['speed']
       max_collisions = DIFFICULTIES[self.difficulty]['max_collisions']




       for car in self.enemy_cars:
           self.draw_car(car['x'], car['y'], car['color'])




           car['y'] -= enemy_speed
           car['x'] += car['direction'] * DIFFICULTIES[self.difficulty]['enemy_speed']




           if car['x'] <= TRACK_LEFT_BOUNDARY + 20 or car['x'] >= TRACK_RIGHT_BOUNDARY - 20:
               car['direction'] *= -1




           if self.check_collision(car):
               if not car['passed']:
                   self.collisions += 1
                   car['passed'] = True




           elif self.check_car_passed(car):
               self.score += 1
               car['passed'] = True




           if car['y'] > 0:
               new_enemy_cars.append(car)




           if self.collisions >= max_collisions:
               self.game_over = True




       self.enemy_cars = new_enemy_cars




   def draw_special_car(self):
       if self.special_car:
           if not self.paused:
               self.special_car['y'] -= SPECIAL_CAR_SPEED
               self.special_car['x'] += self.special_car['direction'] * DIFFICULTIES[self.difficulty]['enemy_speed']




               if (self.special_car['x'] <= TRACK_LEFT_BOUNDARY + 20 or
                       self.special_car['x'] >= TRACK_RIGHT_BOUNDARY - 20):
                   self.special_car['direction'] *= -1




               if self.check_collision(self.special_car):
                   if not self.special_car['passed']:
                       self.collisions += 1
                       self.special_car = None
               elif (self.special_car['y'] < self.car_y and
                     not self.special_car['passed'] and
                     self.collisions > 0):
                   self.collisions -= 1
                   self.special_car['passed'] = True




               if self.special_car and self.special_car['y'] <= 0:
                   self.special_car = None




           if self.special_car:
               self.draw_car(self.special_car['x'], self.special_car['y'], self.special_car['color'])




   def keyboard(self, key, x, y):
       self.keys[key] = True
       if key == b'\x1b':
           glutLeaveMainLoop()




   def keyboard_up(self, key, x, y):
       if key in self.keys:
           del self.keys[key]




   def mouse(self, button, state, x, y):
       if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
           if self.game_state == MENU:
               self.handle_menu_click(x, y)
           elif not self.handle_button_click(x, y):
               pass




   def handle_input(self):
       if self.paused:
           return




       if ((self.keys.get(b'a', False) or self.keys.get(b'A', False)) and
               self.car_x - CAR_WIDTH / 2 > TRACK_LEFT_BOUNDARY):
           self.car_x -= self.move_speed




       if ((self.keys.get(b'd', False) or self.keys.get(b'D', False)) and
               self.car_x + CAR_WIDTH / 2 < TRACK_RIGHT_BOUNDARY):
           self.car_x += self.move_speed




       if ((self.keys.get(b'w', False) or self.keys.get(b'W', False)) and
               self.car_y + CAR_HEIGHT < SCREEN_HEIGHT):
           self.car_y += self.move_speed




       if ((self.keys.get(b's', False) or self.keys.get(b'S', False)) and
               self.car_y > 0):
           self.car_y -= self.move_speed




   def display(self):
    glClear(GL_COLOR_BUFFER_BIT)


    if self.game_state == MENU:
        self.draw_menu()
    elif not self.game_over:
        self.draw_background()
        if not self.paused:
            self.handle_input()
            self.spawn_enemy_car()
            self.spawn_special_car()
        self.draw_track()
        self.draw_car(self.car_x, self.car_y, (1.0, 0.0, 0.0))
        self.draw_enemy_cars()
        self.draw_special_car()
        self.draw_control_buttons()


        max_collisions = DIFFICULTIES[self.difficulty]['max_collisions']
        self.draw_text(10, SCREEN_HEIGHT - 30, f"Score: {self.score}")
        self.draw_text(10, SCREEN_HEIGHT - 50, f"Collisions: {self.collisions}/{max_collisions}")
    else:
        game_over_message = f"Game Over! Final Score: {self.score}"
        self.draw_text(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, game_over_message)


        if not self.flag_game_over:    #glutLeaveMainLoop() function er bodole flag use korchhi
            print(game_over_message)
            self.flag_game_over = True


    glutSwapBuffers()


   def idle(self):
       glutPostRedisplay()




   def run(self):
       glutDisplayFunc(self.display)
       glutKeyboardFunc(self.keyboard)
       glutKeyboardUpFunc(self.keyboard_up)
       glutMouseFunc(self.mouse)
       glutIdleFunc(self.idle)
       glutMainLoop()
def main():
   game = CarRacingGame()
   game.run()




if __name__ == '__main__':
   main()









