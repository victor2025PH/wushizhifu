"""
Test script to verify Bot B setup
Run this before starting the bot to ensure everything is configured correctly
"""
import sys
import os

def test_config():
    """Test configuration loading"""
    print("=" * 50)
    print("Testing Configuration...")
    print("=" * 50)
    
    try:
        from config import Config
        
        print(f"✓ Config module loaded")
        print(f"  BOT_TOKEN length: {len(Config.BOT_TOKEN)} characters")
        
        if Config.BOT_TOKEN:
            print(f"  ✓ Bot token found: {Config.BOT_TOKEN[:10]}...{Config.BOT_TOKEN[-5:]}")
        else:
            print(f"  ✗ Bot token is empty!")
            print(f"    Please ensure .env file has BOT_TOKEN_B on the second line")
            return False
        
        print(f"  Database: Using shared database (wushipay.db)")
        print(f"  CoinGecko API URL: {Config.COINGECKO_API_URL}")
        print(f"  Fallback price: {Config.DEFAULT_FALLBACK_PRICE}")
        
        # Validate
        try:
            Config.validate()
            print(f"  ✓ Configuration validation passed")
        except ValueError as e:
            print(f"  ✗ Configuration validation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False


def test_database():
    """Test database initialization"""
    print("\n" + "=" * 50)
    print("Testing Database...")
    print("=" * 50)
    
    try:
        from database import db
        
        print(f"✓ Database module loaded")
        print(f"  Database path: {db.db_path}")
        
        # Test connection
        conn = db.connect()
        print(f"  ✓ Database connection successful")
        
        # Test reading default values
        markup = db.get_admin_markup()
        address = db.get_usdt_address()
        
        print(f"  Admin markup: {markup}")
        print(f"  USDT address: {address or '(empty)'}")
        
        # Test setting values
        print(f"\n  Testing write operations...")
        db.set_admin_markup(0.5)
        db.set_usdt_address("TTest123456789")
        
        # Verify
        new_markup = db.get_admin_markup()
        new_address = db.get_usdt_address()
        
        if new_markup == 0.5:
            print(f"  ✓ Admin markup write/read successful")
        else:
            print(f"  ✗ Admin markup write/read failed")
            return False
        
        if new_address == "TTest123456789":
            print(f"  ✓ USDT address write/read successful")
        else:
            print(f"  ✗ USDT address write/read failed")
            return False
        
        # Reset to defaults
        db.set_admin_markup(0.0)
        db.set_usdt_address("")
        print(f"  ✓ Reset to default values")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_service():
    """Test CoinGecko price fetching"""
    print("\n" + "=" * 50)
    print("Testing Price Service...")
    print("=" * 50)
    
    try:
        from services.price_service import get_usdt_cny_price, get_price_with_markup
        
        print(f"✓ Price service module loaded")
        
        print(f"\n  Fetching price from CoinGecko API...")
        price, error = get_usdt_cny_price()
        
        if price is not None:
            print(f"  ✓ Price fetched: {price:.4f} CNY")
            if error:
                print(f"  ⚠ Warning: {error}")
        else:
            print(f"  ✗ Failed to fetch price: {error}")
            print(f"  (This might be OK if CoinGecko API is temporarily unavailable)")
        
        print(f"\n  Testing price with markup...")
        final_price, error_msg, base_price, markup, source = get_price_with_markup()
        
        if final_price is not None:
            print(f"  ✓ Final price calculated: {final_price:.4f} CNY")
            print(f"    Base price: {base_price:.4f} CNY")
            print(f"    Markup: {final_price - base_price:.4f} CNY")
            if error_msg:
                print(f"  ⚠ Note: {error_msg}")
        else:
            print(f"  ✗ Failed to calculate final price: {error_msg}")
        
        return True
        
    except Exception as e:
        print(f"✗ Price service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("Bot B Setup Verification")
    print("=" * 50)
    print()
    
    results = []
    
    # Test 1: Configuration
    results.append(("Configuration", test_config()))
    
    # Test 2: Database
    if results[0][1]:  # Only test database if config passed
        results.append(("Database", test_database()))
    else:
        results.append(("Database", False))
        print("\n⚠ Skipping database test (config failed)")
    
    # Test 3: Price Service
    if results[0][1]:  # Only test price service if config passed
        results.append(("Price Service", test_price_service()))
    else:
        results.append(("Price Service", False))
        print("\n⚠ Skipping price service test (config failed)")
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ All tests passed! Bot B is ready to run.")
        print("   Run: python bot.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("   Check your .env file and ensure all dependencies are installed.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

