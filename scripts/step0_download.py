import os
import urllib.request
import ssl

def main():
    print("Starting Step 0: Downloading Real Swiggy Dataset")
    
    os.makedirs('data/raw', exist_ok=True)
    
    swiggy_url = "https://raw.githubusercontent.com/shwetbhole/Swiggy-Restaurant-Data---India/main/swiggy_all_menus_india.csv"
    swiggy_path = 'data/raw/swiggy_dataset.csv'
    
    context = ssl._create_unverified_context()
    
    try:
        print(f"Downloading {swiggy_url}...")
        with urllib.request.urlopen(swiggy_url, context=context) as response, open(swiggy_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully downloaded to {swiggy_path} (Size: {len(data)/1024/1024:.2f} MB)")
    except Exception as e:
        print(f"Error downloading Swiggy data: {e}")

if __name__ == "__main__":
    main()
