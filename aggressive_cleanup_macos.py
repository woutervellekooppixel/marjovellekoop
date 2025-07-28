#!/usr/bin/env python3
"""
Aggressive WordPress Cleanup Script - macOS compatible
Removes unused plugins and WordPress infrastructure
"""

import os
import shutil
import glob
from pathlib import Path

def get_directory_size(path):
    """Get directory size in bytes - macOS compatible"""
    try:
        result = os.popen(f'du -s "{path}"').read()
        if result.strip():
            # du -s returns size in 512-byte blocks on macOS
            blocks = int(result.strip().split()[0])
            return blocks * 512
        return 0
    except:
        return 0

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
                size = get_directory_size(plugin)
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
            size = get_directory_size('wp-includes')
            shutil.rmtree('wp-includes')
            print(f"🗑️  Removed wp-includes directory: ({size/1024:.1f} KB)")
            total_saved += size
        except Exception as e:
            print(f"❌ Could not remove wp-includes: {e}")
    
    # Check for .DS_Store files and remove them
    ds_store_files = glob.glob('**/.DS_Store', recursive=True)
    for ds_file in ds_store_files:
        try:
            if os.path.exists(ds_file):
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
    original_size = get_directory_size(js_composer_path)
    print(f"📦 js_composer original size: {original_size/1024:.1f} KB")
    
    # List what we're keeping vs removing
    kept_files = []
    removed_files = []
    
    for root, dirs, files in os.walk(js_composer_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, js_composer_path)
            
            if relative_path in essential_files:
                kept_files.append(relative_path)
            else:
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    removed_files.append(relative_path)
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
    
    print(f"✅ Kept {len(kept_files)} essential files")
    print(f"🗑️  Removed {len(removed_files)} unnecessary files")
    print(f"💾 Saved: {total_saved/1024:.1f} KB from js_composer")
    
    return total_saved

def show_final_structure():
    """Show the cleaned up structure"""
    print(f"\n📁 FINAL STRUCTURE:")
    print("=" * 30)
    
    if os.path.exists('wp-content'):
        print("wp-content/")
        for root, dirs, files in os.walk('wp-content'):
            level = root.replace('wp-content', '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show max 5 files per directory
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files)-5} more files")

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
    
    # Show final structure
    show_final_structure()

if __name__ == "__main__":
    main()
