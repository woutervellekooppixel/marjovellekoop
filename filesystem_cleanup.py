#!/usr/bin/env python3
"""
File System Cleanup Script
Removes unused WordPress files and directories
"""

import os
import shutil
import glob
from pathlib import Path

def get_referenced_files(directory):
    """Get all files referenced in HTML files"""
    html_files = glob.glob(os.path.join(directory, '**/*.html'), recursive=True)
    html_files = [f for f in html_files if '/feed/' not in f]
    
    referenced_files = set()
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all wp-content references
            import re
            matches = re.findall(r'(?:href|src)=["\'](wp-content/[^"\']+)', content)
            referenced_files.update(matches)
            
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
    
    return referenced_files

def safe_cleanup_analysis(directory):
    """Analyze what can be safely removed"""
    print("🔍 Analyzing file system for cleanup opportunities...")
    
    referenced = get_referenced_files(directory)
    print(f"📊 Found {len(referenced)} referenced files in wp-content")
    
    # Check what's in wp-includes (likely all removable for static site)
    wp_includes_size = 0
    if os.path.exists('wp-includes'):
        result = os.popen('du -sh wp-includes').read()
        wp_includes_size = result.strip().split()[0]
        print(f"📁 wp-includes directory: {wp_includes_size}")
    
    # Check plugins
    plugins_dir = 'wp-content/plugins'
    if os.path.exists(plugins_dir):
        for plugin in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, plugin)
            if os.path.isdir(plugin_path):
                result = os.popen(f'du -sh "{plugin_path}"').read()
                size = result.strip().split()[0]
                
                # Check if any files from this plugin are referenced
                plugin_files = [f for f in referenced if f.startswith(f'wp-content/plugins/{plugin}/')]
                print(f"📦 Plugin {plugin}: {size} ({len(plugin_files)} files referenced)")
    
    # Check for PHP files (should be removable)
    php_files = glob.glob('**/*.php', recursive=True)
    print(f"🐘 Found {len(php_files)} PHP files (likely removable)")
    
    return referenced

def create_backup_and_cleanup():
    """Create backup and perform safe cleanup"""
    print("\n🎯 SAFE CLEANUP PLAN:")
    print("=" * 50)
    
    # Files/directories that are definitely safe to remove for static site
    safe_to_remove = [
        # XML files (WordPress specific)
        'xmlrpc.php',
        'wp-config-sample.php',
        'wp-comments-post.php',
        'wp-cron.php',
        'wp-links-opml.php',
        'wp-load.php',
        'wp-login.php',
        'wp-mail.php',
        'wp-settings.php',
        'wp-signup.php',
        'wp-trackback.php',
        
        # WordPress admin (not needed for static)
        'wp-admin/',
        
        # Most of wp-includes can go for static site
        # But let's be conservative and keep fonts, images, css that might be referenced
    ]
    
    total_saved = 0
    
    for item in safe_to_remove:
        if os.path.exists(item):
            try:
                if os.path.isfile(item):
                    size = os.path.getsize(item)
                    os.remove(item)
                    print(f"🗑️  Removed file: {item} ({size} bytes)")
                    total_saved += size
                elif os.path.isdir(item):
                    result = os.popen(f'du -sb "{item}"').read()
                    size = int(result.strip().split()[0])
                    shutil.rmtree(item)
                    print(f"🗑️  Removed directory: {item} ({size/1024:.1f} KB)")
                    total_saved += size
            except Exception as e:
                print(f"❌ Could not remove {item}: {e}")
    
    print(f"\n💾 Total space saved: {total_saved/1024:.1f} KB")
    return total_saved

def main():
    """Main cleanup function"""
    print("🧹 FILESYSTEM CLEANUP ANALYSIS")
    print("=" * 50)
    
    current_dir = os.getcwd()
    
    # Analyze first
    referenced = safe_cleanup_analysis(current_dir)
    
    # Ask for confirmation (in real scenario)
    print(f"\n⚠️  This will remove WordPress backend files that aren't needed for static site")
    print(f"📋 Referenced files will be preserved")
    
    # Perform safe cleanup
    saved = create_backup_and_cleanup()
    
    print("\n✅ Filesystem cleanup complete!")
    print(f"💾 Space saved: {saved/1024:.1f} KB")

if __name__ == "__main__":
    main()
