# FinSolve Audit System Guide

## Overview

The FinSolve chatbot now includes comprehensive audit logging to track user activities and document access. This system provides detailed insights into who is accessing what documents and when, helping with compliance and security monitoring.

## Features Added

### 1. Login Audit Logging
- **What it tracks**: Every login attempt (successful and failed)
- **Information logged**:
  - Username and user role
  - Login timestamp and date
  - IP address and user agent
  - Session ID
  - Success/failure status
- **Benefits**: Track user activity patterns, identify security issues, monitor system usage

### 2. Document Access Audit Logging
- **What it tracks**: Every document access during chat queries and document viewing
- **Information logged**:
  - Username and user role
  - Document name accessed
  - Access type (query, view, download)
  - Query text that triggered access
  - Whether access was granted or denied
  - Response accuracy score
  - Number of document chunks accessed
  - Timestamp and session information
- **Benefits**: Ensure compliance with data access policies, track document usage, identify popular content

### 3. Audit Dashboard (C-Level and HR Only)
- **Login Statistics**:
  - Daily login counts and trends
  - Unique user counts
  - Success/failure rates
  - Most active users
  - Login patterns by hour
- **Document Access Statistics**:
  - Most accessed documents
  - Access patterns by user role
  - Daily access trends
  - Access denied events
- **Real-time Metrics**:
  - Today's login count
  - Today's document accesses
  - Currently active users

## How It Works

### Automatic Logging
The audit system works automatically without affecting the chatbot's performance:

1. **Login Events**: Every login attempt is logged with full details
2. **Chat Queries**: When users ask questions, document access is logged
3. **Document Viewing**: When users view documents directly, access is logged
4. **Background Processing**: All logging happens asynchronously to maintain performance

### Database Storage
- **Separate Database**: Audit logs are stored in `audit_logs.db` (separate from main database)
- **Optimized Tables**: Indexed tables for fast querying and reporting
- **Data Retention**: Configurable retention periods for compliance requirements

### Access Control
- **User Access**: Regular users cannot see audit logs
- **Administrator Access**: Only C-Level and HR roles can view audit reports
- **API Protection**: Audit endpoints are protected with role-based authentication

## Using the Audit System

### For Administrators (C-Level and HR)

1. **Login to the chatbot** with C-Level or HR credentials
2. **Check the sidebar** for the "📊 Audit Dashboard" section
3. **View Login Stats**: Click "👥 Login Stats" to see login patterns
4. **View Document Access**: Click "📄 Doc Access" to see document usage
5. **Analyze Data**: Use the expandable sections to see detailed breakdowns

### For Regular Users
- **No changes needed**: The system works transparently
- **Privacy maintained**: Users cannot see others' audit data
- **Performance unaffected**: Logging happens in the background

## API Endpoints

### For Administrators
```
GET /api/v1/audit/login-statistics?days=30
GET /api/v1/audit/document-access-statistics?days=30
GET /api/v1/audit/dashboard
```

### Authentication Required
All audit endpoints require:
- Valid JWT token
- C-Level or HR role
- Proper authorization headers

## Testing the System

Run the test script to verify functionality:
```bash
python test_audit_system.py
```

This will:
- Create sample login and document access logs
- Test statistics retrieval
- Verify dashboard data generation
- Show example audit data

## Database Schema

### Login Audit Table
```sql
CREATE TABLE login_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    user_role TEXT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login_date DATE NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,
    success BOOLEAN DEFAULT 1
);
```

### Document Access Audit Table
```sql
CREATE TABLE document_access_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    user_role TEXT NOT NULL,
    document_name TEXT NOT NULL,
    access_type TEXT NOT NULL,
    query_text TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_date DATE NOT NULL,
    ip_address TEXT,
    session_id TEXT,
    access_granted BOOLEAN DEFAULT 1,
    response_accuracy REAL,
    chunks_accessed INTEGER DEFAULT 0
);
```

## Benefits

### Compliance
- **Audit Trail**: Complete record of who accessed what and when
- **Data Governance**: Track sensitive document access
- **Regulatory Requirements**: Meet compliance standards for data access logging

### Security
- **Access Monitoring**: Identify unusual access patterns
- **Failed Login Tracking**: Monitor potential security threats
- **Role Verification**: Ensure users only access authorized documents

### Analytics
- **Usage Patterns**: Understand how the system is being used
- **Popular Content**: Identify most accessed documents
- **User Behavior**: Track user engagement and activity levels

### Performance
- **Non-intrusive**: Logging doesn't affect chatbot performance
- **Efficient Storage**: Optimized database design for fast queries
- **Background Processing**: All audit operations happen asynchronously

## Configuration

### Retention Settings
- Default: 90 days for login logs, 180 days for document access logs
- Configurable in `audit_logger.py`
- Automatic cleanup available

### Access Control
- Modify role permissions in `auth_utils.py`
- Currently: C-Level and HR can access audit data
- Easily extensible for other roles

## Troubleshooting

### Common Issues
1. **Audit database not created**: Run `python test_audit_system.py` to initialize
2. **Permission denied**: Ensure user has C-Level or HR role
3. **No data showing**: Check if audit logging is enabled and working

### Log Files
- Check `audit_logs.db` for stored data
- Use SQLite browser to inspect tables directly
- Monitor application logs for audit system errors

## Future Enhancements

### Planned Features
- **Export functionality**: CSV/Excel export of audit data
- **Email alerts**: Notifications for suspicious activity
- **Advanced analytics**: Trend analysis and predictions
- **Integration**: Connect with external SIEM systems

### Customization Options
- **Custom retention periods**: Per-table retention settings
- **Additional fields**: Extend logging with custom data
- **Role-based views**: Different audit views for different roles
- **Automated reports**: Scheduled audit reports via email

## Support

For questions or issues with the audit system:
1. Check this documentation first
2. Run the test script to verify functionality
3. Check database permissions and connectivity
4. Review application logs for error messages

The audit system is designed to be robust and self-maintaining, providing valuable insights into system usage while maintaining user privacy and system performance.