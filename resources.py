import os
from typing import Dict, List, Optional

class Resources:
    """リソースファイル管理クラス"""
    
    def __init__(self, images_dir: str = "images", musics_dir: str = "musics"):
        self.images_dir = images_dir
        self.musics_dir = musics_dir
        
        # リソースの辞書
        self.images: Dict[str, Optional[str]] = {}
        self.musics: Dict[str, Optional[str]] = {}
        
        # 利用可能なリソースのリスト
        self.available_images: List[str] = []
        self.available_musics: List[str] = []
        
        # 不足しているファイルのリスト
        self.missing_files: List[str] = []
        
        # リソースをスキャン
        self._scan_resources()
    
    def _scan_resources(self):
        """リソースディレクトリをスキャンしてファイルを登録"""
        print("Scanning resource files...")
        
        # 画像ファイルをスキャン
        if os.path.exists(self.images_dir):
            for filename in os.listdir(self.images_dir):
                if filename.lower().endswith('.png'):
                    # ファイル名から拡張子を除いたキーを作成
                    key = os.path.splitext(filename)[0]
                    filepath = os.path.join(self.images_dir, filename)
                    self.images[key] = filepath
                    self.available_images.append(key)
                    print(f"Image found: {key} -> {filepath}")
        else:
            print(f"Images directory '{self.images_dir}' not found")
        
        # 音楽ファイルをスキャン
        if os.path.exists(self.musics_dir):
            for filename in os.listdir(self.musics_dir):
                if filename.lower().endswith('.mp3'):
                    # ファイル名から拡張子を除いたキーを作成
                    key = os.path.splitext(filename)[0]
                    filepath = os.path.join(self.musics_dir, filename)
                    self.musics[key] = filepath
                    self.available_musics.append(key)
                    print(f"Music found: {key} -> {filepath}")
        else:
            print(f"Musics directory '{self.musics_dir}' not found")
        
        print(f"Scan complete: {len(self.available_images)} images, {len(self.available_musics)} musics")
        print()
    
    def check_required_files(self, required_images: List[str] = None, required_musics: List[str] = None) -> bool:
        """必須ファイルの存在をチェック
        
        Args:
            required_images: 必須画像ファイルのキーのリスト
            required_musics: 必須音楽ファイルのキーのリスト
        
        Returns:
            bool: 全ての必須ファイルが存在するかどうか
        """
        self.missing_files = []
        
        # 必須画像ファイルをチェック
        if required_images:
            for key in required_images:
                if key not in self.images or not os.path.exists(self.images[key]):
                    missing_path = self.images.get(key, f"{self.images_dir}/{key}.png")
                    self.missing_files.append(missing_path)
                    print(f"Required image missing: {key} ({missing_path})")
                else:
                    print(f"Required image found: {key} -> {self.images[key]}")
        
        # 必須音楽ファイルをチェック
        if required_musics:
            for key in required_musics:
                if key not in self.musics or not os.path.exists(self.musics[key]):
                    missing_path = self.musics.get(key, f"{self.musics_dir}/{key}.mp3")
                    self.missing_files.append(missing_path)
                    print(f"Required music missing: {key} ({missing_path})")
                else:
                    print(f"Required music found: {key} -> {self.musics[key]}")
        
        return len(self.missing_files) == 0
    
    def get_image(self, key: str) -> Optional[str]:
        """画像ファイルのパスを取得
        
        Args:
            key: 画像ファイルのキー（拡張子なし）
        
        Returns:
            str: ファイルパス（存在しない場合はNone）
        """
        return self.images.get(key)
    
    def get_music(self, key: str) -> Optional[str]:
        """音楽ファイルのパスを取得
        
        Args:
            key: 音楽ファイルのキー（拡張子なし）
        
        Returns:
            str: ファイルパス（存在しない場合はNone）
        """
        return self.musics.get(key)
    
    def has_image(self, key: str) -> bool:
        """画像ファイルが存在するかチェック"""
        return key in self.images and os.path.exists(self.images[key])
    
    def has_music(self, key: str) -> bool:
        """音楽ファイルが存在するかチェック"""
        return key in self.musics and os.path.exists(self.musics[key])
    
    def print_missing_files_error(self):
        """不足ファイルのエラーメッセージを表示"""
        if self.missing_files:
            print("\n" + "="*50)
            print("MOVIE CANNOT BE CREATED - MISSING REQUIRED FILES:")
            for file in self.missing_files:
                print(f"  - {file}")
            print("="*50)
            print("Please ensure all required files are present and try again.")
    
    def get_resource_summary(self) -> Dict:
        """リソースの概要情報を取得"""
        return {
            'available_images': len(self.available_images),
            'available_musics': len(self.available_musics),
            'total_images': len(self.images),
            'total_musics': len(self.musics),
            'missing_files_count': len(self.missing_files),
            'images_list': self.available_images.copy(),
            'musics_list': self.available_musics.copy()
        }
    
    def print_summary(self):
        """リソースの概要を表示"""
        summary = self.get_resource_summary()
        print("Resource Summary:")
        print(f"  Images: {summary['available_images']} available")
        print(f"  Musics: {summary['available_musics']} available")
        if summary['images_list']:
            print(f"  Available images: {', '.join(summary['images_list'])}")
        if summary['musics_list']:
            print(f"  Available musics: {', '.join(summary['musics_list'])}")
        print()
