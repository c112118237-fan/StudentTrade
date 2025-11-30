from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.services.transaction_service import TransactionService
from app.utils.decorators import login_required

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@bp.route('/')
@login_required
def index():
    """交易列表"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', 'all')  # all, buyer, seller
    status = request.args.get('status', None)

    pagination = TransactionService.get_user_transactions(
        user_id=current_user.id,
        role=role,
        status=status,
        page=page
    )

    return render_template(
        'transactions/index.html',
        transactions=pagination.items,
        pagination=pagination
    )

@bp.route('/<int:id>')
@login_required
def detail(id):
    """交易詳情"""
    transaction = TransactionService.get_transaction_by_id(id)

    if not transaction:
        abort(404)

    # 驗證權限（只有買家或賣家可以查看）
    if transaction.buyer_id != current_user.id and transaction.seller_id != current_user.id:
        abort(403)

    return render_template('transactions/detail.html', transaction=transaction)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    """發起交易"""
    product_id = request.form.get('product_id', type=int)
    transaction_type = request.form.get('transaction_type', 'sale')
    amount = request.form.get('amount', 0, type=float)
    notes = request.form.get('notes', '').strip() or None

    # 驗證必填欄位
    if not product_id:
        flash('商品 ID 不正確', 'error')
        return redirect(url_for('products.index'))

    # 建立交易
    success, result = TransactionService.create_transaction(
        product_id=product_id,
        buyer_id=current_user.id,
        transaction_type=transaction_type,
        amount=amount,
        notes=notes
    )

    if success:
        flash('交易請求已送出！', 'success')
        return redirect(url_for('transactions.detail', id=result.id))
    else:
        flash(result, 'error')
        return redirect(url_for('products.detail', id=product_id))

@bp.route('/<int:id>/accept', methods=['POST'])
@login_required
def accept(id):
    """接受交易"""
    success, result = TransactionService.accept_transaction(id, current_user.id)

    if success:
        flash('交易已接受', 'success')
    else:
        flash(result, 'error')

    return redirect(url_for('transactions.detail', id=id))

@bp.route('/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    """拒絕交易"""
    reason = request.form.get('reason', '').strip() or None

    success, message = TransactionService.reject_transaction(
        transaction_id=id,
        seller_id=current_user.id,
        reason=reason
    )

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('transactions.detail', id=id))

@bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    """完成交易"""
    success, message = TransactionService.complete_transaction(id, current_user.id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('transactions.detail', id=id))

@bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """取消交易"""
    reason = request.form.get('reason', '').strip() or None

    success, message = TransactionService.cancel_transaction(
        transaction_id=id,
        user_id=current_user.id,
        reason=reason
    )

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('transactions.detail', id=id))
