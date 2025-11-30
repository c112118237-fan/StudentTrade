import re
from email_validator import validate_email, EmailNotValidError

def validate_email_format(email):
    """驗證 email 格式"""
    try:
        validate_email(email)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)

def validate_student_email(email):
    """驗證學生 email（必須是學校網域）"""
    is_valid, error = validate_email_format(email)
    if not is_valid:
        return False, error

    # 檢查是否為 .edu 或特定學校網域
    if not (email.endswith('.edu') or email.endswith('.edu.tw')):
        return False, '必須使用學校信箱註冊'

    return True, None

def validate_password_strength(password):
    """驗證密碼格式

    要求：
    - 至少 8 個字元
    - 必須同時包含英文字母和數字
    """
    if len(password) < 8:
        return False, '密碼長度至少需要 8 個字元'

    # 檢查是否只包含英文與數字
    if not re.match(r'^[a-zA-Z0-9]+$', password):
        return False, '密碼只能包含英文與數字'

    # 檢查是否包含至少一個英文字母
    if not re.search(r'[a-zA-Z]', password):
        return False, '密碼必須包含至少一個英文字母'

    # 檢查是否包含至少一個數字
    if not re.search(r'[0-9]', password):
        return False, '密碼必須包含至少一個數字'

    return True, None

def validate_username(username):
    """驗證使用者名稱

    要求：
    - 2-20 個字元
    - 只能包含中文、英文、數字、底線
    """
    if not username or len(username) < 2:
        return False, '使用者名稱至少需要 2 個字元'

    if len(username) > 20:
        return False, '使用者名稱不能超過 20 個字元'

    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', username):
        return False, '使用者名稱只能包含中文、英文、數字、底線'

    return True, None

def validate_student_id(student_id):
    """驗證學號格式

    要求：
    - 8-12 個字元
    - 只能包含英文和數字
    """
    if not student_id:
        return True, None  # 學號為選填

    if len(student_id) < 8 or len(student_id) > 12:
        return False, '學號長度應為 8-12 個字元'

    if not re.match(r'^[a-zA-Z0-9]+$', student_id):
        return False, '學號只能包含英文和數字'

    return True, None

def validate_phone(phone):
    """驗證手機號碼

    要求：
    - 台灣手機號碼格式：09xxxxxxxx
    """
    if not phone:
        return True, None  # 手機為選填

    if not re.match(r'^09\d{8}$', phone):
        return False, '請輸入有效的台灣手機號碼（09xxxxxxxx）'

    return True, None
