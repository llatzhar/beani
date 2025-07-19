import pygame
import math
import os
from resources import Resources

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

class CountdownBeater(Drawable):
    """カウントダウン表示用のオブジェクト"""
    def __init__(self, x, y, initial_count=4, font_size=200):
        super().__init__(x, y)
        self.initial_count = initial_count
        self.current_count = initial_count
        self.font_size = font_size
        self.is_active = True
        self.flash_frame = 0
        self.flash_duration = 10  # 10フレームでフラッシュ効果
    
    def update(self):
        """フレームごとの更新処理"""
        if self.flash_frame > 0:
            self.flash_frame -= 1
    
    def on_beat(self, beat_count):
        """ビートのタイミングでカウントダウン更新"""
        if self.is_active and self.current_count > 0:
            # beat_countは0, 1, 2, 3の順なので、カウントダウンを計算
            # beat_count 0 -> count 4, beat_count 1 -> count 3, ...
            new_count = self.initial_count - beat_count
            if new_count > 0 and new_count != self.current_count:
                self.current_count = new_count
                self.flash_frame = self.flash_duration  # フラッシュ効果を開始
                print(f"Countdown: {self.current_count}")
            elif new_count <= 0:
                self.current_count = 0
                self.is_active = False
                print("Countdown finished!")
    
    def draw(self, screen):
        """カウントダウンを画面に描画"""
        if not self.is_active or self.current_count <= 0:
            return
        
        # フラッシュ効果の計算
        flash_intensity = 1.0
        if self.flash_frame > 0:
            flash_intensity = 1.0 + (self.flash_frame / self.flash_duration) * 0.5
        
        # 大きなフォントでカウントダウン数字を表示
        font = pygame.font.Font(None, int(self.font_size * flash_intensity))
        
        # カウントダウン数字
        color_intensity = min(255, int(255 * flash_intensity))
        text_color = (color_intensity, color_intensity, color_intensity)
        
        text = font.render(str(self.current_count), True, text_color)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)
        
        # 背景に円を描画（ビジュアル効果）
        circle_radius = int(120 * flash_intensity)
        circle_color = (int(100 * flash_intensity), int(100 * flash_intensity), int(100 * flash_intensity))
        pygame.draw.circle(screen, circle_color, (int(self.x), int(self.y)), circle_radius, 3)

class CountdownInfoText(Drawable):
    """カウントダウン説明テキスト用のオブジェクト"""
    def __init__(self, x, y, text="Get ready! Music starts after countdown"):
        super().__init__(x, y)
        self.text = text
        self.alpha = 255
        self.fade_frame = 0
    
    def update(self):
        """フレームごとの更新処理"""
        # テキストの点滅効果
        self.fade_frame += 1
        self.alpha = int(200 + 55 * math.sin(self.fade_frame * 0.1))
    
    def on_beat(self, beat_count):
        """ビートのタイミングでの処理"""
        pass
    
    def draw(self, screen):
        """説明テキストを描画"""
        font = pygame.font.Font(None, 36)
        color = (self.alpha, self.alpha, self.alpha)
        text = font.render(self.text, True, color)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)

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
    def __init__(self, name="Unnamed Scene", duration_beats=None):
        self.drawables = []
        self.name = name
        self.duration_beats = duration_beats  # シーンの再生時間（ビート数）
        self.start_beat = None  # シーン開始時のビート番号
    
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

class CountdownScene(Scene):
    """カウントダウン専用のシーンクラス"""
    def __init__(self, width, height, countdown_beats=4, on_complete_callback=None):
        super().__init__("Countdown Scene", duration_beats=countdown_beats)
        self.countdown_beats = countdown_beats
        self.on_complete_callback = on_complete_callback
        self.is_completed = False
        
        # カウントダウン表示オブジェクトを作成
        countdown_display = CountdownBeater(width // 2, height // 2, initial_count=countdown_beats)
        self.add_drawable(countdown_display)
        
        # 説明テキストオブジェクトを作成
        info_text = CountdownInfoText(width // 2, height // 2 + 150)
        self.add_drawable(info_text)
    
    def on_beat(self, beat_count):
        """ビート処理とカウントダウン完了チェック"""
        super().on_beat(beat_count)
        
        # カウントダウン完了チェック
        # beat_count が countdown_beats に達したら完了
        if not self.is_completed and beat_count >= self.countdown_beats:
            self.is_completed = True
            print(f"CountdownScene completed at beat {beat_count}")
            if self.on_complete_callback:
                self.on_complete_callback()
    
    def is_finished(self):
        """カウントダウンが完了したかどうか"""
        return self.is_completed

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
        
        # カウントダウンとムービー状態
        self.music_ready = False  # 音楽準備完了フラグ
        self.countdown_scene = None  # カウントダウンシーンへの参照
        
        print(f"BPM: {bpm}, Beat interval: {self.beat_interval:.2f}s, Frames per beat: {self.frames_per_beat}")
        print("Time-based beat detection enabled for accurate synchronization")
        print("Press 'H' to toggle heavy processing simulation")
    
    def add_countdown_scene(self, countdown_beats=4):
        """カウントダウンシーンを最初に追加"""
        def on_countdown_complete():
            self.start_music_and_scenes()
        
        self.countdown_scene = CountdownScene(
            self.width, 
            self.height, 
            countdown_beats=countdown_beats,
            on_complete_callback=on_countdown_complete
        )
        
        # カウントダウンシーンを最初に挿入
        self.scenes.insert(0, self.countdown_scene)
        
        print(f"Countdown scene added ({countdown_beats} beats)")
    
    def start_music_and_scenes(self):
        """カウントダウン完了後に音楽を開始し、次のシーンに移動"""
        pygame.mixer.music.play()
        self.music_ready = True
        
        # 音楽開始時刻を記録（音楽位置検出の基準点）
        self.music_start_time = pygame.time.get_ticks()
        
        # ビート管理をリセット - 音楽開始時点を新たな基準点とする
        # beat 0から開始できるよう、last_beat_countを-1にリセット
        self.last_beat_count = -1
        self.start_time = self.music_start_time
        
        # 全シーンの開始ビートをリセット
        for scene in self.scenes:
            scene.start_beat = None
        
        print(f"Music started after countdown! Total scenes: {len(self.scenes)}")
        print(f"Current scene index: {self.current_scene}")
        
        # 次のシーンに移動（ビートリセット後なので正しいbeat 0付近が設定される）
        if len(self.scenes) > 1:
            result = self.switch_to_next_scene()
            print(f"Scene switch result: {result}")
            
            # 新しいシーンの開始ビートを0に設定
            if result and self.current_scene < len(self.scenes):
                self.scenes[self.current_scene].start_beat = 0
                print(f"Scene '{self.scenes[self.current_scene].name}' start_beat set to 0")
        
        print("Scene transitions begin now!")
    
    def play_with_countdown(self, countdown_beats=4):
        """カウントダウン付きでムービーを開始"""
        self.add_countdown_scene(countdown_beats)
        self.start_time = pygame.time.get_ticks()
        self.last_beat_count = -1
        print("Movie started with countdown scene!")
    
    def add_scene(self, scene, duration_beats=None):
        """シーンを追加"""
        if duration_beats is not None:
            scene.duration_beats = duration_beats
        self.scenes.append(scene)
    
    def get_current_scene(self):
        """現在のシーンを取得"""
        if not self.scenes or self.current_scene >= len(self.scenes):
            return None
        return self.scenes[self.current_scene]
    
    def switch_to_next_scene(self):
        """次のシーンに切り替え"""
        old_scene = self.current_scene
        if self.current_scene < len(self.scenes) - 1:
            self.current_scene += 1
            # 新しいシーンの開始ビートを記録
            current_beat = self.get_current_beat_from_music() or self.get_current_beat_from_time()
            if current_beat is not None and self.current_scene < len(self.scenes):
                self.scenes[self.current_scene].start_beat = current_beat
            
            old_scene_name = self.scenes[old_scene].name if old_scene < len(self.scenes) else "Unknown"
            new_scene_name = self.scenes[self.current_scene].name
            print(f"Switched from '{old_scene_name}' to '{new_scene_name}' (scene {self.current_scene + 1}/{len(self.scenes)}) at beat {current_beat}")
            return True
        else:
            print("All scenes completed")
            return False
    
    def check_scene_transition(self, current_beat):
        """シーンの切り替えが必要かチェック"""
        scene = self.get_current_scene()
        if not scene:
            return False
        
        # カウントダウンシーンの場合は特別処理
        if isinstance(scene, CountdownScene):
            if scene.is_finished():
                # カウントダウンが完了したら次のシーンに切り替え
                return self.switch_to_next_scene()
            return False
        
        # 通常のシーンの処理
        if scene.duration_beats is None:
            print(f"Scene '{scene.name}' has no duration_beats set")
            return False
        
        # 現在のシーンの開始ビートが設定されていない場合は設定
        if scene.start_beat is None:
            scene.start_beat = current_beat
            print(f"Scene '{scene.name}' started at beat {current_beat}")
            return False
        
        # シーン内での経過ビート数を計算
        beats_in_scene = current_beat - scene.start_beat
        
        # より詳細なデバッグ情報
        print(f"Scene '{scene.name}': current_beat={current_beat}, start_beat={scene.start_beat}, beats_in_scene={beats_in_scene}, duration_beats={scene.duration_beats}")
        
        # 指定されたビート数に達したら次のシーンに切り替え
        if beats_in_scene >= scene.duration_beats:
            print(f"Scene '{scene.name}' completed after {beats_in_scene} beats, switching to next scene")
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
        """音楽を即座に再生（カウントダウンなし）"""
        pygame.mixer.music.play()
        self.music_ready = True
        self.music_start_time = pygame.time.get_ticks()
        self.start_time = self.music_start_time
        self.last_beat_count = -1
        
        # カウントダウンシーンをスキップして次のシーンに移動
        if (self.scenes and 
            isinstance(self.scenes[self.current_scene], CountdownScene)):
            # カウントダウンシーンを完了状態にする
            self.scenes[self.current_scene].is_completed = True
            # 次のシーンに切り替え
            if len(self.scenes) > 1:
                self.switch_to_next_scene()
        
        # 各シーンの開始ビートをリセット
        for scene in self.scenes:
            scene.start_beat = None
        
        print(f"Music started immediately")
    
    def get_current_beat_from_music(self):
        """音楽の再生位置からビート番号を計算"""
        if not self.music_ready or not pygame.mixer.music.get_busy():
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
                            self.music_ready = False
                        else:
                            # カウントダウン付きで再生
                            self.play_with_countdown()
                    elif event.key == pygame.K_RETURN:
                        # Enterキーで即座に音楽再生（カウントダウンなし）
                        if not pygame.mixer.music.get_busy():
                            self.play_music()
                    elif event.key == pygame.K_h:
                        # Hキーで重い処理モードの切り替え
                        self.heavy_processing_mode = not self.heavy_processing_mode
                        # 現在のシーンの重い処理モードを更新
                        scene = self.get_current_scene()
                        if scene:
                            for drawable in scene.drawables:
                                if hasattr(drawable, 'heavy_processing'):
                                    drawable.heavy_processing = self.heavy_processing_mode
                        print(f"Heavy processing mode: {'ON' if self.heavy_processing_mode else 'OFF'}")
            
            # FPS監視更新
            self.update_fps_monitor()
            
            # ビート検出
            current_beat = None
            
            # 音楽が準備完了している場合は音楽位置を使用、そうでなければ実時間
            if self.music_ready:
                current_beat = self.get_current_beat_from_music()
            
            # フォールバック
            if current_beat is None:
                current_beat = self.get_current_beat_from_time()
            
            # 新しいビートが発生した場合のみon_beatを呼び出し
            if current_beat is not None and current_beat != self.last_beat_count:
                # 音楽開始直後のビート0～4を強制的に処理するため条件を調整
                beat_should_process = current_beat > self.last_beat_count
                
                # 音楽開始直後の場合は、beat 0～4でも処理を実行
                if self.music_ready and hasattr(self, 'music_start_time') and self.music_start_time is not None:
                    time_since_music_start = pygame.time.get_ticks() - self.music_start_time
                    # 音楽開始からしばらくはpygame.mixer.music.get_pos()が正常に動作しない遅延時間がある
                    # 3秒以内で、かつ現在のビートが0～4の範囲内であれば処理を行う
                    if time_since_music_start < 3000 and current_beat <= 4:  # 最初の3秒間でbeat 0-4
                        beat_should_process = True
                
                if beat_should_process:  # 修正された条件を使用
                    # シーンの切り替えをチェック
                    self.check_scene_transition(current_beat)
                    
                    scene = self.get_current_scene()
                    if scene:
                        # CountdownSceneの場合は生のcurrent_beatを、その他は beat_in_measure を使用
                        if isinstance(scene, CountdownScene):
                            scene.on_beat(current_beat)
                        else:
                            beat_in_measure = current_beat % self.beats_per_measure
                            scene.on_beat(beat_in_measure)
                    
                    # デバッグ情報を常に表示（通常時）
                    scene_num = self.current_scene + 1
                    total_scenes = len(self.scenes)
                    scene_name = scene.name if scene else "Unknown"
                    
                    # 通常のシーンの場合はbeat_in_measureも表示
                    if scene and not isinstance(scene, CountdownScene):
                        beat_in_measure = current_beat % self.beats_per_measure
                        print(f"Beat {current_beat} (measure: {beat_in_measure}) Scene {scene_num}/{total_scenes} ({scene_name})")
                    else:
                        print(f"Beat {current_beat} Scene {scene_num}/{total_scenes} ({scene_name})")
                    
                    # FPS低下時の追加情報
                    if self.actual_fps < self.fps * 0.8:  # 目標FPSの80%以下の場合
                        print(f"  --> FPS Warning: {self.actual_fps:.1f}")
                    
                    self.last_beat_count = current_beat
            
            # 更新処理
            scene = self.get_current_scene()
            if scene:
                scene.update()
            
            # 描画処理
            self.screen.fill((0, 0, 50))  # 濃紺背景
            
            # 現在のシーンを描画
            if scene:
                scene.draw(self.screen)
                
                # シーン情報を画面に表示（カウントダウンシーン以外）
                if not isinstance(scene, CountdownScene):
                    font = pygame.font.Font(None, 24)
                    scene_num = self.current_scene + 1
                    total_scenes = len(self.scenes)
                    scene_text = font.render(f"Scene {scene_num}/{total_scenes} - {scene.name}", True, (255, 255, 255))
                    self.screen.blit(scene_text, (10, 50))
                    
                    # シーンの残り時間表示
                    if scene.duration_beats is not None and scene.start_beat is not None:
                        beats_in_scene = current_beat - scene.start_beat if current_beat else 0
                        remaining_beats = max(0, scene.duration_beats - beats_in_scene)
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
    # === リソース管理の初期化 ===
    resources = Resources()
    
    # 必須ファイルの定義
    required_images = ['star_1']  # star_1は必須
    required_musics = ['base']    # base.mp3は必須
    
    # 必須ファイルの存在チェック
    if not resources.check_required_files(required_images, required_musics):
        resources.print_missing_files_error()
        return
    
    # リソースの概要表示
    resources.print_summary()
    print("All required files found - proceeding with movie creation...")
    print()
    
    # ムービー初期化
    movie = Movie(width=800, height=600, fps=30, bpm=120)
    
    # 音楽ファイル読み込み（必ず存在する）
    movie.load_music(resources.get_music('base'))
    
    # === シーン1: ZoomBeaterのシーン (8ビート = 2小節) ===
    scene1 = Scene("Star Zoom Scene", duration_beats=8)
    
    # ZoomBeaterオブジェクト作成（画面中央に配置）
    zoom_beater = ZoomBeater(400, 300, resources.get_image('star_1'), scale=1.0, zoom_scale=1.5)
    scene1.add_drawable(zoom_beater)
    
    # 複数のZoomBeaterを追加（star_2があれば使用、なければstar_1を使用）
    positions = [(200, 150), (600, 150), (200, 450), (600, 450)]
    for i, (x, y) in enumerate(positions):
        image_path = resources.get_image('star_2') or resources.get_image('star_1')
        zoom_beater2 = ZoomBeater(x, y, image_path, scale=0.8, zoom_scale=1.3)
        scene1.add_drawable(zoom_beater2)
    
    print("Scene 1: ZoomBeater scene created")
    
    # === シーン2: FlashBeaterのシーン (8ビート = 2小節) ===
    scene2 = Scene("Colorful Flash Scene", duration_beats=8)
    
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
    
    # === シーン3: 混合シーン (16ビート = 4小節) ===
    scene3 = Scene("Mixed Effects Scene", duration_beats=16)
    
    # 中央に大きなFlashBeater
    center_flash = FlashBeater(400, 300, radius=80, color=(50, 50, 200), flash_color=(255, 255, 0))
    scene3.add_drawable(center_flash)
    
    # 周囲に小さなZoomBeater（star_1を使用）
    circle_positions = []
    for angle in range(0, 360, 45):  # 8方向
        rad = math.radians(angle)
        x = 400 + 150 * math.cos(rad)
        y = 300 + 150 * math.sin(rad)
        circle_positions.append((x, y))
    
    for x, y in circle_positions:
        small_zoom = ZoomBeater(int(x), int(y), resources.get_image('star_1'), scale=0.4, zoom_scale=0.8)
        scene3.add_drawable(small_zoom)
    
    print("Scene 3: Mixed scene created")
    
    # シーンをムービーに追加
    movie.add_scene(scene1)  # 8ビート
    movie.add_scene(scene2)  # 8ビート
    movie.add_scene(scene3)  # 16ビート
    movie.add_scene(scene2)  # 8ビート
    print(f"Total scenes: {len(movie.scenes)}")

    # カウントダウン付きで音楽再生開始
    movie.play_with_countdown()
    
    print("Movie started with countdown! Controls:")
    print("  SPACE: Start with countdown / Stop music / Cancel countdown")
    print("  ENTER: Start immediately (no countdown)")
    print("  H: Toggle heavy processing simulation")
    print("Time-based beat synchronization enabled - beats will stay in sync even with low FPS")
    print("Scenes will automatically switch based on beat count")
    
    # ムービー実行
    movie.run()

if __name__ == "__main__":
    main()
