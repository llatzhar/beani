import pygame
import math

class Countdown:
    """カウントダウン管理クラス（シーンから独立）"""
    def __init__(self, width, height, countdown_beats=4):
        self.countdown_beats = countdown_beats
        self.is_active = False
        self.is_completed = False
        self.start_time = None
        self.beat_interval_ms = 500  # 120BPMでの1ビートの時間（ms）
        self.last_beat_processed = -1
        
        # 表示位置
        self.center_x = width // 2
        self.center_y = height // 2
        self.info_y = height // 2 + 150
        
        # カウントダウン表示用
        self.current_count = countdown_beats
        self.flash_frame = 0
        self.flash_duration = 10  # 10フレームでフラッシュ効果
        
        # 情報テキスト用
        self.text = "Get ready! Music starts after countdown"
        self.alpha = 255
        self.fade_frame = 0
    
    def start_countdown(self, beat_interval_ms):
        """カウントダウン開始"""
        self.is_active = True
        self.is_completed = False
        self.start_time = pygame.time.get_ticks()
        self.beat_interval_ms = beat_interval_ms
        self.last_beat_processed = -1
        self.current_count = self.countdown_beats
        print(f"Countdown started for {self.countdown_beats} beats")
    
    def update(self):
        """フレームごとの更新処理"""
        if not self.is_active or self.is_completed:
            return
        
        # 現在の経過時間からビート計算
        current_time = pygame.time.get_ticks()
        elapsed_ms = current_time - self.start_time
        current_beat = int(elapsed_ms / self.beat_interval_ms)
        
        # カウントダウン完了チェック
        if current_beat >= self.countdown_beats:
            self.is_completed = True
            self.is_active = False
            print(f"Countdown completed!")
            return
        
        # ビートが進んだときのカウントダウン更新
        if current_beat != self.last_beat_processed and current_beat < self.countdown_beats:
            new_count = self.countdown_beats - current_beat
            if new_count != self.current_count and new_count > 0:
                self.current_count = new_count
                self.flash_frame = self.flash_duration  # フラッシュ効果を開始
                print(f"Countdown: {self.current_count}")
            self.last_beat_processed = current_beat
        
        # フラッシュ効果の更新
        if self.flash_frame > 0:
            self.flash_frame -= 1
        
        # 情報テキストの点滅効果
        self.fade_frame += 1
        self.alpha = int(200 + 55 * math.sin(self.fade_frame * 0.1))
    
    def draw(self, screen):
        """カウントダウンを描画"""
        if not self.is_active or self.is_completed or self.current_count <= 0:
            return
        
        # カウントダウン数字の描画
        # フラッシュ効果の計算
        flash_intensity = 1.0
        if self.flash_frame > 0:
            flash_intensity = 1.0 + (self.flash_frame / self.flash_duration) * 0.5
        
        # 大きなフォントでカウントダウン数字を表示
        font_size = int(200 * flash_intensity)
        font = pygame.font.Font(None, font_size)
        
        # カウントダウン数字
        color_intensity = min(255, int(255 * flash_intensity))
        text_color = (color_intensity, color_intensity, color_intensity)
        
        text = font.render(str(self.current_count), True, text_color)
        text_rect = text.get_rect(center=(self.center_x, self.center_y))
        screen.blit(text, text_rect)
        
        # 背景に円を描画（ビジュアル効果）
        circle_radius = int(120 * flash_intensity)
        circle_color = (int(100 * flash_intensity), int(100 * flash_intensity), int(100 * flash_intensity))
        pygame.draw.circle(screen, circle_color, (self.center_x, self.center_y), circle_radius, 3)
        
        # 情報テキストの描画
        info_font = pygame.font.Font(None, 36)
        info_color = (self.alpha, self.alpha, self.alpha)
        info_text = info_font.render(self.text, True, info_color)
        info_rect = info_text.get_rect(center=(self.center_x, self.info_y))
        screen.blit(info_text, info_rect)
