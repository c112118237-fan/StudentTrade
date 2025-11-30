from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.services.auth_service import AuthService
from app.utils.decorators import login_required, anonymous_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """註冊"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        username = request.form.get('username', '').strip()
        student_id = request.form.get('student_id', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        department = request.form.get('department', '').strip() or None

        # 驗證必填欄位
        if not all([email, password, username]):
            flash('請填寫所有必填欄位', 'error')
            return render_template('auth/register.html')

        # 驗證密碼確認
        if password != confirm_password:
            flash('兩次輸入的密碼不一致', 'error')
            return render_template('auth/register.html')

        # 呼叫註冊服務
        success, result = AuthService.register_user(
            email=email,
            password=password,
            username=username,
            student_id=student_id,
            phone=phone,
            department=department
        )

        if success:
            flash('註冊成功！請重新登入', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result, 'error')

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """登入"""
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # 驗證必填欄位
        if not all([identifier, password]):
            flash('請填寫使用者名稱或信箱，以及密碼', 'error')
            return render_template('auth/login.html')

        # 呼叫登入服務
        success, result = AuthService.login_user(identifier, password)

        if success:
            login_user(result, remember=bool(remember))
            flash(f'歡迎回來，{result.username}！', 'success')

            # 取得重導向 URL
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('products.index'))
        else:
            flash(result, 'error')

    return render_template('auth/login.html')

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """登出"""
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('products.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """個人資料"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            # 更新個人資料
            username = request.form.get('username', '').strip()
            student_id = request.form.get('student_id', '').strip() or None
            phone = request.form.get('phone', '').strip() or None
            department = request.form.get('department', '').strip() or None
            bio = request.form.get('bio', '').strip() or None

            success, result = AuthService.update_profile(
                user=current_user,
                username=username,
                student_id=student_id,
                phone=phone,
                department=department,
                bio=bio
            )

            if success:
                flash('個人資料已更新', 'success')
            else:
                flash(result, 'error')

        elif action == 'change_password':
            # 變更密碼
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not all([old_password, new_password, confirm_password]):
                flash('請填寫所有密碼欄位', 'error')
            elif new_password != confirm_password:
                flash('兩次輸入的新密碼不一致', 'error')
            else:
                success, message = AuthService.change_password(
                    user=current_user,
                    old_password=old_password,
                    new_password=new_password
                )

                if success:
                    flash(message, 'success')
                else:
                    flash(message, 'error')

        return redirect(url_for('auth.profile'))

    # GET 請求：取得使用者統計資料
    stats = AuthService.get_user_stats(current_user)

    return render_template('auth/profile.html', stats=stats)
