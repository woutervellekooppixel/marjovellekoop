#!/usr/bin/env python3
"""
Verify all essential files are present for Vercel deployment
"""

import os
import glob

def verify_essential_files():
    """Check that all essential files are present"""
    print("🔍 VERIFYING ESSENTIAL FILES FOR VERCEL DEPLOYMENT")
    print("=" * 60)
    
    # Essential JavaScript files
    js_files = [
        'wp-includes/js/jquery/jquery.min.js',
        'wp-includes/js/jquery/jquery-migrate.min.js', 
        'wp-includes/js/jquery/ui/core.min.js',
        'wp-includes/js/hoverIntent.min.js',
        'wp-includes/js/jquery/jquery.form.min.js',
        'wp-content/themes/bridge/js/default.min.js',
        'wp-content/plugins/js_composer/assets/js/dist/js_composer_front.min.js'
    ]
    
    # Essential CSS files
    css_files = [
        'wp-content/themes/bridge/style.css',
        'wp-content/themes/bridge/css/stylesheet.min.css',
        'wp-content/themes/bridge/css/responsive.min.css',
        'wp-content/plugins/js_composer/assets/css/js_composer.min.css'
    ]
    
    # Essential images
    image_files = [
        'wp-content/uploads/2018/06/favi.png',
        'wp-content/uploads/2018/06/marjo-vellekoop-logo.png',
        'wp-content/uploads/2018/06/sebastian-pichler-20071-unsplash.jpg',
        'wp-content/uploads/2018/06/30.png'
    ]
    
    # HTML files
    html_files = [
        'index.html',
        'begeleiding/index.html',
        'werkwijze/index.html', 
        'contact/index.html',
        'marjo-vellekoop/index.html',
        'algemene-voorwaarden/index.html'
    ]
    
    all_good = True
    
    print("📄 CHECKING HTML FILES:")
    for file in html_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ MISSING: {file}")
            all_good = False
    
    print(f"\n⚡ CHECKING JAVASCRIPT FILES:")
    for file in js_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size/1024:.1f} KB)")
        else:
            print(f"❌ MISSING: {file}")
            all_good = False
    
    print(f"\n🎨 CHECKING CSS FILES:")
    for file in css_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size/1024:.1f} KB)")
        else:
            print(f"❌ MISSING: {file}")
            all_good = False
    
    print(f"\n🖼️  CHECKING ESSENTIAL IMAGES:")
    for file in image_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size/1024:.1f} KB)")
        else:
            print(f"❌ MISSING: {file}")
            all_good = False
    
    # Check for any broken links in HTML
    print(f"\n🔗 CHECKING FOR POTENTIAL 404 ISSUES:")
    
    # Check for remaining wp-includes references that might be missing
    for html_file in html_files:
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for wp-includes references
            import re
            wp_includes_refs = re.findall(r'(?:src|href)=["\']([^"\']*wp-includes/[^"\']*)["\']', content)
            
            for ref in wp_includes_refs:
                if not os.path.exists(ref):
                    print(f"⚠️  {html_file} references missing file: {ref}")
                    all_good = False
    
    print(f"\n📊 DEPLOYMENT READINESS:")
    if all_good:
        print("🎉 ALL ESSENTIAL FILES PRESENT!")
        print("✅ Website is ready for Vercel deployment")
        print("🚀 Header images should now work correctly")
    else:
        print("❌ Some files are missing - deployment may have issues")
    
    return all_good

def main():
    verify_essential_files()

if __name__ == "__main__":
    main()
