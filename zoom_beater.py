"""
ビートに合わせて画像を拡大/縮小するオブジェクト
"""
import pygame
from drawable import Drawable


class ZoomBeater(Drawable):
    """ビートに合わせて画像を拡大/縮小するオブジェクト"""
    def __init__(self, x, y, image_path, scale=1.0, zoom_scale=1.5, heavy_processing=False):
        super().__init__(x, y)
        self.original_image = pygame.image.load(image_path)
        self.scale = scale
        self.zoom_scale = zoom_scale
        self.current_scale = scale
        self.zoom_frame = 0
        self.zoom_duration = 3  # 3フレームで元のサイズに戻る
        self.heavy_processing = heavy_processing  # 重い処理のシミュレーション
        
        # 初期画像の準備
        self.image = pygame.transform.scale(
            self.original_image, 
            (int(self.original_image.get_width() * self.scale),
             int(self.original_image.get_height() * self.scale))
        )
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        """フレームごとの更新処理"""
        # 重い処理のシミュレーション（デバッグ用）
        if self.heavy_processing:
            import time
            time.sleep(0.01)  # 10msの遅延をシミュレート
        
        if self.zoom_frame > 0:
            # ズーム中の処理：3フレームで元のサイズに戻る
            progress = 1.0 - (self.zoom_frame / self.zoom_duration)
            self.current_scale = self.scale + (self.zoom_scale - self.scale) * progress
            self.zoom_frame -= 1
            
            # 画像のスケール更新
            new_width = int(self.original_image.get_width() * self.current_scale)
            new_height = int(self.original_image.get_height() * self.current_scale)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def on_beat(self, beat, measure):
        """ビートのタイミングで拡大開始"""
        self.zoom_frame = self.zoom_duration
        self.current_scale = self.zoom_scale
        
        # 即座に拡大画像を作成
        new_width = int(self.original_image.get_width() * self.current_scale)
        new_height = int(self.original_image.get_height() * self.current_scale)
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def draw(self, screen):
        """画像を描画"""
        screen.blit(self.image, self.rect)
