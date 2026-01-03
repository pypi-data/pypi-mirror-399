import asyncio
import os

from zopassport import ZoPassportSDK

# Replace with your actual client key
CLIENT_KEY = os.environ.get("ZO_CLIENT_KEY", "YOUR_CLIENT_KEY")


async def main() -> None:
    sdk = ZoPassportSDK(client_key=CLIENT_KEY, debug=True)
    await sdk.initialize()

    if sdk.is_authenticated and sdk.user:
        print(f"✅ Already authenticated as: {sdk.user.first_name}")
    else:
        print("🔒 Not authenticated. Starting login flow...")
        country_code = input("Enter Country Code (e.g. 91): ")
        phone = input("Enter Phone Number: ")

        # Step 1: Send OTP
        print("Sending OTP...")
        otp_result = await sdk.auth.send_otp(country_code, phone)
        if otp_result["success"]:
            print(f"✅ OTP sent: {otp_result['message']}")
        else:
            print(f"❌ Failed to send OTP: {otp_result['message']}")
            await sdk.close()
            return

        # Step 2: Verify OTP
        otp = input("Enter OTP: ")
        login_result = await sdk.login_with_phone(country_code, phone, otp)

        if login_result["success"]:
            print(f"✅ Login successful! Welcome {login_result['user'].first_name}")
        else:
            print(f"❌ Login failed: {login_result['error']}")
            await sdk.close()
            return

    # Profile
    print("\nFetching latest profile...")
    token = await sdk.storage.get_item("zo_access_token")
    if token:
        profile = await sdk.profile.get_profile(token)
        if profile["success"]:
            print(f"👤 User: {profile['profile'].first_name} {profile['profile'].last_name}")
            print(f"   Bio: {profile['profile'].bio}")
    else:
        print("❌ No access token found")

    # Wallet
    print("\nFetching wallet balance...")
    balance = await sdk.wallet.get_balance()
    print(f"💰 Balance: {balance} $Zo")

    # Cleanup
    await sdk.close()


if __name__ == "__main__":
    asyncio.run(main())
