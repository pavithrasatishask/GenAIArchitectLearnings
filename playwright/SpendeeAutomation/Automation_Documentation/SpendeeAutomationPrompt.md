# 🤖 **Comprehensive Prompt for Spendee Transaction Automation** 

## **Main Objective:**
Create a complete Python automation system that extracts financial transactions from PDF statements (GPay and PhonePe), intelligently categorizes them, and automatically adds them to the Spendee expense tracking web application using browser automation. **The solution must be extremely client-friendly with direct function call support and flexible parameter handling.**

---

## **📋 Detailed Requirements:**

### **1. PDF Processing & Data Extraction:**
- **Extract transactions** from GPay PDF statements with date format "01Oct,2025" and amounts like "₹1,960"
- **Parse PhonePe PDF statements** with date format "Oct 29, 2025" and DEBIT/CREDIT transaction types
- **Dynamic month/year filtering** based on user input or parameters (not hardcoded)
- **Extract merchant names** from patterns like "PaidtoMERCHANT" and "ReceivedfromPERSON"
- **Detect income vs expense** transactions automatically (credits vs debits)
- **Generate clean transaction notes** from raw PDF content

### **2. Intelligent Transaction Categorization:**
- **Food & Drink**: zomato, swiggy, dominos, restaurants, cafes
- **Groceries**: blinkit, lulu, dmart, samvrudhi, grofers, bigbasket
- **Shopping**: amazon, meesho, kushals, lenskart, urbancompany, lifestyle
- **Gifts**: All income/credit transactions should be categorized as gifts
- **Monthly Expenses Filter**: Automatically SKIP recurring payments like rent (mygate), utilities (gail gas), salaries, and personal transfers
- **Case-insensitive matching** with space removal for robust keyword detection

### **3. Browser Automation for Spendee:**
- **Login automation** to https://app.spendee.com/auth/login with credentials
- **Navigate to Cash Wallet** and access transaction forms
- **Automatically select transaction type**: "Income" for credits, "Expenses" for debits
- **Fill form fields**: category, date (dd/mm/yyyy format), note, amount
- **Submit each transaction** and verify successful addition
- **Handle errors gracefully** with retry mechanisms and fallback selectors

### **4. Client-Friendly Interface (CRITICAL REQUIREMENT):**
- **Direct function call support**: `run_automation(email, password, month, year, gpay_pdf, phonepe_pdf)`
- **Flexible parameter handling**: Accept all, some, or no parameters
- **Multiple usage modes**: Direct calls, command line, interactive prompts
- **Template files**: Provide ready-to-use client templates
- **No hardcoded values**: All credentials and dates must be parameterized

### **5. Data Management & Debugging:**
- **Generate JSON output files** for transaction validation and debugging
- **Provide detailed console logs** showing extraction progress, categorization decisions, and automation steps
- **Save separate files** for GPay, PhonePe, and combined transaction data
- **Include transaction summaries** with counts per category and total amounts

---

## **🛠️ Technical Specifications:**

### **Required Libraries:**
```python
from playwright.sync_api import sync_playwright, Page
import pdfplumber
import time
import os
import re
import json
import sys
from datetime import datetime
from typing import List, Dict
```

### **Key Configuration Parameters:**
```python
# NO HARDCODED VALUES - All must be parameters
LOGIN_URL = "https://app.spendee.com/auth/login"
DASHBOARD_URL = "https://app.spendee.com/dashboard"
# Email, password, month, year, PDF paths - ALL from parameters
```

### **Core Functions to Implement:**

1. **`main(email=None, password=None, target_month=None, target_year=None, gpay_pdf=None, phonepe_pdf=None)`**
   - Master function accepting all parameters
   - Falls back to prompts for missing parameters
   - Orchestrates entire workflow

2. **`run_automation(...)`** - CLIENT-FRIENDLY WRAPPER
   - Simple wrapper around main() function
   - Primary interface for client usage
   - Same parameter signature as main()

3. **`get_target_month_year()`**
   - Handle command line args, user input, or defaults
   - Support format: MM/YYYY or individual month/year
   - Default to previous month if no input

4. **`get_pdf_files()`**
   - Handle command line args, user input, or defaults
   - Verify file existence and provide feedback
   - Support custom file paths

5. **`extract_gpay_transactions(pdf_path, target_month, target_year)`**
   - Parse GPay PDF with pdfplumber and month filtering
   - Extract date, merchant, amount, and transaction type
   - Apply categorization and return transaction list

6. **`extract_phonepe_transactions(pdf_path, target_month, target_year)`**
   - Parse PhonePe PDF format with DEBIT/CREDIT detection
   - Handle different date format and structure
   - Apply same categorization logic as GPay

7. **`categorize_transaction(merchant, note, is_income=False)`**
   - Implement keyword-based categorization with income parameter
   - Handle income vs expense routing (Gifts for income)
   - Return tuple of (category, label)

8. **`add_transaction_to_spendee(page, transaction)`**
   - Browser automation for form filling with optimized selectors
   - Handle transaction type selection (Income/Expenses)
   - Submit form and verify success

---

## **🎯 Client Usage Patterns (PRIMARY REQUIREMENT):**

### **Pattern 1: Direct Function Call (RECOMMENDED)**
```python
from spendeeMonthlyUpdate import run_automation

# Complete automation
run_automation(
    email="client@email.com",
    password="client_password",
    target_month=10,
    target_year=2025,
    gpay_pdf="October_GPay.pdf",
    phonepe_pdf="October_PhonePe.pdf"
)

# Partial parameters (prompts for missing ones)
run_automation(email="client@email.com", password="password123")
```

### **Pattern 2: Client Template File**
```python
# simple_client_template.py
from spendeeMonthlyUpdate import run_automation

def run_my_automation():
    MY_EMAIL = "client@email.com"
    MY_PASSWORD = "password123"
    TARGET_MONTH = 10
    TARGET_YEAR = 2025
    GPAY_PDF = "GPay_Oct.pdf"
    PHONEPE_PDF = "PhonePe_Oct.pdf"
    
    run_automation(MY_EMAIL, MY_PASSWORD, TARGET_MONTH, TARGET_YEAR, GPAY_PDF, PHONEPE_PDF)
```

### **Pattern 3: Command Line Usage**
```bash
python spendeeMonthlyUpdate.py 10 2025 GPay.pdf PhonePe.pdf
python spendeeMonthlyUpdate.py --help
```

### **Pattern 4: Interactive Mode**
```python
from spendeeMonthlyUpdate import run_automation
run_automation()  # Will prompt for all missing parameters
```

---

## **📊 Expected Output Behavior:**

### **Console Output Sample:**
```
🗓️ Found target date: '01Oct,2025' in line 6
💰 Found amount line 9: '01Oct,2025 PaidtoKUSHALS ₹1,960'
🏪 Extracted merchant from amount line: 'KUSHALS'
📋 Processing transaction: 'KUSHALS' - ₹1960 (EXPENSE)
🛍️ MATCHED Shopping keyword: 'kushals'
✅ Extracted: KUSHALS - ₹1960 [Shopping] - kushals

✓ Transaction 1 completed. Waiting 3 seconds before next transaction...
```

### **JSON Output Structure:**
```json
{
  "date": "01/10/2025",
  "merchant": "KUSHALSRETAILPVTLTD52",
  "category": "Shopping",
  "label": "kushals",
  "amount": "1960.0",
  "currency": "INR",
  "note": "PaidtoKUSHALSRETAILPVTLTD52",
  "transaction_type": "Expenses"
}
```

### **Final Summary:**
```
📊 Total transactions extracted for 10/2025: 17
✅ Successfully added 17 transactions!
🎉 Automation complete!
```

---

## **🎯 Success Criteria:**

### **Functional Requirements:**
- ✅ Extract 100% of target month transactions from both PDF sources
- ✅ Correctly categorize 95%+ of transactions automatically
- ✅ Successfully add all transactions to Spendee with proper income/expense classification
- ✅ Generate comprehensive JSON debug files for validation
- ✅ Complete execution in under 60 seconds for typical monthly statements

### **Error Handling Requirements:**
- ✅ Graceful handling of PDF parsing errors
- ✅ Browser automation resilience with multiple selector fallbacks
- ✅ Clear error messages with specific context
- ✅ Automatic retry mechanisms for transient failures
- ✅ Page closure detection and recovery

### **Performance Requirements:**
- ✅ Process 15-20 transactions in under 45 seconds
- ✅ Memory usage under 100MB during execution
- ✅ No screenshot overhead (optimize for speed)
- ✅ Minimal selector complexity (single selectors preferred)

---

## **💡 Implementation Approach:**

### **Phase 1: Core PDF Processing**
1. Implement robust PDF text extraction using pdfplumber
2. Create regex patterns for date and amount extraction
3. Build merchant name parsing logic
4. Add income detection for "Receivedfrom" patterns

### **Phase 2: Categorization System**
1. Create comprehensive keyword dictionaries
2. Implement case-insensitive, space-removed matching
3. Add monthly expense filtering logic
4. Build income routing to "Gifts" category

### **Phase 3: Browser Automation**
1. Implement Playwright-based login automation
2. Create robust form field selection with fallbacks
3. Add transaction type selection (Income/Expenses)
4. Build form submission with error recovery

### **Phase 4: Integration & Optimization**
1. Combine all components into main workflow
2. Add comprehensive logging and debugging
3. Optimize selectors and remove overhead
4. Generate detailed progress reporting

---

## **🔍 Advanced Features to Include:**

### **1. Income Detection Logic:**
```python
# Detect credit transactions from patterns like:
is_income = any(keyword in amount_line for keyword in 
              ['Receivedfrom', 'Received from', 'received'])
```

### **2. Monthly Expense Filtering:**
```python
# Skip recurring monthly payments:
monthly_expense_keywords = [
    'kanchanamurugesan', 'mygate', 'gailgaslimited', 
    'komalkhattar', 'sandhiyaradhakrishnan'
]
```

### **3. Smart Merchant Extraction:**
```python
# Extract merchant from various patterns:
if "PaidtoMERCHANT" in line:
    merchant = line.replace("Paidto", "").strip()
elif "ReceivedfromPERSON" in line:
    merchant = line.replace("Receivedfrom", "").strip()
```

---

## **📝 Deliverables Expected:**

1. **`spendeeMonthlyUpdate.py`** - Complete automation script with client-friendly interface
2. **`simple_client_template.py`** - Ready-to-use template for clients
3. **`run_automation()` function** - Primary client interface with flexible parameters
4. **JSON debug files** - Transaction extraction validation
5. **Console logging** - Detailed progress and error reporting
6. **Help documentation** - Usage examples and parameter descriptions
7. **Multi-mode support** - Direct calls, command line, interactive prompts

---

## **🔧 Advanced Client-Friendly Features:**

### **Parameter Flexibility:**
- **All parameters optional**: Function works with 0 to 6 parameters
- **Smart defaults**: Previous month, default file names, environment variables
- **Command line integration**: Support both function calls and CLI usage
- **Interactive fallbacks**: Prompt only for missing critical parameters

### **Template System:**
```python
# Client just needs to update these lines:
MY_EMAIL = "their@email.com"
MY_PASSWORD = "their_password"
TARGET_MONTH = 11
TARGET_YEAR = 2025
GPAY_PDF = "November_GPay.pdf"
PHONEPE_PDF = "November_PhonePe.pdf"
```

### **Error Handling & Validation:**
- **Parameter validation**: Month (1-12), file existence, email format
- **Graceful degradation**: Continue with partial data if some files missing
- **Clear error messages**: Specific context for each failure
- **Recovery mechanisms**: Retry automation, alternative selectors

---

**🎯 Final Goal:** Create a production-ready automation that is incredibly easy for clients to use with a simple function call while maintaining 100% accuracy in transaction processing. The system should be flexible enough to handle various client needs while being simple enough for non-technical users.

**📊 Expected Client Experience:** 
- 30-second setup time (just edit 6 variables)
- Zero learning curve (simple function call)
- 100% reliability with error recovery
- Complete transaction automation with no manual steps

---

*This prompt should generate a complete, robust, and extremely client-friendly financial transaction automation system that prioritizes ease of use while maintaining all technical capabilities.*