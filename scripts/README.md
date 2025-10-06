# TutorConnect Database Migration Scripts

This directory contains database migration scripts for the TutorConnect application. These scripts help apply schema changes and updates to your database safely and efficiently.

## 📋 Available Scripts

### 1. `auto_migrate.py` - **Recommended**
Automatically applies the rating column migration for the enhanced tutor search feature.

```bash
python scripts/auto_migrate.py
```

**Features:**
- ✅ Adds `rating` column to `tutors` table
- ✅ Sets demo ratings for existing tutors (3.0-5.0 stars)
- ✅ Automatic execution (no prompts)
- ✅ Safe error handling with rollback
- ✅ Perfect for CI/CD pipelines

### 2. `simple_migrate.py` - Interactive Version
Interactive migration script with user confirmations.

```bash
python scripts/simple_migrate.py
```

**Features:**
- ✅ User confirmation before changes
- ✅ Detailed schema information display
- ✅ Step-by-step progress reporting
- ✅ Good for manual database management

### 3. `migrate_db.py` - General Purpose Tool
Comprehensive database migration helper with multiple options.

```bash
# Check current database schema
python scripts/migrate_db.py --check

# Add rating column specifically
python scripts/migrate_db.py --add-rating

# Create all tables from models
python scripts/migrate_db.py --create-tables

# Show backup commands
python scripts/migrate_db.py --backup
```

### 4. `migrate_add_rating.py` - Specific Migration
Detailed migration script specifically for adding the rating column.

```bash
python scripts/migrate_add_rating.py
```

## 🔧 What These Scripts Do

### Rating Column Migration
The main migration adds a `rating` column to the `tutors` table:

```sql
ALTER TABLE tutors 
ADD COLUMN rating FLOAT DEFAULT 0.0 
COMMENT 'Average tutor rating (0.0 to 5.0)';
```

**Changes Applied:**
- Adds `rating` FLOAT column with default value 0.0
- Updates existing tutors with demo ratings (3.0-5.0)
- Enables rating-based search in the `/tutorsearch` feature

## 🚀 Quick Start

1. **Backup your database first!**
   ```bash
   # For MySQL/MariaDB
   mysqldump -u username -p database_name > backup.sql
   ```

2. **Run the automatic migration:**
   ```bash
   cd /path/to/tutorconnect
   python scripts/auto_migrate.py
   ```

3. **Verify the migration worked:**
   - Check that the `rating` column exists in the `tutors` table
   - Test the `/tutorsearch` route with rating filters
   - Verify existing tutors have ratings assigned

## 📋 Prerequisites

### Environment Setup
- Python 3.7+ with required packages
- MySQL/MariaDB database running
- Proper `.env` file with database credentials:

```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_INSTANCE=your_database_name
```

### Required Python Packages
```bash
pip install python-dotenv mysql-connector-python
```

## 🛡️ Safety Features

All migration scripts include:

- ✅ **Column existence checks** - Won't duplicate columns
- ✅ **Database connection validation** 
- ✅ **Transaction safety** (where applicable)
- ✅ **Error handling with clear messages**
- ✅ **Rollback capability on failures**

## 🔍 Troubleshooting

### Common Issues

**1. Database Connection Error**
```
❌ Database connection error: Access denied for user
```
**Solution:** Check your `.env` file credentials and database server status.

**2. Column Already Exists**
```
✅ Rating column already exists in tutors table.
```
**Solution:** This is normal! The migration has already been applied.

**3. Transaction Error**
```
❌ Database connection error: Transaction already in progress
```
**Solution:** Use `auto_migrate.py` which handles transactions properly.

### Verification Steps

After running migration, verify it worked:

```sql
-- Check column exists
DESCRIBE tutors;

-- Check sample ratings
SELECT fullname, rating FROM tutors LIMIT 5;

-- Test rating-based queries
SELECT COUNT(*) FROM tutors WHERE rating >= 4.0;
```

## 🎯 Migration History

| Date | Script | Description | Status |
|------|--------|-------------|---------|
| 2024-09-28 | `auto_migrate.py` | Add rating column for tutor search | ✅ Complete |

## 📝 Notes

- **Demo Ratings**: Scripts assign random ratings (3.0-5.0) to existing tutors for demonstration purposes
- **Production**: In production, implement a proper rating system based on student reviews
- **Backup**: Always backup your database before running migrations
- **Testing**: Test migrations on a development database first

## 🔗 Related Features

These migrations support:
- Enhanced tutor search at `/tutorsearch`
- Rating-based filtering (1-5 stars)
- Improved tutor discovery experience
- Future rating and review system implementation

## 💡 Best Practices

1. **Always backup** before migrations
2. **Test on development** environment first
3. **Run during low-traffic** periods
4. **Monitor application** after migration
5. **Keep migration scripts** for deployment automation

---

For questions or issues with migrations, check the application logs or contact the development team.