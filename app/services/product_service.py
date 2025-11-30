from app.extensions import db
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.category import Category
from app.utils.file_upload import FileUploadService
from sqlalchemy import or_, and_
from datetime import datetime

class ProductService:
    """商品服務類別"""

    @staticmethod
    def get_products(page=1, per_page=12, search=None, category_id=None,
                    condition=None, min_price=None, max_price=None,
                    sort_by='created_at', order='desc', status='active'):
        """取得商品列表（分頁）

        Args:
            page: 頁數
            per_page: 每頁數量
            search: 搜尋關鍵字
            category_id: 分類 ID
            condition: 商品狀況
            min_price: 最低價格
            max_price: 最高價格
            sort_by: 排序欄位（created_at, price, view_count）
            order: 排序方向（asc, desc）
            status: 商品狀態

        Returns:
            Pagination 物件
        """
        query = Product.query

        # 篩選狀態
        if status:
            query = query.filter_by(status=status)

        # 搜尋關鍵字
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    Product.title.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )

        # 分類篩選
        if category_id:
            query = query.filter_by(category_id=category_id)

        # 狀況篩選
        if condition:
            query = query.filter_by(condition=condition)

        # 價格篩選
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        # 排序
        order_column = getattr(Product, sort_by, Product.created_at)
        if order == 'desc':
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # 分頁
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_product_by_id(product_id, increment_view=False):
        """取得單一商品

        Args:
            product_id: 商品 ID
            increment_view: 是否增加瀏覽次數

        Returns:
            Product 或 None
        """
        product = Product.query.get(product_id)

        if product and increment_view:
            product.increment_view_count()

        return product

    @staticmethod
    def create_product(seller_id, title, description, price, category_id,
                      condition, location, transaction_method, images=None):
        """建立商品

        Args:
            seller_id: 賣家 ID
            title: 商品標題
            description: 商品描述
            price: 價格
            category_id: 分類 ID
            condition: 商品狀況
            location: 交易地點
            transaction_method: 交易方式
            images: 圖片檔案列表（最多 5 張）

        Returns:
            (success: bool, product: Product or error_message: str)
        """
        try:
            # 驗證分類是否存在
            category = Category.query.get(category_id)
            if not category:
                return False, '分類不存在'

            # 驗證價格
            if price < 0:
                return False, '價格不能為負數'

            # 建立商品
            product = Product(
                user_id=seller_id,
                title=title.strip(),
                description=description.strip() if description else '',
                price=price,
                category_id=category_id,
                condition=condition,
                location=location.strip() if location else None,
                transaction_method=transaction_method.strip() if transaction_method else None,
                status='active'
            )

            db.session.add(product)
            db.session.flush()  # 取得 product.id

            # 上傳圖片
            if images:
                for idx, image_file in enumerate(images[:5]):  # 最多 5 張
                    if image_file and image_file.filename:
                        success, result = FileUploadService.upload_product_image(image_file)
                        if success:
                            product_image = ProductImage(
                                product_id=product.id,
                                image_url=result,
                                is_primary=(idx == 0),
                                sort_order=idx
                            )
                            db.session.add(product_image)
                        else:
                            db.session.rollback()
                            return False, result

            db.session.commit()
            return True, product

        except Exception as e:
            db.session.rollback()
            return False, f'建立商品失敗：{str(e)}'

    @staticmethod
    def update_product(product_id, seller_id, title=None, description=None,
                      price=None, category_id=None, condition=None,
                      location=None, transaction_method=None):
        """更新商品

        Args:
            product_id: 商品 ID
            seller_id: 賣家 ID（驗證擁有權）
            其他參數同 create_product

        Returns:
            (success: bool, product: Product or error_message: str)
        """
        try:
            product = Product.query.get(product_id)

            if not product:
                return False, '商品不存在'

            # 驗證擁有權
            if product.user_id != seller_id:
                return False, '您沒有權限編輯此商品'

            # 檢查商品狀態（已售出不可編輯）
            if product.status == 'sold':
                return False, '已售出的商品無法編輯'

            # 更新欄位
            if title is not None:
                product.title = title.strip()
            if description is not None:
                product.description = description.strip()
            if price is not None:
                if price < 0:
                    return False, '價格不能為負數'
                product.price = price
            if category_id is not None:
                category = Category.query.get(category_id)
                if not category:
                    return False, '分類不存在'
                product.category_id = category_id
            if condition is not None:
                product.condition = condition
            if location is not None:
                product.location = location.strip()
            if transaction_method is not None:
                product.transaction_method = transaction_method.strip()

            db.session.commit()
            return True, product

        except Exception as e:
            db.session.rollback()
            return False, f'更新商品失敗：{str(e)}'

    @staticmethod
    def delete_product(product_id, seller_id):
        """刪除商品（軟刪除，改為 inactive 狀態）

        Args:
            product_id: 商品 ID
            seller_id: 賣家 ID（驗證擁有權）

        Returns:
            (success: bool, message: str)
        """
        try:
            product = Product.query.get(product_id)

            if not product:
                return False, '商品不存在'

            # 驗證擁有權
            if product.user_id != seller_id:
                return False, '您沒有權限刪除此商品'

            # 檢查是否有進行中的交易
            if product.status == 'pending':
                return False, '此商品有進行中的交易，無法刪除'

            # 軟刪除（改為 inactive）
            product.status = 'inactive'

            # 刪除圖片檔案
            for image in product.images:
                FileUploadService.delete_file(image.image_url)

            db.session.commit()
            return True, '商品已下架'

        except Exception as e:
            db.session.rollback()
            return False, f'刪除商品失敗：{str(e)}'

    @staticmethod
    def add_product_image(product_id, seller_id, image_file):
        """新增商品圖片

        Args:
            product_id: 商品 ID
            seller_id: 賣家 ID（驗證擁有權）
            image_file: 圖片檔案

        Returns:
            (success: bool, product_image: ProductImage or error_message: str)
        """
        try:
            product = Product.query.get(product_id)

            if not product:
                return False, '商品不存在'

            # 驗證擁有權
            if product.user_id != seller_id:
                return False, '您沒有權限編輯此商品'

            # 檢查圖片數量（最多 5 張）
            if product.images.count() >= 5:
                return False, '商品圖片最多 5 張'

            # 上傳圖片
            success, result = FileUploadService.upload_product_image(image_file)
            if not success:
                return False, result

            # 建立 ProductImage
            is_first_image = product.images.count() == 0
            sort_order = product.images.count()

            product_image = ProductImage(
                product_id=product_id,
                image_url=result,
                is_primary=is_first_image,
                sort_order=sort_order
            )

            db.session.add(product_image)
            db.session.commit()

            return True, product_image

        except Exception as e:
            db.session.rollback()
            return False, f'新增圖片失敗：{str(e)}'

    @staticmethod
    def delete_product_image(image_id, seller_id):
        """刪除商品圖片

        Args:
            image_id: 圖片 ID
            seller_id: 賣家 ID（驗證擁有權）

        Returns:
            (success: bool, message: str)
        """
        try:
            product_image = ProductImage.query.get(image_id)

            if not product_image:
                return False, '圖片不存在'

            # 驗證擁有權
            if product_image.product.user_id != seller_id:
                return False, '您沒有權限刪除此圖片'

            # 刪除檔案
            FileUploadService.delete_file(product_image.image_url)

            # 刪除資料庫記錄
            db.session.delete(product_image)

            # 如果刪除的是主圖，設定下一張為主圖
            if product_image.is_primary:
                next_image = ProductImage.query.filter_by(
                    product_id=product_image.product_id
                ).order_by(ProductImage.sort_order).first()

                if next_image:
                    next_image.is_primary = True

            db.session.commit()
            return True, '圖片已刪除'

        except Exception as e:
            db.session.rollback()
            return False, f'刪除圖片失敗：{str(e)}'

    @staticmethod
    def get_user_products(user_id, status=None, page=1, per_page=12):
        """取得使用者的商品列表

        Args:
            user_id: 使用者 ID
            status: 商品狀態（None 表示全部）
            page: 頁數
            per_page: 每頁數量

        Returns:
            Pagination 物件
        """
        query = Product.query.filter_by(seller_id=user_id)

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(Product.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)
