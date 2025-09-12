# CloneGallery Database Documentation

This directory contains all database-related files for the CloneGallery application, including migrations, seeders, and management tools.

## 📁 Directory Structure

```
database/
├── README.md                 # This documentation
├── manage.py                 # Unified database management script
├── migrate.py                # Migration manager
├── seed.py                   # Seeder manager
├── init.py                   # Legacy initialization script
├── schema.sql                # Complete database schema
├── migrations/               # Database migration files
│   ├── 001_initial_schema.sql
│   ├── 002_add_indexes.sql
│   └── 003_add_triggers.sql
└── seeders/                  # Database seeder files
    ├── 001_users_seeder.sql
    ├── 002_tags_seeder.sql
    ├── 003_images_seeder.sql
    ├── 004_image_tags_seeder.sql
    ├── 005_albums_seeder.sql
    └── 006_analytics_seeder.sql
```

## 🚀 Quick Start

### Using the Management Script

```bash
# Complete database setup
python database/manage.py setup

# Run migrations only
python database/manage.py migrate

# Seed with sample data
python database/manage.py seed

# Check database status
python database/manage.py status

# Reset database (clear all data)
python database/manage.py reset

# Create backup
python database/manage.py backup

# Restore from backup
python database/manage.py restore backup_file.db
```

### Using Docker Compose

```bash
# Run migrations
docker-compose run --rm db-migrate

# Seed database
docker-compose run --rm db-seed

# Reset database
docker-compose run --rm db-reset

# Check database status
docker-compose exec db python /app/database/manage.py status
```

## 🗄️ Database Schema

### Core Tables

#### Users
- **id**: Primary key (TEXT)
- **email**: Unique email address
- **name**: Display name
- **role**: Admin, Editor, or Visitor
- **avatar**: Profile image URL
- **joined_at**: Account creation date
- **uploads**: Number of images uploaded
- **views**: Total profile views

#### Images
- **id**: Primary key (TEXT)
- **title**: Image title
- **caption**: Image description
- **alt_text**: Accessibility text
- **url**: Full-size image URL
- **thumbnail**: Thumbnail image URL
- **uploader_id**: Foreign key to users
- **uploaded_at**: Upload timestamp
- **privacy**: Public or private
- **views**: View count
- **is_ai_generated**: Boolean flag
- **width/height**: Image dimensions
- **size**: File size
- **format**: Image format (JPEG, PNG, etc.)

#### Tags
- **id**: Primary key (INTEGER)
- **name**: Tag name (unique)
- **count**: Number of images with this tag
- **trending**: Boolean trending flag

#### Albums
- **id**: Primary key (TEXT)
- **title**: Album name
- **description**: Album description
- **cover_image_id**: Foreign key to images
- **created_by**: Foreign key to users
- **privacy**: Public or private
- **image_count**: Number of images in album

### Junction Tables

#### image_tags
Links images to tags (many-to-many relationship)

#### album_images
Links albums to images with position ordering

#### user_likes
Tracks user likes (one like per user per image)

### Metadata Tables

#### ai_generation_meta
Stores AI generation parameters for generated images

#### analytics
Stores application metrics and statistics

#### migrations
Tracks applied database migrations

#### seeders
Tracks applied database seeders

## 🔄 Migration System

### Creating a New Migration

1. Create a new file in `migrations/` directory
2. Name it with format: `XXX_description.sql` (where XXX is the next number)
3. Include the migration version in the migrations table

Example:
```sql
-- Migration: 004_add_new_feature.sql
-- Description: Add new feature table
-- Created: 2024-12-19

CREATE TABLE new_feature (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO migrations (version, description) VALUES ('004', 'Add new feature table');
```

### Migration Best Practices

- Always include rollback information in comments
- Test migrations on sample data
- Use transactions where possible
- Include proper indexes
- Update foreign key constraints

## 🌱 Seeder System

### Creating a New Seeder

1. Create a new file in `seeders/` directory
2. Name it with format: `XXX_table_name_seeder.sql`
3. Use `INSERT OR IGNORE` to avoid duplicates
4. Include proper foreign key references

Example:
```sql
-- Seeder: 007_new_table_seeder.sql
-- Description: Seed new table with sample data

INSERT OR IGNORE INTO new_table (id, name) VALUES
(1, 'Sample Item 1'),
(2, 'Sample Item 2');
```

### Seeder Best Practices

- Use `INSERT OR IGNORE` to prevent duplicates
- Include realistic sample data
- Maintain referential integrity
- Use consistent naming conventions

## 🔧 Management Commands

### Database Manager (`manage.py`)

The unified management script provides these commands:

#### `setup`
Complete database setup including migrations and seeding

#### `migrate`
Run all pending migrations

#### `seed [--force]`
Seed database with sample data
- `--force`: Re-run all seeders even if already applied

#### `reset`
Clear all data from the database (with confirmation)

#### `status`
Show migration and seeder status

#### `backup [--output PATH]`
Create database backup
- `--output`: Specify backup file path

#### `restore BACKUP_PATH`
Restore database from backup

### Individual Tools

#### Migration Manager (`migrate.py`)

```bash
python database/migrate.py migrate
python database/migrate.py status
python database/migrate.py rollback VERSION
```

#### Seeder Manager (`seed.py`)

```bash
python database/seed.py seed
python database/seed.py seed --force
python database/seed.py reset
python database/seed.py status
```

## 🐳 Docker Integration

### Database Service

The `db` service in docker-compose.yml:
- Runs migrations on startup
- Seeds database with sample data
- Includes health checks
- Uses persistent volume for data

### Migration Services

- `db-migrate`: Runs migrations only
- `db-seed`: Seeds database only
- `db-reset`: Resets database

### Usage

```bash
# Run specific migration
docker-compose run --rm db-migrate

# Seed database
docker-compose run --rm db-seed

# Reset database
docker-compose run --rm db-reset

# Access database shell
docker-compose exec db sqlite3 /app/data/clonegallery.db
```

## 📊 Sample Data

The seeders provide comprehensive sample data:

### Users (5 users)
- Admin accounts with full access
- Editor accounts for content management
- Visitor accounts for viewing

### Images (8 images)
- Mix of regular and AI-generated images
- Various formats and sizes
- Realistic metadata

### Tags (20 tags)
- Popular photography categories
- Trending indicators
- Proper counts

### Albums (6 albums)
- Themed collections
- Cover images
- Proper image counts

### Analytics (15 metrics)
- Application statistics
- Performance metrics
- Usage data

## 🔒 Security Considerations

### Data Protection
- All user data is properly sanitized
- SQL injection prevention through parameterized queries
- Input validation on all fields

### Access Control
- Role-based permissions
- Private vs public content
- User-specific data isolation

### Backup Strategy
- Regular automated backups
- Point-in-time recovery
- Cross-region replication (for production)

## 🚨 Troubleshooting

### Common Issues

#### Migration Fails
```bash
# Check migration status
python database/manage.py status

# Check database file permissions
ls -la clonegallery.db

# Reset and re-run
python database/manage.py reset
python database/manage.py setup
```

#### Seeder Fails
```bash
# Check seeder status
python database/manage.py status

# Force re-run seeders
python database/manage.py seed --force
```

#### Database Locked
```bash
# Check for running processes
lsof clonegallery.db

# Kill processes if needed
kill -9 PID
```

### Recovery

#### From Backup
```bash
python database/manage.py restore backup_file.db
```

#### Complete Reset
```bash
python database/manage.py reset
python database/manage.py setup
```

## 📈 Performance

### Indexes
- All foreign keys are indexed
- Frequently queried columns are indexed
- Composite indexes for complex queries

### Optimization
- Proper data types
- Normalized schema
- Efficient queries

### Monitoring
- Query performance tracking
- Index usage analysis
- Storage optimization

## 🔮 Future Enhancements

### Planned Features
- [ ] PostgreSQL support
- [ ] Database replication
- [ ] Automated backups
- [ ] Performance monitoring
- [ ] Query optimization tools
- [ ] Data migration tools
- [ ] Schema validation
- [ ] Rollback capabilities

### Migration Roadmap
- [ ] Version 2.0: PostgreSQL migration
- [ ] Version 2.1: Advanced indexing
- [ ] Version 2.2: Performance optimization
- [ ] Version 3.0: Multi-tenant support
