"""
Fragment API Test Application - EASY MODE 🚀

This demonstrates the simplified one-call API.
Compare with app.py to see how much simpler it is!
"""

import asyncio
from afragment import (
    AsyncFragmentClient,
    FragmentAPIError,
    AuthenticationError,
    InvalidRecipientError,
    nano_to_ton,
    extract_ref_id,
    extract_transaction_text,
    format_transaction_comment,
)

# ============================================
# YOUR CREDENTIALS
# ============================================
FRAGMENT_HASH = "058607f449e6b366f5"
FRAGMENT_COOKIE = "stel_ssid=356fcbc0bc5f534084_1169402249720117667; stel_dt=480; stel_token=73676e56735445e81a379cafdf21b95573676e4c736761b28c26a9d636da5858ea959; stel_ton_token=9rNB6BN76bmiae7ZeTpLVpf9HEaziOFyDVcokkFRiFqcdnvdOdQvP8VqAdVNySfBWnUPTqVfO1s-9NHNjw22MzmP_Ytv0s1N-7VFJh0ljhh3qQKYyBZvY25gEQweK9kWFD1SpdFBX9z8Ya1ovrCFJS9M29ZVy18nUA80br2SWK9vCIVq34Vc6WBhuAMAg-s8n8oDnhpY"
WALLET_ADDRESS = "UQBb8vnBJTfSNa9mvxRfpcWEqD4lPV6ICVbYbsBbeUjPUySP"
# ============================================


async def buy_stars_easy(username: str, quantity: int):
    """Purchase Telegram Stars - ONE CALL! 🌟"""
    print(f"\n{'='*50}")
    print(f"🌟 Buying {quantity} Stars for @{username}")
    print('='*50)

    async with AsyncFragmentClient(FRAGMENT_HASH, FRAGMENT_COOKIE) as client:
        # Just ONE call - that's it!
        result = await client.buy_stars(username, quantity, WALLET_ADDRESS)
        
        print_result(result, "stars", quantity=quantity)
        return result


async def gift_premium_easy(username: str, months: int):
    """Gift Telegram Premium - ONE CALL! ⭐"""
    print(f"\n{'='*50}")
    print(f"⭐ Gifting {months} months Premium to @{username}")
    print('='*50)

    async with AsyncFragmentClient(FRAGMENT_HASH, FRAGMENT_COOKIE) as client:
        # Just ONE call - that's it!
        result = await client.buy_premium(username, months, WALLET_ADDRESS)
        
        print_result(result, "premium", months=months)
        return result


async def topup_ton_easy(username: str, amount: int):
    """Topup TON balance - ONE CALL! 💎"""
    print(f"\n{'='*50}")
    print(f"💎 Topping up {amount} TON for @{username}")
    print('='*50)

    async with AsyncFragmentClient(FRAGMENT_HASH, FRAGMENT_COOKIE) as client:
        # Just ONE call - that's it!
        result = await client.buy_ton_topup(username, amount, WALLET_ADDRESS)
        
        print_result(result, "topup")
        return result


def print_result(result: dict, tx_type: str, **kwargs):
    """Print transaction details in a nice format."""
    print(f"\n✅ Success!")
    print(f"   Recipient: {result['recipient']['name']}")
    
    if result.get("amount"):
        print(f"   Price: {result['amount']} TON")
    
    tx = result["transaction"]
    if tx and tx.get("messages"):
        msg = tx["messages"][0]
        address = msg["address"]
        amount_nano = int(msg["amount"])
        payload = msg["payload"]
        
        # Extract polished comment from payload
        comment = extract_transaction_text(payload, tx_type, **kwargs)
        if not comment:
            ref_id = extract_ref_id(payload)
            comment = format_transaction_comment(tx_type, ref_id=ref_id, **kwargs)
        
        ref_id = extract_ref_id(payload)
        
        print(f"\n📤 Transaction Details:")
        print(f"   Send to:  {address}")
        print(f"   Amount:   {nano_to_ton(amount_nano)} TON ({amount_nano} nanoTON)")
        print(f"   Comment:  {comment.replace(chr(10), ' ')}")
        if ref_id:
            print(f"   Ref ID:   {ref_id}")


async def main():
    """Main entry point with interactive menu."""
    
    if not FRAGMENT_HASH or not FRAGMENT_COOKIE:
        print("\n❌ Please fill in your credentials in app_easy.py!")
        return

    print("\n" + "="*50)
    print("   Fragment API - EASY MODE 🚀")
    print("="*50)
    print("\nSelect an action:")
    print("  1. 🌟 Buy Telegram Stars")
    print("  2. ⭐ Gift Telegram Premium")
    print("  3. 💎 TON Balance Topup")
    print("  0. Exit")

    choice = input("\nYour choice: ").strip()

    try:
        if choice == "1":
            username = input("Username (without @): ").strip()
            quantity = int(input("Quantity of Stars (min 50): ").strip())
            await buy_stars_easy(username, quantity)

        elif choice == "2":
            username = input("Username (without @): ").strip()
            print("Duration options: 3, 6, or 12 months")
            months = int(input("Months: ").strip())
            await gift_premium_easy(username, months)

        elif choice == "3":
            username = input("Username (without @): ").strip()
            amount = int(input("Amount in TON (min 1): ").strip())
            await topup_ton_easy(username, amount)

        elif choice == "0":
            print("Goodbye! 👋")
            return

        else:
            print("Invalid choice!")

    except InvalidRecipientError as e:
        print(f"\n❌ User not found: {e}")
    except AuthenticationError as e:
        print(f"\n❌ Auth failed: {e}")
    except FragmentAPIError as e:
        print(f"\n❌ API Error: {e}")
    except ValueError as e:
        print(f"\n❌ Input Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n" + "="*50)
    print("Done! ✨")


if __name__ == "__main__":
    asyncio.run(main())
