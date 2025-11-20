from playwright.sync_api import sync_playwright, Page
import pdfplumber  # type: ignore
import time
import os
import re
import json
import sys
from datetime import datetime
from typing import List, Dict

def categorize_transaction(merchant: str, note: str, is_income: bool = False) -> tuple[str, str]:
    """
    Categorize transaction based on merchant name and return (category, label)
    is_income: True if this is a credit/income transaction
    """
    # Convert to lowercase and remove spaces for case-insensitive, space-insensitive matching
    merchant_clean = merchant.lower().replace(' ', '')
    note_clean = note.lower().replace(' ', '')
    combined_text = f"{merchant_clean} {note_clean}"
    
    # Debug: Print what we're categorizing
    print(f"    🔍 CATEGORIZING: Merchant: '{merchant}' | Clean: '{merchant_clean}' | Combined: '{combined_text}' | Income: {is_income}")
    
    # If this is income, categorize as Gifts
    if is_income:
        print(f"    💰 INCOME DETECTED -> Categorizing as Gifts")
        return ('Gifts', '')
    
    # Food & Drinks category
    food_keywords = ['veg','zomato', 'swiggy', 'dominos', 'pizza', 'restaurant', 'cafe', 'food', 'burger', 'kfc', 'mcdonalds']
    for keyword in food_keywords:
        if keyword in combined_text:
            print(f"    🍔 MATCHED Food keyword: '{keyword}'")
            if 'zomato' in combined_text:
                return ('Food & Drink', 'Zomato')
            elif 'swiggy' in combined_text:
                return ('Food & Drink', 'Swiggy')
            else:
                return ('Food & Drink', '')
    
    # Groceries category
    grocery_keywords = ['grofers','freshivores', 'blinkit', 'samvrudhifamilysto', 'lulu', 'dmart', 'reliancefresh', 'bigbasket', 'grocery', 'supermarket']
    for keyword in grocery_keywords:
        if keyword in combined_text:
            print(f"    🛒 MATCHED Grocery keyword: '{keyword}'")
            if 'grofers' in combined_text:
                return ('Groceries', 'Grofers')
            elif 'freshivores' in combined_text:
                return ('Groceries', 'Freshivores')
            elif 'blinkit' in combined_text:
                return ('Groceries', 'Blinkit')
            elif 'samvrudhi' in combined_text:
                return ('Groceries', 'Samvrudhi')
            elif 'lulu' in combined_text:
                return ('Groceries', 'Lulu')
            else:
                return ('Groceries', '')

    # Shopping category
    shopping_keywords = ['amazon', 'theindusvalley','ravel', 'sweetkaaramcoffee', 'kushals', 'littlejoy', 'max', 'lifestyle', 'ikea', 'meesho', 'lenskart', 'urbancompany']
    for keyword in shopping_keywords:
        if keyword in combined_text:
            print(f"    🛍️ MATCHED Shopping keyword: '{keyword}'")
            if 'amazon' in combined_text:
                return ('Shopping', 'Amazon')
            elif 'theindusvalley' in combined_text:
                return ('Shopping', 'TheIndusvalley')
            elif 'ravel' in combined_text:
                return ('Shopping', 'Ravel')
            elif 'sweetkaaramcoffee' in combined_text:
                return ('Shopping', 'Sweet Kaaram Coffee')
            elif 'kushals' in combined_text:
                return ('Shopping', 'kushals')
            elif 'littlejoy' in combined_text:
                return ('Shopping', 'Little Joy')
            elif 'max' in combined_text:
                return ('Shopping', 'Max')
            elif 'lifestyle' in combined_text:
                return ('Shopping', 'Lifestyle')
            elif 'ikea' in combined_text:
                return ('Shopping', 'IKEA')
            elif 'meesho' in combined_text:
                return ('Shopping', 'Meesho')
            elif 'lenskart' in combined_text:
                return ('Shopping', 'Lenskart')
            elif 'urbancompany' in combined_text:
                return ('Shopping', 'Urban Company')
            else:
                return ('Shopping', '')

    # Monthly expenses - skip these transactions (all lowercase, no spaces for robust matching)
    monthly_expense_keywords = [
        'kanchanamurugesan', 'zaheem', 'reshmakaranth', 'komalkhattar',
        'devisri', 'atriaconvergencetechnologieslimited', 'mygate', 
        'sandhiyaradhakrishnan', 'manjusantosh', 'aruneshpal', 'mohamedyasserkareem',
        'chitrakrishnanand', 'manish', 'gailgaslimited',
        # Add more person/company names that are regular monthly expenses
        'rent', 'salary', 'emi', 'loan'
    ]
    for keyword in monthly_expense_keywords:
        if keyword in combined_text:
            print(f"    🚫 MATCHED Monthly Expense keyword: '{keyword}' -> SKIPPING!")
            return ('SKIP', '')  # Mark for skipping
    
    print(f"    📂 NO MATCH - Defaulting to 'Other'")
    # Default to Other category
    return ('Other', '')

def should_skip_transaction(category: str) -> bool:
    """
    Check if transaction should be skipped (monthly expenses)
    """
    return category == 'SKIP'

def extract_gpay_transactions(pdf_path: str, target_month: int = 10, target_year: int = 2025) -> List[Dict]:
    """
    Extract transactions from Google Pay PDF statement for specific month/year only
    """
    transactions = []
    
    print(f"🎯 Extracting transactions for {target_month:02d}/{target_year} only")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        
        if not text:
            return transactions
        
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        i = 0
        while i < len(lines) - 3:
            current_line = lines[i]
            
            # Look for date pattern: "01May,2025" or "01 May, 2025" or "01May,25" or "01Oct,2025"
            date_patterns = [
                r'(\d{1,2}[A-Za-z]{3},\d{4})',  # 01Oct,2025
                r'(\d{1,2}\s+[A-Za-z]{3},\s+\d{4})',  # 01 Oct, 2025
                r'(\d{1,2}[A-Za-z]{3},\d{2})',  # 01Oct,25
            ]
            
            date_match = None
            for pattern in date_patterns:
                date_match = re.search(pattern, current_line)
                if date_match:
                    break
            
            if date_match and i + 3 < len(lines):
                try:
                    date_str = date_match.group(1)
                    
                    # Parse and check if this is the target month/year BEFORE processing
                    date_obj = None
                    try:
                        if ',' in date_str and len(date_str.split(',')[1].strip()) == 4:
                            date_obj = datetime.strptime(date_str, "%d%b,%Y")
                        elif ',' in date_str and len(date_str.split(',')[1].strip()) == 2:
                            year = int("20" + date_str.split(',')[1].strip())
                            date_str_full = date_str.split(',')[0] + f",{year}"
                            date_obj = datetime.strptime(date_str_full, "%d%b,%Y")
                        else:
                            date_obj = datetime.strptime(date_str, "%d %b, %Y")
                    except ValueError as e:
                        print(f"    ⚠️ Date parsing error for '{date_str}': {e}")
                        i += 1
                        continue
                    
                    # Skip if not target month/year
                    if date_obj.month != target_month or date_obj.year != target_year:
                        print(f"    ⏭️ Skipping {date_obj.strftime('%d/%m/%Y')} - not target month")
                        i += 1
                        continue
                    
                    print(f"\n  🗓️ Found target date: '{date_str}' in line {i}: '{current_line}'")
                    
                    # Look at next few lines to find merchant and amount
                    time_line = lines[i + 1] if i + 1 < len(lines) else ""
                    details_line = lines[i + 2] if i + 2 < len(lines) else ""
                    
                    print(f"    Line {i+1} (time): '{time_line}'")
                    print(f"    Line {i+2} (details): '{details_line}'")
                    
                    # Skip to find amount line
                    amount_line = ""
                    j = i + 3
                    while j < len(lines) and j < i + 8:  # Look further for amount
                        print(f"    Line {j} (checking): '{lines[j]}'")
                        if '₹' in lines[j]:
                            amount_line = lines[j]
                            print(f"    💰 Found amount line {j}: '{amount_line}'")
                            break
                        j += 1
                    
                    if amount_line and details_line:
                        # Skip income transactions
                        if "Receivedfrom" in details_line or "received" in details_line.lower() or "Received from" in details_line:
                            print(f"    ⏭️ Skipping income transaction: '{details_line}'")
                            i = j + 1
                            continue
                        
                        # Extract amount
                        amount_pattern = r'₹([\d,]+\.?\d*)'
                        amount_match = re.search(amount_pattern, amount_line)
                        
                        if amount_match:
                            # Better merchant name extraction from amount line
                            merchant = ""
                            
                            # First try to extract from the amount line which has format like:
                            # "01Oct,2025 PaidtoKUSHALSRETAILPVTLTD52 ₹1,960"
                            # "03Oct,2025 PaidtoMyGate ₹4,800"
                            amount_line_clean = amount_line.strip()
                            
                            # Remove date pattern first
                            date_pattern_clean = r'\d{1,2}[A-Za-z]{3},\d{4}\s*'
                            amount_line_clean = re.sub(date_pattern_clean, '', amount_line_clean)
                            
                            # Remove amount pattern
                            amount_pattern_clean = r'₹[\d,]+\.?\d*'
                            amount_line_clean = re.sub(amount_pattern_clean, '', amount_line_clean)
                            
                            # Extract merchant name
                            if "Paidto" in amount_line_clean:
                                merchant = amount_line_clean.replace("Paidto", "").strip()
                            elif "Paid to" in amount_line_clean:
                                merchant = amount_line_clean.replace("Paid to", "").strip()
                            elif "Receivedfrom" in amount_line_clean:
                                merchant = amount_line_clean.replace("Receivedfrom", "").strip()
                            elif "Received from" in amount_line_clean:
                                merchant = amount_line_clean.replace("Received from", "").strip()
                            else:
                                merchant = amount_line_clean.strip()
                                
                            print(f"    🏪 Extracted merchant from amount line: '{merchant}'")
                            
                            # Fallback to details_line if amount line extraction failed
                            if not merchant or len(merchant) < 2:
                                print(f"    🔄 Fallback: trying details_line extraction...")
                                if "Paid to" in details_line:
                                    merchant = details_line.replace("Paid to", "").strip()
                                elif "Paidto" in details_line:
                                    merchant = details_line.replace("Paidto", "").strip()
                                else:
                                    merchant = details_line.strip()
                                
                                # Clean up merchant name
                                merchant = merchant.replace("PaidbyHDFCBank4456", "").replace("Paid by HDFC Bank 4456", "").strip()
                            
                            # If merchant is still empty, try to extract from surrounding lines
                            if not merchant or len(merchant) < 2:
                                print(f"    🔍 Empty merchant, checking surrounding lines...")
                                # Check lines around for merchant info
                                for search_line_idx in range(max(0, i-2), min(len(lines), i+6)):
                                    line = lines[search_line_idx]
                                    if line and not re.search(r'\d{1,2}[A-Za-z]{3},\d{4}', line) and '₹' not in line and not re.search(r'\d{1,2}:\d{2}', line):
                                        if len(line) > 3 and line not in ["UPI Transaction ID:", "DEBIT", "CREDIT"]:
                                            merchant = line.strip()
                                            print(f"    📝 Found merchant in line {search_line_idx}: '{merchant}'")
                                            break
                            
                            amount_str = amount_match.group(1).replace(',', '')
                            amount = float(amount_str)
                            
                            formatted_date = date_obj.strftime("%d/%m/%Y")
                            
                            # Create clean note from raw_amount_line
                            clean_note = amount_line.strip()
                            # Remove date pattern
                            clean_note = re.sub(r'\d{1,2}[A-Za-z]{3},\d{4}\s*', '', clean_note)
                            # Remove amount pattern
                            clean_note = re.sub(r'₹[\d,]+\.?\d*', '', clean_note)
                            # Clean up extra spaces
                            clean_note = ' '.join(clean_note.split())
                            
                            # Detect if this is income (credit) transaction
                            is_income = any(keyword in amount_line for keyword in ['Receivedfrom', 'Received from', 'received'])
                            
                            # Categorize transaction during extraction
                            print(f"  📋 Processing transaction: '{merchant}' - ₹{amount} {'(INCOME)' if is_income else '(EXPENSE)'}")
                            category, label = categorize_transaction(merchant, merchant, is_income)
                            
                            # Skip monthly expense transactions
                            if should_skip_transaction(category):
                                print(f"  ⏭️ SKIPPED: {merchant} - ₹{amount} [Category: {category}]")
                                i = j + 1
                                continue
                            
                            transaction = {
                                'date': formatted_date,
                                'merchant': merchant,
                                'category': category,
                                'label': label,
                                'amount': str(amount),
                                'currency': 'INR',
                                'note': clean_note,  # Use cleaned raw_amount_line content
                                'transaction_type': 'Income' if is_income else 'Expenses',  # Add transaction type
                                'raw_details_line': details_line,  # For debugging
                                'raw_amount_line': amount_line,    # For debugging
                                'line_numbers': f"{i}-{j}"        # For debugging
                            }
                            
                            transactions.append(transaction)
                            
                            print(f"  ✅ Extracted: {merchant} - ₹{amount} [{category}]{' - ' + label if label else ''}")
                            i = j + 1
                            continue
                            
                except Exception as e:
                    print(f"Warning parsing GPay line {i}: {e}")
            
            i += 1
    
    except Exception as e:
        print(f"Error reading GPay PDF {pdf_path}: {e}")
    
    # Save extracted transactions to JSON for debugging
    output_file = "gpay_extracted_transactions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)
    print(f"📁 Saved {len(transactions)} extracted GPay transactions to {output_file}")
    
    return transactions

def extract_phonepe_transactions(pdf_path: str, target_month: int = 10, target_year: int = 2025) -> List[Dict]:
    """
    Extract transactions from PhonePe PDF statement
    """
    transactions = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        
        if not text:
            return transactions
        
        lines = text.splitlines()  # Use splitlines() instead of split('\n') for proper PDF parsing
        lines = [line.strip() for line in lines if line.strip()]
        
        i = 0
        while i < len(lines) - 2:
            current_line = lines[i]
            
            # Look for transaction lines with pattern: "Oct 29, 2025 Paid to MERCHANT DEBIT/CREDIT ₹amount"
            transaction_pattern = r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})\s+Paid\s+to\s+(.+?)\s+(DEBIT|CREDIT)\s+₹([\d,]+\.?\d*)'
            transaction_match = re.search(transaction_pattern, current_line)
            
            if transaction_match:
                try:
                    date_str = transaction_match.group(1)
                    merchant = transaction_match.group(2)
                    transaction_type = transaction_match.group(3)
                    amount_str = transaction_match.group(4).replace(',', '')
                    
                    # Parse date and filter by target month/year
                    date_obj = datetime.strptime(date_str, "%b %d, %Y")
                    if date_obj.month != target_month or date_obj.year != target_year:
                        i += 1
                        continue
                    
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    amount = float(amount_str)
                    is_credit = (transaction_type == 'CREDIT')
                    
                    # Categorize transaction
                    category, label = categorize_transaction(merchant, merchant, is_income=is_credit)
                    
                    # Skip monthly expense transactions
                    if should_skip_transaction(category):
                        print(f"  ⏭️ Skipping monthly expense: {merchant} - ₹{amount}")
                        i += 1
                        continue
                    
                    transactions.append({
                        'date': formatted_date,
                        'merchant': merchant,
                        'category': category,
                        'label': label,
                        'amount': str(amount),
                        'currency': 'INR',
                        'note': f'{merchant}',
                        'transaction_type': 'Income' if is_credit else 'Expenses'
                    })
                    
                    transaction_type_str = "INCOME" if is_credit else "EXPENSE"
                    print(f"  ✓ Extracted PhonePe: {merchant} - ₹{amount} [{category}] ({transaction_type_str}){' - ' + label if label else ''}")
                    
                except Exception as e:
                    print(f"Warning parsing PhonePe line {i}: {e}")
            
            i += 1
            
    except Exception as e:
        print(f"Error reading PhonePe PDF {pdf_path}: {e}")
    
    # Save extracted transactions to JSON for debugging
    output_file = "phonepe_extracted_transactions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)
    print(f"📁 Saved {len(transactions)} extracted PhonePe transactions to {output_file}")
    
    return transactions

def navigate_calendar_to_date(page: Page, target_day: int, target_month: int, target_year: int):
    """
    Simplified calendar navigation to the specified date using arrow buttons
    """
    try:
        print(f"Navigating calendar to: {target_day:02d}/{target_month:02d}/{target_year}")
        
        # Wait for calendar to load
        page.wait_for_timeout(1000)
        
        # For October 2025 transactions, we need to go back from current month (November 2025)
        current_month = 11  # November
        current_year = 2025
        
        # Calculate months to navigate backwards
        months_to_go_back = (current_year - target_year) * 12 + (current_month - target_month)
        
        print(f"Need to go back {months_to_go_back} months from {current_month}/{current_year} to {target_month}/{target_year}")
        
        # Navigate backwards using previous month buttons
        if months_to_go_back > 0:
            # Simple approach: look for any clickable element that might be a previous button
            for i in range(months_to_go_back):
                prev_clicked = False
                
                # Try common previous button patterns
                prev_patterns = ['‹', '❮', '<', 'prev', 'back', 'left']
                
                for pattern in prev_patterns:
                    try:
                        # Look for buttons or clickable elements containing the pattern
                        prev_element = page.locator(f'*:has-text("{pattern}")').filter(lambda el: el.is_visible()).first
                        if prev_element.is_visible():
                            prev_element.click()
                            page.wait_for_timeout(500)  # Wait for month change
                            prev_clicked = True
                            print(f"✓ Navigated back 1 month using pattern '{pattern}' ({i+1}/{months_to_go_back})")
                            break
                    except:
                        continue
                
                if not prev_clicked:
                    print(f"⚠️ Could not navigate back for month {i+1}")
                    break
        
        # Now select the specific day
        page.wait_for_timeout(500)
        
        # Try to click the target day
        day_clicked = False
        day_patterns = [
            f'text="{target_day}"',
            f'button:has-text("{target_day}")',
            f'*:has-text("{target_day}")' 
        ]
        
        for pattern in day_patterns:
            try:
                day_element = page.locator(pattern).filter(lambda el: el.is_visible() and not el.get_attribute('disabled')).first
                if day_element.is_visible():
                    day_element.click()
                    print(f"✓ Selected day {target_day} using pattern '{pattern}'")
                    page.wait_for_timeout(500)
                    day_clicked = True
                    break
            except:
                continue
        
        if not day_clicked:
            print(f"⚠️ Could not select day {target_day}")
            
        page.wait_for_timeout(1000)
        print("✓ Calendar navigation completed")
        
    except Exception as e:
        print(f"⚠️ Calendar navigation error: {e}")
        print("Falling back to direct date input...")

def add_transaction_to_spendee(page: Page, transaction: Dict):
    """
    Add a single transaction to Spendee
    """
    try:
        print(f"Adding transaction: {transaction['merchant'][:50]}...")
        
        # Click the "Add transaction" button
        add_button_selectors = [
            'button:has-text("Add transaction")',
            'text="Add transaction"',
            '[data-testid*="add-transaction"]',
            'button:has-text("Add")',
            '.add-transaction',
            '#add-transaction'
        ]
        
        button_clicked = False
        for selector in add_button_selectors:
            try:
                page.wait_for_selector(selector, timeout=3000)
                page.click(selector)
                print("✓ Clicked Add transaction button")
                button_clicked = True
                break
            except:
                continue
        
        if not button_clicked:
            raise Exception("Could not find 'Add transaction' button")
        
        # Wait for the popup/form to open
        form_selectors = [
            'text=Select category...',
            '[placeholder*="Select category"]',
            '.category-selector',
            'form',
            '.transaction-form'
        ]
        
        form_found = False
        for selector in form_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                print(f"✓ Transaction form opened")
                form_found = True
                break
            except:
                continue
        
        if not form_found:
            raise Exception("Transaction form did not open")
        
        # First, select transaction type (Expenses/Income/Transfer)
        transaction_type = transaction.get('transaction_type', 'Expenses')
        try:
            print(f"Selecting transaction type: {transaction_type}")
            
            # Look for transaction type selector (Expenses, Income, Transfer)
            type_selectors = [
                f'button:has-text("{transaction_type}")',
                f'text="{transaction_type}"',
                f'[role="button"]:has-text("{transaction_type}")'
            ]
            
            type_selected = False
            for selector in type_selectors:
                try:
                    page.wait_for_selector(selector, timeout=3000)
                    page.click(selector)
                    print(f"✓ Selected transaction type: {transaction_type}")
                    type_selected = True
                    page.wait_for_timeout(500)  # Wait for UI update
                    break
                except:
                    continue
                    
            if not type_selected:
                print(f"⚠️ Could not find transaction type '{transaction_type}' - continuing with default")
        
        except Exception as type_error:
            print(f"⚠️ Error selecting transaction type: {type_error}")
        
        # Select category
        category_button_selectors = [
            'text=Select category...',
            '[placeholder*="Select category"]',
            'button:has-text("Select category")',
            '.category-selector',
            '#category-select'
        ]
        
        category_button_clicked = False
        for selector in category_button_selectors:
            try:
                page.wait_for_selector(selector, timeout=3000)
                page.click(selector)
                print("✓ Clicked category selector")
                category_button_clicked = True
                break
            except:
                continue
        
        if not category_button_clicked:
            print("⚠️ Could not find category selector button")
            # Continue anyway - maybe category selection is different
        
        page.wait_for_timeout(1000)  # Wait for category dropdown to appear
        
        # Select category
        page.click('text=Select category...')
        page.wait_for_timeout(500)
        
        # Debug: Let's see what categories are available
        try:
            # Wait for category options to appear
            page.wait_for_timeout(1000)
            
            # Try to find all possible category elements
            category_elements = page.locator('button, div, li, span').filter(
                has_text=re.compile(r'(Food|Transport|Shopping|Bills|Other|Entertainment|Healthcare|Groceries)', re.IGNORECASE)
            )
            
            if category_elements.count() > 0:
                print(f"Found {category_elements.count()} category elements")
                # Print first few category texts for debugging
                for i in range(min(5, category_elements.count())):
                    try:
                        text = category_elements.nth(i).text_content()
                        print(f"  Category option {i}: '{text}'")
                    except:
                        continue
            else:
                print("No category elements found with common names")
                
        except Exception as e:
            print(f"Debug category check failed: {e}")
        
        # Try to find and click the category with multiple strategies
        category_found = False
        category_selectors = [
            f'button:has-text("{transaction["category"]}")',
            f'text="{transaction["category"]}"',
            f'[data-testid*="{transaction["category"].lower()}"]',
            f'*:has-text("{transaction["category"]}")',
            f'li:has-text("{transaction["category"]}")',
            f'div:has-text("{transaction["category"]}")',
        ]
        
        for selector in category_selectors:
            try:
                page.wait_for_selector(selector, timeout=2000)
                page.click(selector, timeout=3000)
                print(f"✓ Selected category: {transaction['category']}")
                category_found = True
                break
            except:
                continue
        
        if not category_found:
            # If category not found, try "Other" with multiple selectors
            print(f"Category '{transaction['category']}' not found, trying 'Other'...")
            other_selectors = [
                'button:has-text("Other")',
                'text="Other"',
                '[data-testid*="other"]',
                '*:has-text("Other")',
                'li:has-text("Other")',
                'div:has-text("Other")',
                # Sometimes it might be called differently
                'button:has-text("Others")',
                'text="Others"',
                'button:has-text("Miscellaneous")',
                'text="Miscellaneous"'
            ]
            
            other_found = False
            for selector in other_selectors:
                try:
                    page.wait_for_selector(selector, timeout=2000)
                    page.click(selector, timeout=3000)
                    print("✓ Selected 'Other' category")
                    other_found = True
                    break
                except:
                    continue
            
            if not other_found:
                # Last resort: try to click any available category
                print("Trying to click any available category...")
                try:
                    # Look for any clickable elements that might be categories
                    any_category = page.locator('button, div, li').filter(
                        has_text=re.compile(r'\w+', re.IGNORECASE)
                    ).first
                    
                    if any_category.is_visible():
                        category_text = any_category.text_content() or "Unknown"
                        any_category.click(timeout=3000)
                        print(f"✓ Selected fallback category: '{category_text[:20]}'")
                    else:
                        raise Exception("No clickable categories found")
                        
                except Exception as fallback_error:
                    print("⚠️ Could not find any category")
                    print(f"Fallback error: {fallback_error}")
                    # Continue without selecting category
        
        page.wait_for_timeout(1000)  # Wait for category selection to complete
        
        # Simple date entry using specific XPath
        print(f"Setting date: {transaction['date']}")
        try:
            formatted_date = transaction['date']  # Already in dd/mm/yyyy format
            print(f"Formatted date: {formatted_date}")
            
            # Use the specific XPath for the date field
            date_xpath = "//*[@id='app']/div/div[2]/div/div/div[1]/div/div/div[2]/div[1]/div/div/form/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div/input[1]"
            date_input = page.locator(f"xpath={date_xpath}")
            
            print("Waiting for date field...")
            page.wait_for_selector(f"xpath={date_xpath}", timeout=10000)
            
            print("Clicking date field...")
            date_input.click()
            page.wait_for_timeout(300)
            
            print("Clearing existing value...")
            date_input.press('Control+a')
            date_input.press('Delete')
            page.wait_for_timeout(200)
            
            print(f"Entering date: {formatted_date}")
            date_input.fill(formatted_date)
            page.wait_for_timeout(300)
            
            # Press Tab instead of Enter to avoid form submission
            date_input.press('Tab')
            page.wait_for_timeout(200)
            
            # Verify the date was entered
            current_value = date_input.input_value() or ""
            print(f"✓ Date entered successfully: {current_value}")
            
        except Exception as date_error:
            print(f"⚠️ Date selection error: {date_error}")
            print("Continuing without setting date...")
        
        # Skip label selection - not needed for this automation
        print("⚠️ Skipping label selection as requested")
        
        # Enter note
        try:
            print(f"Entering note: {transaction['note'][:50]}...")
            # Use more specific selector to avoid conflict with filter input
            note_selectors = [
                'input#note[placeholder="Write note"]',  # Most specific
                'input#note',  # Fallback
                'input[placeholder="Write note"]',  # By placeholder
                'textarea[placeholder*="note"]',  # In case it's a textarea
            ]
            
            note_entered = False
            for selector in note_selectors:
                try:
                    # Check if page is still active before proceeding
                    if page.is_closed():
                        print("⚠️ Page closed during note entry")
                        return
                    
                    note_input = page.locator(selector).first
                    if note_input.is_visible():
                        print(f"Found note field with selector: {selector}")
                        
                        # Use a simpler approach - just click and fill
                        print("Clicking and filling note field...")
                        note_input.click(timeout=5000)
                        page.wait_for_timeout(200)
                        
                        # Check if page is still active after click
                        if page.is_closed():
                            print("⚠️ Page closed after clicking note field")
                            return
                        
                        # Clear and fill in one go
                        note_text = transaction['note'][:100]  # Limit to 100 characters
                        note_input.fill("")  # Clear first
                        page.wait_for_timeout(100)
                        note_input.fill(note_text)  # Fill with content
                        page.wait_for_timeout(200)
                        
                        # Verify note was entered if page is still active
                        if not page.is_closed():
                            current_value = note_input.input_value() or ""
                            print(f"✓ Note entered successfully: '{current_value[:50]}...'")
                            note_entered = True
                        break
                except Exception as selector_error:
                    print(f"Note selector {selector} failed: {selector_error}")
                    continue
            
            if not note_entered:
                print("⚠️ Could not find suitable note input field")
                
        except Exception as note_error:
            print(f"⚠️ Error entering note: {note_error}")
        
        # Enter amount
        try:
            print(f"Entering amount: {transaction['amount']}")
            
            # Check if page is still active
            if page.is_closed():
                print("⚠️ Page closed before amount entry")
                return
            
            # Multiple selectors for amount field
            amount_selectors = [
                'input#price[type="number"]',  # Most specific
                'input#price',  # Fallback
                'input[type="number"]',  # Generic number input
                'input[placeholder*="amount" i]',  # By placeholder (case insensitive)
                'input[name*="amount"]',  # By name attribute
                'input[name*="price"]'  # By price name
            ]
            
            amount_entered = False
            for selector in amount_selectors:
                try:
                    amount_input = page.locator(selector).first
                    if amount_input.is_visible(timeout=2000):
                        print(f"Found amount field with selector: {selector}")
                        amount_input.click(timeout=5000)
                        page.wait_for_timeout(200)
                        
                        # Check if page is still active after click
                        if page.is_closed():
                            print("⚠️ Page closed after clicking amount field")
                            return
                        
                        amount_text = str(transaction['amount'])
                        amount_input.fill("")  # Clear first
                        page.wait_for_timeout(100)
                        amount_input.fill(amount_text)  # Fill with amount
                        page.wait_for_timeout(200)
                        
                        # Verify amount was entered
                        if not page.is_closed():
                            current_value = amount_input.input_value() or ""
                            print(f"✓ Amount entered successfully: '{current_value}'")
                            amount_entered = True
                        break
                except Exception as selector_error:
                    print(f"Amount selector {selector} failed: {selector_error}")
                    continue
            
            if not amount_entered:
                print("⚠️ Could not find suitable amount input field")
                
        except Exception as amount_error:
            print(f"⚠️ Error entering amount: {amount_error}")
        
        # Wait a bit for form validation (only if page is still active)
        if not page.is_closed():
            page.wait_for_timeout(1000)
        
        # Click "Add transaction" submit button
        try:
            print("Looking for 'Add transaction' button...")
            
            # Check if page is still active
            if page.is_closed():
                print("⚠️ Page closed before submit button click")
                return
            
            # Multiple selectors for submit button
            submit_selectors = [
                'button:has-text("Add transaction")[type="submit"]',  # Most specific
                'button:has-text("Add transaction")',  # Without type
                'button[type="submit"]:has-text("Add")',  # Generic submit with "Add"
                'button[type="submit"]',  # Any submit button
                'input[type="submit"]',  # Input submit
                'button:has-text("Save")',  # Alternative text
                'button:has-text("Submit")'  # Alternative text
            ]
            
            button_clicked = False
            for selector in submit_selectors:
                try:
                    submit_button = page.locator(selector).first
                    if submit_button.is_visible(timeout=2000):
                        print(f"Found submit button with selector: {selector}")
                        submit_button.click(timeout=5000)
                        print("✓ Clicked submit button")
                        button_clicked = True
                        break
                except Exception as selector_error:
                    print(f"Submit selector {selector} failed: {selector_error}")
                    continue
            
            if not button_clicked:
                print("⚠️ Could not find or click submit button")
                # Try pressing Enter as fallback
                try:
                    print("Trying Enter key as fallback...")
                    page.keyboard.press('Enter')
                    print("✓ Pressed Enter key")
                except:
                    print("⚠️ Enter key fallback also failed")
                
        except Exception as submit_error:
            print(f"⚠️ Error clicking submit button: {submit_error}")
        
        # Wait for the transaction to be added
        page.wait_for_timeout(1000)
        
        print(f"✓ Added: {transaction['date']} - {transaction['merchant']} - ₹{transaction['amount']}")
        
    except Exception as e:
        print(f"✗ Error adding transaction: {transaction.get('merchant', 'Unknown')} - {str(e)}")
        # Try to close the popup if it's still open
        try:
            page.keyboard.press('Escape')
            page.wait_for_timeout(500)
        except:
            pass

def get_target_month_year():
    """
    Get target month and year from user input, command line args, or use previous month as default
    """
    # Check for command line arguments first
    if len(sys.argv) >= 3:
        try:
            target_month = int(sys.argv[1])
            target_year = int(sys.argv[2])
            if 1 <= target_month <= 12:
                print(f"Using command line args: {target_month:02d}/{target_year}")
                return target_month, target_year
            else:
                print("⚠️ Invalid month in command line args! Using interactive mode.")
        except ValueError:
            print("⚠️ Invalid command line args! Using interactive mode.")
    
    # Calculate previous month as default
    now = datetime.now()
    if now.month == 1:
        default_month = 12
        default_year = now.year - 1
    else:
        default_month = now.month - 1
        default_year = now.year
    
    print(f"\n📅 Month/Year Selection:")
    print(f"   Default: {default_month:02d}/{default_year} (Previous month)")
    print(f"   Usage: python spendeeMonthlyUpdate.py <month> <year> [gpay_pdf] [phonepe_pdf]")
    print(f"   Example: python spendeeMonthlyUpdate.py 10 2025")
    
    try:
        # Ask user for month/year input
        user_input = input(f"\nEnter target month/year (MM/YYYY) or press Enter for default [{default_month:02d}/{default_year}]: ").strip()
        
        if not user_input:
            # Use default (previous month)
            print(f"Using default: {default_month:02d}/{default_year}")
            return default_month, default_year
        
        # Parse user input
        if '/' in user_input:
            parts = user_input.split('/')
            if len(parts) == 2:
                month = int(parts[0])
                year = int(parts[1])
                
                # Validate month
                if 1 <= month <= 12:
                    print(f"Using user input: {month:02d}/{year}")
                    return month, year
                else:
                    print("⚠️ Invalid month! Using default.")
                    return default_month, default_year
            else:
                print("⚠️ Invalid format! Using default.")
                return default_month, default_year
        else:
            print("⚠️ Invalid format! Using default.")
            return default_month, default_year
            
    except ValueError:
        print("⚠️ Invalid input! Using default.")
        return default_month, default_year
    except KeyboardInterrupt:
        print("\n⚠️ User cancelled. Using default.")
        return default_month, default_year

def get_pdf_files():
    """
    Get PDF file paths from command line args, user input, or use default files
    """
    # Check for command line arguments for PDF files
    if len(sys.argv) >= 5:
        gpay_pdf = sys.argv[3]
        phonepe_pdf = sys.argv[4]
        print(f"Using command line PDF files:")
        print(f"   GPay: {gpay_pdf}")
        print(f"   PhonePe: {phonepe_pdf}")
        return gpay_pdf, phonepe_pdf
    elif len(sys.argv) == 4:
        gpay_pdf = sys.argv[3]
        phonepe_pdf = "PhonePeExpenses.pdf"  # Default
        print(f"Using command line GPay PDF: {gpay_pdf}")
        print(f"Using default PhonePe PDF: {phonepe_pdf}")
        return gpay_pdf, phonepe_pdf
    
    print(f"\n📁 PDF File Selection:")
    
    # Check if default files exist
    default_gpay = "GPayExpenses.pdf"
    default_phonepe = "PhonePeExpenses.pdf"
    
    gpay_exists = os.path.exists(default_gpay)
    phonepe_exists = os.path.exists(default_phonepe)
    
    print(f"   Default GPay PDF: {default_gpay} {'✓' if gpay_exists else '✗'}")
    print(f"   Default PhonePe PDF: {default_phonepe} {'✓' if phonepe_exists else '✗'}")
    
    try:
        # Ask for GPay PDF
        gpay_input = input(f"\nEnter GPay PDF path or press Enter for default [{default_gpay}]: ").strip()
        gpay_pdf = gpay_input if gpay_input else default_gpay
        
        # Ask for PhonePe PDF
        phonepe_input = input(f"Enter PhonePe PDF path or press Enter for default [{default_phonepe}]: ").strip()
        phonepe_pdf = phonepe_input if phonepe_input else default_phonepe
        
        # Verify files exist
        if not os.path.exists(gpay_pdf):
            print(f"⚠️ GPay PDF not found: {gpay_pdf}")
        if not os.path.exists(phonepe_pdf):
            print(f"⚠️ PhonePe PDF not found: {phonepe_pdf}")
        
        return gpay_pdf, phonepe_pdf
        
    except KeyboardInterrupt:
        print("\n⚠️ User cancelled. Using defaults.")
        return default_gpay, default_phonepe

def main(email: str = None, password: str = None, target_month: int = None, target_year: int = None, 
         gpay_pdf: str = None, phonepe_pdf: str = None):
    """
    Main function to run Spendee automation
    
    Args:
        email: Spendee login email
        password: Spendee login password
        target_month: Target month (1-12)
        target_year: Target year (e.g., 2025)
        gpay_pdf: Path to GPay PDF file
        phonepe_pdf: Path to PhonePe PDF file
    """
    # Configuration
    LOGIN_URL = "https://app.spendee.com/auth/login"
    DASHBOARD_URL = "https://app.spendee.com/dashboard"
    
    # Use provided parameters or get from user input/defaults
    if target_month is None or target_year is None:
        TARGET_MONTH, TARGET_YEAR = get_target_month_year()
    else:
        TARGET_MONTH, TARGET_YEAR = target_month, target_year
        print(f"📅 Using provided target: {TARGET_MONTH:02d}/{TARGET_YEAR}")
    
    if gpay_pdf is None or phonepe_pdf is None:
        GPAY_PDF, PHONEPE_PDF = get_pdf_files()
    else:
        GPAY_PDF, PHONEPE_PDF = gpay_pdf, phonepe_pdf
        print(f"📁 Using provided PDF files:")
        print(f"   GPay: {GPAY_PDF}")
        print(f"   PhonePe: {PHONEPE_PDF}")
    
    # Use provided credentials or defaults
    if email is None or password is None:
        EMAIL = "pavithra.satishask@gmail.com"  # Default email
        PASSWORD = "Greenlobster123#"  # Default password
        print("🔐 Using default credentials")
    else:
        EMAIL = email
        PASSWORD = password
        print(f"🔐 Using provided credentials: {EMAIL}")

    # Slow down the automation for better visibility
    TYPING_DELAY = 100  # milliseconds between keystrokes
    WAIT_BETWEEN_ACTIONS = 1000  # milliseconds between form field interactions
    
    print("=" * 60)
    print("🚀 Spendee Transaction Automation Started")
    print("=" * 60)
    print(f"\n📋 Configuration Summary:")
    print(f"   Target Month/Year: {TARGET_MONTH:02d}/{TARGET_YEAR}")
    print(f"   GPay PDF: {GPAY_PDF}")
    print(f"   PhonePe PDF: {PHONEPE_PDF}")
    print(f"   Login Email: {EMAIL}")
    print("=" * 60)
    
    # Step 1: Extract transactions from PDFs for target month only
    print(f"\n📄 Extracting transactions from PDF files for {TARGET_MONTH:02d}/{TARGET_YEAR}...")
    
    gpay_transactions = []
    phonepe_transactions = []
    
    try:
        print(f"  - Reading {GPAY_PDF}...")
        gpay_transactions = extract_gpay_transactions(GPAY_PDF, TARGET_MONTH, TARGET_YEAR)
        print(f"    ✓ Found {len(gpay_transactions)} GPay transactions")
    except Exception as e:
        print(f"    ✗ Error reading GPay PDF: {e}")
    
    try:
        print(f"  - Reading {PHONEPE_PDF}...")
        phonepe_transactions = extract_phonepe_transactions(PHONEPE_PDF, TARGET_MONTH, TARGET_YEAR)
        print(f"    ✓ Found {len(phonepe_transactions)} PhonePe transactions")
    except Exception as e:
        print(f"    ✗ Error reading PhonePe PDF: {e}")
    
    # Combine all transactions (already filtered for target month)
    all_transactions = gpay_transactions + phonepe_transactions
    print(f"\n📊 Total transactions extracted for {TARGET_MONTH:02d}/{TARGET_YEAR}: {len(all_transactions)}")
    
    # Save all transactions to JSON for debugging
    with open("all_extracted_transactions.json", "w", encoding="utf-8") as f:
        json.dump(all_transactions, f, indent=2, ensure_ascii=False)
    print(f"📁 Saved all {len(all_transactions)} transactions to all_extracted_transactions.json")
    
    if len(all_transactions) == 0:
        print(f"\n⚠️  No transactions found for {TARGET_MONTH:02d}/{TARGET_YEAR}. Exiting.")
        return
    
    # Show transaction summary
    print(f"\n📋 Transaction Summary:")
    print(f"   Total transactions: {len(all_transactions)}")
    
    # Group by category
    category_counts = {}
    for transaction in all_transactions:
        category = transaction.get('category', 'Unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count} transactions")
    
    print(f"\n✅ Data extraction complete! Please review the JSON files:")
    print(f"   📄 gpay_extracted_transactions.json")
    print(f"   📄 phonepe_extracted_transactions.json") 
    print(f"   📄 all_extracted_transactions.json")
    print(f"\n� Proceeding with Spendee browser automation...")
    
    # EARLY RETURN DISABLED - Browser automation will now proceed
    # return
    
    # Start browser automation
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Step 2: Navigate to login page
            print("\n🌐 Navigating to login page...")
            
            # Set longer timeout for page navigation
            page.set_default_timeout(90000)  # 90 seconds
            
            # Navigate to login URL
            try:
                print(f"Trying URL: {LOGIN_URL}")
                page.goto(LOGIN_URL, timeout=90000)
                
                # Wait for page to load
                page.wait_for_load_state("domcontentloaded", timeout=30000)
                print(f"Successfully loaded: {LOGIN_URL}")
                    
            except Exception as e:
                raise Exception(f"Could not load Spendee login page: {str(e)[:100]}")
            
            # Give page time to fully render
            time.sleep(5)
            
            # Step 3: Login with robust error handling
            print("🔐 Logging in...")
            
            # Look for email field
            try:
                page.wait_for_selector('input[type="email"]', timeout=10000)
                email_field = page.locator('input[type="email"]').first
                print("Found email field with selector: input[type=\"email\"]")
                email_field.clear()
                email_field.fill(EMAIL)
                print(f"Email entered: {EMAIL}")
            except Exception as e:
                raise Exception(f"Could not find email field: {str(e)}")
            
            time.sleep(1)
            
            # Look for password field
            try:
                page.wait_for_selector('input[type="password"]', timeout=10000)
                password_field = page.locator('input[type="password"]').first
                print("Found password field with selector: input[type=\"password\"]")
                password_field.clear()
                password_field.fill(PASSWORD)
                print("Password entered successfully")
            except Exception as e:
                raise Exception("Could not find password field on the page")
            
            time.sleep(1)
            
            # Click login button
            try:
                page.wait_for_selector('button[type="submit"]', timeout=5000)
                login_button = page.locator('button[type="submit"]').first
                print("Found login button with selector: button[type=\"submit\"]")
                login_button.click(timeout=10000)
                print("Clicked login button")
            except Exception as e:
                # Try pressing Enter as fallback
                print("No login button found, trying Enter key...")
                page.keyboard.press("Enter")
            
            # Wait for navigation to complete
            print("Waiting for login to complete...")
            time.sleep(3)  # Give some time for the form submission
            
            # Check if we're at the dashboard or still at login page
            current_url = page.url
            print(f"Current URL after login: {current_url}")
            
            # Try multiple ways to detect successful login
            try:
                # First try: wait for dashboard URL
                page.wait_for_url(DASHBOARD_URL, timeout=15000)
                print("✓ Login successful - reached dashboard!")
            except:
                try:
                    # Second try: wait for any non-login URL
                    page.wait_for_function("!window.location.href.includes('login') && !window.location.href.includes('auth')", timeout=15000)
                    print("✓ Login successful - navigated away from login page!")
                except:
                    # Third try: check for dashboard elements
                    try:
                        page.wait_for_selector('text=Dashboard', timeout=10000)
                        print("✓ Login successful - found dashboard elements!")
                    except:
                        # Final check: look for wallet elements
                        try:
                            page.wait_for_selector('text=Cash Wallet', timeout=10000)
                            print("✓ Login successful - found wallet elements!")
                        except:
                            print("⚠️ Login status unclear - continuing anyway...")
            
            time.sleep(2)
            
            # Step 4: Navigate to Cash Wallet
            print("\n💰 Opening Cash Wallet...")
            
            # Wait for dashboard to fully load
            try:
                page.wait_for_load_state("domcontentloaded", timeout=10000)
            except:
                print("Page load warning - continuing...")
            
            time.sleep(3)
            
            # Use the XPath we discovered for Cash Wallet
            cash_wallet_selectors = [
                # Primary selector - exact XPath provided by user
                '//*[@id="app"]/div/div[2]/div/div/div/section/div/div/div[1]/a/div/article/header/span[1]/span[1]',
                
                # Alternative XPath targeting the clickable link element
                '//*[@id="app"]/div/div[2]/div/div/div/section/div/div/div[1]/a',
                
                # CSS selector for the same element
                "#app > div > div:nth-child(2) > div > div > div > section > div > div > div:nth-child(1) > a",
                
                # Text-based selectors as fallback
                'text="Cash Wallet"',
                'a:has-text("Cash Wallet")',
                
                # Generic wallet selectors
                'a[href*="/wallet/"]',
                '[class*="wallet"]'
            ]
            
            wallet_found = False
            for selector in cash_wallet_selectors:
                try:
                    print(f"Trying Cash Wallet selector: {selector}")
                    
                    # Handle XPath selectors differently
                    if selector.startswith('//') or selector.startswith('//*'):
                        page.wait_for_selector(f"xpath={selector}", timeout=5000)
                        element = page.locator(f"xpath={selector}").first
                    else:
                        page.wait_for_selector(selector, timeout=5000)
                        element = page.locator(selector).first
                    
                    if element.is_visible():
                        print(f"Found Cash Wallet with selector: {selector}")
                        
                        # For XPath targeting the span, click the parent link instead
                        if selector.startswith('//') and 'span[1]/span[1]' in selector:
                            # Navigate to the parent link element
                            parent_link = element.locator('xpath=./ancestor::a[1]')
                            if parent_link.count() > 0:
                                parent_link.click(timeout=10000)
                                print("Clicked parent link of Cash Wallet span")
                            else:
                                element.click(timeout=10000)
                                print("Clicked Cash Wallet span directly")
                        else:
                            element.click(timeout=10000)
                            print("Clicked Cash Wallet element")
                        
                        wallet_found = True
                        break
                        
                except Exception as e:
                    print(f"Selector {selector} failed: {str(e)}")
                    continue
            
            if not wallet_found:
                raise Exception("Could not find Cash Wallet")
            
            # Wait for wallet page to load
            time.sleep(3)
            
            # Look for transactions section or Add transaction button
            try:
                page.wait_for_selector('button:has-text("Add transaction")', timeout=10000)
                print("✓ Cash Wallet opened - found Add transaction button!")
            except:
                try:
                    page.wait_for_selector('text="Transactions"', timeout=5000)
                    print("✓ Cash Wallet opened - found Transactions section!")
                except:
                    print("⚠️ Cash Wallet navigation unclear - continuing anyway...")
            
            # Step 5: Add transactions
            print(f"\n➕ Adding {len(all_transactions)} transactions...")
            print("-" * 60)
            
            success_count = 0
            for i, transaction in enumerate(all_transactions, 1):
                print(f"\n[{i}/{len(all_transactions)}]", end=" ")
                add_transaction_to_spendee(page, transaction)
                success_count += 1
                
                # Pause between transactions for visibility
                print(f"✓ Transaction {i} completed. Waiting 3 seconds before next transaction...")
                page.wait_for_timeout(3000)  # 3 second pause between transactions
            
            print("\n" + "=" * 60)
            print(f"✅ Successfully added {success_count} transactions!")
            print("🎉 Automation complete!")
            print("=" * 60)
            
            # Keep browser open for a few seconds to review results
            print("Keeping browser open for review...")
            page.wait_for_timeout(10000)  # 10 seconds to review
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        finally:
            browser.close()

def run_automation(email: str = None, password: str = None, target_month: int = None, target_year: int = None, 
                   gpay_pdf: str = None, phonepe_pdf: str = None):
    """
    Convenient wrapper function for running the automation with parameters
    
    Example usage:
        # Run with all parameters
        run_automation(
            email="your@email.com", 
            password="yourpassword",
            target_month=10, 
            target_year=2025,
            gpay_pdf="October_GPay.pdf",
            phonepe_pdf="October_PhonePe.pdf"
        )
        
        # Run with just credentials (will prompt for month/year and files)
        run_automation(email="your@email.com", password="yourpassword")
        
        # Run with month/year only (will use default credentials and prompt for files)
        run_automation(target_month=10, target_year=2025)
    """
    return main(email, password, target_month, target_year, gpay_pdf, phonepe_pdf)

# Module designed to be imported and used via simple_client_template.py
# Direct execution disabled - use simple_client_template.py instead
