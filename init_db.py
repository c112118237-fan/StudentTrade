"""
資料庫初始化腳本

使用方法：
1. 確保 Docker 容器正在運行
2. 執行：python init_db.py
"""

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.transaction import Transaction
from app.models.message import Message
from app.models.notification import Notification
from app.models.review import Review

def init_database():
    """初始化資料庫"""
    app = create_app()

    with app.app_context():
        print('正在建立資料庫表格...')

        # 刪除所有表格（警告：這會清空所有資料！）
        db.drop_all()

        # 建立所有表格
        db.create_all()

        print('✓ 資料庫表格建立成功')

        # 建立預設分類
        print('\n正在建立預設分類...')
        categories = [
            Category(name='書籍教材', slug='books'),
            Category(name='電子產品', slug='electronics'),
            Category(name='生活用品', slug='daily-goods'),
            Category(name='服飾配件', slug='fashion'),
            Category(name='運動休閒', slug='sports'),
            Category(name='其他', slug='others')
        ]

        for category in categories:
            db.session.add(category)
            print(f'  ✓ {category.name}')

        db.session.commit()
        print('✓ 預設分類建立成功')

        print('\n資料庫初始化完成！')
        print('\n下一步：')
        print('1. 啟動應用：python run.py')
        print('2. 訪問：http://localhost:5000')
        print('3. 註冊新使用者開始使用')

if __name__ == '__main__':
    print('=' * 60)
    print('StudentTrade 資料庫初始化')
    print('=' * 60)
    print('\n警告：此操作會刪除所有現有資料！')

    confirm = input('\n確定要繼續嗎？(yes/no): ')

    if confirm.lower() in ['yes', 'y']:
        init_database()
    else:
        print('已取消操作')
