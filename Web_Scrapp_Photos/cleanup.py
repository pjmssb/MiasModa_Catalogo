import os

# Change to the script directory
os.chdir(r'C:\Users\pjmss\Documents\PM_CTO-Proyectos\MiasModa_Catalogo\Web_Scrapp_Photos')

files_to_delete = [
    'analyze_sample.py',
    'array_1.json',
    'array_2.json',
    'debug_final.py',
    'debug_page.html',
    'debug_scraper.py',
    'extract_json.py',
    'first_page_debug.html',
    'match_6_1.txt',
    'miasmoda_scraper.py',
    'miasmoda_scraper_final.py',
    'miasmoda_scraper_fixed.py',
    'miasmoda_scraper_v2.py',
    'miasmoda_scraper_working.py',
    'script_22.js',
    'test_json_structure.py'
]

for file in files_to_delete:
    try:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted: {file}")
        else:
            print(f"File not found: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")

print("\nCleanup completed!")
print("Remaining files:")
for item in os.listdir('.'):
    if os.path.isfile(item):
        print(f"  {item}")
