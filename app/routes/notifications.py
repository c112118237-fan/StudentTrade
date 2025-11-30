from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.services.notification_service import NotificationService
from app.utils.decorators import login_required

bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@bp.route('/')
@login_required
def index():
    """通知列表"""
    page = request.args.get('page', 1, type=int)
    unread_only = request.args.get('unread', 0, type=int)

    pagination = NotificationService.get_user_notifications(
        user_id=current_user.id,
        unread_only=bool(unread_only),
        page=page
    )

    unread_count = NotificationService.get_unread_count(current_user.id)

    return render_template(
        'notifications/index.html',
        notifications=pagination.items,
        pagination=pagination,
        unread_count=unread_count
    )

@bp.route('/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    """標記通知為已讀"""
    success, message = NotificationService.mark_as_read(id, current_user.id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': message}), 400
    else:
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('notifications.index'))

@bp.route('/read-all', methods=['POST'])
@login_required
def mark_all_read():
    """標記所有通知為已讀"""
    success, result = NotificationService.mark_all_as_read(current_user.id)

    if success:
        flash(f'已標記 {result} 則通知為已讀', 'success')
    else:
        flash(result, 'error')

    return redirect(url_for('notifications.index'))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """刪除通知"""
    success, message = NotificationService.delete_notification(id, current_user.id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('notifications.index'))
