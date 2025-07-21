import math
from resources import Resources
from movie import Movie
from scene import Scene
from zoom_beater import ZoomBeater
from flash_beater import FlashBeater
from beat_image_beater import BeatImageBeater
from move_beater import MoveBeater


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
    
    # ZoomBeaterオブジェクト作成（画面中央に配置、優先順位1で前景に）
    zoom_beater = ZoomBeater(400, 300, resources.get_image('star_1'), scale=1.0, zoom_scale=1.5, priority=1)
    scene1.add_drawable(zoom_beater)
    
    # 複数のZoomBeaterを追加（priority=0で背景に）
    positions = [(200, 150), (600, 150), (200, 450), (600, 450)]
    for i, (x, y) in enumerate(positions):
        image_path = resources.get_image('star_2') or resources.get_image('star_1')
        zoom_beater2 = ZoomBeater(x, y, image_path, scale=0.8, zoom_scale=1.3, priority=0)
        scene1.add_drawable(zoom_beater2)
    
    print("Scene 1: ZoomBeater scene created")
    
    # === シーン2: FlashBeaterのシーン (8ビート = 2小節) ===
    scene2 = Scene("Colorful Flash Scene", duration_beats=8)
    
    # FlashBeaterオブジェクト作成（priority設定で重なり順を制御）
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
        # 中央の円（400, 150）は最前面に（priority=2）、他は背景順に
        priority = 2 if (x, y) == (400, 150) else i
        flash_beater = FlashBeater(x, y, radius=40, color=color, flash_color=(255, 255, 255), priority=priority)
        scene2.add_drawable(flash_beater)
    
    print("Scene 2: FlashBeater scene created")
    
    # === シーン3: 混合シーン (16ビート = 4小節) ===
    scene3 = Scene("Mixed Effects Scene", duration_beats=16)
    
    # 中央に大きなFlashBeater（最背景 priority=0）
    center_flash = FlashBeater(400, 300, radius=80, color=(50, 50, 200), flash_color=(255, 255, 0), priority=0)
    scene3.add_drawable(center_flash)
    
    # 周囲に小さなZoomBeater（star_1を使用、前景 priority=1）
    circle_positions = []
    for angle in range(0, 360, 45):  # 8方向
        rad = math.radians(angle)
        x = 400 + 150 * math.cos(rad)
        y = 300 + 150 * math.sin(rad)
        circle_positions.append((x, y))
    
    for x, y in circle_positions:
        small_zoom = ZoomBeater(int(x), int(y), resources.get_image('star_1'), scale=0.4, zoom_scale=0.8, priority=1)
        scene3.add_drawable(small_zoom)
    
    print("Scene 3: Mixed scene created")
    
    # === シーン4: BeatImageBeaterのシーン (8ビート = 2小節) ===
    scene4 = Scene("Beat Image Scene", duration_beats=8)
    jrc_1 = resources.get_image('jrc_1')
    jrc_2 = resources.get_image('jrc_2')
    jrc_3 = resources.get_image('jrc_3')

    
    # 中央にBeatImageBeater（各拍で異なる画像を表示）
    beat_image_beater = BeatImageBeater(
        400, 300,
        jrc_2,  # デフォルト画像
        [jrc_1,jrc_1,jrc_3,jrc_1],  # 各拍の画像
        scale=1.2,
        priority=1
    )
    scene4.add_drawable(beat_image_beater)
    
    
    print("Scene 4: BeatImageBeater scene created")
    
    # === シーン5: MoveBeaterのシーン (8ビート = 2小節) ===
    scene5 = Scene("Moving Animation Scene", duration_beats=8)
    
    # 利用可能な画像を取得
    star_images = [
        resources.get_image('star_1'),
        resources.get_image('star_2')
    ]
    star_images = [img for img in star_images if img is not None]
    
    flower_images = [
        resources.get_image('flower_1'),
        resources.get_image('flower_2')
    ]
    flower_images = [img for img in flower_images if img is not None]
    
    jrc_images = [
        resources.get_image('jrc_1'),
        resources.get_image('jrc_2'),
        resources.get_image('jrc_3')
    ]
    jrc_images = [img for img in jrc_images if img is not None]
    
    # 画像がない場合はstar_1で代用
    if not star_images:
        star_images = [resources.get_image('star_1')]
    if not flower_images:
        flower_images = [resources.get_image('star_1')]
    if not jrc_images:
        jrc_images = [resources.get_image('star_1')]
    
    # 横に移動するMoveBeater（左から右へ）
    move_beater1 = MoveBeater(
        -50, 150,  # 画面左外から開始
        star_images,
        velocity_x=2, velocity_y=0,  # 右に移動
        scale=0.8,
        priority=1,
        wrap_screen=True,
        screen_width=800, screen_height=600
    )
    scene5.add_drawable(move_beater1)
    
    # 縦に移動するMoveBeater（上から下へ）
    move_beater2 = MoveBeater(
        650, -50,  # 画面上外から開始
        flower_images,
        velocity_x=0, velocity_y=1.5,  # 下に移動
        scale=0.6,
        priority=1,
        wrap_screen=True,
        screen_width=800, screen_height=600
    )
    scene5.add_drawable(move_beater2)
    
    # 斜めに移動するMoveBeater（跳ね返りモード）
    move_beater3 = MoveBeater(
        100, 100,
        jrc_images,
        velocity_x=3, velocity_y=2,  # 斜め移動
        scale=0.7,
        priority=2,
        wrap_screen=False,  # 跳ね返りモード
        screen_width=800, screen_height=600
    )
    scene5.add_drawable(move_beater3)
    
    # その場で画像切り替えのみ（速度0,0）
    move_beater4 = MoveBeater(
        400, 500,
        [resources.get_image('star_1'), resources.get_image('star_2')] if resources.get_image('star_2') else [resources.get_image('star_1')],
        velocity_x=0, velocity_y=0,  # 移動なし
        scale=1.0,
        priority=0,  # 背景
        wrap_screen=True,
        screen_width=800, screen_height=600
    )
    scene5.add_drawable(move_beater4)
    
    print("Scene 5: MoveBeater scene created")
    
    # シーンをムービーに追加
    movie.add_scene(scene4)  # 8ビート
    movie.add_scene(scene1)  # 8ビート  
    movie.add_scene(scene5)  # 8ビート (新しいMoveBeaterシーン)
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
