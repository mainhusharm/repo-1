# Trading Journal - Production Deployment Guide

## 🚀 Quick Start

### Local Testing
```bash
# Run the complete deployment script
python3 production_deployment_complete.py

# Start the application
python3 run_production.py
```

### Server Deployment

#### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx supervisor -y

# Install Node.js (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. Deploy Application
```bash
# Clone your repository
git clone <your-repo-url> /var/www/trading-journal
cd /var/www/trading-journal

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Run deployment script
python3 production_deployment_complete.py

# Set proper permissions
sudo chown -R www-data:www-data /var/www/trading-journal
sudo chmod -R 755 /var/www/trading-journal
```

#### 3. Configure Nginx
```bash
# Copy nginx configuration
sudo cp nginx-trading-journal.conf /etc/nginx/sites-available/trading-journal

# Update paths in the configuration file
sudo nano /etc/nginx/sites-available/trading-journal
# Replace /path/to/your/app with /var/www/trading-journal
# Replace your-domain.com with your actual domain

# Enable site
sudo ln -s /etc/nginx/sites-available/trading-journal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Configure Systemd Service
```bash
# Copy service file
sudo cp trading-journal.service /etc/systemd/system/

# Update paths in service file
sudo nano /etc/systemd/system/trading-journal.service
# Replace /path/to/your/app with /var/www/trading-journal

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable trading-journal
sudo systemctl start trading-journal
sudo systemctl status trading-journal
```

## 🔧 Configuration

### Environment Variables (.env.production)
```bash
# Security (CHANGE THESE!)
SECRET_KEY=your_super_secret_production_key_change_this
JWT_SECRET_KEY=your_jwt_secret_production_key_change_this

# Database
DATABASE_URL=sqlite:///instance/production.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/trading_journal

# CORS (Update with your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=pbkdf2:sha256:260000$your_hash_here
```

### SSL/HTTPS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🐛 Troubleshooting

### Issue 1: Dashboard Flickering
**Fixed in this deployment:**
- Optimized React component re-renders
- Reduced API call frequency
- Added proper caching mechanisms

### Issue 2: Error 405 on Account Creation
**Fixed in this deployment:**
- Added CORS preflight handling for all routes
- Fixed HTTP method handling in Flask
- Added proper OPTIONS request support

### Issue 3: Admin MPIN Redirect
**Fixed in this deployment:**
- Improved token validation logic
- Added fallback authentication for production
- Fixed session persistence issues

### Common Issues

#### Application won't start
```bash
# Check logs
sudo journalctl -u trading-journal -f

# Check if port is in use
sudo netstat -tlnp | grep :5000

# Restart service
sudo systemctl restart trading-journal
```

#### Database errors
```bash
# Recreate database
cd /var/www/trading-journal
source venv/bin/activate
python3 create_db.py
```

#### Permission errors
```bash
# Fix permissions
sudo chown -R www-data:www-data /var/www/trading-journal
sudo chmod -R 755 /var/www/trading-journal
```

## 📊 Monitoring

### Check Application Status
```bash
# Service status
sudo systemctl status trading-journal

# Application logs
sudo journalctl -u trading-journal -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Performance Monitoring
```bash
# Install htop for system monitoring
sudo apt install htop -y

# Monitor processes
htop

# Check disk usage
df -h

# Check memory usage
free -h
```

## 🔐 Security Checklist

- [ ] Changed default SECRET_KEY and JWT_SECRET_KEY
- [ ] Updated CORS_ORIGINS to your actual domain
- [ ] Enabled HTTPS with SSL certificate
- [ ] Set up firewall (ufw)
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Admin MPIN changed from default (optional)

## 🔄 Updates and Maintenance

### Updating the Application
```bash
cd /var/www/trading-journal
git pull origin main
source venv/bin/activate
python3 production_deployment_complete.py
sudo systemctl restart trading-journal
```

### Database Backup
```bash
# For SQLite
cp instance/production.db instance/backup_$(date +%Y%m%d_%H%M%S).db

# For PostgreSQL
pg_dump trading_journal > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 📞 Support

- **Admin MPIN**: 180623
- **Default Admin Username**: admin
- **Application Port**: 5000
- **Database**: SQLite (default) or PostgreSQL

For issues, check the troubleshooting section above or review the application logs.
