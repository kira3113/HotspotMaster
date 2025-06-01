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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

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
        
        # Generate commands
        commands = []
        generated_users = []  # Store user data for Excel export
        users_count = end_number - start_number + 1
        
        for i in range(start_number, end_number + 1):
            # Generate random password
            password = ''.join(random.choice(charset) for _ in range(password_length))
            
            # Parse IP address to increment last octet
            ip_parts = base_ip.split('.')
            if len(ip_parts) == 3:
                # Base IP is like "192.168.10", add the incrementing number
                user_ip = f"{base_ip}.{i}"
            elif len(ip_parts) == 4:
                # Base IP is like "192.168.10.100", increment the last octet
                ip_parts[3] = str(int(ip_parts[3]) + i - start_number)
                user_ip = '.'.join(ip_parts)
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
