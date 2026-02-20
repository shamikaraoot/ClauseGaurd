"""
Production-ready web scraper for Terms & Conditions pages.
Uses multi-strategy approach: requests → httpx → Playwright
"""
import re
import logging
from typing import Optional
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException

# Try to import optional dependencies
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Timeout settings
REQUEST_TIMEOUT = 15
PLAYWRIGHT_TIMEOUT = 15000  # milliseconds

# Latest Chrome User-Agent
CHROME_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def scrape_terms_and_conditions(url: str) -> str:
    """
    Fetches and cleans Terms & Conditions page text using multi-strategy approach.
    
    Strategy order:
    1. Try requests with full browser headers
    2. If blocked (403), try httpx with different headers
    3. If content empty/JS-rendered, use Playwright
    
    Args:
        url: URL to scrape
        
    Returns:
        Cleaned text content
        
    Raises:
        HTTPException: With clear error messages for various failure scenarios
    """
    # Validate URL
    if not url or not url.strip():
        raise HTTPException(
            status_code=400,
            detail="Invalid URL: URL cannot be empty"
        )
    
    url = url.strip()
    
    # Basic URL validation
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid URL format: {url}"
        )
    
    # Ensure HTTPS/HTTP scheme
    if parsed.scheme not in ['http', 'https']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported URL scheme: {parsed.scheme}. Only http and https are supported."
        )
    
    # Check robots.txt (log warning if disallowed, but don't block)
    try:
        check_robots_txt(url)
    except Exception as e:
        logger.warning(f"Could not check robots.txt: {e}")
    
    # Strategy 1: Try requests with full browser headers
    try:
        logger.info(f"Strategy 1: Attempting requests with browser headers for {url}")
        text = scrape_with_requests(url)
        if text and len(text.strip()) > 100:
            logger.info(f"Successfully scraped {len(text)} characters using requests")
            return text
    except HTTPException as e:
        # Re-raise HTTPException as-is
        raise e
    except Exception as e:
        logger.warning(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Try httpx if available
    if HTTPX_AVAILABLE:
        try:
            logger.info(f"Strategy 2: Attempting httpx for {url}")
            text = scrape_with_httpx(url)
            if text and len(text.strip()) > 100:
                logger.info(f"Successfully scraped {len(text)} characters using httpx")
                return text
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}")
    else:
        logger.info("httpx not available, skipping Strategy 2")
    
    # Strategy 3: Try Playwright if available
    if PLAYWRIGHT_AVAILABLE:
        try:
            logger.info(f"Strategy 3: Attempting Playwright for {url}")
            text = scrape_with_playwright(url)
            if text and len(text.strip()) > 100:
                logger.info(f"Successfully scraped {len(text)} characters using Playwright")
                return text
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.warning(f"Strategy 3 failed: {e}")
    else:
        logger.warning("Playwright not available, skipping Strategy 3")
    
    # All strategies failed
    raise HTTPException(
        status_code=400,
        detail=(
            "Unable to fetch Terms & Conditions from this URL. "
            "The website may block automated requests, require JavaScript rendering, "
            "or have strict access controls. Please copy and paste the text directly."
        )
    )


def scrape_with_requests(url: str) -> str:
    """Strategy 1: Use requests library with full browser headers."""
    headers = {
        "User-Agent": CHROME_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            stream=False
        )
        
        # Check for 403/401 errors
        if response.status_code == 403:
            raise HTTPException(
                status_code=400,
                detail="Website blocked automated requests (403 Forbidden). The site may require JavaScript rendering or have bot detection."
            )
        
        if response.status_code == 401:
            raise HTTPException(
                status_code=400,
                detail="Website requires authentication (401 Unauthorized). Cannot access Terms & Conditions."
            )
        
        response.raise_for_status()
        
        # Parse and extract text
        soup = BeautifulSoup(response.content, "lxml")
        text = extract_clean_text(soup)
        
        if not text or len(text.strip()) < 100:
            raise ValueError("Extracted content is too short or empty")
        
        return text
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=400,
            detail=f"Request timeout reached ({REQUEST_TIMEOUT}s). The website took too long to respond."
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=400,
            detail="Connection error. Unable to reach the website. Check your internet connection or the URL."
        )
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 403:
            raise HTTPException(
                status_code=400,
                detail="Website blocked automated requests (403 Forbidden). Trying alternative methods..."
            )
        raise HTTPException(
            status_code=400,
            detail=f"HTTP error {e.response.status_code if e.response else 'unknown'}: {str(e)}"
        )


def scrape_with_httpx(url: str) -> str:
    """Strategy 2: Use httpx with HTTP/2 support and different headers."""
    if not HTTPX_AVAILABLE:
        raise ValueError("httpx is not installed")
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        with httpx.Client(
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            http2=True
        ) as client:
            response = client.get(url)
            
            if response.status_code == 403:
                raise HTTPException(
                    status_code=400,
                    detail="Website blocked automated requests (403 Forbidden). JavaScript rendering may be required."
                )
            
            response.raise_for_status()
            
            # Parse and extract text
            soup = BeautifulSoup(response.content, "lxml")
            text = extract_clean_text(soup)
            
            if not text or len(text.strip()) < 100:
                raise ValueError("Extracted content is too short or empty")
            
            return text
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=400,
            detail=f"Request timeout reached ({REQUEST_TIMEOUT}s). The website took too long to respond."
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=400,
            detail="Connection error. Unable to reach the website."
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            raise HTTPException(
                status_code=400,
                detail="Website blocked automated requests (403 Forbidden). Trying JavaScript rendering..."
            )
        raise HTTPException(
            status_code=400,
            detail=f"HTTP error {e.response.status_code}: {str(e)}"
        )


def scrape_with_playwright(url: str) -> str:
    """Strategy 3: Use Playwright to render JavaScript and extract text."""
    if not PLAYWRIGHT_AVAILABLE:
        raise ValueError("Playwright is not installed. Run: python -m playwright install")
    
    try:
        with sync_playwright() as p:
            # Launch headless browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=CHROME_USER_AGENT,
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            try:
                # Navigate to page
                page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                
                # Remove unwanted elements
                page.evaluate("""
                    () => {
                        // Remove navigation, header, footer, cookie banners
                        const selectors = [
                            'nav', 'header', 'footer', 'aside',
                            '[class*="cookie"]', '[id*="cookie"]',
                            '[class*="banner"]', '[id*="banner"]',
                            '[class*="popup"]', '[id*="popup"]',
                            '[class*="modal"]', '[id*="modal"]',
                            'script', 'style', 'noscript'
                        ];
                        selectors.forEach(selector => {
                            document.querySelectorAll(selector).forEach(el => el.remove());
                        });
                    }
                """)
                
                # Get page content
                html_content = page.content()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, "lxml")
                text = extract_clean_text(soup)
                
                if not text or len(text.strip()) < 100:
                    raise ValueError("Extracted content is too short or empty")
                
                return text
                
            except PlaywrightTimeoutError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Page load timeout ({PLAYWRIGHT_TIMEOUT/1000}s). The website took too long to load."
                )
            finally:
                browser.close()
                
    except Exception as e:
        if "playwright" in str(e).lower() or "chromium" in str(e).lower():
            raise HTTPException(
                status_code=500,
                detail="Playwright browser not installed. Run: python -m playwright install"
            )
        raise HTTPException(
            status_code=400,
            detail=f"Playwright scraping failed: {str(e)}"
        )


def extract_clean_text(soup: BeautifulSoup) -> str:
    """
    Extract and clean text content from BeautifulSoup object.
    Removes navigation, footer, headers, scripts, styles, and other noise.
    """
    # Remove unwanted elements
    for element in soup.find_all([
        "script", "style", "nav", "header", "footer", "aside",
        "noscript", "meta", "link", "iframe", "svg", "img"
    ]):
        element.decompose()
    
    # Remove cookie banners and popups (common class/id patterns)
    for element in soup.find_all(class_=re.compile(r"cookie|banner|popup|modal|overlay", re.I)):
        element.decompose()
    
    for element in soup.find_all(id=re.compile(r"cookie|banner|popup|modal|overlay", re.I)):
        element.decompose()
    
    # Try to find main content area
    content_selectors = [
        'main',
        'article',
        '[role="main"]',
        '.content',
        '#content',
        '.main-content',
        '#main-content',
        'div[class*="terms"]',
        'div[class*="condition"]',
        'div[id*="terms"]',
        'div[id*="condition"]',
        '.terms-content',
        '#terms-content',
    ]
    
    text_content = None
    for selector in content_selectors:
        elements = soup.select(selector)
        if elements:
            # Get the largest text block (likely main content)
            largest_element = max(elements, key=lambda e: len(e.get_text()))
            candidate_text = largest_element.get_text()
            if len(candidate_text) > 500:  # Reasonable minimum
                text_content = candidate_text
                break
    
    # Fallback: get all text from body
    if not text_content or len(text_content) < 500:
        body = soup.find("body")
        if body:
            text_content = body.get_text()
    
    if not text_content:
        return ""
    
    # Clean up the text
    return clean_text(text_content)


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def check_robots_txt(url: str) -> None:
    """
    Check robots.txt to see if scraping is allowed.
    Logs a warning if disallowed, but doesn't block scraping.
    """
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        if not rp.can_fetch(CHROME_USER_AGENT, url):
            logger.warning(
                f"robots.txt disallows scraping of {url}. "
                "Proceeding anyway, but consider respecting robots.txt in production."
            )
    except Exception:
        # Silently fail - robots.txt check is optional
        pass
