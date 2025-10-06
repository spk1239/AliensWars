import pygame.font
import pygame

class Button():

    def __init__(self, ai_game, msg, y_offset=0, button_color=(0, 255, 0)):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        self.width, self.height = 250, 60
        self.button_color = button_color
        self.text_color = (255, 255, 255)
        self.outline_color = (0, 0, 0)
        self.font = pygame.font.SysFont(None, 48)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = self.screen_rect.centerx
        self.rect.centery = self.screen_rect.centery + y_offset

        self.prep_msg(msg)

    def prep_msg(self, msg):
        # Простой способ - рендерим текст дважды с небольшим смещением
        self.msg = msg
        self.msg_image = self.font.render(msg, True, self.text_color)
        self.msg_outline = self.font.render(msg, True, self.outline_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        # Рисуем кнопку
        pygame.draw.rect(self.screen, self.button_color, self.rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2, border_radius=10)
        
        # Рисуем обводку текста (8 направлений вокруг основного текста)
        outline_positions = [
            (self.msg_image_rect.x - 1, self.msg_image_rect.y - 1),
            (self.msg_image_rect.x, self.msg_image_rect.y - 1),
            (self.msg_image_rect.x + 1, self.msg_image_rect.y - 1),
            (self.msg_image_rect.x - 1, self.msg_image_rect.y),
            (self.msg_image_rect.x + 1, self.msg_image_rect.y),
            (self.msg_image_rect.x - 1, self.msg_image_rect.y + 1),
            (self.msg_image_rect.x, self.msg_image_rect.y + 1),
            (self.msg_image_rect.x + 1, self.msg_image_rect.y + 1)
        ]
        
        for pos in outline_positions:
            self.screen.blit(self.msg_outline, pos)
        
        # Рисуем основной текст поверх обводки
        self.screen.blit(self.msg_image, self.msg_image_rect)