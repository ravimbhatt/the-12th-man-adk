import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from .state import AgentState

def scraper_node(state: AgentState) -> AgentState:
    print(f"--- [Step 2] Scraper: Fetching Data ---")
    
    if state.get("final_results") and "error" in state["final_results"]:
        return state

    scores = {}
    commentary_text = []

    with sync_playwright() as p:
        # Launch visible browser (Stealth Mode)
        browser = p.chromium.launch(
            headless=False, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # --- A. SCORES ---
        try:
            print(f"   >>> Scorecard: {state['match_url']}")
            page.goto(state["match_url"], timeout=60000, wait_until="domcontentloaded")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 600)")
            
            page.wait_for_selector("table.ds-table", timeout=15000)
            scorecard_html = page.content()
            
            # Parse Tables
            soup = BeautifulSoup(scorecard_html, 'html.parser')
            all_tables = soup.find_all('table', class_='ds-table')
            
            batting_tables = []
            for table in all_tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                if "B" in headers and "R" in headers and "O" not in headers:
                    batting_tables.append(table)
            
            for team_idx, table in enumerate(batting_tables[:2], 1):
                rows = table.find_all('tr')
                pos = 1
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3 and cols[0].find('a'):
                        try:
                            val = cols[2].text.strip().split()[0].replace('*', '')
                            if val.isdigit():
                                scores[f"T{team_idx}-{pos}"] = int(val)
                                pos += 1
                        except: continue
            
        except Exception as e:
            print(f"   ❌ Scorecard Failed: {e}")
            browser.close()
            state["final_results"] = {"error": f"Score scraping failed: {str(e)}"}
            return state

        # --- B. COMMENTARY ---
        try:
            print(f"   >>> Commentary: {state['commentary_url']}")
            page.goto(state["commentary_url"], timeout=60000, wait_until="domcontentloaded")
            time.sleep(2)
            
            # Grab summary header
            summary_elem = page.query_selector("div.ds-text-tight-m")
            if summary_elem:
                commentary_text.append(f"RESULT: {summary_elem.inner_text()}")

            # Grab recent balls
            comms = page.query_selector_all("div.ci-html-content") 
            if not comms:
                comms = page.query_selector_all("p.ds-text-typo-body")
            
            for comm in comms[:5]:
                text = comm.inner_text().strip()
                if len(text) > 10:
                    commentary_text.append(text)
            
        except Exception as e:
            print(f"   ⚠️ Commentary Failed: {e}")
            commentary_text.append("Commentary unavailable.")
        
        browser.close()

    state["match_scores"] = scores
    state["match_commentary"] = commentary_text
    return state