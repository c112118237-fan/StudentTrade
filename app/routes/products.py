from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.services.product_service import ProductService
from app.models.category import Category
from app.utils.decorators import login_required

bp = Blueprint('products', __name__)

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

    return render_template(
        'products/detail.html',
        product=product,
        similar_products=similar_products
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
        transaction_method = request.form.get('transaction_method', '').strip()

        # 取得上傳的圖片
        images = []
        for i in range(5):
            image_file = request.files.get(f'image_{i}')
            if image_file and image_file.filename:
                images.append(image_file)

        # 驗證必填欄位
        if not all([title, category_id, condition]):
            flash('請填寫所有必填欄位', 'error')
            categories = Category.query.all()
            return render_template('products/form.html', categories=categories)

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
    categories = Category.query.all()
    return render_template('products/form.html', categories=categories, product=None)

@bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """編輯商品"""
    product = ProductService.get_product_by_id(id)

    if not product:
        abort(404)

    # 驗證擁有權
    if product.seller_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        category_id = request.form.get('category_id', type=int)
        condition = request.form.get('condition', '')
        location = request.form.get('location', '').strip()
        transaction_method = request.form.get('transaction_method', '').strip()

        # 驗證必填欄位
        if not all([title, category_id, condition]):
            flash('請填寫所有必填欄位', 'error')
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
    categories = Category.query.all()
    return render_template('products/form.html', categories=categories, product=product)

@bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """刪除商品"""
    success, message = ProductService.delete_product(id, current_user.id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('products.my_products'))

@bp.route('/my-products')
@login_required
def my_products():
    """我的商品"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)

    pagination = ProductService.get_user_products(
        user_id=current_user.id,
        status=status,
        page=page
    )

    return render_template(
        'products/my_products.html',
        products=pagination.items,
        pagination=pagination
    )
