#!/usr/bin/env python3
"""
Comprehensive Security and Failure Testing Suite for FinSolve Chatbot
Tests security vulnerabilities, failure scenarios, and edge cases.
"""

import requests
import json
import time
import sqlite3
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import jwt
import hashlib
import random
ing


class SecurityTester:
    """Comprehensive "
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        selfken = None
        self.valid_refresh_token = None
    
    def run_all_security_tests(self, Any]:
        """Run all security tests ""
    ")
        print("=" * 60)
        
        results = {
       ormat(),
            "total_tests": 0,
            "passed": 0,
     0,
            "critical_issues": [],
            "warnings": [],
         }
        }
        
        # Test categories
        test_categories = [
     
ity),
       
            ("Authoriza
      ation),
            ("Rate Limiting", self.test,
            ("CORS Security", self.test_cors_securi
          
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n🧪 Testing: {category_name}")
            print("-" * 40)
            
            category_results = test_function()
            results["test_categories"][category_name] =ts
            
            # Update totals
            results["total_tests"] += category_results["
            results["passd"]
            results["failed"] += category_resuiled"]
            
           ssues
            if category_results.get("critical_issues"):
                results["critical_issues"].extend(category_results["critical_issues"])
            
            if category_results.get("warnings"):
       
        
        # Generate summary
        self.print_security_summary(results)
        return results
    
    def test_authentication_security(sel
        """Test authentication security vulnerabilities."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": 
        
      = [
            ("Brute Force Protection", self.test_brute_force_protection),
            ("Password Strength", self.test_password_stre,
            ("Invalid Credentials", self.test_invalid_ntials),
            ("Empty Credentials", self.test_empt
        ),
            ("Username En)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
    
                test_result = test_func()
         
              
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                n')}")
                    if test_result.get("
 on')}")
                    else:
             n')}")
            except Exception as e:
                results["failed"] += 1
                p
                results["cr)
        
        return results
    
    def test_br Any]:
        """Test if the "
        # Attempt multip
        failed_attempts = 0
      ):
            try:
                rost(
               
                    dat},
                    timeout=5
                )
                if respons== 401:
                    failed_attempts += 1
                elif response.status_code == 
              "}
                tis
            except:
                pass
        
        # If all 10 attempts went through e
        if failed 8:
            return {
         
                "critical"
                "reason": "No brute force protection 
            }
        
        retuted"}
    
    def test_password_strength(self) - Any]:
        """T"
        # This is more of a policy check since we can't create new users
        # We'ts
        weak_pass
        
        # Since we can't creweak
        # The test accounts all use "passwweak
        return {
            "passed": False,
        se,
            "reason": "Test accounts use weak passwords (password123) - should enforce stronger password poli"
        }
    
 
  ."""
        try:
            response = requests.post(
              ",
             word"},
     =5
            )
            
            if respo:
                # Check if error message doesn't reveal whexists
      ()
                if "user" in error_msg and "not found" in error_msg:
                    return {
        e,
                        False,
                        "reason": "Error message
                    }
                return {"passed": True, "reason":on"}
            else:
                return {

                    "critical": True,
                    "r}"
                }
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Request "}
    
    def test_empty_credentials(self) -
       ""
        test_cases = [
       
            {"username": "admin", "password": ""},
            {"username": "", "password": "password123"}
        ]
        
        for credentials in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    data=credentials,
                    timeout=5
                )
                
                if response.
                    return {
                        "passed": False,
               
                        "rs}"
                    }
         cept:
         pass
        
        return {"passed": True, "reason": "Properly rejects em"}
    
    def test_login_sqlny]:
    ""
        sql_payloads = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
    --",
            "' OR 1=1 --",
            "admin"
        ]
        
        for payload:
            try:
                response = requests.post(
                    f"{sel",
                    data={"username": d"},
                    t
                )
                
                # ess
            :
                    return 
                        "passed": False,
                        "critical": True,
                        "reason": f"Possible SQL injection"
                    }
            except:
                pass
     
        return {"passed": True, "reason": "No SQL injection vulnogin"}
    
    def y]:
        """Test if the system reveals valid usernames."""
        valid_user = "admin"
        inv"
        
     try:
            # Test with vd
            response1 = requests.post(
                f"{self.base_url",
                data={"username": valid_usrd"},
                timeout=5
            )
            
 
            respons.post(
                f"{self.base_url}/auth/login",
                data={"username": invalid_user, "password": "wrong_password"},
                timeout=5
            )
            
      e
            if response1.sde:
                return {
                    "passed": False,
                    "critical": False,
   mes"
                }
            
    
            msg2 = resp"")
        
            if msg1 != msg2:
                return {
                    "passed": False,
                    "se,
                    "reason": "Different error messages reveal username validity"
                }
            
            return {"passed": True, "reason": 
            
        except Exception as e:
           "}
    
    def test_jwt_security(self) -> Dict[y]:
        """Test JWT token security."""
        results = {"total": 0, "passed" []}
        
        # First, get a valid token
        self.get_valid_token()
        
      = [
            ("Token Manipulation", self.test_token_manipul),
            ("Token Expiry", self.test_token_expiry),
            (,
            (",
            ("Token Reuse", self.test_token_reuse)
        ]
        
    
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
        
                    print(f"  ✅ {test_name}: PASSED")
      :
                 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', '}")
                    if test_result.g"):
                      ")
                    else:
                        re')}")
            :
                results["fa"] += 1
           
                results["critical_issues"].
        
        return results
    
    def get_valid_token(self) -> bool:
        """Get a valid tok"
        try
            response = requests.post(
                f"{self.base_ur
                data={"username": "admin", "password123"},
                timeout=5
            )
            
            if response.status_co0:
                data )
                self.valid_token = da")
       ken")
                return True
        
            pass
        return False
    
    def test_token_manipulaty]:
        """Test JWT token manipulation."""
        if not self.valid_token:
            return {"passed": False, "critical": Trueing"}
        
        # Try to he token
        try:
            # Decode without verification to see the payload
            payload = jwt.decode(self.valid_token, options={"verify_
            
            # Try to change the role to C-evel
            payload["role"] = "C-Level"
            
            # Create a new token with the same secret (this should fail if secret is strong)
            weak_secrets = ["secret", "key", "your_su
            
            for secret in weak_secrets:
                t
                    manipulated_token = jwt.encode(payload, seHS256")
                    
                    # Test if torks
                    response = requests.get(
             ",
                        headers={"Authoriza
                        timeout=5
          
         
                    if response.status_code == 200:
                        return {
              
     
                            "reason": f"Token manipulation successful with secret: {secret}"
                        }
                except:
    continue
            
            return
            
        except Ee:
            return (e)}"}
    
    def test_algorithm_confusion(self) -> Dict[str, Any]:
        """Test algorithm confusion attac"
        if not self.valid_token:
            return {"passed": False, "critical": True, 
        
        try:
            # Decode ayload
 
            
            # Try to create a token 
            none_token = jwt.encode(payload, one")
            
            # Test if the none algorithm toks
            res
                f"{self.base_url,
          en}"},
                timeout=5
        
            
            if resp 200:
                return {
                    "pas,
                    "critica True,
          "
                }
            
            return {"passed": True, "rea"}
            
        e:
            return {"passed": False, "critical": True, "reason": f"Algorithm conf}
    
    def test_secret_keytr, Any]:
        """Test JWT
        # This is based on the code
        secret = "your_super_secret_key_finsolve_2024"
        
        # Check secret strength
        issues = []
        
     32:
            issues.appe")
        
        if secret.lower(_2024"]:
            issues.append("Secret key is predictable/default")
        
        if not any(c.isupper() for c in se
            i
        
     t):
            issues.append("Secret key lacks numbers")
  
       secret):
            issues.append("Secret cters")
        
        if issues:
            return {
                "passed": False,
                "critic: True,
   }"
            }
        
        return {"passed": True, "reason": "Secre"}
    
    :
 
        if not self.valid_token:
            return {"passe}
        
        try:
            # Decode token to iry
 e})
            exp = payload.get("exp")
            
            if not exp:
                return {
                    "passed": False,
                    "critical": True,
                    "re
                }
            
            # Check if expiry is reasonablig)
            exp_timemp(exp)
            now = datetime.now()
    - now
            
            if time_diff.to
                return 
                    "passed": False,
                    "critical": False,
                    "reason": f"Token ex"
                }
  
            return {"passed": True, "reason": f"Token expiry reasonable: {tes"}
            
        except Exception as e:
     "}
    
    def test_token_reuse(s
        """Test if tokens can be reused after logout"""
        # Since there's no logout endpoint, 
    eck
        return {
         
            "critical": F
            "reason":ide"
        }
    
    def test_sql_injection(self) -> Dict[stny]:
        """Test SQL injection vulnerabiliti"
        results = {"total": 0, "pa
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("Chat Query SQL Injection",
            ("Search n),
            ("Hisction)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_func()
                if test_result["passed"]:
       += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
 = 1
                    print(f"  ❌ {test_nam}")
                    if test_result):
                        results[")}")
                    else:
                        results["warnings"].a')}")
            except Exceptio e:
    1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["crit}")
        
        return results
    
    def test_chat_sql_injectiny]:
   
        if not self.valid_token:
            return {"passed": False, "critical": True, "reasoe"}
        
        sql_payloads = [
            "'; DROP TABLE chat_messages; --",
            "' UNION SELECT * FROM use
            "' OR 1=1 --",
            "'; INSERT INTO chat_messages VALUES ('hacke
        ]
        
        headers =
        
        for payload in sql_payloads:
            try:
                response = requests.post(
                    f"{s
                    jsond},
                    headers=headers,
               ut=10
                )
                
                # Check for SQL error messages or unexpected
                if response.status_code == 500:
                    error_text = response.t
                    if any(ke
       urn {
                            se,
                        e,
             d}"
                        }
                
                # If we get a successful response with sus
    200:
    ()
                    response_text = str(response_data).lower()
                
                        return {
            False,
                            "critical": True,
                            "reason": f"Possible SQL injection with payload: {d}"
                        }
                        
         ion as e:
                # Network errors are expected and don't indicate SQL injection
    
        
        return {"passed": Truet"}
    
    def test_search_sql_injection(self) -> Dict[str, Any]:
        """Test SQL injection in search functionali""
        if not self.valid_token:
            return {"passed":
        
        # Test search endpoint if it exists
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        sql_payloads = [
            "'; DROP TABLE chat_sessions; --",
            "' UNION SELECT username, password_hash FROM users --",
            "' OR 1=1 --"
        ]
        
        for payloaads:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/chat/history
                    params={"query": payload}
                    headers=headers,
                    timeou
                )
                
                if response.status_code == 500:
                   t.lower()
            
                        
                            "passed": False,
                            "critical": True,
                            "reason": f"Syload}"
                        }
                        
            except:
                connue
  
        return {"passed": True, "reason": "No arch"}
    
    def test_history_sql_injectio
        """Test SQL injection in histo
        if not self.valid_token:
            return {"passed": False, "critical": True, "rlable"}
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        # Test sessr
        try:
            response = requests.
                f"{self.base_url}/api/v1/chat/history/session/'; DROP TAB",
                headers=headers,
                timeout=10
            )
            
            e == 500:
              
                if any(keyword in ):
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": "SQL injection indpoint"
                    }
        except:
            pass
        
        r"}
    
    def test_authorization_b, Any]:
        """Test authorization bypass att"""
        results = {"to": []}
        
        tests = [
      s),
            ("Invalid Token Access", self.test_invalid_token_access),
          ,
            ("Cross-Use
        ]
        
        for test_name, test_func in tests:
            results["total"
            try:
                test_result = test_func()
                if test_result["passed"]:
        += 1
                    print(f"  ✅ {test_name}: PASSED")
            else:
                    results["failed"] += 1
   ")
       al"):
                        results["crit")
                    else:
                        results["warn")
            except Exceas e:
                result= 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{r(e)}")
        
        return results
    
    def test_no_token_access(self) -> Dict[str, Any]:
        """Test access without authentication token."""
        protected_endpoints = [
            "/chat",
            "/api/v1/user/profile",
            "/ons",
            "/api/v1/analytics/accuracy"
        ]
        
        for endpoint in protected_endpoint
        ry:
                response = requests.get(f"{self.base_url}ut=5)
                
                if response.status_co1:
                    return {
           lse,
                        "criti": True,
                        "reason": f"Endpoint {endpe})"
     }
        
                continue
        
        return {"passed": True, "reason": "All protected endpoication"}
    
    def test_invalid_t

        invalid_tokens = [
            "invalid_token",
            "Bearer invalid",
    ture",
            ""
       
        
        
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{self.base_ur",
                    headers=headers,
                    timeout=5
                )
                
       
       eturn {
                        "passed,
                        "critical":
                        "reason": f"Invalid token accepted: {token[:20]}..."
                    }
        cept:
                continue
        
        return {"passed": True, "reason": "Invalid tokens ped"}
    
    def test_role_escalation(self) -> Dict[str, Any]:
        """Test role escalation att""
        # Get tokens for different roles
        roles_to_test = [
         "),
            ("finance_user", "Finance")
        ]
        
        for usernamest:
            try:
                e user
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    data={"username123"},
                    timeout=5
                )
                
                if response.status_code == 200:
 )
                    h
                    
                    # Try to access C-Ltent
                    chat_response = requests.post(
                        f"{self.base_url}/chat",
                        json={"query": "Show ,
          rs,
                        timeout=10
           )
          
                    if chat_
                        response_data = chat_response.json()
                        response_text = respo).lower()
                      
                        # Check if sensitive information is leaked
                        sensitive_keywords = ["ed"]
  
                            return {
                                "passed"e,
                                "critical": True,
                                "reason": f"Role esc
   }
            except:
       inue
        
        return {"passed": True, "reason": "No role escalation vulnerabilities d
    
    def test_cross
        """Test if users can ac."""
        # This would require testing chat history access between different users
        # Since we don't have user-speci
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot verify user data isolation - need to testry"
        }
    
    def test_input_validation(self) -> Dict[str, Any]:
        """Test input val"""
        results = {"tot
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("XSS in Chat", self.test_xss_chat),
            ("Large Input Handling", self.test_larget),
            ("Special Characters", self.test_special_characters),
     tion)
        ]
        
        for test_name, test_f tests:
            results["total"] += 1
            try:
                test_resu()
                if test
                    results["passed
       
                else:
   ] += 1
       ")
                    if test_result.get("critical"):
                        results[)
                    else:
                        results["warnings")
            except Exception as e:
    
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["crit)
        
        return results
    
    def test_xss_chat(se
        """
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No v}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x o
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        headers = {"Authorization": f"Bearer {self.valioken}"}
        
        for payload in xss_payloads:
            try:
            
                    f"{self.base_url}/chat",
                    json={"querd},
              =headers,
   ut=10
                )
                
                if response.status_code == 200:
                    respons)
        _data)
                    
                    # Check if the payng
    :
                        return {
                            "passed": False,
                            "critical": True,
           
              
            except:
                continue
        
   
    
    def test_large_input(self) -> Dict[str, Any]:
        """Test handling of large inputs."""
        if not self.valid_token:
      lable"}
        
        # Test with very l query
        lary
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"query": larg,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 0:
                return {
                    "passed": False,
             
                    "reason": "Ser"
                }
            elif response.status_code == 3:
                return {"passed":
            elif respo00:
                return {"passed":"}
       
            return {"passed": True, "r}
            
        except Exception as e:
      {
      
                "critical": False,
                "reason": f"Larg)}"
            }
    
    def tetr, Any]:
        """Test handling of special characters."""
       ken:
            return {"pas}
        
        special_chars = [
            "测试中文字符",  # Chineses
            "🚀🔒# Emojis
            "\x00\xrs
            "\\n\\sequences
            "NULL\0test"  # Null bytes
        ]
      
        headers = {"Authorization": f"Bearer {self.valid_to"}
        
        for cha
            try:
                response = requests.post(
           t",
                    json={"query": f"Test with special characters: {"},
                    headers=headers,
       =10
                )
                
                if 500:
           
                        "passe,
                  e,
                        "reason": f"Server erro}"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Special characters handled properly"}
    
   r, Any]:
        """Test null byte injection."""
        if not self.valid
            return {"p
        
        null_payloads = [
            "test\x00.txt",
            "query\0admin",
            "search\x00' OR 1=1 --"
      ]
        
        headers = {"Autho
        
        for payload in null_payloads:
            try:
                response = requests.post(
                 
                    json={"query": payload},
                    headers=headers,
                  
                )
                
                if resp0:
   er()
                    if "null" in error_text or "byte" in error_text:
                        return {
                            "passed": False,
                            "critical": True,
    load)}"
                        }
            except:
                contin
        
        re}
    
    def test_rate_limiting(:
        """Test""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        tests = [
            ("API Rate Limiting", self.t),
            ("Login Rate Limiting", self.test_logimiting)
        ]
        
        for test_name, test_func in test
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["pa
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["fa += 1
              )
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
   e:
                        results["warnings"].')}")
            except Exception as e:
   
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{tes}")
        
        return results
    
    def test_api_rate_limiting(self) -> Dict[str, Any]:
        """Test API rang."""
        if not self.valid_token:
            self.get_valid_token()
        
        if notn:
            returnilable"}
        
        headers = {"Authorizaten}"}
        
        # Make rapid requests
        rate_limited = False
        for i in range(20):
            ry:
                respo
                    fat",
                    json={"query": f"Test query {i}"},
                    headers=headers,
                    timeout=5
                )
                
                if response.statu
      
                    break
        
                time.sleep(0.1)  # Small delay
            except:
                continue
        
        if not rate_limited:
            retu{
                "passed": False,
                "critical": False,
                "reason": "No API rate limiting detected - allows unlimited requests"
            }
        
        return {"passed": True, "reason": "API r
    
    def test_login_rate_limiting(self) -> Dict[str:
        """Test login rate limitin""
        # This is 
        return self.test_brute_
    
    def test_cors_ser, Any]:
     "
        results = {"total": 0, "passed": 
        
        tests = [
            ("CORS Configuration", self.test_cors_configu
            ("Preflight Requests", self.test_preflight_requests)
        ]
        
        for test_name, test_f:
            results["total"] += 1
           :
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
     )
                else:
                    results["failed"] += 1
                    pri}")
                    if test_result.get("critical"):
  )}")
                 else:
                        results["warnings"].append(f"{test_name}: {test_result.get('re")
            except Exception  e:
                results["failed"] += 1
                print(f"  ❌ {teste)}")
                results["critic
        
        return results
    
    def test:
        """Test 
        try:
            response = requests.options(
                f"{self.base_url}/c
                headers={"Origin": "om"},
                timeout=5
            )
         
     = {
                "Access-Contro
                "Access-Control-Allow-Methods": response.headers.get("Access),
                "Access-Control-Allow-Headers": respons")
            }
            
     n)
            i
                return {
                    "passed": False,
                    "critical": Flse,
                    "reason": "CORS allows aon"
                }
            
     e"}
            
        except Exception as e:
            return {"passed": False, "critical": True, ""}
    
    def testtr, Any]:
        """Test CORS preflight requests."""
        try:
            reions(
                f"{selt",
                headers={
                    "Origin": "http://localhost:8501",
                    "Access-Control-Request-MethOST",
                    "Access-Control-Request-H"
                },
                timeout=5
            )
            
         
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Preflight request fa"
            }
            
         
            
        except Exception as :
            return {"passed": 
    
    def test_session_security(self) -> Dict[stny]:
        """Test session security."""
        result
        
        tests = [
    n),
            ("Session Hijacking", self.test_session_hijacking),
     ssions)
        ]
        
        for test_name, 
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["pass:
                    results["passed"] += 1
                    print(
                else:
                    resul] += 1
                    print(f"  ❌)
                    if test_result.get("critical"):
                        results["critical_
 e:
                        results["warnings"].app}")
       :
          1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].a}")
        
        return 
    
    def test_session_fixation(self) -> Dict[str, Any]:
    "
        # JWT tokens are stateless, so session fixation is less of a concern
        # But we should check if tokenerated
        return {
            "passed": True,
            "reason": "JWT tokens aplicable"
        }
    
    def test_session_hija]:
        """Test session hijacking protection."""
        # Checg
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.v
            return {"passed": False, "critical": True, "reason": 
        
        # Try using the same token from different user agent
        headers1 = {
          ,
            "User
        }
        
        headers2 = {
            "Authorization": f"Bear}",
            "User.0"
        }
        
        try:
        
            response2 = requests.get(f"{self.base_url}/api/v1/user/profile", headers=headers2, timeout=
            
            if response1.status_cod:
               turn {
                    "passed": False,
                    "critical": False,
      "
                }
            
            return {"passed": True, "reason": "Some session ped"}
            
        except Exception as e:
}
    
    def test_]:
        """Te"""
        # Login multiple times and check if all tokens work
        tokens = []
        
        for i in range
            try:
                response = requests.post(
    login",
                   "},
                    timeou5
                )
                
                if response.status_code == 200:
                    token = response.json().get("an")
                    if token:
                     n)
            except:
                continue
        
        if len(tokens) < 2:
            return 
        
        # Test if allly
        valid_tokens = 0
        for token in tokens:
            try:
         
              
           
                    timeout=5
                )
                if response.status_cod= 200:
                    valid_tokens += 1
            except:
                continue
        
        if valid_tokens == len(tokens):
            return {
                "passed": False,
                "c: False,
                "reason": f"All {len(tokens)} concurrent sesst"
            }
        
        return {"passed": T"}
    
    def print_security_summarny]):
        """Print comprehensive security tey."""
        pr"="*60)
   MMARY")
        print("="*60)
        
        print(f"📊 Total Tests: {results['total_tests']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📈 Success Rate: {(results['passed']/results['total_te")
        
      
            print(f"\n🚨 CRITICAL SECURITY ISSUES ({len(results['critical_issues'])}):")
            for i, issue in enumerate(results['critical_issus'], 1):
                print(f"  {i}. {issue}")
     
        if results['wngs']:
            print(f"\n⚠️  SECURITY WARNINGS ({len(results
        1):
              
        
        print(f"\n📋 DETAILED RESULTS BY CGORY:")
        for cat
            success_rate = (category_results['passed']/category_results['total']*100) if c
            print(f"  {category}: {category_results['pass)
        
        # Securidations
        print(f"\n💡 SECURITY RECOMMENDATIONS:")
        recommendations = [
            "Implement rate limiting for API endpoints",
            "Use stronger JWT tropy",
     s",
            "Implement proper input validation and sanitization",
            "Add request size limits to prevent DoS attac
   gout",
            "Review CORS configurat
            "Add comprehensive logging for security 
            "Implement proper error handling to avoid in
      
        ]
        
        for i, rec in enumerate(recommendations, :
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


def main():
    """Run comprehensive securit"
    print("te")
    print("This will te
  ")
    
    # Wait for user conn
    input("\nPress Enter to start testin)
    
    tester = Security
    results = tester.run_)
    
    # Save results to 
    time")
    results_file = f"secujson"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Return exit code based ssues
    if results['critica]:
        print(f"\n❌ TESTING COMPLETED WITH {len(results['critical_i")
    eturn 1
    else:
        print(f"\n✅ 



if __name__ == ":
    exit(main())