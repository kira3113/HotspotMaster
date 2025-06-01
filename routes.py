import string
import random
import csv
import io
from flask import render_template, request, redirect, url_for, flash, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, ActivityLog
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('generator'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('generator'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/generator', methods=['GET', 'POST'])
@login_required
def generator():
    if request.method == 'POST':
        # Get form data
        base_name = request.form['base_name']
        base_ip = request.form['base_ip']
        comment = request.form['comment']
        start_number = int(request.form['start_number'])
        end_number = int(request.form['end_number'])
        password_length = int(request.form['password_length'])
        
        # Character types
        char_types = []
        if 'uppercase' in request.form:
            char_types.append('uppercase')
        if 'lowercase' in request.form:
            char_types.append('lowercase')
        if 'numbers' in request.form:
            char_types.append('numbers')
        if 'special' in request.form:
            char_types.append('special')
        
        # Validation
        if not char_types:
            flash('Please select at least one character type.', 'error')
            return render_template('generator.html')
        
        if start_number > end_number:
            flash('Start number cannot be greater than end number.', 'error')
            return render_template('generator.html')
        
        # Validate IP range (1-254 for last octet)
        if start_number < 1 or end_number > 254:
            flash('IP range must be between 1 and 254.', 'error')
            return render_template('generator.html')
        
        # Generate character set
        charset = ''
        if 'uppercase' in char_types:
            charset += string.ascii_uppercase
        if 'lowercase' in char_types:
            charset += string.ascii_lowercase
        if 'numbers' in char_types:
            charset += string.digits
        if 'special' in char_types:
            charset += '!@#$%^&*'
        
        # Generate commands (optimized for speed)
        commands = []
        generated_users = []  # Store user data for Excel export
        users_count = end_number - start_number + 1
        
        # Pre-calculate IP base parts for efficiency
        ip_parts = base_ip.split('.')
        is_partial_ip = len(ip_parts) == 3
        base_ip_int = int(ip_parts[3]) if len(ip_parts) == 4 else 0
        
        # Generate all users in one loop (optimized)
        for i in range(start_number, end_number + 1):
            # Generate random password (optimized)
            password = ''.join(random.choices(charset, k=password_length))
            
            # Calculate IP address efficiently
            if is_partial_ip:
                user_ip = f"{base_ip}.{i}"
            elif len(ip_parts) == 4:
                user_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{base_ip_int + i - start_number}"
            else:
                user_ip = base_ip
            
            username = f"{base_name}{i}"
            
            # Store user data for Excel export
            generated_users.append({
                'name': username,
                'password': password,
                'ip': user_ip,
                'comment': comment
            })
            
            # Generate command in the new format
            command = f' add comment={comment} address={user_ip} name={username} password={password}'
            commands.append(command)
        
        # Log activity
        activity = ActivityLog(
            user_id=current_user.id,
            base_name=base_name,
            base_ip=base_ip,
            comment=comment,
            start_number=start_number,
            end_number=end_number,
            password_length=password_length,
            character_types=','.join(char_types),
            users_generated=users_count
        )
        
        db.session.add(activity)
        db.session.commit()
        
        # Store generated users in session for Excel export
        session['generated_users'] = generated_users
        session['export_metadata'] = {
            'base_name': base_name,
            'comment': comment,
            'users_count': users_count,
            'generated_by': current_user.username,
            'export_date': datetime.now().isoformat()
        }
        
        # Format the commands with the header
        commands_text = '/ip hotspot user\n' + '\n'.join(commands)
        
        return render_template('generator.html', commands=commands, commands_text=commands_text)
    
    return render_template('generator.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('generator'))
    
    users = User.query.all()
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    return render_template('admin.html', users=users, recent_activities=recent_activities)

@app.route('/admin/create_user', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('generator'))
    
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    is_admin = 'is_admin' in request.form
    
    # Validation
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('admin'))
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'error')
        return redirect(url_for('admin'))
    
    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'error')
        return redirect(url_for('admin'))
    
    # Create new user
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=is_admin
    )
    
    db.session.add(user)
    db.session.commit()
    
    flash(f'User "{username}" created successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('generator'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/activity')
@login_required
def activity():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if current_user.is_admin:
        # Admin can see all activities
        activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        # Regular users can only see their own activities
        activities = ActivityLog.query.filter_by(user_id=current_user.id).order_by(
            ActivityLog.timestamp.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('activity.html', activities=activities)

@app.route('/export_activity')
@login_required
def export_activity():
    if current_user.is_admin:
        activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    else:
        activities = ActivityLog.query.filter_by(user_id=current_user.id).order_by(
            ActivityLog.timestamp.desc()
        ).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Username', 'Date/Time', 'Base Name', 'Base IP', 'Comment', 
                     'Start Number', 'End Number', 'Password Length', 'Character Types', 
                     'Users Generated'])
    
    # Write data
    for activity in activities:
        writer.writerow([
            activity.user.username,
            activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            activity.base_name,
            activity.base_ip,
            activity.comment,
            activity.start_number,
            activity.end_number,
            activity.password_length,
            activity.character_types,
            activity.users_generated
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=activity_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/export_users_excel')
@login_required
def export_users_excel():
    # Check if there are generated users in session
    if 'generated_users' not in session or not session['generated_users']:
        flash('No users to export. Please generate users first.', 'error')
        return redirect(url_for('generator'))
    
    generated_users = session['generated_users']
    metadata = session.get('export_metadata', {})
    
    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Generated Users"
    
    # Set up styling
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    center_alignment = Alignment(horizontal="center", vertical="center")
    
    # Add headers
    headers = ['Name', 'Password']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
    
    # Add user data
    for row, user in enumerate(generated_users, 2):
        ws.cell(row=row, column=1, value=user['name'])
        ws.cell(row=row, column=2, value=user['password'])
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create filename with metadata
    export_datetime = datetime.now()
    export_date = export_datetime.strftime("%d-%m-%Y")
    export_time = export_datetime.strftime("%H-%M-%S")
    base_name = metadata.get('base_name', 'users')
    comment = metadata.get('comment', 'export')
    users_count = metadata.get('users_count', len(generated_users))
    generated_by = metadata.get('generated_by', current_user.username)
    
    # Clean filename components (remove special characters)
    safe_base_name = ''.join(c for c in base_name if c.isalnum() or c in ('-', '_'))
    safe_comment = ''.join(c for c in comment if c.isalnum() or c in ('-', '_'))
    safe_generated_by = ''.join(c for c in generated_by if c.isalnum() or c in ('-', '_'))
    
    filename = f"{safe_base_name}_{safe_comment}_{users_count}users_{safe_generated_by}_{export_date}_{export_time}.xlsx"
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response
