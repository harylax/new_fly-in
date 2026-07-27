import pygame

pygame.init()

WIDTH = 1600
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Déplacement")

clock = pygame.time.Clock()

BACKGROUND = pygame.image.load('isometric-city-bg-1600x800-darker.png')
drone = pygame.image.load('drone-isometric-facing-right.png')
DRONE_IMG = pygame.transform.smoothscale(drone, (100, 100))

x = 100
y = 100
vel = 5


def redraw_window(x: int, y: int) -> None:
    global screen
    # screen.fill((20, 20, 20))

    screen.blit(BACKGROUND, (0, 0))

    pygame.draw.circle(screen, (0, 190, 20), (50, 400), 30)
    screen.blit(DRONE_IMG, (x, y))

    # pygame.draw.rect(screen, (0, 255, 0), (x, y, 50, 50))
    # pygame.draw.line(screen, (0,255,0), (x,y), (x + 100, y), 15)

    pygame.display.flip()


running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False

    if keys[pygame.K_LEFT] and x > 0:
        x -= vel

    if keys[pygame.K_RIGHT] and x < WIDTH - 50:
        x += vel

    if keys[pygame.K_UP] and y > 0:
        y -= vel

    if keys[pygame.K_DOWN] and y < HEIGHT - 50:
        y += vel

    redraw_window(x, y)

    clock.tick(60)

pygame.quit()
