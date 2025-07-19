import pygame
import math
import os

class Drawable:
    """描画可能オブジェクトの基底クラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def update(self):
        """フレームごとに呼ばれる更新処理"""
        pass
    
    def on_beat(self, beat_count):
        """ビートのタイミングで呼ばれる処理"""
        pass
    
    def draw(self, screen):
        """描画処理"""
        pass

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
    
    def on_beat(self, beat_count):
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

class FlashBeater(Drawable):
    """ビートに合わせて色が変化する円形オブジェクト"""
    def __init__(self, x, y, radius=50, color=(255, 255, 255), flash_color=(255, 255, 0)):
        super().__init__(x, y)
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
    
    def on_beat(self, beat_count):
        """ビートのタイミングでフラッシュ開始"""
        self.flash_frame = self.flash_duration
        self.current_color = self.flash_color
    
    def draw(self, screen):
        """円を描画"""
        pygame.draw.circle(screen, self.current_color, (int(self.x), int(self.y)), self.radius)

class Scene:
    """シーンクラス"""
    def __init__(self):
        self.drawables = []
    
    def add_drawable(self, drawable):
        """Drawableオブジェクトを追加"""
        self.drawables.append(drawable)
    
    def update(self):
        """全てのDrawableオブジェクトを更新"""
        for drawable in self.drawables:
            drawable.update()
    
    def on_beat(self, beat_count):
        """全てのDrawableオブジェクトにビート通知"""
        for drawable in self.drawables:
            drawable.on_beat(beat_count)
    
    def draw(self, screen):
        """全てのDrawableオブジェクトを描画"""
        for drawable in self.drawables:
            drawable.draw(screen)

class Movie:
    """ムービークラス"""
    def __init__(self, width=800, height=600, fps=30, bpm=120, beats_per_measure=4):
        pygame.init()
        pygame.mixer.init()
        
        self.width = width
        self.height = height
        self.fps = fps
        self.bpm = bpm
        self.beats_per_measure = beats_per_measure
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("beani - Movie Player")
        self.clock = pygame.time.Clock()
        
        # BPM計算
        # 120BPMの場合、1分間に120ビート = 1ビートあたり0.5秒
        self.beat_interval = 60.0 / bpm  # 秒
        self.beat_interval_ms = self.beat_interval * 1000  # ミリ秒
        self.frames_per_beat = int(fps * self.beat_interval)
        
        # 時間ベースのビート管理
        self.start_time = None
        self.music_start_time = None
        self.last_beat_time = 0
        self.beat_count = 0
        self.last_beat_count = -1  # 前回処理したビート番号
        
        # フレーム管理
        self.frame_count = 0
        self.scenes = []
        self.current_scene = 0
        
        # パフォーマンス監視
        self.actual_fps = fps
        self.fps_samples = []
        self.last_fps_time = 0
        self.heavy_processing_mode = False  # 重い処理モードのフラグ
        
        print(f"BPM: {bpm}, Beat interval: {self.beat_interval:.2f}s, Frames per beat: {self.frames_per_beat}")
        print("Time-based beat detection enabled for accurate synchronization")
        print("Press 'H' to toggle heavy processing simulation")
    
    def add_scene(self, scene, duration_beats=None):
        """シーンを追加"""
        self.scenes.append({
            'scene': scene,
            'duration_beats': duration_beats,  # シーンの再生時間（ビート数）
            'start_beat': None  # シーン開始時のビート番号
        })
    
    def get_current_scene_info(self):
        """現在のシーン情報を取得"""
        if not self.scenes or self.current_scene >= len(self.scenes):
            return None
        return self.scenes[self.current_scene]
    
    def switch_to_next_scene(self):
        """次のシーンに切り替え"""
        if self.current_scene < len(self.scenes) - 1:
            self.current_scene += 1
            # 新しいシーンの開始ビートを記録
            current_beat = self.get_current_beat_from_music() or self.get_current_beat_from_time()
            if current_beat is not None and self.current_scene < len(self.scenes):
                self.scenes[self.current_scene]['start_beat'] = current_beat
            print(f"Switched to scene {self.current_scene + 1}/{len(self.scenes)}")
            return True
        else:
            print("All scenes completed")
            return False
    
    def check_scene_transition(self, current_beat):
        """シーンの切り替えが必要かチェック"""
        scene_info = self.get_current_scene_info()
        if not scene_info or scene_info['duration_beats'] is None:
            return False
        
        # 現在のシーンの開始ビートが設定されていない場合は設定
        if scene_info['start_beat'] is None:
            scene_info['start_beat'] = current_beat
            return False
        
        # シーン内での経過ビート数を計算
        beats_in_scene = current_beat - scene_info['start_beat']
        
        # 指定されたビート数に達したら次のシーンに切り替え
        if beats_in_scene >= scene_info['duration_beats']:
            return self.switch_to_next_scene()
        
        return False
    
    def load_music(self, music_file):
        """音楽ファイルを読み込み"""
        if os.path.exists(music_file):
            pygame.mixer.music.load(music_file)
            print(f"Loaded music: {music_file}")
        else:
            print(f"Music file not found: {music_file}")
    
    def play_music(self):
        """音楽を再生"""
        pygame.mixer.music.play()
        self.music_start_time = pygame.time.get_ticks()
        self.start_time = self.music_start_time
        self.last_beat_time = 0
        self.beat_count = 0
        self.last_beat_count = -1
        print(f"Music started at {self.music_start_time}ms")
    
    def get_current_beat_from_music(self):
        """音楽の再生位置からビート番号を計算"""
        if not pygame.mixer.music.get_busy() or self.music_start_time is None:
            return None
        
        # 音楽の再生位置を取得（ミリ秒）
        music_pos = pygame.mixer.music.get_pos()
        if music_pos == -1:  # 音楽が停止している場合
            return None
        
        # 音楽開始からの経過時間
        elapsed_time_ms = music_pos
        
        # ビート番号を計算
        current_beat = int(elapsed_time_ms / self.beat_interval_ms)
        return current_beat
    
    def get_current_beat_from_time(self):
        """実時間からビート番号を計算（フォールバック）"""
        if self.start_time is None:
            return None
        
        current_time = pygame.time.get_ticks()
        elapsed_time_ms = current_time - self.start_time
        current_beat = int(elapsed_time_ms / self.beat_interval_ms)
        return current_beat
    
    def update_fps_monitor(self):
        """FPS監視を更新"""
        current_time = pygame.time.get_ticks()
        if self.last_fps_time > 0:
            frame_time = current_time - self.last_fps_time
            if frame_time > 0:
                current_fps = 1000.0 / frame_time
                self.fps_samples.append(current_fps)
                
                # 過去1秒間のサンプルを保持
                if len(self.fps_samples) > 60:
                    self.fps_samples.pop(0)
                
                self.actual_fps = sum(self.fps_samples) / len(self.fps_samples)
        
        self.last_fps_time = current_time
    
    def run(self):
        """メインループ"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # スペースキーで音楽再生/停止
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                        else:
                            self.play_music()
                    elif event.key == pygame.K_h:
                        # Hキーで重い処理モードの切り替え
                        self.heavy_processing_mode = not self.heavy_processing_mode
                        # 全てのZoomBeaterの重い処理モードを更新
                        scene_info = self.get_current_scene_info()
                        if scene_info and scene_info['scene']:
                            for drawable in scene_info['scene'].drawables:
                                if hasattr(drawable, 'heavy_processing'):
                                    drawable.heavy_processing = self.heavy_processing_mode
                        print(f"Heavy processing mode: {'ON' if self.heavy_processing_mode else 'OFF'}")
            
            # FPS監視更新
            self.update_fps_monitor()
            
            # 実時間ベースのビート検出
            current_beat = None
            
            # まず音楽の再生位置からビートを取得
            current_beat = self.get_current_beat_from_music()
            
            # 音楽が停止中または取得できない場合は実時間ベースにフォールバック
            if current_beat is None:
                current_beat = self.get_current_beat_from_time()
            
            # 新しいビートが発生した場合のみon_beatを呼び出し
            if current_beat is not None and current_beat != self.last_beat_count:
                if current_beat > self.last_beat_count:  # ビートが進んだ場合のみ
                    # シーンの切り替えをチェック
                    self.check_scene_transition(current_beat)
                    
                    beat_in_measure = current_beat % self.beats_per_measure
                    scene_info = self.get_current_scene_info()
                    if scene_info and scene_info['scene']:
                        scene_info['scene'].on_beat(beat_in_measure)
                    
                    # デバッグ情報（パフォーマンス低下時のみ表示）
                    if self.actual_fps < self.fps * 0.8:  # 目標FPSの80%以下の場合
                        scene_num = self.current_scene + 1
                        total_scenes = len(self.scenes)
                        print(f"Beat {current_beat} (measure: {beat_in_measure}) Scene {scene_num}/{total_scenes} - FPS: {self.actual_fps:.1f}")
                    
                    self.last_beat_count = current_beat
            
            # 更新処理
            scene_info = self.get_current_scene_info()
            if scene_info and scene_info['scene']:
                scene_info['scene'].update()
            
            # 描画処理
            self.screen.fill((0, 0, 50))  # 濃紺背景
            if scene_info and scene_info['scene']:
                scene_info['scene'].draw(self.screen)
            
            # シーン情報を画面に表示
            if scene_info:
                font = pygame.font.Font(None, 24)
                scene_num = self.current_scene + 1
                total_scenes = len(self.scenes)
                scene_text = font.render(f"Scene {scene_num}/{total_scenes}", True, (255, 255, 255))
                self.screen.blit(scene_text, (10, 50))
                
                # シーンの残り時間表示
                if scene_info['duration_beats'] is not None and scene_info['start_beat'] is not None:
                    beats_in_scene = current_beat - scene_info['start_beat'] if current_beat else 0
                    remaining_beats = max(0, scene_info['duration_beats'] - beats_in_scene)
                    remaining_text = font.render(f"Remaining: {remaining_beats} beats", True, (255, 255, 255))
                    self.screen.blit(remaining_text, (10, 75))
            
            # FPS情報を画面に表示（デバッグ用）
            if hasattr(pygame, 'font') and self.actual_fps < self.fps * 0.9:
                font = pygame.font.Font(None, 36)
                fps_text = font.render(f"FPS: {self.actual_fps:.1f}", True, (255, 255, 0))
                self.screen.blit(fps_text, (10, 10))
            
            pygame.display.flip()
            self.clock.tick(self.fps)
            self.frame_count += 1
        
        pygame.quit()

def main():
    """メイン関数"""
    # ムービー初期化
    movie = Movie(width=800, height=600, fps=30, bpm=120)
    
    # 音楽ファイル読み込み
    movie.load_music("base.mp3")
    
    # === シーン1: ZoomBeaterのシーン (16ビート = 4小節) ===
    scene1 = Scene()
    
    # ZoomBeaterオブジェクト作成（画面中央に配置）
    if os.path.exists("images/star_1.png"):
        zoom_beater = ZoomBeater(400, 300, "images/star_1.png", scale=1.0, zoom_scale=1.5)
        scene1.add_drawable(zoom_beater)
        
        # 複数のZoomBeaterを追加
        positions = [(200, 150), (600, 150), (200, 450), (600, 450)]
        for i, (x, y) in enumerate(positions):
            if os.path.exists("images/star_2.png"):
                zoom_beater2 = ZoomBeater(x, y, "images/star_2.png", scale=0.8, zoom_scale=1.3)
            else:
                zoom_beater2 = ZoomBeater(x, y, "images/star_1.png", scale=0.6, zoom_scale=1.2)
            scene1.add_drawable(zoom_beater2)
        
        print("Scene 1: ZoomBeater scene created")
    else:
        print("Warning: images/star_1.png not found")
    
    # === シーン2: FlashBeaterのシーン (12ビート = 3小節) ===
    scene2 = Scene()
    
    # FlashBeaterオブジェクト作成
    colors = [
        (255, 100, 100),  # 赤
        (100, 255, 100),  # 緑
        (100, 100, 255),  # 青
        (255, 255, 100),  # 黄
        (255, 100, 255),  # マゼンタ
    ]
    
    flash_positions = [
        (150, 200), (400, 150), (650, 200),
        (200, 350), (600, 350), (400, 450)
    ]
    
    for i, (x, y) in enumerate(flash_positions):
        color = colors[i % len(colors)]
        flash_beater = FlashBeater(x, y, radius=40, color=color, flash_color=(255, 255, 255))
        scene2.add_drawable(flash_beater)
    
    print("Scene 2: FlashBeater scene created")
    
    # === シーン3: 混合シーン (20ビート = 5小節) ===
    scene3 = Scene()
    
    # 中央に大きなFlashBeater
    center_flash = FlashBeater(400, 300, radius=80, color=(50, 50, 200), flash_color=(255, 255, 0))
    scene3.add_drawable(center_flash)
    
    # 周囲に小さなZoomBeater（画像がある場合）
    if os.path.exists("images/star_1.png"):
        circle_positions = []
        for angle in range(0, 360, 45):  # 8方向
            rad = math.radians(angle)
            x = 400 + 150 * math.cos(rad)
            y = 300 + 150 * math.sin(rad)
            circle_positions.append((x, y))
        
        for x, y in circle_positions:
            small_zoom = ZoomBeater(int(x), int(y), "images/star_1.png", scale=0.4, zoom_scale=0.8)
            scene3.add_drawable(small_zoom)
    
    print("Scene 3: Mixed scene created")
    
    # シーンをムービーに追加（再生時間を指定）
    movie.add_scene(scene1, duration_beats=8)  # 2小節
    movie.add_scene(scene2, duration_beats=8)  # 1小節
    movie.add_scene(scene3, duration_beats=16)  # 2小節
    
    print(f"Total scenes: {len(movie.scenes)}")
    print("Scene durations: 8, 8, 16 beats respectively")

    # 音楽再生開始
    movie.play_music()
    
    print("Movie started! Press SPACE to play/stop music, H to toggle heavy processing")
    print("Time-based beat synchronization enabled - beats will stay in sync even with low FPS")
    print("Scenes will automatically switch based on beat count")
    
    # ムービー実行
    movie.run()

if __name__ == "__main__":
    main()
