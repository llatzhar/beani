"""
ビートに合わせて色が変化する円形オブジェクト
"""
import pygame
from drawable import Drawable


class FlashBeater(Drawable):
    """ビートに合わせて色が変化する円形オブジェクト"""
    def __init__(self, x, y, radius=50, color=(255, 255, 255), flash_color=(255, 255, 0), priority=0):
        super().__init__(x, y, priority)
        self.radius = radius
        self.base_color = color
        self.flash_color = flash_color
        self.current_color = color
        self.flash_frame = 0
        self.flash_duration = 5  # 5フレームで元の色に戻る
    
    def update(self):
        """フレームごとの更新処理"""
        if self.flash_frame > 0:
            # フラッシュ中の処理：5フレームで元の色に戻る
            progress = 1.0 - (self.flash_frame / self.flash_duration)
            
            # 色を線形補間
            r = int(self.base_color[0] + (self.flash_color[0] - self.base_color[0]) * progress)
            g = int(self.base_color[1] + (self.flash_color[1] - self.base_color[1]) * progress)
            b = int(self.base_color[2] + (self.flash_color[2] - self.base_color[2]) * progress)
            
            self.current_color = (r, g, b)
            self.flash_frame -= 1
        else:
            self.current_color = self.base_color
    
    def on_beat(self, beat, measure):
        """ビートのタイミングでフラッシュ開始"""
        self.flash_frame = self.flash_duration
        self.current_color = self.flash_color
    
    def draw(self, screen):
        """円を描画"""
        pygame.draw.circle(screen, self.current_color, (int(self.x), int(self.y)), self.radius)
