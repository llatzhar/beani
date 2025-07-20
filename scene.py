"""
シーンクラス - Drawableオブジェクトの集合を管理
"""


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
    
    def on_beat(self, beat, measure):
        """全てのDrawableオブジェクトにビート通知"""
        for drawable in self.drawables:
            drawable.on_beat(beat, measure)
    
    def draw(self, screen):
        """全てのDrawableオブジェクトを描画"""
        for drawable in self.drawables:
            drawable.draw(screen)
