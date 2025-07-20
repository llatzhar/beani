"""
描画可能オブジェクトの基底クラス
"""

class Drawable:
    """描画可能オブジェクトの基底クラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def update(self):
        """フレームごとに呼ばれる更新処理"""
        pass
    
    def on_beat(self, beat, measure):
        """ビートのタイミングで呼ばれる処理
        
        Args:
            beat: 絶対ビート番号（0から開始）
            measure: 小節内でのビート番号（0-3の循環）
        """
        pass
    
    def draw(self, screen):
        """描画処理"""
        pass
