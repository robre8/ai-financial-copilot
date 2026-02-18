#!/usr/bin/env python3
"""
Diagnostic test script for AI Financial Copilot API
Tests each endpoint systematically and reports detailed errors
"""

import requests
import json
import time
from pathlib import Path

# Cambiar aquí si necesitas probar en localhost
BASE_URL = "https://ai-financial-copilot.onrender.com"  # 🔹 Cambiar a http://localhost:8000 para local
TIMEOUT = 30

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_health_check():
    """Test 1: Health check endpoint"""
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {repr(e)}")
        return False

def test_upload_pdf():
    """Test 2: PDF upload endpoint"""
    print_header("TEST 2: PDF Upload")
    
    # Crear un pequeño archivo PDF de prueba
    test_pdf = Path("test.pdf")
    if not test_pdf.exists():
        print("⚠️  Creating minimal test PDF...")
        # Crear un PDF mínimo válido
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000212 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
306
%%EOF
"""
        test_pdf.write_bytes(pdf_content)
    
    try:
        with open(test_pdf, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            response = requests.post(
                f"{BASE_URL}/upload-pdf",
                files=files,
                timeout=TIMEOUT
            )
        
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response (raw): {response.text[:500]}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {repr(e)}")
        return False

def test_ask_question():
    """Test 3: Ask question endpoint"""
    print_header("TEST 3: Ask Question")
    
    payload = {
        "question": "What is the company's total revenue?",
        "use_context": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json=payload,
            timeout=TIMEOUT
        )
        
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
        except:
            print(f"Response (raw): {response.text[:500]}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {repr(e)}")
        return False

def main():
    print("\n" + "🔍 AI FINANCIAL COPILOT - DIAGNOSTIC TEST SUITE 🔍".center(60))
    print(f"Testing: {BASE_URL}\n")
    
    start_time = time.time()
    results = {}
    
    # Run tests
    results["Health Check"] = test_health_check()
    time.sleep(1)  # Brief pause between tests
    
    results["PDF Upload"] = test_upload_pdf()
    time.sleep(1)
    
    results["Ask Question"] = test_ask_question()
    
    elapsed = time.time() - start_time
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"Time: {elapsed:.2f}s\n")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check logs above for details.")
    
    # Cleanup
    test_pdf = Path("test.pdf")
    if test_pdf.exists():
        test_pdf.unlink()

if __name__ == "__main__":
    main()
