# Database Configuration

## Development Setup (SQLite)

For local development, the project is configured to use SQLite by default. No additional setup is required.

## Production Setup (MySQL)

### Prerequisites

1. Install MySQL 8.0+ on your system
2. Create a database for the project

### MySQL Database Setup

1. **Install MySQL** (if not already installed):
   - Windows: Download from https://dev.mysql.com/downloads/installer/
   - macOS: `brew install mysql`
   - Linux: `sudo apt-get install mysql-server`

2. **Start MySQL service**:
   ```bash
   # Windows
   net start MySQL80
   
   # macOS
   brew services start mysql
   
   # Linux
   sudo systemctl start mysql
   ```

3. **Create database and user**:
   ```sql
   # Login to MySQL
   mysql -u root -p
   
   # Create database
   CREATE DATABASE veetssuites_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   # Create user (optional, for better security)
   CREATE USER 'veetssuites_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   
   # Grant privileges
   GRANT ALL PRIVILEGES ON veetssuites_db.* TO 'veetssuites_user'@'localhost';
   
   # Flush privileges
   FLUSH PRIVILEGES;
   
   # Exit
   EXIT;
   ```

4. **Update .env file** with MySQL credentials:
   ```env
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=veetssuites_db
   DB_USER=veetssuites_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Switching Between SQLite and MySQL

The database configuration is controlled by environment variables in the `.env` file:

- **For SQLite** (development):
  ```env
  DB_ENGINE=django.db.backends.sqlite3
  DB_NAME=db.sqlite3
  ```

- **For MySQL** (production):
  ```env
  DB_ENGINE=django.db.backends.mysql
  DB_NAME=veetssuites_db
  DB_USER=your_user
  DB_PASSWORD=your_password
  DB_HOST=localhost
  DB_PORT=3306
  ```

### Troubleshooting

**Error: "No module named 'MySQLdb'"**
- Solution: Ensure `mysqlclient` is installed: `pip install mysqlclient`

**Error: "Access denied for user"**
- Solution: Check your MySQL credentials in the `.env` file
- Verify the user has proper permissions on the database

**Error: "Can't connect to MySQL server"**
- Solution: Ensure MySQL service is running
- Check if the host and port are correct in `.env`

### Database Migrations

After any model changes, run:
```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations
```

### Database Backup (Production)

```bash
# Backup
mysqldump -u veetssuites_user -p veetssuites_db > backup_$(date +%Y%m%d).sql

# Restore
mysql -u veetssuites_user -p veetssuites_db < backup_20240101.sql
```
