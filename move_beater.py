"""
複数画像を切り替えながら等速移動するオブジェクト
"""
import pygame
from drawable import Drawable


class MoveBeater(Drawable):
    """複数画像をビートに合わせて切り替えながら等速移動するオブジェクト"""
    def __init__(self, x, y, image_paths, velocity_x=0, velocity_y=0, scale=1.0, 
                 heavy_processing=False, priority=0, wrap_screen=True, screen_width=800, screen_height=600):
        """
        Args:
            x, y: 初期位置
            image_paths: 画像パスのリスト（ビートごとに切り替わる）
            velocity_x, velocity_y: 移動速度（ピクセル/フレーム）
            scale: 画像のスケール
            heavy_processing: 重い処理シミュレーション
            priority: 描画優先順位
            wrap_screen: 画面端での折り返し有効/無効
            screen_width, screen_height: 画面サイズ（折り返し計算用）
        """
        super().__init__(x, y, priority)
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.scale = scale
        self.heavy_processing = heavy_processing
        self.wrap_screen = wrap_screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 位置を浮動小数点で管理（正確な移動のため）
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 画像リストを読み込み
        self.images = []
        for image_path in image_paths:
            if image_path:
                image = pygame.image.load(image_path)
                if scale != 1.0:
                    image = pygame.transform.scale(
                        image,
                        (int(image.get_width() * scale),
                         int(image.get_height() * scale))
                    )
                self.images.append(image)
        
        # 画像がない場合のエラー回避
        if not self.images:
            raise ValueError("At least one valid image path must be provided")
        
        # 現在の画像とインデックス
        self.current_image_index = 0
        self.current_image = self.images[self.current_image_index]
        
        # 矩形を初期化
        self.rect = self.current_image.get_rect(center=(int(self.float_x), int(self.float_y)))
        
        # ビート切り替えの管理
        self.last_beat = -1  # 前回処理したビート番号
        
        print(f"MoveBeater created: {len(self.images)} images, velocity=({velocity_x}, {velocity_y})")
    
    def update(self):
        """フレームごとの更新処理"""
        # 重い処理のシミュレーション（デバッグ用）
        if self.heavy_processing:
            import time
            time.sleep(0.01)  # 10msの遅延をシミュレート
        
        # 位置を更新
        self.float_x += self.velocity_x
        self.float_y += self.velocity_y
        
        # 画面端での処理
        if self.wrap_screen:
            self._wrap_around_screen()
        else:
            self._bounce_off_screen()
        
        # 整数座標に変換して矩形を更新
        self.x = int(self.float_x)
        self.y = int(self.float_y)
        self.rect = self.current_image.get_rect(center=(self.x, self.y))
    
    def _wrap_around_screen(self):
        """画面端で反対側に移動"""
        image_width = self.current_image.get_width()
        image_height = self.current_image.get_height()
        
        # 画像が完全に画面外に出たら反対側から登場
        if self.float_x > self.screen_width + image_width // 2:
            self.float_x = -image_width // 2
        elif self.float_x < -image_width // 2:
            self.float_x = self.screen_width + image_width // 2
            
        if self.float_y > self.screen_height + image_height // 2:
            self.float_y = -image_height // 2
        elif self.float_y < -image_height // 2:
            self.float_y = self.screen_height + image_height // 2
    
    def _bounce_off_screen(self):
        """画面端で跳ね返り"""
        image_width = self.current_image.get_width()
        image_height = self.current_image.get_height()
        
        # 左右の端で跳ね返り
        if self.float_x <= image_width // 2:
            self.float_x = image_width // 2
            self.velocity_x = abs(self.velocity_x)  # 右向きに変更
        elif self.float_x >= self.screen_width - image_width // 2:
            self.float_x = self.screen_width - image_width // 2
            self.velocity_x = -abs(self.velocity_x)  # 左向きに変更
        
        # 上下の端で跳ね返り
        if self.float_y <= image_height // 2:
            self.float_y = image_height // 2
            self.velocity_y = abs(self.velocity_y)  # 下向きに変更
        elif self.float_y >= self.screen_height - image_height // 2:
            self.float_y = self.screen_height - image_height // 2
            self.velocity_y = -abs(self.velocity_y)  # 上向きに変更
    
    def on_beat(self, beat, measure):
        """ビートのタイミングで画像を切り替え
        
        Args:
            beat: 絶対ビート番号
            measure: 小節内でのビート番号（0-3の循環）
        """
        # 同じビートで複数回呼ばれることを防ぐ
        if beat == self.last_beat:
            return
        self.last_beat = beat
        
        # 次の画像に切り替え
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.current_image = self.images[self.current_image_index]
        
        # 矩形を更新（画像サイズが変わる可能性があるため）
        self.rect = self.current_image.get_rect(center=(self.x, self.y))
    
    def draw(self, screen):
        """画像を描画"""
        screen.blit(self.current_image, self.rect)
    
    def set_velocity(self, velocity_x, velocity_y):
        """移動速度を変更"""
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
    
    def set_position(self, x, y):
        """位置を設定"""
        self.float_x = float(x)
        self.float_y = float(y)
        self.x = int(self.float_x)
        self.y = int(self.float_y)
        self.rect = self.current_image.get_rect(center=(self.x, self.y))
    
    def add_image(self, image_path):
        """実行時に画像を追加"""
        if image_path:
            image = pygame.image.load(image_path)
            if self.scale != 1.0:
                image = pygame.transform.scale(
                    image,
                    (int(image.get_width() * self.scale),
                     int(image.get_height() * self.scale))
                )
            self.images.append(image)
    
    def get_image_count(self):
        """画像数を取得"""
        return len(self.images)
    
    def get_current_image_index(self):
        """現在の画像インデックスを取得"""
        return self.current_image_index
