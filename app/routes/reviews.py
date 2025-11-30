from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.services.notification_service import ReviewService
from app.services.transaction_service import TransactionService
from app.models.user import User
from app.utils.decorators import login_required

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@bp.route('/new/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def create(transaction_id):
    """提交評價"""
    # 取得交易
    transaction = TransactionService.get_transaction_by_id(transaction_id)

    if not transaction:
        abort(404)

    # 檢查是否可以評價
    can_review, message = ReviewService.can_review(transaction_id, current_user.id)

    if not can_review:
        flash(message, 'error')
        return redirect(url_for('transactions.detail', id=transaction_id))

    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip() or None

        # 驗證評分
        if not rating or not (1 <= rating <= 5):
            flash('請選擇評分（1-5 星）', 'error')
            return render_template('reviews/form.html', transaction=transaction)

        # 建立評價
        success, result = ReviewService.create_review(
            transaction_id=transaction_id,
            reviewer_id=current_user.id,
            rating=rating,
            comment=comment
        )

        if success:
            flash('評價已提交！', 'success')
            return redirect(url_for('transactions.detail', id=transaction_id))
        else:
            flash(result, 'error')

    return render_template('reviews/form.html', transaction=transaction)

@bp.route('/users/<int:user_id>')
def user_reviews(user_id):
    """查看使用者評價"""
    user = User.query.get_or_404(user_id)

    # 取得評價列表
    page = request.args.get('page', 1, type=int)
    pagination = ReviewService.get_user_reviews(user_id, page=page)

    # 取得評價統計
    stats = ReviewService.get_user_stats(user_id)

    return render_template(
        'reviews/list.html',
        user=user,
        reviews=pagination.items,
        pagination=pagination,
        stats=stats
    )
