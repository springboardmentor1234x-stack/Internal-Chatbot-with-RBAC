#!/usr/bin/env python3
"""
Comprehensive login test for all users
"""
import requests
import json

def test_all_users():
    """Test all user accounts"""
    
    all_users = [
        {"username": "admin", "expected_role": "C-Level"},
        {"username": "finance_user", "expected_role": "Finance"},
        {"username": "marketing_user", "expected_role": "Marketing"},
        {"username": "hr_user", "expected_role": "HR"},
        {"username": "engineering_user", "expected_role": "Engineering"},
        {"username": "employee", "expected_role": "Employee"},
        {"username": "intern_user", "expected_role": "Intern"},
    ]
    
    print("🔍 COMPREHENSIVE LOGIN TEST")
    print("=" * 60)
    
    successful_logins = 0
    failed_logins = 0
    
    for user in all_users:
        username = user["username"]
        expected_role = user["expected_role"]
        
        print(f"\n🧪 {username}")
        print("-" * 30)
        
        try:
            # Quick login test
            response = requests.post(
                'http://127.0.0.1:8000/auth/login',
                data={'username': username, 'password': 'password123'},
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_role = data.get("user", {}).get("role", "Unknown")
                
                print(f"✅ LOGIN SUCCESS")
                print(f"   Expected Role: {expected_role}")
                print(f"   Actual Role: {actual_role}")
                print(f"   Role Match: {'✅' if actual_role == expected_role else '❌'}")
                print(f"   Has Token: {'✅' if data.get('access_token') else '❌'}")
                
                successful_logins += 1
                
            else:
                print(f"❌ LOGIN FAILED")
                print(f"   Status Code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown')}")
                except:
                    print(f"   Response: {response.text[:100]}")
                
                failed_logins += 1
                
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR - Backend not running")
            failed_logins += 1
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT - Backend too slow")
            failed_logins += 1
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            failed_logins += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successful logins: {successful_logins}/{len(all_users)}")
    print(f"❌ Failed logins: {failed_logins}/{len(all_users)}")
    
    if successful_logins == len(all_users):
        print("\n🎉 ALL USERS CAN LOGIN SUCCESSFULLY!")
        print("The issue might be in the frontend interface, not the backend API.")
    elif failed_logins > 0:
        print(f"\n⚠️ {failed_logins} users cannot login - backend issue detected")
    
    return successful_logins, failed_logins

if __name__ == "__main__":
    test_all_users()