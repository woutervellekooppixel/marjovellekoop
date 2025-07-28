#!/usr/bin/env python3
"""
Remove PHP callback references from all HTML files
"""

import os
import re
import glob

def fix_php_references():
    """Remove references to deleted PHP callback files"""
    print("🔧 FIXING PHP CALLBACK REFERENCES")
    print("=" * 50)
    
    # Find all HTML files (excluding feed files)
    html_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html') and '/feed/' not in root:
                html_files.append(os.path.join(root, file))
    
    for html_file in html_files:
        print(f"📄 Processing: {html_file}")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove the PHP callback CSS links
            content = re.sub(
                r'<link rel="stylesheet" id="bridge-style-dynamic-css" href="[^"]*style_dynamic_callback\.php[^"]*" type="text/css" media="all">\s*',
                '',
                content
            )
            
            content = re.sub(
                r'<link rel="stylesheet" id="bridge-style-dynamic-responsive-css" href="[^"]*style_dynamic_responsive_callback\.php[^"]*" type="text/css" media="all">\s*',
                '',
                content
            )
            
            # Also remove any JS callback references if they exist
            content = re.sub(
                r'<script[^>]*src="[^"]*default_dynamic_callback\.php[^"]*"[^>]*></script>\s*',
                '',
                content
            )
            
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed PHP references in {html_file}")
            else:
                print(f"ℹ️  No PHP references found in {html_file}")
                
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")

def main():
    fix_php_references()
    print(f"\n✅ PHP CALLBACK CLEANUP COMPLETE!")
    print(f"🚀 All HTML files should now work without PHP dependencies")

if __name__ == "__main__":
    main()
