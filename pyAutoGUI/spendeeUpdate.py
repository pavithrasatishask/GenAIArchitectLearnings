# ============================================================================
# SPENDEE EXPENSE AUTOMATION FROM GPAY & PHONEPE PDFs
# ============================================================================

try:
    from pypdf import PdfReader  # type: ignore
except ImportError:
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except ImportError:
        print("ERROR: Please install pypdf or PyPDF2")
        print("Run: pip install pypdf")
        exit(1)

import pyautogui  # type: ignore
import time
import re
from datetime import datetime
from pathlib import Path

# ============================================================================
# SPENDEE COORDINATES DICTIONARY
# ============================================================================

SPENDEE_COORDS = {
    "add_transaction_button": (99, 145),
    "close_button": (60, 145),
    "close_x_button": (980, 172),
    "category_dropdown": (108, 229),
    "date_field": (265, 229),
    "note_field": (460, 229),
    "label_dropdown": (648, 229),
    "amount_field": (812, 229),
    "currency_dropdown": (914, 229),
    "recurrence_dropdown": (670, 295),
    "attachment_button": (633, 294),
    "keep_open_checkbox": (193, 301),
    "submit_button": (890, 294),
    "expenses_tab": (78, 270),
    "income_tab": (160, 270),
    "transfer_tab": (242, 270),
}


# ============================================================================
# CATEGORY MAPPING
# ============================================================================

CATEGORY_MAPPING = {
    # Food & Dining
    "zomato": "Food & Drink",
    "swiggy": "Food & Drink",
    "restaurant": "Food & Drink",
    "cafe": "Food & Drink",
    "food": "Food & Drink",
    "dominos": "Food & Drink",
    "pizza": "Food & Drink",
    "mcdonald": "Food & Drink",
    "kfc": "Food & Drink",
    "burger": "Food & Drink",
    "starbucks": "Food & Drink",
    
    # Groceries
    "grocery": "Groceries",
    "groceries": "Groceries",
    "supermarket": "Groceries",
    "big bazaar": "Groceries",
    "dmart": "Groceries",
    "reliance fresh": "Groceries",
    "more": "Groceries",
    "bigbasket": "Groceries",
    "blinkit": "Groceries",
    "dunzo": "Groceries",
    "zepto": "Groceries",
    "instamart": "Groceries",
    
    # Transport
    "uber": "Transport",
    "ola": "Transport",
    "metro": "Transport",
    "petrol": "Transport",
    "fuel": "Transport",
    "parking": "Transport",
    "rapido": "Transport",
    "bus": "Transport",
    "train": "Transport",
    "taxi": "Transport",
    
    # Bills & Utilities
    "electricity": "Bills & Fees",
    "water": "Bills & Fees",
    "internet": "Bills & Fees",
    "mobile": "Bills & Fees",
    "recharge": "Bills & Fees",
    "airtel": "Bills & Fees",
    "jio": "Bills & Fees",
    "vodafone": "Bills & Fees",
    "bsnl": "Bills & Fees",
    "broadband": "Bills & Fees",
    "wifi": "Bills & Fees",
    "bill": "Bills & Fees",
    
    # Healthcare
    "hospital": "Healthcare",
    "medical": "Healthcare",
    "doctor": "Healthcare",
    "pharmacy": "Healthcare",
    "medicine": "Healthcare",
    "apollo": "Healthcare",
    "clinic": "Healthcare",
    "health": "Healthcare",
    
    # Education
    "school": "Education",
    "education": "Education",
    "books": "Education",
    "course": "Education",
    "tuition": "Education",
    "fees": "Education",
    
    # Shopping
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "myntra": "Shopping",
    "ajio": "Shopping",
    "shopping": "Shopping",
    "clothes": "Shopping",
    "fashion": "Shopping",
    "meesho": "Shopping",
    
    # Entertainment
    "movie": "Entertainment",
    "cinema": "Entertainment",
    "netflix": "Entertainment",
    "prime": "Entertainment",
    "hotstar": "Entertainment",
    "spotify": "Entertainment",
    "youtube": "Entertainment",
    
    # Fitness
    "gym": "Sport & Hobbies",
    "fitness": "Sport & Hobbies",
    "yoga": "Sport & Hobbies",
    "sports": "Sport & Hobbies",
    
    # Beauty
    "salon": "Beauty",
    "beauty": "Beauty",
    "spa": "Beauty",
    
    # Others
    "gift": "Gifts",
    "loan": "Loan",
    "emi": "Monthly Expenses",
    "rent": "Monthly Expenses",
}

CREDIT_KEYWORDS = [
    "received", "refund", "cashback", "credited", "credit",
    "reward", "reversal", "returned", "money received"
]

# ============================================================================
# PDF PARSING FUNCTIONS
# ============================================================================

def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            print(f"  → Extracted {len(text)} characters from PDF")
            
            # Save first 2000 characters to debug file for analysis
            debug_file = f"{Path(pdf_path).stem}_debug.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(text[:2000])
            print(f"  → Saved first 2000 chars to {debug_file} for analysis")
            
            return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def is_credit_transaction(description):
    """Check if transaction is a credit (to be excluded from expenses)"""
    description_lower = description.lower()
    return any(keyword in description_lower for keyword in CREDIT_KEYWORDS)

def categorize_transaction(description):
    """Categorize transaction based on description keywords"""
    description_lower = description.lower()
    
    for keyword, category in CATEGORY_MAPPING.items():
        if keyword in description_lower:
            return category
    
    return "Other"

def parse_gpay_transactions(pdf_path):
    """Parse Google Pay PDF and extract transactions"""
    print(f"\nParsing GPay PDF: {pdf_path}")
    
    text = extract_text_from_pdf(pdf_path)
    transactions = []
    
    if not text:
        print("  ⚠ Could not extract text from PDF")
        return transactions
    
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    print(f"  → Processing {len(lines)} lines after filtering")
    
    i = 0
    while i < len(lines) - 3:
        current_line = lines[i]
        
        # Look for date pattern: "01May,2025"
        date_pattern = r'(\d{1,2}[A-Za-z]{3},\d{4})'
        date_match = re.search(date_pattern, current_line)
        
        if date_match and i + 3 < len(lines):
            try:
                # Extract date from current line
                date_str = date_match.group(1)
                
                # Next line should be time: "05:04AM"
                time_line = lines[i + 1]
                
                # Next line should be transaction details: "PaidtoSwiggy" or "ReceivedfromSigaNarayanan"
                details_line = lines[i + 2]
                
                # Skip to find amount line (look for ₹ symbol)
                amount_line = ""
                j = i + 3
                while j < len(lines) and j < i + 6:  # Look ahead max 3 lines
                    if '₹' in lines[j]:
                        amount_line = lines[j]
                        break
                    j += 1
                
                if amount_line and details_line:
                    # Skip "Received" transactions (income)
                    if "Receivedfrom" in details_line or "received" in details_line.lower():
                        print(f"  → Skipping income: {details_line}")
                        i = j + 1
                        continue
                    
                    # Extract amount
                    amount_pattern = r'₹([\d,]+\.?\d*)'
                    amount_match = re.search(amount_pattern, amount_line)
                    
                    if amount_match:
                        # Clean up description
                        description = details_line.replace("Paidto", "Paid to ").replace("PaidbyHDFCBank4456", "").strip()
                        amount_str = amount_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        
                        # Parse date: "01May,2025" -> "01/05/2025"
                        date_obj = datetime.strptime(date_str, "%d%b,%Y")
                        formatted_date = date_obj.strftime("%d/%m/%Y")
                        
                        category = categorize_transaction(description)
                        
                        transactions.append({
                            "category": category,
                            "amount": amount,
                            "date": formatted_date,
                            "note": description,
                            "label": "GPay",
                            "source": "GPay"
                        })
                        
                        print(f"  → Found: {description} - ₹{amount} on {formatted_date}")
                        i = j + 1
                        continue
                        
            except Exception as e:
                print(f"  Warning parsing line {i}: {e}")
        
        i += 1
    
    print(f"  → Found {len(transactions)} expense transactions")
    return transactions

def parse_phonepe_transactions(pdf_path):
    """Parse PhonePe PDF and extract transactions"""
    print(f"\nParsing PhonePe PDF: {pdf_path}")
    
    text = extract_text_from_pdf(pdf_path)
    transactions = []
    
    if not text:
        print("  ⚠ Could not extract text from PDF")
        return transactions
    
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]
    
    print(f"  → Processing {len(lines)} lines after filtering")
    if len(lines) > 0:
        print(f"  → First 3 lines: {lines[:3]}")
        print(f"  → Last 3 lines: {lines[-3:]}")
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Single-line format
        pattern = r'(\d{1,2}\s+\w+\s+\d{4})\s+(.+?)\s+(Debit|Credit)\s+[₹\+\-]?([\d,]+\.?\d*)'
        match = re.search(pattern, line, re.IGNORECASE)
        
        if match:
            try:
                date_str = match.group(1)
                description = match.group(2).strip()
                trans_type = match.group(3).strip().lower()
                amount_str = match.group(4).replace(',', '')
                
                if trans_type != 'debit':
                    print(f"  → Skipping {trans_type}: {description}")
                    i += 1
                    continue
                
                amount = float(amount_str)
                date_obj = datetime.strptime(date_str, "%d %b %Y")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                category = categorize_transaction(description)
                
                transactions.append({
                    "category": category,
                    "amount": amount,
                    "date": formatted_date,
                    "note": f"{description}",
                    "label": "PhonePe",
                    "source": "PhonePe"
                })
                
                i += 1
                continue
                
            except Exception as e:
                print(f"  Warning: {line[:50]}... - {e}")
                i += 1
                continue
        
        # Multi-line format (4 lines)
        if i + 3 < len(lines):
            date_line = lines[i].strip()
            detail_line = lines[i+1].strip()
            type_line = lines[i+2].strip()
            amount_line = lines[i+3].strip()
            
            date_pattern = r'(\d{1,2}\s+\w+\s+\d{4})'
            date_match = re.search(date_pattern, date_line)
            type_match = type_line.lower() in ['debit', 'credit']
            amount_pattern = r'[₹\+\-]?([\d,]+\.?\d*)'
            amount_match = re.search(amount_pattern, amount_line)
            
            if date_match and type_match and amount_match and detail_line:
                try:
                    date_str = date_match.group(1)
                    description = detail_line
                    trans_type = type_line.lower()
                    
                    if trans_type != 'debit':
                        print(f"  → Skipping {trans_type}: {description}")
                        i += 4
                        continue
                    
                    amount = float(amount_match.group(1).replace(',', ''))
                    date_obj = datetime.strptime(date_str, "%d %b %Y")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    category = categorize_transaction(description)
                    
                    transactions.append({
                        "category": category,
                        "amount": amount,
                        "date": formatted_date,
                        "note": f"{description}",
                        "label": "PhonePe",
                        "source": "PhonePe"
                    })
                    
                    i += 4
                    continue
                    
                except Exception as e:
                    print(f"  Warning: {e}")
        
        i += 1
    
    print(f"  → Found {len(transactions)} expense transactions")
    return transactions

# ============================================================================
# CONTINUATION - Load expenses and helper functions
# ============================================================================

def load_expenses_from_pdfs(gpay_pdf="GPayExpenses.pdf", phonepe_pdf="PhonePeExpenses.pdf"):
    """Load and combine expenses from both PDFs"""
    all_transactions = []
    
    print("\n" + "="*70)
    print("LOADING EXPENSES FROM PDF FILES")
    print("="*70)
    
    gpay_path = Path(gpay_pdf)
    phonepe_path = Path(phonepe_pdf)
    
    if gpay_path.exists():
        gpay_transactions = parse_gpay_transactions(gpay_path)
        all_transactions.extend(gpay_transactions)
    else:
        print(f"\n⚠ Warning: GPay PDF not found: {gpay_pdf}")
    
    if phonepe_path.exists():
        phonepe_transactions = parse_phonepe_transactions(phonepe_path)
        all_transactions.extend(phonepe_transactions)
    else:
        print(f"\n⚠ Warning: PhonePe PDF not found: {phonepe_pdf}")
    
    # Sort by date
    all_transactions.sort(key=lambda x: datetime.strptime(x['date'], "%d/%m/%Y"))
    
    print(f"\n{'='*70}")
    print(f"TOTAL TRANSACTIONS LOADED: {len(all_transactions)}")
    print(f"{'='*70}\n")
    
    # Display summary
    if all_transactions:
        print("Transaction Summary by Category:")
        category_totals = {}
        for t in all_transactions:
            cat = t['category']
            category_totals[cat] = category_totals.get(cat, 0) + t['amount']
        
        for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: ₹{total:,.2f}")
        
        total_amount = sum(t['amount'] for t in all_transactions)
        print(f"\n  TOTAL: ₹{total_amount:,.2f}")
    
    return all_transactions

# ============================================================================
# PYAUTOGUI HELPER FUNCTIONS
# ============================================================================

def wait(seconds=1):
    """Wait for specified seconds"""
    time.sleep(seconds)

def click_and_wait(x, y, wait_time=0.5):
    """Click at coordinates and wait"""
    pyautogui.click(x, y)
    wait(wait_time)

def type_text(text, interval=0.05):
    """Type text with specified interval"""
    pyautogui.write(text, interval=interval)
    wait(0.3)

def clear_field():
    """Clear current field"""
    pyautogui.hotkey('ctrl', 'a')
    wait(0.2)
    pyautogui.press('delete')
    wait(0.2)

# ============================================================================
# SPENDEE AUTOMATION FUNCTIONS
# ============================================================================

def add_expense_to_spendee(category_name, amount, date, note, label, keep_popup_open=False):
    """Add a single expense transaction to Spendee"""
    
    print(f"Adding: {category_name} - ₹{amount} - {date}")
    
    try:
        # Step 1: Click "Add transaction" button
        print("  → Opening form...")
        click_and_wait(
            SPENDEE_COORDS["add_transaction_button"][0],
            SPENDEE_COORDS["add_transaction_button"][1],
            wait_time=1.5
        )
        
        # Step 2: Select Category
        print(f"  → Category: {category_name}")
        click_and_wait(
            SPENDEE_COORDS["category_dropdown"][0],
            SPENDEE_COORDS["category_dropdown"][1],
            wait_time=1
        )
        
        # Ensure Expenses tab is selected
        click_and_wait(
            SPENDEE_COORDS["expenses_tab"][0],
            SPENDEE_COORDS["expenses_tab"][1],
            wait_time=0.5
        )
        
        # Type category to search and select
        type_text(category_name)
        wait(0.5)
        pyautogui.press('enter')
        wait(0.5)
        
        # Step 3: Enter Date
        print(f"  → Date: {date}")
        click_and_wait(
            SPENDEE_COORDS["date_field"][0],
            SPENDEE_COORDS["date_field"][1]
        )
        clear_field()
        type_text(date)
        wait(0.3)
        
        # Step 4: Enter Note
        if note:
            print(f"  → Note: {note[:30]}...")
            click_and_wait(
                SPENDEE_COORDS["note_field"][0],
                SPENDEE_COORDS["note_field"][1]
            )
            type_text(note[:100])
            wait(0.3)
        
        # Step 5: Enter Amount
        print(f"  → Amount: ₹{amount}")
        click_and_wait(
            SPENDEE_COORDS["amount_field"][0],
            SPENDEE_COORDS["amount_field"][1]
        )
        clear_field()
        type_text(str(amount))
        wait(0.3)
        
        # Step 6: Add Label
        if label:
            print(f"  → Label: {label}")
            click_and_wait(
                SPENDEE_COORDS["label_dropdown"][0],
                SPENDEE_COORDS["label_dropdown"][1]
            )
            wait(0.5)
            type_text(label)
            wait(0.5)
            pyautogui.press('enter')
            wait(0.3)
        
        # Step 7: Keep open checkbox
        if keep_popup_open:
            click_and_wait(
                SPENDEE_COORDS["keep_open_checkbox"][0],
                SPENDEE_COORDS["keep_open_checkbox"][1]
            )
        
        # Step 8: Submit
        print("  → Submitting...")
        click_and_wait(
            SPENDEE_COORDS["submit_button"][0],
            SPENDEE_COORDS["submit_button"][1],
            wait_time=2
        )
        
        print(f"✓ Success!\n")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False

def add_all_expenses_to_spendee(transactions):
    """Add all transactions from the list to Spendee"""
    
    if not transactions:
        print("No transactions to add!")
        return
    
    print("\n" + "="*70)
    print(f"ADDING {len(transactions)} TRANSACTIONS TO SPENDEE")
    print("="*70)
    print("\nMake sure:")
    print("  1. Spendee Cash Wallet transactions page is open")
    print("  2. Browser window is maximized")
    print("  3. 'Add transaction' button is visible")
    print("\nStarting in 5 seconds...")
    print("="*70 + "\n")
    wait(5)
    
    success_count = 0
    fail_count = 0
    
    for idx, transaction in enumerate(transactions, 1):
        print(f"\n[{idx}/{len(transactions)}] Processing...")
        
        keep_open = (idx < len(transactions))
        
        success = add_expense_to_spendee(
            category_name=transaction["category"],
            amount=transaction["amount"],
            date=transaction["date"],
            note=transaction["note"],
            label=transaction["label"],
            keep_popup_open=keep_open
        )
        
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        if keep_open:
            wait(1)
    
    print("\n" + "="*70)
    print("AUTOMATION COMPLETE!")
    print("="*70)
    print(f"✓ Successfully added: {success_count} transactions")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count} transactions")
    print("="*70 + "\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SPENDEE EXPENSE AUTOMATION SCRIPT")
    print("="*70)
    print("\nThis script will:")
    print("  1. Read expenses from GPay and PhonePe PDF files")
    print("  2. Automatically categorize them")
    print("  3. Add them to Spendee app")
    print("\nRequired files in same directory:")
    print("  - gpay_expenses.pdf")
    print("  - phonepe_expenses.pdf")
    print("="*70)
    
    # Load transactions from PDFs
    transactions = load_expenses_from_pdfs()
    
    if not transactions:
        print("\n⚠ No transactions found! Please check your PDF files.")
        print("  Make sure the PDFs are in the same directory as this script.")
        exit(1)
    
    # Ask user confirmation
    print("\nReady to add these transactions to Spendee?")
    response = input("Type 'yes' to continue or 'no' to cancel: ").strip().lower()
    
    if response == 'yes':
        add_all_expenses_to_spendee(transactions)
    else:
        print("\nAutomation cancelled.")
        print("Transactions were loaded but not added to Spendee.")

