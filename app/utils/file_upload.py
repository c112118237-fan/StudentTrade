import os
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from app.utils.helpers import allowed_file, generate_filename

class FileUploadService:
    """檔案上傳服務"""

    @staticmethod
    def upload_product_image(file, max_size=(800, 800)):
        """上傳商品圖片

        Args:
            file: FileStorage 物件
            max_size: 圖片最大尺寸 (width, height)

        Returns:
            (success: bool, url: str or error_message: str)
        """
        if not file:
            return False, '沒有選擇檔案'

        if file.filename == '':
            return False, '沒有選擇檔案'

        # 檢查檔案類型
        if not allowed_file(file.filename):
            return False, '不支援的檔案格式（僅支援 PNG, JPG, JPEG, GIF, WEBP）'

        try:
            # 產生唯一檔名
            filename = generate_filename(file.filename)

            # 建立上傳目錄路徑
            upload_folder = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'products'
            )
            os.makedirs(upload_folder, exist_ok=True)

            # 完整檔案路徑
            filepath = os.path.join(upload_folder, filename)

            # 使用 Pillow 處理圖片
            img = Image.open(file)

            # 轉換 RGBA 為 RGB（處理 PNG 透明背景）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # 等比例縮放圖片
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 儲存圖片（JPEG 格式，品質 85）
            img.save(filepath, 'JPEG', quality=85, optimize=True)

            # 返回相對 URL
            url = f'/static/uploads/products/{filename}'
            return True, url

        except Exception as e:
            return False, f'上傳失敗：{str(e)}'

    @staticmethod
    def upload_avatar(file, max_size=(200, 200)):
        """上傳使用者頭像

        Args:
            file: FileStorage 物件
            max_size: 圖片最大尺寸 (width, height)

        Returns:
            (success: bool, url: str or error_message: str)
        """
        if not file:
            return False, '沒有選擇檔案'

        if file.filename == '':
            return False, '沒有選擇檔案'

        # 檢查檔案類型
        if not allowed_file(file.filename):
            return False, '不支援的檔案格式（僅支援 PNG, JPG, JPEG, GIF, WEBP）'

        try:
            # 產生唯一檔名
            filename = generate_filename(file.filename)

            # 建立上傳目錄路徑
            upload_folder = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'avatars'
            )
            os.makedirs(upload_folder, exist_ok=True)

            # 完整檔案路徑
            filepath = os.path.join(upload_folder, filename)

            # 使用 Pillow 處理圖片
            img = Image.open(file)

            # 轉換 RGBA 為 RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # 裁切為正方形（中心裁切）
            width, height = img.size
            min_dimension = min(width, height)
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension
            img = img.crop((left, top, right, bottom))

            # 縮放圖片
            img = img.resize(max_size, Image.Resampling.LANCZOS)

            # 儲存圖片
            img.save(filepath, 'JPEG', quality=90, optimize=True)

            # 返回相對 URL
            url = f'/static/uploads/avatars/{filename}'
            return True, url

        except Exception as e:
            return False, f'上傳失敗：{str(e)}'

    @staticmethod
    def delete_file(file_url):
        """刪除檔案

        Args:
            file_url: 檔案 URL（例如：/static/uploads/products/xxx.jpg）

        Returns:
            bool: 是否成功刪除
        """
        try:
            # 跳過預設圖片
            if 'placeholder' in file_url:
                return True

            # 從 URL 取得檔案路徑
            if file_url.startswith('/static/'):
                file_url = file_url[8:]  # 移除 '/static/'

            filepath = os.path.join(
                current_app.root_path,
                'static',
                file_url
            )

            # 刪除檔案
            if os.path.exists(filepath):
                os.remove(filepath)
                return True

            return False

        except Exception as e:
            current_app.logger.error(f'刪除檔案失敗：{str(e)}')
            return False
