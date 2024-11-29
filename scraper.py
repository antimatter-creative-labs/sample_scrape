# scraper.py

from playwright.sync_api import sync_playwright

def scrape_shadow_dom(page, url):
    try:
        # Navigate to the target URL
        page.goto(url)
        
        # Wait for the main container to load
        page.wait_for_selector('.ihf-container')
        
        # Add a delay to ensure elements inside the Shadow DOM have time to load
        page.wait_for_timeout(2500)  # Wait for 2.5 seconds (adjust as needed)
        
        # Access Shadow DOM (main container selector)
        shadow_host = page.query_selector('.ihf-container')  # Adjust selector as needed
        if not shadow_host:
            print(f"Shadow host not found for URL: {url}")
            return {"url": url, "error": "Shadow host not found"}
        
        # Evaluate shadowRoot and get data
        data = page.evaluate('''
            shadowHost => {
                const shadowRoot = shadowHost.shadowRoot;
                if (!shadowRoot) {
                    return { error: "ShadowRoot not found!" };
                }

                // Extract all features as label-value pairs
                const features = Array.from(shadowRoot.querySelectorAll('.feature-body .ui-grid-container')).map(container => {
                    const label = container.querySelector('.feature-label p')?.innerText.trim();
                    const value = container.querySelector('.feature-value p')?.innerText.trim();
                    return label && value ? { label, value } : null;
                }).filter(feature => feature !== null); // Remove any null entries

                // Extract other data
                return {
                    listing_number: shadowRoot.querySelector('.listing-number p')?.innerText || "N/A",
                    price: shadowRoot.querySelector('.list-price span:last-of-type')?.innerText || "N/A",
                    address: (shadowRoot.querySelector('.listing-address-1')?.innerText || "") + ', ' + (shadowRoot.querySelector('.listing-address-2')?.innerText || "N/A"),
                    bedrooms: shadowRoot.querySelector('.bedrooms p')?.innerText || "N/A",
                    bathrooms: shadowRoot.querySelector('.bathrooms p')?.innerText || "N/A",
                    square_feet: shadowRoot.querySelector('.square-feet p')?.innerText || "N/A",
                    description: shadowRoot.querySelector('.listing-description p')?.innerText || "N/A",
                    features: features,
                    images: Array.from(shadowRoot.querySelectorAll('.listing-photo-carousel img'))
                        .map(img => img.src)
                        .filter(src => !src.startsWith('data:image/'))  // Exclude base64 images
                };
            }
        ''', shadow_host)
        
        # Include the URL in the data for reference
        data['url'] = url

        return data

    except Exception as e:
        print(f"Error scraping URL {url}: {e}")
        return {"url": url, "error": str(e)}
