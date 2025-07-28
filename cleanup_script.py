#!/usr/bin/env python3
"""
WordPress to Static HTML Cleanup Script
Removes WordPress-specific elements from HTML files
"""

import os
import re
import glob
from pathlib import Path

def clean_html_content(content):
    """Remove WordPress-specific elements from HTML content"""
    
    # Remove WordPress meta tags
    wp_meta_patterns = [
        r'<link rel="profile"[^>]*>',
        r'<link rel="pingback"[^>]*>',
        r'<link rel="alternate"[^>]*rss[^>]*>',
        r'<link rel="https://api\.w\.org/"[^>]*>',
        r'<link rel="EditURI"[^>]*>',
        r'<meta name="generator"[^>]*WordPress[^>]*>',
        r'<meta name="generator"[^>]*WPBakery[^>]*>',
        r'<link rel="canonical"[^>]*>',
        r'<link rel="shortlink"[^>]*>',
    ]
    
    for pattern in wp_meta_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Remove WordPress emoji script and styles
    emoji_patterns = [
        r'<script[^>]*>.*?window\._wpemojiSettings.*?</script>',
        r'<style[^>]*wp-emoji[^>]*>.*?</style>',
    ]
    
    for pattern in emoji_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove WordPress CSS files (be selective)
    wp_css_patterns = [
        r'<link[^>]*wp-block-library[^>]*>',
        r'<link[^>]*mediaelement[^>]*>',
        r'<link[^>]*wp-mediaelement[^>]*>',
    ]
    
    for pattern in wp_css_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Remove recent comments CSS
    content = re.sub(r'<style[^>]*>\.recentcomments[^<]*</style>', '', content, flags=re.IGNORECASE)
    
    # Clean up multiple empty lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content

def process_html_files(directory):
    """Process all HTML files in the directory"""
    html_files = glob.glob(os.path.join(directory, '**/*.html'), recursive=True)
    
    processed_files = []
    
    for file_path in html_files:
        print(f"Processing: {file_path}")
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Clean the content
            cleaned_content = clean_html_content(original_content)
            
            # Only write if content changed
            if cleaned_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                processed_files.append(file_path)
                print(f"  ✓ Cleaned: {os.path.basename(file_path)}")
            else:
                print(f"  - No changes: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")
    
    return processed_files

def main():
    """Main cleanup function"""
    print("🧹 Starting WordPress cleanup...")
    print("=" * 50)
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Process HTML files
    processed = process_html_files(current_dir)
    
    print("=" * 50)
    print(f"✅ Cleanup complete!")
    print(f"📁 Processed {len(processed)} files")
    
    if processed:
        print("\n📝 Files modified:")
        for file_path in processed:
            print(f"  - {os.path.basename(file_path)}")

if __name__ == "__main__":
    main()
