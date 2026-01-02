import requests
from typing import Dict, List, Tuple
from .platforms import Platforms

def check_username(username: str) -> Tuple[Dict[str, str], List[str]]:
    """
    Check if a username exists on various platforms.
    
    Args:
        username: The username to check
        
    Returns:
        Tuple containing (found_platforms, error_platforms)
    """
    print(f"\n[+] Checking username: {username}\n")
    
    found_platforms = {}
    error_platforms = []
    total_checked = 0
    
    for platform_name, url_template in Platforms.items():
        profile_url = url_template.format(username)
        total_checked += 1
        
        try:
            response = requests.get(
                profile_url, 
                timeout=5,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # Check if the profile exists
            if response.status_code == 200:
                # Some platforms return 200 even for non-existent profiles
                # We can add platform-specific checks if needed
                print(f"[✓ FOUND] {platform_name}: {profile_url}")
                found_platforms[platform_name] = profile_url
            else:
                print(f"[✗ NOT FOUND] {platform_name}")
                
        except requests.exceptions.Timeout:
            print(f"[⌛ TIMEOUT] {platform_name}")
            error_platforms.append(f"{platform_name} (timeout)")
        except requests.exceptions.ConnectionError:
            print(f"[🔌 CONNECTION ERROR] {platform_name}")
            error_platforms.append(f"{platform_name} (connection)")
        except requests.exceptions.RequestException as e:
            print(f"[⚠ ERROR] {platform_name}: {type(e).__name__}")
            error_platforms.append(f"{platform_name} ({type(e).__name__})")
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"[+] SUMMARY:")
    print(f"   • Total platforms checked: {total_checked}")
    print(f"   • Found on: {len(found_platforms)} platforms")
    print(f"   • Errors: {len(error_platforms)} platforms")
    
    if found_platforms:
        print(f"\n[+] Found profiles:")
        for platform, url in found_platforms.items():
            print(f"   • {platform}: {url}")
    
    if error_platforms:
        print(f"\n[!] Platforms with errors:")
        for error in error_platforms:
            print(f"   • {error}")
    
    return found_platforms, error_platforms

    


def main():
    
    print("Userrecon")
    print("=" * 50)
    
    while True:
        username = input("\nEnter username to check (or 'quit' to exit): ").strip()
        
        if username.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if username:
            check_username(username)
        else:
            print("[!] Please enter a valid username")

if __name__ == "__main__":
    main()
