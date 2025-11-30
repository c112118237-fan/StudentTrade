from datetime import datetime
from flask import url_for
from werkzeug.utils import secure_filename
import os

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg', 'gif', 'webp'}):
    """檢查檔案類型是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_filename(original_filename):
    """產生唯一檔名（使用時間戳記）"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
    secure_name = secure_filename(original_filename)
    name, ext = os.path.splitext(secure_name)
    return f"{timestamp}_{name}{ext}"

def format_price(price):
    """格式化價格（加上千分位逗號）"""
    try:
        return f"NT$ {int(price):,}"
    except (ValueError, TypeError):
        return "NT$ 0"

def get_product_condition_label(condition):
    """取得商品狀況標籤"""
    conditions = {
        'new': '全新',
        'like_new': '近全新',
        'good': '良好',
        'fair': '普通',
        'poor': '需修理'
    }
    return conditions.get(condition, condition)

def get_product_status_label(status):
    """取得商品狀態標籤"""
    statuses = {
        'active': '販售中',
        'pending': '交易中',
        'sold': '已售出',
        'inactive': '已下架'
    }
    return statuses.get(status, status)

def get_transaction_status_label(status):
    """取得交易狀態標籤"""
    statuses = {
        'pending': '待確認',
        'accepted': '已接受',
        'rejected': '已拒絕',
        'in_progress': '進行中',
        'completed': '已完成',
        'cancelled': '已取消'
    }
    return statuses.get(status, status)

def get_transaction_type_label(transaction_type):
    """取得交易類型標籤"""
    types = {
        'sale': '購買',
        'exchange': '交換',
        'free': '免費索取'
    }
    return types.get(transaction_type, transaction_type)

def get_pagination_info(pagination):
    """取得分頁資訊"""
    return {
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'prev_num': pagination.prev_num,
        'next_num': pagination.next_num
    }

def truncate_text(text, length=100):
    """截斷文字並加上省略符號"""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length] + '...'

def get_flash_category_class(category):
    """取得 Flash 訊息的 CSS class"""
    mapping = {
        'success': 'alert-success',
        'error': 'alert-error',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }
    return mapping.get(category, 'alert-info')
