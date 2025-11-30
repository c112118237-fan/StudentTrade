from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import current_user
from app.services.message_service import MessageService
from app.utils.decorators import login_required

bp = Blueprint('messages', __name__, url_prefix='/messages')

@bp.route('/')
@login_required
def index():
    """訊息列表（對話列表）"""
    conversations = MessageService.get_conversations_list(current_user.id)
    unread_count = MessageService.get_unread_count(current_user.id)

    return render_template(
        'messages/index.html',
        conversations=conversations,
        unread_count=unread_count
    )

@bp.route('/<int:user_id>')
@login_required
def chat(user_id):
    """對話詳情"""
    from app.models.user import User

    # 取得對話對象
    other_user = User.query.get_or_404(user_id)

    # 不能與自己對話
    if user_id == current_user.id:
        flash('無法與自己對話', 'error')
        return redirect(url_for('messages.index'))

    # 取得對話記錄
    page = request.args.get('page', 1, type=int)
    pagination = MessageService.get_conversation(
        user_id=current_user.id,
        other_user_id=user_id,
        page=page
    )

    # 標記所有訊息為已讀
    MessageService.mark_conversation_as_read(current_user.id, user_id)

    # 取得對話列表（用於側邊欄）
    conversations = MessageService.get_conversations_list(current_user.id)

    return render_template(
        'messages/chat.html',
        other_user=other_user,
        messages=pagination.items,
        pagination=pagination,
        conversations=conversations
    )

@bp.route('/send', methods=['POST'])
@login_required
def send():
    """發送訊息"""
    receiver_id = request.form.get('receiver_id', type=int)
    content = request.form.get('content', '').strip()
    product_id = request.form.get('product_id', None, type=int)

    # 驗證必填欄位
    if not receiver_id or not content:
        flash('請填寫收件者和訊息內容', 'error')
        return redirect(url_for('messages.index'))

    # 發送訊息
    success, result = MessageService.send_message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
        product_id=product_id
    )

    if success:
        # 判斷是否為 AJAX 請求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': {
                    'id': result.id,
                    'content': result.content,
                    'created_at': result.created_at.isoformat()
                }
            })
        else:
            flash('訊息已發送', 'success')
            return redirect(url_for('messages.chat', user_id=receiver_id))
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': result
            }), 400
        else:
            flash(result, 'error')
            return redirect(url_for('messages.index'))

@bp.route('/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    """標記訊息為已讀"""
    success, message = MessageService.mark_as_read(id, current_user.id)

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
        return redirect(url_for('messages.index'))
