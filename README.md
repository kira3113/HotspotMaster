# MikroTik Hotspot User Generator

A comprehensive Flask web application for generating MikroTik hotspot user commands with user authentication, activity tracking, and administrative features.

![MikroTik Hotspot User Generator](generated-icon.png)

## Features

### 🔐 User Authentication System
- **User Registration**: Secure account creation with email validation
- **User Login**: Session-based authentication with remember me functionality
- **Role-based Access**: Admin and regular user roles with different permissions
- **Secure Logout**: Complete session cleanup

### 🛠️ MikroTik Command Generator
- **Customizable Base Settings**: Configure base username, IP address, and comments
- **Flexible Numbering**: Set start and end numbers for user generation (1-254 range)
- **Password Generation**: Configurable password length (1-32 characters)
- **Character Type Selection**: Choose from uppercase, lowercase, numbers, and special characters
- **Real-time Validation**: Form validation with immediate feedback
- **Command Format**: Generates properly formatted MikroTik RouterOS commands

### 📊 Activity Tracking & Logging
- **Complete Activity History**: Track every user generation session
- **Detailed Logging**: Records timestamp, user, settings used, and number of users generated
- **User-specific Views**: Regular users see only their activity, admins see all activity
- **CSV Export**: Export activity logs for external analysis
- **Pagination**: Efficient browsing of large activity datasets

### 👨‍💼 Administrative Dashboard
- **User Management**: View all registered users and their roles
- **System Statistics**: Quick overview of total users, admins, and activity
- **Recent Activity Monitor**: Real-time view of latest user generations
- **Export Capabilities**: Download complete activity reports

### 🎨 Professional UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap 5**: Modern, clean interface with professional styling
- **Font Awesome Icons**: Intuitive iconography throughout the application
- **Real-time Feedback**: Loading states, success/error messages, and form validation
- **Copy to Clipboard**: One-click copying of generated commands

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Modern web browser

### Environment Variables
```bash
DATABASE_URL=postgresql://username:password@host:port/database_name
SESSION_SECRET=your-secure-session-secret-key
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mikrotik-hotspot-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Create `.env` file or set environment variables
   - Configure `DATABASE_URL` for PostgreSQL connection
   - Set `SESSION_SECRET` for secure sessions

4. **Initialize the database**
   ```bash
   python app.py
   ```
   The application will automatically create tables and a default admin user.

5. **Run the application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## Usage Guide

### Getting Started

1. **Access the Application**
   - Navigate to `http://localhost:5000`
   - Use demo admin credentials: `admin` / `admin123`
   - Or register a new account

2. **Generate MikroTik Commands**
   - Fill out the generator form with your requirements
   - Set base username (e.g., "user", "guest")
   - Configure base IP address (e.g., "192.168.10")
   - Choose number range (1-254)
   - Set password parameters
   - Click "Generate Users"

3. **Copy Commands**
   - Generated commands appear in the output panel
   - Use "Copy to Clipboard" button for easy copying
   - Commands are formatted for direct use in MikroTik RouterOS

### Command Output Format

The application generates commands in the following format:

```
/ip hotspot user
 add comment=Guest User address=192.168.10.1 name=user1 password=abc123
 add comment=Guest User address=192.168.10.2 name=user2 password=def456
 add comment=Guest User address=192.168.10.3 name=user3 password=ghi789
```

### Form Parameters

| Parameter | Description | Range/Format | Example |
|-----------|-------------|--------------|---------|
| Base Name | Username prefix | Text | user, guest, client |
| Base IP | IP address prefix (3 octets) | xxx.xxx.xxx | 192.168.10 |
| Comment | Common comment for all users | Text | Guest User, Temp Access |
| Start Number | First user number | 1-254 | 1 |
| End Number | Last user number | 1-254 | 50 |
| Password Length | Character count | 1-32 | 8 |
| Character Types | Password composition | Checkboxes | Uppercase, Numbers |

### Administrative Features

**Admin Dashboard Access**
- Login with admin credentials
- View user statistics and management
- Monitor system-wide activity
- Export comprehensive reports

**User Management**
- View all registered users
- See user roles and registration dates
- Track individual user activity counts

**Activity Monitoring**
- Real-time activity feed
- Detailed generation logs
- Export to CSV for analysis
- Filter by user or date ranges

## Technical Specifications

### Technology Stack
- **Backend**: Flask 3.x (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap 5, Font Awesome, Vanilla JavaScript
- **Styling**: Custom CSS with CSS variables
- **Server**: Gunicorn WSGI server

### Database Schema

**Users Table**
- ID, username, email, password_hash
- Role flags (is_admin)
- Registration timestamp

**Activity Log Table**
- User reference, timestamp
- Generation parameters (base_name, base_ip, comment)
- Range settings (start_number, end_number)
- Password configuration (length, character_types)
- Results (users_generated count)

### Security Features
- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection
- Input validation and sanitization
- SQL injection prevention via ORM
- Role-based access control

### Performance Optimizations
- Database connection pooling
- Pagination for large datasets
- Optimized queries with proper indexing
- Client-side validation for better UX
- Efficient asset loading

## API Documentation

The application is designed as a web interface and does not expose REST APIs. All functionality is accessed through the web interface.

## Customization

### Styling
- Modify `static/css/style.css` for custom themes
- Update CSS variables in `:root` for color schemes
- Bootstrap classes can be overridden for layout changes

### Functionality
- Extend `models.py` for additional data fields
- Modify `routes.py` for new features or validation rules
- Update templates for UI changes
- Enhance JavaScript in `static/js/app.js` for client-side features

## Troubleshooting

### Common Issues

**Database Connection Errors**
- Verify PostgreSQL is running
- Check DATABASE_URL environment variable
- Ensure database exists and user has permissions

**Session Issues**
- Set SESSION_SECRET environment variable
- Clear browser cookies and cache
- Restart the application

**Permission Errors**
- Check file permissions for static assets
- Verify user roles in database
- Restart application after role changes

### Support

For technical support or feature requests, please check the application logs and verify your configuration matches the requirements listed above.

## License

This project is open source and available under the MIT License.

---

**Built with Flask & Bootstrap | Designed for MikroTik RouterOS Administrators**