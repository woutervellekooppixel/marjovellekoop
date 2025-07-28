#!/usr/bin/env python3
"""
Advanced WordPress Cleanup Script
More aggressive cleanup of WordPress elements
"""

import os
import re
import glob
import shutil
from pathlib import Path

def advanced_clean_html_content(content):
    """More aggressive cleanup of WordPress elements"""
    
    # Remove more WordPress and plugin CSS/JS
    patterns_to_remove = [
        # Plugin CSS/JS that might not be needed
        r'<link[^>]*bridge-core[^>]*>',
        r'<link[^>]*tablepress[^>]*>',
        
        # Many jQuery UI components that are likely unused
        r'<script[^>]*jquery/ui/accordion[^>]*>',
        r'<script[^>]*jquery/ui/autocomplete[^>]*>',
        r'<script[^>]*jquery/ui/button[^>]*>',
        r'<script[^>]*jquery/ui/controlgroup[^>]*>',
        r'<script[^>]*jquery/ui/checkboxradio[^>]*>',
        r'<script[^>]*jquery/ui/datepicker[^>]*>',
        r'<script[^>]*jquery/ui/dialog[^>]*>',
        r'<script[^>]*jquery/ui/draggable[^>]*>',
        r'<script[^>]*jquery/ui/droppable[^>]*>',
        r'<script[^>]*jquery/ui/effect[^>]*>',
        r'<script[^>]*jquery/ui/menu[^>]*>',
        r'<script[^>]*jquery/ui/mouse[^>]*>',
        r'<script[^>]*jquery/ui/progressbar[^>]*>',
        r'<script[^>]*jquery/ui/resizable[^>]*>',
        r'<script[^>]*jquery/ui/selectable[^>]*>',
        r'<script[^>]*jquery/ui/slider[^>]*>',
        r'<script[^>]*jquery/ui/sortable[^>]*>',
        r'<script[^>]*jquery/ui/spinner[^>]*>',
        r'<script[^>]*jquery/ui/tabs[^>]*>',
        r'<script[^>]*jquery/ui/tooltip[^>]*>',
        
        # WordPress dist files that are likely unused
        r'<script[^>]*wp-includes/js/dist/hooks[^>]*>',
        r'<script[^>]*wp-includes/js/dist/i18n[^>]*>',
        r'<script[^>]*wp-includes/js/dist/dom-ready[^>]*>',
        r'<script[^>]*wp-includes/js/dist/a11y[^>]*>',
        
        # Comment reply (if no comments are used)
        r'<script[^>]*comment-reply[^>]*>',
        
        # Media element (if no media is used)
        r'<script[^>]*mediaelement[^>]*>',
        r'<script[^>]*wp-mediaelement[^>]*>',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Clean up multiple empty lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content

def clean_body_classes(content):
    """Clean up WordPress body classes"""
    # Remove WordPress-specific body classes
    wp_body_classes = [
        r'wp-singular',
        r'page-template[^"]*',
        r'page-id-\d+',
        r'wp-theme-bridge',
        r'bridge-core[^"]*',
        r'qode[^"]*',
        r'wpb-js-composer',
        r'js-comp-ver[^"]*',
        r'vc_responsive',
    ]
    
    for class_pattern in wp_body_classes:
        content = re.sub(rf'\s+{class_pattern}', '', content)
        content = re.sub(rf'{class_pattern}\s+', '', content)
    
    return content

def process_html_files_advanced(directory):
    """Advanced processing of HTML files"""
    html_files = glob.glob(os.path.join(directory, '**/*.html'), recursive=True)
    
    # Skip feed files
    html_files = [f for f in html_files if '/feed/' not in f]
    
    processed_files = []
    
    for file_path in html_files:
        print(f"Advanced cleaning: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Apply advanced cleaning
            cleaned_content = advanced_clean_html_content(original_content)
            cleaned_content = clean_body_classes(cleaned_content)
            
            if cleaned_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                processed_files.append(file_path)
                print(f"  ✓ Advanced cleaned: {os.path.basename(file_path)}")
            else:
                print(f"  - No additional changes: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    return processed_files

def analyze_file_usage(directory):
    """Analyze which files are actually referenced"""
    print("\n🔍 Analyzing file usage...")
    
    html_files = glob.glob(os.path.join(directory, '**/*.html'), recursive=True)
    html_files = [f for f in html_files if '/feed/' not in f]
    
    referenced_files = set()
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all href and src references
        href_matches = re.findall(r'(?:href|src)=["\'](wp-content/[^"\']+)', content)
        referenced_files.update(href_matches)
    
    print(f"📊 Found {len(referenced_files)} referenced files")
    return referenced_files

def main():
    """Main advanced cleanup function"""
    print("🧹 Starting ADVANCED WordPress cleanup...")
    print("=" * 60)
    
    current_dir = os.getcwd()
    
    # Advanced HTML cleaning
    processed = process_html_files_advanced(current_dir)
    
    # Analyze usage
    referenced = analyze_file_usage(current_dir)
    
    print("=" * 60)
    print(f"✅ Advanced cleanup complete!")
    print(f"📁 Processed {len(processed)} files")
    print(f"📊 {len(referenced)} files are still referenced")

if __name__ == "__main__":
    main()
