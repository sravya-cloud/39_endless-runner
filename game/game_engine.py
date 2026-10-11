import pygame
from .player import Player
from .obstacle import Obstacle

# Game Engine

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)

GAME_OVER_INPUT_DELAY = 30  # frames before a key press is accepted on Game Over

MAX_SPEED = 18  # px/frame ceiling for the speed ramp

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        self.player = Player(80, self.ground_y)

        self.speed = 6
        self.speed_increase_per_frame = 0.003
        self.max_speed = MAX_SPEED

        self.spawn_interval = 70  # frames between obstacle spawns
        self._spawn_timer = 0
        self.obstacles = []

        self.distance = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False
        self.game_over_frames = 0
        self.should_quit = False
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)

    def handle_event(self, event):
        if self.game_over:
            # Brief grace period so a key held/mashed at the moment of impact
            # doesn't dismiss the screen before it can be read.
            if event.type == pygame.KEYDOWN and self.game_over_frames >= GAME_OVER_INPUT_DELAY:
                self.should_quit = True
            return
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        # Reserved for continuously-held-key input; this runner only
        # needs an edge-triggered jump, handled in handle_event.
        pass

    def update(self):
        if self.game_over:
            self.game_over_frames += 1
            return

        self.speed = min(self.speed + self.speed_increase_per_frame, self.max_speed)
        self.player.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(Obstacle(self.width, self.ground_y))

        for obstacle in self.obstacles:
            obstacle.move(self.speed)

        # Swept test: the whole span each obstacle covered this frame, so
        # no speed can let one skip past the player.
        player_rect = self.player.rect()
        for obstacle in self.obstacles:
            if obstacle.swept_rect().colliderect(player_rect):
                self.game_over = True
                return

        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

        self.distance += self.speed

    def render(self, screen):
        pygame.draw.line(screen, BROWN, (0, self.ground_y), (self.width, self.ground_y), 4)

        pygame.draw.rect(screen, WHITE, self.player.rect())
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        lines = [
            (self.title_font, "Game Over", (255, 255, 255), -60),
            (self.font, f"Final Score: {self.score}", (255, 255, 255), 0),
        ]
        if self.game_over_frames >= GAME_OVER_INPUT_DELAY:
            lines.append((self.font, "Press any key to exit", (220, 220, 220), 50))
        for font, text, color, dy in lines:
            surf = font.render(text, True, color)
            screen.blit(surf, surf.get_rect(center=(self.width // 2, self.height // 2 + dy)))
