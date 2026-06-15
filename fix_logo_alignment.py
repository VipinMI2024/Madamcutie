import os
import re

def update_css():
    css_path = 'css/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # Revert to left-aligned logo by default
    css = css.replace(
        '.nav-container {\n    height: 100%;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    position: relative;\n}',
        '.nav-container {\n    height: 100%;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n}'
    )
    
    css = css.replace(
        '.logo-wrapper {\n    display: flex;\n    align-items: center;\n    gap: var(--spacing-sm);\n    position: absolute;\n    left: 50%;\n    transform: translateX(-50%);\n}',
        '.logo-wrapper {\n    display: flex;\n    align-items: center;\n    gap: var(--spacing-sm);\n}'
    )
    
    # Add media query to center logo on mobile
    mobile_logo_css = """
@media (max-width: 900px) {
    .nav-container {
        position: relative;
    }
    .logo-wrapper {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }
}
"""
    if '@media (max-width: 900px) {\n    .nav-container {' not in css:
        css += mobile_logo_css
        
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)

def update_html():
    for filename in os.listdir('.'):
        if not filename.endswith('.html'):
            continue
            
        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()
            
        # Remove inline styles that center the logo
        html = html.replace('class="container nav-container" style="position: relative;"', 'class="container nav-container"')
        html = html.replace('class="logo-wrapper" style="position: absolute; left: 50%; transform: translateX(-50%);"', 'class="logo-wrapper"')
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

def git_commit():
    os.system('git add .')
    os.system('git commit -m "Fix logo alignment to left on desktop and center on mobile"')
    os.system('git push')

update_css()
update_html()
git_commit()
print("Done updating logo alignment and committing.")
