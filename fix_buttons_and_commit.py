import os
import re

def update_css():
    css_path = 'css/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # Make madam-card text smaller on mobile
    mobile_css = """
@media (max-width: 600px) {
    .grid-2, .grid-3, .grid-4 { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .madam-card h3 { font-size: 0.9rem !important; margin-bottom: 4px !important; }
    .madam-card p { font-size: 0.75rem !important; margin-bottom: 6px !important; white-space: normal !important; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    .madam-card span { font-size: 0.85rem !important; }
    .add-to-cart-btn { font-size: 0.75rem !important; padding: 2px 10px !important; }
}
"""
    if 'madam-card h3 { font-size: 0.9rem !important;' not in css:
        css += mobile_css
        
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)

def update_html():
    for filename in ['shop.html', 'index.html']:
        if not os.path.exists(filename):
            continue
            
        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()
            
        # Update custom-cart-logic
        old_script_start = '<script id="custom-cart-logic">'
        old_script_end = '</script>'
        
        if old_script_start in html:
            start_idx = html.find(old_script_start)
            end_idx = html.find(old_script_end, start_idx) + len(old_script_end)
            
            new_script = """<script id="custom-cart-logic">
            document.addEventListener('DOMContentLoaded', () => {
                let cart = JSON.parse(localStorage.getItem('madamCart')) || [];
                const cartCountEl = document.querySelector('.cart-count');
                
                function updateCartCount() {
                    if(cartCountEl) cartCountEl.textContent = cart.length;
                }
                updateCartCount();
                
                // Set initial state for buttons based on cart
                document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
                    const card = btn.closest('.madam-card');
                    if(card) {
                        const titleEl = card.querySelector('h3 a');
                        const title = titleEl ? titleEl.textContent : 'Dress';
                        const inCart = cart.some(item => item.title === title);
                        if(inCart) {
                            btn.textContent = 'ADDED';
                            btn.style.background = '#ff007f';
                            btn.style.color = 'white';
                        }
                    }
                    
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        if (btn.textContent === 'ADDED') return; // already added
                        
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
                        
                        btn.textContent = 'ADDED';
                        btn.style.background = '#ff007f';
                        btn.style.color = 'white';
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
            </script>"""
            
            html = html[:start_idx] + new_script + html[end_idx:]
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

def git_commit():
    os.system('git add .')
    os.system('git commit -m "Update Add buttons to stay ADDED and improve mobile responsiveness"')

update_css()
update_html()
git_commit()
print("Done updating and committing.")
