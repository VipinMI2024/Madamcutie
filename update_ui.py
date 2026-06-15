import re
import os
from bs4 import BeautifulSoup

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
    if '.nav-container {' in css:
        css = css.replace('.nav-container {\n    height: 100%;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n}', 
        '.nav-container {\n    height: 100%;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    position: relative;\n}')
        
        css = css.replace('.logo-wrapper {\n    display: flex;\n    align-items: center;\n    gap: var(--spacing-sm);\n}',
        '.logo-wrapper {\n    display: flex;\n    align-items: center;\n    gap: var(--spacing-sm);\n    position: absolute;\n    left: 50%;\n    transform: translateX(-50%);\n}')
        
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)

def update_html_files():
    for filename in ['shop.html', 'index.html']:
        if not os.path.exists(filename):
            continue
            
        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        # Add love icon and ADD button
        cards = soup.find_all('div', class_='madam-card')
        for card in cards:
            img_container = card.find('div', style=lambda s: s and 'aspect-ratio' in s)
            if not img_container:
                continue
                
            # Check if already added
            if img_container.find('button', class_='add-to-cart-btn'):
                continue
                
            # Extract product info
            title_el = card.find('h3')
            title = title_el.text.strip() if title_el else "Dress"
            
            price_el = card.find('span', style=lambda s: s and 'font-weight: 600' in s)
            price_text = price_el.text.strip() if price_el else "₹0"
            price = "".join([c for c in price_text if c.isdigit()])
            if not price:
                price = "0"
                
            img_el = img_container.find('img')
            img_src = img_el['src'] if img_el else ""
            
            add_btn_html = f"""
            <button class="add-to-cart-btn" data-title="{title}" data-price="{price}" data-img="{img_src}" style="position: absolute; bottom: 10px; right: 10px; background: white; border: 1.5px solid #ff007f; color: #ff007f; border-radius: 4px; padding: 4px 15px; font-weight: bold; font-size: 0.85rem; z-index: 3; cursor: pointer;">ADD</button>
            """
            love_icon_html = """
            <div class="love-icon" style="position: absolute; top: 10px; right: 10px; z-index: 3; cursor: pointer;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff007f" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
            </div>
            """
            
            img_container.append(BeautifulSoup(add_btn_html, 'html.parser'))
            img_container.append(BeautifulSoup(love_icon_html, 'html.parser'))
            
            # Make title text smaller on mobile
            if title_el and title_el.find('a'):
                title_el.find('a')['style'] = title_el.find('a').get('style', '') + '; font-size: clamp(0.9rem, 2vw, 1.2rem);'
            
        # Add cart logic script
        if not soup.find('script', id='custom-cart-logic'):
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
                        const item = {
                            title: btn.getAttribute('data-title'),
                            price: parseInt(btn.getAttribute('data-price')),
                            img: btn.getAttribute('data-img')
                        };
                        cart.push(item);
                        localStorage.setItem('madamCart', JSON.stringify(cart));
                        updateCartCount();
                        
                        // visual feedback
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
                
                // Toggle heart
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
            if soup.body:
                soup.body.append(BeautifulSoup(script_html, 'html.parser'))
                
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))

update_css()
update_html_files()
print("Done")
