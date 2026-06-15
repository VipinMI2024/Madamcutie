import re
import os

def update_css():
    css_path = 'css/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # Change mobile grid to 2 columns
    css = re.sub(
        r'@media \(max-width: 600px\) \{\s*\.grid-2, \.grid-3, \.grid-4 \{ grid-template-columns: 1fr; \}\s*\}',
        '@media (max-width: 600px) {\n    .grid-2, .grid-3, .grid-4 { grid-template-columns: repeat(2, 1fr); gap: 10px; }\n}',
        css
    )
    
    # Update header layout to center logo
    if '.nav-container {\n    height: 100%;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n}' in css:
        css = css.replace('.nav-container {\n    height: 100%;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n}', 
        '.nav-container {\n    height: 100%;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    position: relative;\n}')
        
    if '.logo-wrapper {\n    display: flex;\n    align-items: center;\n    gap: var(--spacing-sm);\n}' in css:
        css = css.replace('.logo-wrapper {\n    display: flex;\n    align-items: center;\n    gap: var(--spacing-sm);\n}',
        '.logo-wrapper {\n    display: flex;\n    align-items: center;\n    gap: var(--spacing-sm);\n    position: absolute;\n    left: 50%;\n    transform: translateX(-50%);\n}')
        
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)

def update_html_files():
    for filename in ['shop.html', 'index.html']:
        if not os.path.exists(filename):
            continue
            
        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()
            
        # Add buttons
        # We need to find the <a href="product.html"> enclosing the img.
        add_btn_str = """
                        <button class="add-to-cart-btn" style="position: absolute; bottom: 10px; right: 10px; background: white; border: 1.5px solid #ff007f; color: #ff007f; border-radius: 4px; padding: 4px 15px; font-weight: bold; font-size: 0.85rem; z-index: 3; cursor: pointer;">ADD</button>
                        <div class="love-icon" style="position: absolute; top: 10px; right: 10px; z-index: 3; cursor: pointer;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff007f" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                        </div>
                        <a href="product.html"
"""
        html = re.sub(r'<a href="product.html"[^>]*><img', add_btn_str.strip() + r'><img', html)
        
        # Add custom logic script
        if 'custom-cart-logic' not in html:
            script_html = """
            <script id="custom-cart-logic">
            document.addEventListener('DOMContentLoaded', () => {
                let cart = JSON.parse(localStorage.getItem('madamCart')) || [];
                const cartCountEl = document.querySelector('.cart-count');
                
                function updateCartCount() {
                    if(cartCountEl) cartCountEl.textContent = cart.length;
                }
                updateCartCount();
                
                document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        const card = btn.closest('.madam-card');
                        const titleEl = card.querySelector('h3 a');
                        const priceEl = card.querySelector('span[style*="font-weight: 600"]');
                        const imgEl = card.querySelector('img');
                        
                        const item = {
                            title: titleEl ? titleEl.textContent : 'Dress',
                            price: priceEl ? parseInt(priceEl.textContent.replace(/\D/g,'')) : 0,
                            img: imgEl ? imgEl.src : ''
                        };
                        cart.push(item);
                        localStorage.setItem('madamCart', JSON.stringify(cart));
                        updateCartCount();
                        
                        const originalText = btn.textContent;
                        btn.textContent = 'ADDED';
                        btn.style.background = '#ff007f';
                        btn.style.color = 'white';
                        setTimeout(() => {
                            btn.textContent = originalText;
                            btn.style.background = 'white';
                            btn.style.color = '#ff007f';
                        }, 1000);
                    });
                });
                
                document.querySelectorAll('.love-icon svg').forEach(svg => {
                    svg.addEventListener('click', (e) => {
                        e.preventDefault();
                        if(svg.getAttribute('fill') === 'none') {
                            svg.setAttribute('fill', '#ff007f');
                        } else {
                            svg.setAttribute('fill', 'none');
                        }
                    });
                });
            });
            </script>
            """
            html = html.replace('</body>', script_html + '\n</body>')
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

update_css()
update_html_files()
print("Done")
