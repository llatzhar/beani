"""
4拍子に合わせて異なる画像を表示するオブジェクト
"""
import pygame
from drawable import Drawable


class BeatImageBeater(Drawable):
    """4拍子の各拍に合わせて異なる画像を表示するオブジェクト"""
    def __init__(self, x, y, default_image_path, beat_images_paths, scale=1.0, heavy_processing=False, priority=0):
        """
        Args:
            x, y: 位置
            default_image_path: 通常時に表示する画像のパス
            beat_images_paths: 各拍で表示する画像のパスのリスト [拍0の画像, 拍1の画像, 拍2の画像, 拍3の画像]
            scale: 画像のスケール
            heavy_processing: 重い処理シミュレーション
            priority: 描画優先順位
        """
        super().__init__(x, y, priority)
        self.scale = scale
        self.heavy_processing = heavy_processing
        
        # 通常時の画像を読み込み
        self.default_image = pygame.image.load(default_image_path)
        self.default_image = pygame.transform.scale(
            self.default_image,
            (int(self.default_image.get_width() * scale),
             int(self.default_image.get_height() * scale))
        )
        
        # 各拍用の画像を読み込み（4拍分）
        self.beat_images = []
        for i, image_path in enumerate(beat_images_paths[:4]):  # 最大4つまで
            if image_path:
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(
                    image,
                    (int(image.get_width() * scale),
                     int(image.get_height() * scale))
                )
                self.beat_images.append(image)
            else:
                # 画像パスがNoneの場合はデフォルト画像を使用
                self.beat_images.append(self.default_image)
        
        # 4拍に満たない場合はデフォルト画像で補完
        while len(self.beat_images) < 4:
            self.beat_images.append(self.default_image)
        
        # 現在の状態
        self.current_image = self.default_image
        self.beat_frame = 0  # ビート画像表示の残りフレーム数
        self.beat_duration = 10  # 10フレーム間ビート画像を表示
        self.current_beat_index = 0  # 現在のビート番号（0-3）
        
        self.rect = self.current_image.get_rect(center=(x, y))
    
    def update(self):
        """フレームごとの更新処理"""
        # 重い処理のシミュレーション（デバッグ用）
        if self.heavy_processing:
            import time
            time.sleep(0.01)  # 10msの遅延をシミュレート
        
        if self.beat_frame > 0:
            # ビート画像表示中
            self.beat_frame -= 1
            if self.beat_frame == 0:
                # ビート画像表示終了、デフォルト画像に戻る
                self.current_image = self.default_image
                self.rect = self.current_image.get_rect(center=(self.x, self.y))
    
    def on_beat(self, beat, measure):
        """ビートのタイミングでビート画像表示開始
        
        Args:
            beat: 絶対ビート番号
            measure: 小節内でのビート番号（0-3の循環）
        """
        # 小節内のビート番号（0-3）に応じて画像を選択
        self.current_beat_index = measure % 4
        self.current_image = self.beat_images[self.current_beat_index]
        self.beat_frame = self.beat_duration
        
        # 画像の位置を更新
        self.rect = self.current_image.get_rect(center=(self.x, self.y))
    
    def draw(self, screen):
        """画像を描画"""
        screen.blit(self.current_image, self.rect)
    
    def set_beat_image(self, beat_index, image_path):
        """特定の拍の画像を変更
        
        Args:
            beat_index: ビート番号（0-3）
            image_path: 新しい画像のパス
        """
        if 0 <= beat_index < 4 and image_path:
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(
                image,
                (int(image.get_width() * self.scale),
                 int(image.get_height() * self.scale))
            )
            self.beat_images[beat_index] = image
