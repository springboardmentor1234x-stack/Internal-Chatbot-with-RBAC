#!/usr/bin/env python3
"""
Test script for the audit logging system
Tests both login and document access logging functionality
"""
import sys
import os
import time
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.audit_logger import (
        log_login_attempt, log_document_access, 
        get_login_statistics, get_document_access_statistics,
        get_audit_dashboard_data
    )
    print("✅ Successfully imported audit logger")
except ImportError as e:
    print(f"❌ Failed to import audit logger: {e}")
    sys.exit(1)

def test_login_logging():
    """Test login audit logging"""
    print("\n🔐 Testing Login Audit Logging...")
    
    # Test successful logins
    test_users = [
        ("admin", "C-Level"),
        ("finance_user", "Finance"),
        ("marketing_user", "Marketing"),
        ("employee", "Employee"),
        ("intern_user", "Intern")
    ]
    
    for username, role in test_users:
        success = log_login_attempt(
            username=username,
            user_role=role,
            success=True,
            ip_address="127.0.0.1",
            user_agent="Test Browser",
            session_id=f"test_session_{username}_{int(time.time())}"
        )
        
        if success:
            print(f"  ✅ Logged successful login for {username} ({role})")
        else:
            print(f"  ❌ Failed to log login for {username}")
    
    # Test a failed login
    failed_success = log_login_attempt(
        username="unknown_user",
        user_role="unknown",
        success=False,
        ip_address="192.168.1.100",
        user_agent="Test Browser"
    )
    
    if failed_success:
        print("  ✅ Logged failed login attempt")
    else:
        print("  ❌ Failed to log failed login attempt")

def test_document_access_logging():
    """Test document access audit logging"""
    print("\n📄 Testing Document Access Audit Logging...")
    
    # Test document access scenarios
    test_accesses = [
        {
            "username": "admin",
            "user_role": "C-Level",
            "document_name": "quarterly_financial_report.md",
            "access_type": "query",
            "query_text": "What was our Q4 revenue?",
            "access_granted": True,
            "response_accuracy": 92.5,
            "chunks_accessed": 3
        },
        {
            "username": "finance_user",
            "user_role": "Finance",
            "document_name": "quarterly_financial_report.md",
            "access_type": "view",
            "access_granted": True,
            "chunks_accessed": 1
        },
        {
            "username": "employee",
            "user_role": "Employee",
            "document_name": "quarterly_financial_report.md",
            "access_type": "query",
            "query_text": "Show me financial data",
            "access_granted": False,
            "chunks_accessed": 0
        },
        {
            "username": "marketing_user",
            "user_role": "Marketing",
            "document_name": "market_report_q4_2024.md",
            "access_type": "query",
            "query_text": "What are our marketing metrics?",
            "access_granted": True,
            "response_accuracy": 89.2,
            "chunks_accessed": 2
        }
    ]
    
    for access in test_accesses:
        success = log_document_access(
            username=access["username"],
            user_role=access["user_role"],
            document_name=access["document_name"],
            access_type=access["access_type"],
            query_text=access.get("query_text"),
            access_granted=access["access_granted"],
            response_accuracy=access.get("response_accuracy"),
            chunks_accessed=access["chunks_accessed"],
            session_id=f"test_session_{access['username']}_{int(time.time())}"
        )
        
        status = "✅" if success else "❌"
        access_status = "granted" if access["access_granted"] else "denied"
        print(f"  {status} Logged {access_status} access: {access['username']} -> {access['document_name']}")

def test_statistics_retrieval():
    """Test statistics retrieval functions"""
    print("\n📊 Testing Statistics Retrieval...")
    
    # Test login statistics
    try:
        login_stats = get_login_statistics(7)  # Last 7 days
        if login_stats and not login_stats.get("error"):
            total_stats = login_stats.get("total_statistics", {})
            print(f"  ✅ Login Stats - Total: {total_stats.get('total_attempts', 0)}, "
                  f"Successful: {total_stats.get('successful_logins', 0)}, "
                  f"Failed: {total_stats.get('failed_logins', 0)}")
            
            daily_stats = login_stats.get("daily_statistics", [])
            print(f"  📅 Daily records: {len(daily_stats)} days")
            
            top_users = login_stats.get("top_users", [])
            print(f"  👥 Top users: {len(top_users)} users")
        else:
            print(f"  ❌ Failed to get login statistics: {login_stats.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ Error getting login statistics: {e}")
    
    # Test document access statistics
    try:
        doc_stats = get_document_access_statistics(7)  # Last 7 days
        if doc_stats and not doc_stats.get("error"):
            doc_list = doc_stats.get("document_statistics", [])
            print(f"  ✅ Document Stats - {len(doc_list)} documents accessed")
            
            role_stats = doc_stats.get("role_statistics", [])
            print(f"  🎭 Role breakdown: {len(role_stats)} roles")
            
            denied_stats = doc_stats.get("access_denied_statistics", [])
            print(f"  🚫 Access denied events: {len(denied_stats)} events")
        else:
            print(f"  ❌ Failed to get document statistics: {doc_stats.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ Error getting document statistics: {e}")

def test_dashboard_data():
    """Test dashboard data retrieval"""
    print("\n🎛️ Testing Dashboard Data Retrieval...")
    
    try:
        dashboard_data = get_audit_dashboard_data()
        if dashboard_data and not dashboard_data.get("error"):
            today_summary = dashboard_data.get("today_summary", {})
            print(f"  ✅ Today's Summary - Logins: {today_summary.get('logins', 0)}, "
                  f"Doc Accesses: {today_summary.get('document_accesses', 0)}, "
                  f"Active Users: {today_summary.get('active_users', 0)}")
            
            print(f"  📊 Dashboard generated at: {dashboard_data.get('generated_at', 'Unknown')}")
        else:
            print(f"  ❌ Failed to get dashboard data: {dashboard_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ Error getting dashboard data: {e}")

def main():
    """Run all audit system tests"""
    print("🚀 Starting Audit System Tests")
    print("=" * 50)
    
    # Run tests
    test_login_logging()
    test_document_access_logging()
    
    # Wait a moment for database writes to complete
    print("\n⏳ Waiting for database operations to complete...")
    time.sleep(2)
    
    test_statistics_retrieval()
    test_dashboard_data()
    
    print("\n" + "=" * 50)
    print("✅ Audit System Tests Completed!")
    print("\n💡 Tips:")
    print("  • Check audit_logs.db file in the project root")
    print("  • Login as admin or hr_user to see audit dashboard in the frontend")
    print("  • Document access is logged automatically during chat queries")
    print("  • All audit data is stored securely and can be exported for compliance")

if __name__ == "__main__":
    main()