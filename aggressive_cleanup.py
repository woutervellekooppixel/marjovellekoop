#!/usr/bin/env python3
"""
Aggressive WordPress Cleanup Script
Removes unused plugins and WordPress infrastructure
"""

import os
import shutil
import glob
from pathlib import Path

def aggressive_cleanup():
    """Remove unused WordPress components aggressively"""
    print("🧹 AGGRESSIVE WORDPRESS CLEANUP")
    print("=" * 50)
    
    total_saved = 0
    
    # Remove unused plugins completely
    unused_plugins = [
        'wp-content/plugins/tablepress',
        'wp-content/plugins/bridge-core'
    ]
    
    for plugin in unused_plugins:
        if os.path.exists(plugin):
            try:
                result = os.popen(f'du -sb "{plugin}"').read()
                size = int(result.strip().split()[0])
                shutil.rmtree(plugin)
                print(f"🗑️  Removed unused plugin: {plugin} ({size/1024:.1f} KB)")
                total_saved += size
            except Exception as e:
                print(f"❌ Could not remove {plugin}: {e}")
    
    # Remove PHP callback files (not needed for static site)
    php_files = [
        'wp-content/themes/bridge/css/style_dynamic_callback.php',
        'wp-content/themes/bridge/css/style_dynamic_responsive_callback.php',
        'wp-content/themes/bridge/js/default_dynamic_callback.php'
    ]
    
    for php_file in php_files:
        if os.path.exists(php_file):
            try:
                size = os.path.getsize(php_file)
                os.remove(php_file)
                print(f"🗑️  Removed PHP file: {php_file} ({size} bytes)")
                total_saved += size
            except Exception as e:
                print(f"❌ Could not remove {php_file}: {e}")
    
    # Remove wp-includes (most of it is not needed for static site)
    if os.path.exists('wp-includes'):
        try:
            result = os.popen('du -sb wp-includes').read()
            size = int(result.strip().split()[0])
            shutil.rmtree('wp-includes')
            print(f"🗑️  Removed wp-includes directory: ({size/1024:.1f} KB)")
            total_saved += size
        except Exception as e:
            print(f"❌ Could not remove wp-includes: {e}")
    
    # Check for .DS_Store files and remove them
    ds_store_files = glob.glob('**/.DS_Store', recursive=True)
    for ds_file in ds_store_files:
        try:
            size = os.path.getsize(ds_file)
            os.remove(ds_file)
            print(f"🗑️  Removed .DS_Store: {ds_file}")
            total_saved += size
        except Exception as e:
            print(f"❌ Could not remove {ds_file}: {e}")
    
    return total_saved

def clean_js_composer():
    """Clean up js_composer plugin - keep only essential files"""
    print("\n🎨 CLEANING JS_COMPOSER PLUGIN")
    print("=" * 40)
    
    js_composer_path = 'wp-content/plugins/js_composer'
    if not os.path.exists(js_composer_path):
        print("❌ js_composer not found")
        return 0
    
    # Keep only essential CSS and JS files that are actually referenced
    essential_files = [
        'assets/css/js_composer.min.css',
        'assets/js/dist/js_composer_front.min.js'
    ]
    
    total_saved = 0
    
    # Get current size
    result = os.popen(f'du -sb "{js_composer_path}"').read()
    original_size = int(result.strip().split()[0])
    
    # Remove everything except essential files
    for root, dirs, files in os.walk(js_composer_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, js_composer_path)
            
            if relative_path not in essential_files:
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    total_saved += size
                except Exception as e:
                    pass
    
    # Remove empty directories
    for root, dirs, files in os.walk(js_composer_path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                if not os.listdir(dir_path):  # if directory is empty
                    os.rmdir(dir_path)
            except Exception as e:
                pass
    
    print(f"📦 js_composer: reduced by {total_saved/1024:.1f} KB")
    return total_saved

def main():
    """Main cleanup function"""
    print("🔥 AGGRESSIVE WORDPRESS CLEANUP")
    print("=" * 50)
    
    # First do the aggressive cleanup
    saved1 = aggressive_cleanup()
    
    # Then clean js_composer
    saved2 = clean_js_composer()
    
    total_saved = saved1 + saved2
    
    print(f"\n✅ CLEANUP COMPLETE!")
    print(f"💾 Total space saved: {total_saved/1024:.1f} KB ({total_saved/1024/1024:.1f} MB)")
    
    # Show remaining structure
    print(f"\n📁 REMAINING STRUCTURE:")
    os.system('find wp-content -type d | head -20')

if __name__ == "__main__":
    main()
