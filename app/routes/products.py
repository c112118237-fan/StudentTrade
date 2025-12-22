from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.services.product_service import ProductService
from app.services.notification_service import ReviewService
from app.models.category import Category
from app.extensions import db
from app.utils.decorators import login_required

bp = Blueprint('products', __name__)

DEFAULT_CATEGORY_NAMES = ['書籍', '文具', '電子產品', '生活用品', '運動', '其他']


def get_or_seed_categories():
    """取得分類列表，如為空則建立預設分類"""
    categories = Category.query.order_by(Category.sort_order, Category.id).all()
    if categories:
        return categories

    # 建立預設分類
    for idx, name in enumerate(DEFAULT_CATEGORY_NAMES):
        db.session.add(Category(name=name, sort_order=idx))
    db.session.commit()
    return Category.query.order_by(Category.sort_order, Category.id).all()

@bp.route('/')
@bp.route('/products')
def index():
    """商品列表（首頁）"""
    # 取得查詢參數
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', None, type=int)
    condition = request.args.get('condition', None)
    min_price = request.args.get('min_price', None, type=float)
    max_price = request.args.get('max_price', None, type=float)
    
    # Handle combined sort parameter (e.g., "price-asc")
    sort_param = request.args.get('sort', '')
    if sort_param and '-' in sort_param:
        sort_by, order = sort_param.split('-', 1)
    else:
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

    # 取得商品列表
    pagination = ProductService.get_products(
        page=page,
        search=search,
        category_id=category_id,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order
    )

    # 取得分類列表
    categories = Category.query.filter_by(parent_id=None).all()

    return render_template(
        'products/index.html',
        products=pagination.items,
        pagination=pagination,
        categories=categories
    )

@bp.route('/products/<int:id>')
def detail(id):
    """商品詳情"""
    # 檢查是否登入（商品詳情需要登入才能查看）
    if not current_user.is_authenticated:
        flash('請先登入以查看商品詳情', 'warning')
        return redirect(url_for('auth.login', next=request.url))

    # 取得商品（增加瀏覽次數）
    product = ProductService.get_product_by_id(id, increment_view=True)

    if not product:
        abort(404)

    # 取得相似商品（同分類，排除當前商品）
    similar_products = ProductService.get_products(
        category_id=product.category_id,
        per_page=4
    ).items
    similar_products = [p for p in similar_products if p.id != id]

    seller_stats = ReviewService.get_user_stats(product.user_id)

    return render_template(
        'products/detail.html',
        product=product,
        similar_products=similar_products,
        seller_stats=seller_stats
    )

@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def create():
    """刊登商品"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        category_id = request.form.get('category_id', type=int)
        condition = request.form.get('condition', '')
        location = request.form.get('location', '').strip()
        transaction_methods = request.form.getlist('transaction_methods')
        transaction_method = ', '.join(m for m in transaction_methods if m)

        # 取得上傳的圖片（支援多檔 input name="images"）
        images = [
            f for f in request.files.getlist('images')
            if f and f.filename
        ]
        if not images:
            # 向後相容舊欄位 image_0 ~ image_4
            for i in range(5):
                image_file = request.files.get(f'image_{i}')
                if image_file and image_file.filename:
                    images.append(image_file)

        # 驗證必填欄位
        if not all([title, category_id, condition]):
            flash('請填寫所有必填欄位', 'error')
            categories = get_or_seed_categories()
            return render_template('products/form.html', categories=categories, product=None)

        if not transaction_method:
            flash('請至少選擇一種交易方式', 'error')
            categories = get_or_seed_categories()
            return render_template('products/form.html', categories=categories, product=None)

        # 建立商品
        success, result = ProductService.create_product(
            seller_id=current_user.id,
            title=title,
            description=description,
            price=price,
            category_id=category_id,
            condition=condition,
            location=location,
            transaction_method=transaction_method,
            images=images
        )

        if success:
            flash('商品已成功刊登！', 'success')
            return redirect(url_for('products.detail', id=result.id))
        else:
            flash(result, 'error')

    # GET 請求：顯示表單
    categories = get_or_seed_categories()
    return render_template('products/form.html', categories=categories, product=None)

@bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """編輯商品"""
    product = ProductService.get_product_by_id(id)

    if not product:
        abort(404)

    # 驗證擁有權
    if product.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        category_id = request.form.get('category_id', type=int)
        condition = request.form.get('condition', '')
        location = request.form.get('location', '').strip()
        transaction_methods = request.form.getlist('transaction_methods')
        transaction_method = ', '.join(m for m in transaction_methods if m)

        # 驗證必填欄位
        if not all([title, category_id, condition]):
            flash('請填寫所有必填欄位', 'error')
            categories = Category.query.all()
            return render_template('products/form.html', categories=categories, product=product)

        if not transaction_method:
            flash('請至少選擇一種交易方式', 'error')
            categories = Category.query.all()
            return render_template('products/form.html', categories=categories, product=product)

        # 更新商品
        success, result = ProductService.update_product(
            product_id=id,
            seller_id=current_user.id,
            title=title,
            description=description,
            price=price,
            category_id=category_id,
            condition=condition,
            location=location,
            transaction_method=transaction_method
        )

        if success:
            flash('商品已更新', 'success')
            return redirect(url_for('products.detail', id=id))
        else:
            flash(result, 'error')

    # GET 請求：顯示表單
    categories = get_or_seed_categories()
    return render_template('products/form.html', categories=categories, product=product)

@bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """刪除商品（軟刪除）"""
    from app.models.product import Product
    
    product = Product.query.get_or_404(id)
    
    # 驗證權限
    if product.user_id != current_user.id:
        flash('您沒有權限刪除此商品', 'error')
        return redirect(url_for('products.my_products'))
    
    # 軟刪除
    product.status = 'deleted'
    db.session.commit()
    
    flash('商品已刪除', 'success')
    return redirect(url_for('products.my_products'))

@bp.route('/products/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    """切換商品狀態（上架/下架）"""
    from app.models.product import Product
    from app import db
    
    product = Product.query.get_or_404(id)
    
    # 驗證權限
    if product.user_id != current_user.id:
        flash('您沒有權限修改此商品', 'error')
        return redirect(url_for('products.detail', id=id))
    
    # 切換狀態
    new_status = request.form.get('status', 'inactive')
    
    if new_status not in ['active', 'inactive']:
        flash('無效的狀態', 'error')
        return redirect(url_for('products.detail', id=id))
    
    product.status = new_status
    db.session.commit()
    
    if new_status == 'inactive':
        flash('商品已下架', 'success')
    else:
        flash('商品已重新上架', 'success')
    
    return redirect(url_for('products.detail', id=id))

@bp.route('/my-products')
@login_required
def my_products():
    """我的商品管理"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')  # all, active, inactive, deleted
    
    # 構建查詢
    from app.models.product import Product
    query = Product.query.filter_by(user_id=current_user.id)
    
    # 狀態篩選
    if status_filter == 'active':
        query = query.filter_by(status='active')
    elif status_filter == 'inactive':
        query = query.filter_by(status='inactive')
    elif status_filter == 'deleted':
        query = query.filter_by(status='deleted')
    # 'all' 顯示除了deleted之外的所有商品
    elif status_filter == 'all':
        query = query.filter(Product.status.in_(['active', 'inactive']))
    
    # 按建立時間倒序
    query = query.order_by(Product.created_at.desc())
    
    # 分頁
    pagination = query.paginate(page=page, per_page=12, error_out=False)

    return render_template(
        'products/my_products.html',
        products=pagination.items,
        pagination=pagination,
        status_filter=status_filter
    )

@bp.route('/my')
@login_required
def my():
    """我的賣場（重定向到seller頁面）"""
    return redirect(url_for('products.seller', user_id=current_user.id))

@bp.route('/seller/<int:user_id>')
def seller(user_id):
    """賣家個人頁面"""
    from app.models.user import User
    
    seller = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    
    # 獲取該賣家的所有上架商品（僅顯示 active 狀態）
    pagination = ProductService.get_user_products(
        user_id=user_id,
        status='active',
        page=page
    )
    
    seller_stats = ReviewService.get_user_stats(user_id)

    return render_template(
        'products/seller.html',
        seller=seller,
        products=pagination.items,
        pagination=pagination,
        seller_stats=seller_stats
    )
