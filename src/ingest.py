# src/ingest.py
import requests, json, os
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
OUT_RAW = Path("data/raw")
OUT_PROC = Path("data/processed")
OUT_RAW.mkdir(parents=True, exist_ok=True)
OUT_PROC.mkdir(parents=True, exist_ok=True)

URL = "https://www.ontario.ca/laws/statute/02r30"  # the statute you provided

def fetch(url):
    headers = {"User-Agent":"legal-chatbot/1.0 (+your-email@example.com)"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def parse_statute(html):
    soup = BeautifulSoup(html, "html.parser")

    # Try to find main content container - various sites differ; we try a couple of strategies.
    main = soup.find("main") or soup.find("article") or soup.find(id="content") or soup.body

    sections = []
    # We'll treat h2/h3/h4 as section headings; collect following <p> until next heading
    headings = main.find_all(["h2", "h3", "h4"])
    if not headings:
        # fallback: collect <h1> then paragraphs
        headings = main.find_all(["h1", "h2", "h3"])

    for h in headings:
        title = h.get_text(strip=True)
        texts = []
        for sib in h.find_next_siblings():
            if sib.name and sib.name.startswith("h") and len(sib.name) <= 2:  # next heading
                break
            if sib.name == "p":
                texts.append(sib.get_text(" ", strip=True))
            # include list items if present
            if sib.name in ("ul","ol"):
                texts.append(" ".join(li.get_text(" ", strip=True) for li in sib.find_all("li")))
        body = "\n\n".join(texts).strip()
        if body:
            sections.append({"title": title, "text": body})

    # If headings detection failed, fallback: split the whole main text into chunks by paragraphs
    if not sections:
        paras = [p.get_text(" ", strip=True) for p in main.find_all("p")]
        for i,p in enumerate(paras):
            sections.append({"title": f"paragraph_{i}", "text": p})

    return sections

def main():
    print("Fetching statute...")
    html = fetch(URL)
    Path(OUT_RAW / "statute.html").write_text(html, encoding="utf-8")
    print("Parsing statute...")
    sections = parse_statute(html)
    Path(OUT_PROC / "sections.json").write_text(json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(sections)} sections to data/processed/sections.json")

if __name__ == "__main__":
    main()
