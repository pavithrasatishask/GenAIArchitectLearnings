#!/usr/bin/env python3
"""
Simple Client Template - Option 1 (Direct Function Call)

This is the easiest way for clients to use the Spendee automation.
Just update the parameters below and run!
"""

from spendeeMonthlyUpdate import run_automation

# 🔧 CLIENT SETUP - UPDATE THESE VALUES
def run_my_automation():
    """
    Run Spendee automation with your specific details
    """
    
    # ✏️ UPDATE THESE VALUES:
    MY_EMAIL = "your.email@example.com"              # Your Spendee login email
    MY_PASSWORD = "your_secure_password"             # Your Spendee password
    TARGET_MONTH = 10                                # Month to process (1-12)
    TARGET_YEAR = 2025                               # Year to process
    GPAY_PDF = "GPayExpenses.pdf"                   # Path to your GPay PDF
    PHONEPE_PDF = "PhonePeExpenses.pdf"             # Path to your PhonePe PDF
    
    print("🚀 Starting Spendee Automation")
    print("=" * 50)
    print(f"📧 Email: {MY_EMAIL}")
    print(f"📅 Target: {TARGET_MONTH:02d}/{TARGET_YEAR}")
    print(f"📄 GPay PDF: {GPAY_PDF}")
    print(f"📄 PhonePe PDF: {PHONEPE_PDF}")
    print("=" * 50)
    
    # Run the automation
    run_automation(
        email=MY_EMAIL,
        password=MY_PASSWORD,
        target_month=TARGET_MONTH,
        target_year=TARGET_YEAR,
        gpay_pdf=GPAY_PDF,
        phonepe_pdf=PHONEPE_PDF
    )
    
    print("🎉 Automation completed!")

if __name__ == "__main__":
    # Safety check
    if "your.email@example.com" in str(run_my_automation.__code__.co_consts):
        print("🛑 Please update your email and password in the function above!")
        print("   Look for the '# ✏️ UPDATE THESE VALUES:' section")
        print("   Update MY_EMAIL and MY_PASSWORD with your actual credentials")
    else:
        run_my_automation()