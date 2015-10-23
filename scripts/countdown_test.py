import picamera
import pygame
import time

pygame.font.init()
SCREEN_W = 1366
SCREEN_H = 788 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COUNTDOWN_LOCATION = (500, 635)
N_COUNTDOWN = 5
BOTTOM_RESERVE = 50 ## reserved room at bottom for countdown
FONTSIZE = 100 ## countdown fontsize

camera = picamera.PiCamera()
camera.led = False

camera.preview_alpha = 255
camera.preview_window = (0, 0, SCREEN_W, SCREEN_H - BOTTOM_RESERVE)
camera.preview_fullscreen = False

pygame.display.init()
# size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
screen.fill((0, 0, 0))        
pygame.display.update()

camera.start_preview()

font = pygame.font.Font(None, FONTSIZE)

text_color = WHITE

led_state = False

for i in range(N_COUNTDOWN):
    screen.fill(BLACK)
    text = font.render(str(N_COUNTDOWN - i), 1, text_color)
    textpos = text.get_rect()
    textpos.center = COUNTDOWN_LOCATION
    screen.blit(text, textpos)
    pygame.display.flip()
    if i < N_COUNTDOWN - 2:
        time.sleep(1)
        led_state = not led_state
        camera.led = led_state
    else:
        for j in range(5):
            time.sleep(.2)
            led_state = not led_state
            camera.led = led_state
        
camera.stop_preview()
