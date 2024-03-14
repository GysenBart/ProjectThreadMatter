from os import path
import os
import sys
import pygame
import threading
import settings
import sprites
import time
from subprocess import Popen, PIPE

class Game:
    def __init__(self):
        self.nodeId = sys.argv[1]
        #self.command = '/home/ubuntu/connectedhomeip/out/standalone/chip-tool levelcontrol read current-level ' + str(self.nodeId) + ' 2'
        self.command = "/home/ubuntu/scripts/matterTool.sh interactive start"
        self.levelcontrol = "levelcontrol subscribe current-level 0 1 " + str(self.nodeId) + " 2\n"
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(settings.TITLE)
        self.screen = pygame.display.set_mode(settings.WIN_SIZE)
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.sfx = {
            sound: pygame.mixer.Sound(path.join(settings.SFX, f'{sound}.wav'))
            for sound in ('bounce', 'explosion', 'launch', 'level')
        }

        self.running = True
        self.sensor_data = 128

    def reset(self):
        self.sprites.empty()
        self.bricks.empty()
        self.status = sprites.Status(2, 0, (self.sprites,))
        self.wall = []
        self.stack_bricks()
        self.paddle = sprites.Paddle((self.sprites,))
        self.paddle.set_parent(self)
        self.spare_balls = 5
        self.score = 0
        self.speed = 5
        self.splash_screen = None
        self.launch()

    def getSensorValue(self):
        return self.sensor_data

    def start(self):
        self.sprites.empty()
        self.splash_screen = sprites.SplashScreen(
            settings.TITLE, (self.sprites,)
        )

    def over(self):
        self.sprites.empty()
        self.splash_screen = sprites.SplashScreen('GAME OVER', (self.sprites,))

    def stack_bricks(self):
        layers = (self.sprites, self.bricks)
        for i in range(len(settings.BRICK_LINES)):
            color = settings.BRICK_COLORS[i]
            y = settings.BRICK_LINES[i]
            for x in settings.BRICK_COLUMNS:
                brick = sprites.Brick(color, (x, y), layers)
                self.wall.append(brick)

    def breakout(self, brick):
        self.score += settings.POINTS.get(brick.color, 0)
        self.status.score = self.score
        self.wall.remove(brick)
        self.sfx['explosion'].play()
        if not self.wall:
            self.level_up()

    def launch(self):
        self.ball = sprites.Ball(self, self.speed, (self.sprites,))
        self.sfx['launch'].play()

    def out(self):
        if self.spare_balls:
            self.spare_balls -= 1
            self.status.spare_balls = self.spare_balls
            self.launch()
        else:
            self.over()

    def level_up(self):
        self.sfx['level'].play()
        self.sprites.remove((self.ball,))
        self.ball.kill()
        self.stack_bricks()
        self.speed += 2
        self.launch()

    def update(self):
        self.sprites.update()

    def draw(self):
        self.screen.fill(settings.BLACK)
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if self.splash_screen:
                    self.reset()
                    return

    def loop(self):
        while self.running:
            self.clock.tick(settings.FPS)
            self.update()
            self.draw()
            self.events()

    #This is the threading function, it reads the sensor data and it will convert it into an integer and 
    def read_sensor_input(self):
        proc = Popen([self.command], shell=True, text=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        line_found = False
        while not line_found:
            line = proc.stdout.readline()
            print(line)
            line.find("Long dispatch") > -1: # type: ignore
            line_found=True

        print("We reached the end of the startup")
        proc.stdout.flush()
        proc.stderr.flush()
        time.sleep(5)
        print(dir(proc.stdin))
        proc.stdin.write(self.levelcontrol)
        proc.stdin.close()

        output = "128"

        line_found = False

        while self.running:
            while not line_found:

                line = proc.stdout.readline()

                try:
                    data_index = line.index("Data =")
                except ValueError:
                    data_index = False


                if data_index != False:
                    output = line.split("Data = ")[1].split(",")[0]

                posistion = int(output)*2.36

                try:
                    self.paddle.move_to_pos(posistion) 
                except AttributeError:
                    print("Waiting for paddle to get started...")      
                


    def run(self):
        self.running = True
        self.start()

        #Threading was needed to make sure reading the sensor is not interrupting the game speed
        x = threading.Thread(target=self.read_sensor_input)
        x.start()

        #Sleep was needed to make sure the thread is starting and make no exceptions - time can be modified
        time.sleep(20)
        self.loop()
        pygame.quit()


    
def main():
    Game().run()


if __name__ == '__main__':
    main()
