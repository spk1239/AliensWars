import sys
from time import sleep
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from ship import Ship
from bullet import Bullet
from alien import Alien
from star import Star
from button import Button
import pygame
from random import randint


class AlienInvasion:

    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()

        self._create_fleet()
        self._create_stars()

        self.bg_color = (230, 230, 230)

        # Создаем кнопки с большим вертикальным расстоянием
        self.play_button = Button(self, "Play", -150)
        self.easy_button = Button(self, "Easy", -50, (0, 255, 0))
        self.normal_button = Button(self, "Normal", 50, (255, 255, 0))
        self.hard_button = Button(self, "Hard", 150, (255, 0, 0))

        # Текущий уровень сложности
        self.difficulty_level = "normal"

    def run_game(self):
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
        
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if not self.stats.game_active:
                    self._check_play_button(mouse_pos)
                    self._check_difficulty_buttons(mouse_pos)

    def _check_difficulty_buttons(self, mouse_pos):
        """Обрабатывает нажатия на кнопки выбора сложности."""
        easy_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        normal_clicked = self.normal_button.rect.collidepoint(mouse_pos)
        hard_clicked = self.hard_button.rect.collidepoint(mouse_pos)
        
        if easy_clicked:
            self.difficulty_level = "easy"
            self._set_difficulty()
           
        elif normal_clicked:
            self.difficulty_level = "normal"
            self._set_difficulty()
         
        elif hard_clicked:
            self.difficulty_level = "hard"
            self._set_difficulty()
         

    def _set_difficulty(self):
        """Устанавливает настройки сложности в зависимости от выбранного уровня."""
        if self.difficulty_level == "easy":
            self.settings.ship_speed_factor = 2.0
            self.settings.bullet_speed_factor = 4.0
            self.settings.alien_speed_factor = 0.5
            self.settings.speedup_scale = 1.05
            self.settings.bullets_allowed = 6
        elif self.difficulty_level == "normal":
            self.settings.ship_speed_factor = 1.5
            self.settings.bullet_speed_factor = 3.0
            self.settings.alien_speed_factor = 1.0
            self.settings.speedup_scale = 1.1
            self.settings.bullets_allowed = 5
        elif self.difficulty_level == "hard":
            self.settings.ship_speed_factor = 1.0
            self.settings.bullet_speed_factor = 2.0
            self.settings.alien_speed_factor = 1.5
            self.settings.speedup_scale = 1.2
            self.settings.bullets_allowed = 4

    def _start_game(self):
        """Запускает новую игру при нажатии клавиши P."""
        if not self.stats.game_active:
            self.stats.reset_stats()
            self.stats.game_active = True

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()
            
            pygame.mouse.set_visible(False)

    def _check_play_button(self, mouse_pos):
        """Запускает новую игру при нажатии кнопки Play."""
        if self.play_button.rect.collidepoint(mouse_pos):
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()
            
    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            self._start_game()
        # Быстрый выбор сложности клавишами
        elif event.key == pygame.K_1:
            self.difficulty_level = "easy"
            self._set_difficulty()
        elif event.key == pygame.K_2:
            self.difficulty_level = "normal"
            self._set_difficulty()
        elif event.key == pygame.K_3:
            self.difficulty_level = "hard"
            self._set_difficulty()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        self._check_aliens_bottom()

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
        
            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_stars(self):
        star = Star(self)
        star_width, star_height = star.rect.size
    
        number_stars = 100  
    
        for star_number in range(number_stars):
            self._create_star(star_width, star_height)

    def _create_star(self, star_width, star_height):
        star = Star(self)
    
        star_x = randint(10, self.settings.screen_width - star_width - 10)
        star_y = randint(10, self.settings.screen_height - star_height - 10)
    
        star.rect.x = star_x
        star.rect.y = star_y
        self.stars.add(star)
    
    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.stars.draw(self.screen)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()

        if not self.stats.game_active:
            # Отображаем все кнопки
            self.play_button.draw_button()
            self.easy_button.draw_button()
            self.normal_button.draw_button()
            self.hard_button.draw_button()

            # Отображаем текущий уровень сложности
            font = pygame.font.SysFont(None, 48)
            difficulty_text = f"Difficulty: {self.difficulty_level.upper()}"
            text_surface = font.render(difficulty_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.screen.get_rect().centerx
            text_rect.top = self.hard_button.rect.bottom + 30
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()