# ASM (American Society for Microbiology) Website Research Report

**Report Date:** January 14, 2026
**Research Focus:** Event structure, data access, and programmatic integration options

---

## Executive Summary

The American Society for Microbiology (ASM) maintains a comprehensive digital presence at asm.org with multiple event categories, educational webinars, and content organized by topic and audience. However, **programmatic access to event data is limited** - no public API, event-specific RSS feeds, or iCal exports were identified. Data extraction would require web scraping or third-party calendar platforms.

**Key Finding:** ASM journals provide RSS feeds, but events and webinars do not have structured data feeds for programmatic access.

---

## 1. Website Structure & Navigation

### Primary Site URL
- **Main Website:** https://asm.org
- **Events Hub:** https://asm.org/events
- **Webinars Section:** https://asm.org/browse-by-content-type/webinars
- **Education Hub:** https://asm.org/education

### Navigation Categories
1. **Who We Are** - About, governance, strategic roadmap
2. **What We Do** - Advocacy, global health programs, research areas
3. **Membership** - Benefits, directory, ASM Connect
4. **Events & Conferences** - Major conferences and specialized meetings
5. **Education & Careers** - Professional development, career resources
6. **Publications** - Journals, books, digital magazine (*Microcosm*)

### Technology Stack
- **Analytics:** Azure Application Insights, Google Tag Manager
- **Platform:** Custom CMS with structured content metadata
- **Registration:** ExperienceEvent platform for conferences
- **Webinars:** Zoom integration with registration via blueskyelearn.com
- **Learning Platform:** PathLMS (pathlms.com/asm)

---

## 2. Event Structure & Categories

### 2.1 Major Conferences

#### ASM Microbe 2026
- **URL:** https://asm.org/events/asm-microbe/home
- **Dates:** June 4-7, 2026
- **Location:** Walter E. Washington Convention Center, Washington, D.C.
- **Format:** Three independent meetings under one roof (NEW in 2026)

**Three Meeting Tracks:**

1. **ASM Health**
   - Clinical, translational, and public health microbiology
   - Topics: Diagnostics, therapeutics, epidemiology, public health
   - Relevant to: Infectious disease professionals, clinical microbiologists

2. **Applied & Environmental Microbiology**
   - Environmental microbiology, microbial ecology, biotechnology
   - Topics: Sustainable solutions, ecosystem restoration
   - Relevant to: Environmental scientists, biotechnology researchers

3. **Mechanism Discovery**
   - Molecular, genetic, and evolutionary mechanisms
   - Topics: Microbial physiology, host-pathogen interactions, systems biology
   - Relevant to: Basic research scientists, molecular biologists

**Key Features:**
- 200+ sessions across various tracks
- Abstract submission (deadline: January 21, 2026)
- Late-breaking submissions for rapid-fire talks
- Dynamic exhibit hall
- Poster presentations
- Networking opportunities

#### IMARI 2026 (Interdisciplinary Meeting on Antimicrobial Resistance and Innovation)
- **URL:** https://imari.org
- **Co-sponsors:** ASM and IDSA (Infectious Diseases Society of America)
- **Dates:** January 28-30, 2026
- **Location:** Las Vegas, Nevada
- **Focus:** Antimicrobial resistance, drug discovery and development

**Program Themes:**
1. Advances in Antimicrobial Resistance Research
2. Breakthroughs in Translation (bench to clinical)
3. Innovations in Antimicrobial Discovery (AI-powered design)
4. Cross-Sector Collaborations

**Event Structure:**
- Plenary sessions with thought leaders
- Scientific symposia
- Industry programs
- Meet the expert sessions
- Poster sessions
- Special session: New Antimicrobial Agents

**Note:** This is an INAUGURAL conference - first of its kind, highly relevant to infectious disease professionals.

#### ASMCUE (Conference for Undergraduate Educators)
- **URL:** https://asm.org/events/asm-conference-for-undergraduate-educators/home
- **Target Audience:** 350+ microbiology and biology educators
- **Format:** Interactive 3-day conference
- **2025 Location:** San Antonio, Texas (co-located with ABRCMS)
- **2026 Details:** Not yet announced

**Features:**
- Classroom strategy sharing
- Biology education research
- Evidence-based teaching methods
- Networking opportunities
- Three submission types: Sessions, Posters, Microbrews

#### Other ASM Events
- **ASM BIG** (Bioinformatics, Genomics and Big Data) - October 11-14, 2026
- **ASM Conference on Biofilms** - Specialized conference
- **ASM Biothreats** - Biodefense and emerging diseases
- **Clinical Virology Symposium** - Viral infections focus
- **ABRCMS** - Annual Biomedical Research Conference for Minority Students

### 2.2 Event Listing Structure

**Temporal Organization:**
- Upcoming Events (displayed first)
- Past Events (archived by year: 2025, 2024, 2021, 2020)

**Event Display Format:**
- Date range
- Event type designation
- Location
- Brief description
- Registration/submission links

**No Evidence Of:**
- iCal export buttons
- RSS feeds for events
- Google Calendar integration
- Outlook calendar export
- Structured data markup (Schema.org events)

---

## 3. Webinars & Educational Content

### 3.1 Webinar Organization

**Main URL:** https://asm.org/browse-by-content-type/webinars

**Total Webinars:** 70 across 6 pages (as of January 2026)

### 3.2 Content Categorization

#### By Topic (13 Categories)
1. Advocacy
2. Antimicrobial Resistance
3. Applied Sciences
4. Careers
5. Clinical Infections
6. Clinical Public Health Microbiology
7. Diversity & Inclusion
8. Ecology/Evolution
9. Education
10. Ethics
11. Global Health
12. Host-Microbe Biology
13. Molecular Biology

#### By Audience (9 Segments)
1. Clinicians
2. Educators
3. Graduate Students
4. Higher Education Instructors
5. Medical Lab Professionals
6. Policymakers
7. Postdocs
8. Researchers
9. Undergraduate Students

#### By Year
- Range: 2019-2026
- Temporal filtering available

### 3.3 Featured Webinar Series

1. **Journal of Virology Seminar Series**
   - URL: https://asm.org/webinars/journal-of-virology-seminar-series
   - Example: Jan 29, 2026 - Environmental surveillance and One Health approaches

2. **Clinical Microbiology Virtual Journal Club**
   - Ongoing series for clinical lab professionals

3. **mSystems Thinking Series**
   - Systems biology and microbiome research

4. **JMBE Live!**
   - Discussions with authors from Journal of Microbiology & Biology Education
   - Free webinar series for educators

5. **Public Health and Beyond: Career Exploration Series**
   - Professional development focus

6. **Training in NGS for Infectious Disease Applications**
   - URL: https://asm.org/webinars/training-ngs-infectious-diseases
   - 50 hours of free training
   - Focus: Next Generation Sequencing technologies
   - Target: Clinical microbiology workforce

7. **2025 ASMCUE Summer Series**
   - Online gathering (July 9 - August 13, 2025)
   - 6 sessions on evidence-based teaching
   - Zoom format

### 3.4 Webinar Access & Registration

**Registration System:**
- Primary platform: Zoom
- Registration emails sent from: webinars@blueskyelearn.com
- Includes: Calendar invites and Zoom meeting links

**Access Methods:**
1. **Live Attendance**
   - Register via Zoom links on individual webinar pages
   - Automatic calendar invites after registration

2. **On-Demand Access**
   - ASM Online Learning Center: https://www.pathlms.com/asm
   - Watch at your own pace
   - Content tailored by career role

3. **YouTube Archive**
   - Recorded content available on ASM YouTube channel

**Membership Benefits:**
- Free and discounted webinars
- Full access to on-demand webinar library
- Priority registration

**No Calendar Integration Found:**
- No iCal subscription feeds
- No calendar sync options
- No automated calendar updates for new webinars

---

## 4. Infectious Disease Content Categories

### 4.1 Clinical & Public Health Microbiology (CPHM)

**Main URL:** https://asm.org/browse-by-topic/clinical-public-health-microbiology

**Content Volume:**
- **Articles & Case Studies:** 220+ diagnostics resources
- **Webinars:** 33
- **Podcasts:** 119 episodes
- **Policy Statements:** 32
- **Press Releases:** 82
- **Image Galleries:** 53
- **Reports:** 24
- **Videos:** 12

**Sub-topics:**
- Biodefense/Biothreats (26 items)
- Diagnostics (220 items) - **LARGEST CATEGORY**
- Epidemiology (39 items)
- Foodborne (29 items)
- Surveillance

**Target Audiences:**
- Medical Lab Professionals (331 items)
- Clinicians (194 items)
- Researchers (184 items)
- Educators (56 items)
- Graduate Students (31 items)

**Time Range:** 1999-2026 (523 items from 2023 alone)

### 4.2 Infectious Diseases Topic Area

**Main URL:** https://asm.org/browse-by-topic/clinical-infections-disease/infectious-diseases

**Content Types (14 Categories):**
- Articles: 125
- Case Studies: 14
- Events: 1
- Guideline/Protocol: 5
- Image Galleries: 2
- Magazines: 19
- Podcasts: 6
- Policy Statements: 6
- Press Releases: 23
- Reports: 2
- Resource Pages: 3
- Travel Awards: 1
- Videos: 8
- Webinars: 7

**Total Items:** 228 across 19 pages (12 items per page)

**Date Range:** 2004-2025

### 4.3 ASM Microbe CPHM Track

**13 Subtracks:**
- CPHM01: Administering the Clinical/Public Health Microbiology Laboratory
- CPHM04: Diagnostic Immunology
- CPHM06: Diagnostic Mycology
- CPHM08: Diagnostic Public Health Microbiology
- Additional subtracks covering diagnostic technology, susceptibility testing, biosafety, antimicrobial stewardship, surveillance, epidemiology, and One Health

### 4.4 Clinical Infections and Vaccines (CIV) Track

**8 Subtracks:**
- CIV01: Clinical Studies of Adult Infectious Diseases
- CIV02: Infection Prevention and Antimicrobial Stewardship
- CIV05: Clinical Studies of Pediatric Infectious Diseases
- CIV06: Development of Vaccines and Immunization
- CIV07: Infection Biology and Dynamics
- CIV08: Clinical Epidemiology and Population Health

---

## 5. RSS Feeds & Data Access

### 5.1 Available RSS Feeds

**JOURNALS ONLY** - Not Events or Webinars

**RSS Feed Hub:** https://journals.asm.org/asm-journals-rss-feeds

**Available Journal RSS Feeds (15 journals):**

1. **Antimicrobial Agents and Chemotherapy (AAC)**
   - Current Issue RSS
   - Latest Articles RSS

2. **Applied and Environmental Microbiology (AEM)**
   - Current Issue RSS
   - Latest Articles RSS
   - URL: https://aem.asm.org/content/rss

3. **Clinical Microbiology Reviews**
   - Current Issue RSS
   - Latest Articles RSS

4. **EcoSal Plus**
   - Latest Articles RSS

5. **Infection and Immunity**
   - Current Issue RSS
   - Latest Articles RSS

6. **Journal of Bacteriology**
   - Current Issue RSS
   - Latest Articles RSS

7. **Journal of Clinical Microbiology**
   - Current Issue RSS
   - Latest Articles RSS

8. **Journal of Microbiology & Biology Education (JMBE)**
   - Current Issue RSS
   - Latest Articles RSS

9. **Journal of Virology**
   - Current Issue RSS
   - Latest Articles RSS

10. **mBio** (Open Access)
    - Current Issue RSS
    - Latest Articles RSS

11. **Microbiology and Molecular Biology Reviews**
    - Current Issue RSS
    - Latest Articles RSS

12. **Microbiology Resource Announcements**
    - Latest Articles RSS

13. **Microbiology Spectrum** (Open Access)
    - Current Issue RSS
    - Latest Articles RSS

14. **mSphere** (Open Access)
    - Current Issue RSS
    - Latest Articles RSS

15. **mSystems** (Open Access)
    - Current Issue RSS
    - Latest Articles RSS

### 5.2 What's NOT Available

**No RSS Feeds For:**
- Events calendar
- Webinar schedules
- Conference announcements
- Press releases
- News updates

**No iCal/Calendar Exports For:**
- Event listings
- Webinar schedules
- Conference sessions

**No Public API Documented For:**
- Event data
- Webinar listings
- Conference schedules
- Educational content

### 5.3 Email Alerts & Subscriptions

**Available Through ASM Membership:**
- E-TOCs (Table of Contents alerts) for journals
- Citation alerts for articles
- Search alerts for research topics
- Accepted manuscript notifications

**Subscription Contact:**
- Email: ejournals@asmusa.org
- Address: American Society for Microbiology, 1752 N St. NW, Washington, D.C. 20036

**Newsletter:**
- *Microcosm* - Quarterly news magazine for members

---

## 6. Programmatic Access Options

### 6.1 Current State: Limited Programmatic Access

**What Exists:**
1. **Journal RSS Feeds** - Well-documented, stable, XML format
2. **Structured Content Metadata** - Page source contains JSON data structures
3. **PathLMS Integration** - Third-party learning platform (pathlms.com/asm)
4. **Zoom Integration** - Third-party webinar platform

**What's Missing:**
1. **Public API** - No documented REST or GraphQL API
2. **Event Data Feeds** - No RSS, Atom, or iCal for events
3. **Webinar Calendar Sync** - No subscription feeds
4. **Structured Data Markup** - No Schema.org event markup detected

### 6.2 Web Scraping Approach

Since no official API or feeds exist for events/webinars, programmatic access requires web scraping.

#### Technical Considerations

**1. Inspect Page Source for Embedded JSON**
- ASM uses structured content metadata in page source
- Look for `<script type="application/ld+json">` tags
- Check for inline JavaScript data objects
- Example found on infectious diseases page: `data["apiParameters"]`

**2. Network Analysis**
- Use browser DevTools Network tab
- Monitor AJAX/XHR requests when loading content
- ASM uses API endpoints like `/api/bookmarks/loadBookmarks`
- May find undocumented JSON endpoints for content retrieval

**3. HTML Parsing Strategy**
- **Tools:** BeautifulSoup4 (Python) or Cheerio (Node.js)
- **Target Elements:**
  - Event listings with date, title, location
  - Webinar cards with registration links
  - Filtering/pagination structure

**4. Handle Dynamic Content**
- ASM pages use Azure Application Insights and Google Tag Manager
- May require JavaScript rendering
- **Tools:** Selenium, Playwright, or Puppeteer for browser automation

**5. Third-Party Calendar Platforms**
- ASM conferences may use Sched.com for detailed schedules
- Example: https://2025asmcue.sched.com/
- Sched provides better programmatic access (iCal export, API)

#### Sample Scraping Workflow

```python
# Pseudocode for ASM event scraping

import requests
from bs4 import BeautifulSoup
import json

# 1. Fetch events page
url = "https://asm.org/events"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 2. Look for embedded JSON data
scripts = soup.find_all('script', type='application/ld+json')
for script in scripts:
    data = json.loads(script.string)
    # Process event data

# 3. Parse HTML structure
events = soup.find_all('div', class_='event-card')  # Hypothetical class
for event in events:
    title = event.find('h3').text
    date = event.find('time')['datetime']
    location = event.find('span', class_='location').text
    # Store event data

# 4. Handle pagination
next_page = soup.find('a', rel='next')
if next_page:
    # Recursively scrape next page
    pass
```

### 6.3 Alternative Data Sources

**1. Third-Party Event Aggregators**
- **10times.com** - Lists ASM Microbe
  - URL: https://10times.com/asm-microbe-washington-dc
  - May provide structured data or API access

- **NCBI Conferences** - Tracks ASM meetings
  - URL: https://www.nlm.nih.gov/ncbi/conferences/ASM/ASM.html
  - Government source, reliable but limited

**2. Social Media APIs**
- **ASM Twitter/X:** @ASMicrobiology
  - Event announcements via Twitter API
  - Hashtags: #IMARI26, #ASMMicrobe, #ASMCUE

**3. Conference-Specific Platforms**
- **IMARI:** https://imari.org (WordPress site)
  - Check for WordPress REST API endpoint: `/wp-json/wp/v2/`
  - May provide programmatic access to posts/events

- **Sched.com Integration:**
  - ASM conferences may use Sched for detailed schedules
  - Sched provides iCal export and JSON APIs
  - Example: https://2025asmcue.sched.com/

**4. Google Calendar Search**
- Search for public ASM calendars
- If ASM maintains public Google Calendar, can subscribe
- Use Google Calendar API for programmatic access

### 6.4 Rate Limiting & Ethics

**Best Practices:**
- Respect robots.txt: https://asm.org/robots.txt
- Implement rate limiting (1-2 requests per second)
- Cache responses to minimize server load
- Use User-Agent header identifying your application
- Consider reaching out to ASM for partnership/API access

**Contact for Data Access:**
- ASM Membership Services
- Email: service@asmusa.org
- Phone: (202) 737-3600
- Propose partnership for event data feed

---

## 7. Specific URLs Reference

### Primary Navigation
| Resource | URL |
|----------|-----|
| Main Website | https://asm.org |
| Events Hub | https://asm.org/events |
| Webinars | https://asm.org/browse-by-content-type/webinars |
| Education | https://asm.org/education |
| Newsroom | https://asm.org/newsroom |

### Major Conferences
| Conference | URL |
|------------|-----|
| ASM Microbe 2026 | https://asm.org/events/asm-microbe/home |
| IMARI 2026 | https://imari.org |
| ASMCUE | https://asm.org/events/asm-conference-for-undergraduate-educators/home |

### Topic Areas (Infectious Disease Relevant)
| Topic | URL |
|-------|-----|
| Clinical & Public Health Microbiology | https://asm.org/browse-by-topic/clinical-public-health-microbiology |
| Infectious Diseases | https://asm.org/browse-by-topic/clinical-infections-disease/infectious-diseases |
| Antimicrobial Resistance | (Available as filter on webinars/articles) |

### RSS Feeds
| Feed Type | URL |
|-----------|-----|
| All Journal RSS Feeds | https://journals.asm.org/asm-journals-rss-feeds |
| Applied & Environmental Microbiology | https://aem.asm.org/content/rss |

### Learning Platforms
| Platform | URL |
|----------|-----|
| ASM Online Learning Center | https://www.pathlms.com/asm |
| ASMCUE Schedule (Example) | https://2025asmcue.sched.com/ |

### External Integrations
| Service | URL/Contact |
|---------|-------------|
| Webinar Registration Emails | webinars@blueskyelearn.com |
| Journal Subscriptions | ejournals@asmusa.org |
| General Member Services | service@asmusa.org |

---

## 8. Key Findings Summary

### Strengths
1. **Well-organized content hierarchy** with topic and audience filters
2. **Comprehensive webinar offerings** (70+ webinars, 13 topics, 9 audiences)
3. **Strong journal RSS infrastructure** (15 journals, current + latest feeds)
4. **Multiple conference tracks** covering diverse microbiology areas
5. **Rich educational resources** (articles, case studies, protocols, galleries)
6. **Professional integration** with Zoom, PathLMS, ExperienceEvent

### Limitations
1. **No event-specific RSS feeds or iCal exports**
2. **No public API for events or webinars**
3. **No structured data markup (Schema.org) for events**
4. **Limited calendar integration options**
5. **Manual browsing required for event discovery**
6. **No automated notification system for new events**

### Opportunities
1. **Web scraping** - Feasible but requires maintenance
2. **Third-party aggregators** - 10times.com, NCBI conferences
3. **Sched.com integration** - Some conferences use this platform
4. **Partnership approach** - Contact ASM for data access
5. **Social media monitoring** - Twitter/X API for announcements
6. **IMARI WordPress API** - May provide programmatic access

---

## 9. Recommendations for Programmatic Access

### Short-term (Immediate Implementation)

1. **Subscribe to Journal RSS Feeds**
   - Implement RSS reader for relevant journals
   - Monitor: Journal of Clinical Microbiology, Antimicrobial Agents & Chemotherapy
   - Parse for infectious disease keywords

2. **Web Scraping Implementation**
   - Target pages:
     - https://asm.org/events
     - https://asm.org/browse-by-content-type/webinars
     - https://asm.org/browse-by-topic/clinical-infections-disease/infectious-diseases
   - Schedule: Daily checks for new events
   - Store: Date, title, location, URL, description, category

3. **Third-Party Monitoring**
   - Set up alerts on 10times.com for ASM events
   - Subscribe to NCBI conference calendar
   - Monitor ASM social media via Twitter API

### Mid-term (1-3 months)

4. **Partnership Request**
   - Contact ASM technical team
   - Request: Event data API or structured feed
   - Propose: Collaboration for event promotion
   - Benefit to ASM: Increased event visibility

5. **Sched.com Integration**
   - For conferences using Sched (like ASMCUE)
   - Implement iCal subscription
   - Use Sched API if available

6. **Email Parsing System**
   - Set up dedicated email for ASM newsletters
   - Implement automated parsing for event announcements
   - Extract structured data from email content

### Long-term (Strategic)

7. **Community Data Repository**
   - Build shared database of microbiology events
   - Collaborate with other institutions
   - Aggregate from multiple sources (ASM, IDSA, CDC, etc.)

8. **Browser Extension Development**
   - Create tool to automatically extract ASM event data
   - Share with community for crowdsourced updates

9. **AI-Powered Monitoring**
   - Use LLM to monitor ASM website for changes
   - Automated extraction of new event information
   - Natural language processing for categorization

---

## 10. Technical Implementation Example

### Python Script for ASM Event Scraping

```python
"""
ASM Event Scraper
Extracts event data from asm.org/events
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time

class ASMEventScraper:
    def __init__(self):
        self.base_url = "https://asm.org"
        self.events_url = f"{self.base_url}/events"
        self.headers = {
            'User-Agent': 'ASM Event Aggregator (research purposes)'
        }

    def fetch_events_page(self):
        """Fetch the main events page"""
        try:
            response = requests.get(self.events_url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching events page: {e}")
            return None

    def extract_event_data(self, soup):
        """Extract structured event data from HTML"""
        events = []

        # Look for JSON-LD structured data first
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'Event':
                    events.append(self.parse_json_ld_event(data))
            except json.JSONDecodeError:
                pass

        # Fallback to HTML parsing if no JSON-LD found
        if not events:
            events = self.parse_html_events(soup)

        return events

    def parse_json_ld_event(self, data):
        """Parse event from JSON-LD structured data"""
        return {
            'name': data.get('name'),
            'start_date': data.get('startDate'),
            'end_date': data.get('endDate'),
            'location': self.extract_location(data.get('location', {})),
            'description': data.get('description'),
            'url': data.get('url'),
            'event_type': data.get('eventAttendanceMode', 'Unknown')
        }

    def parse_html_events(self, soup):
        """Parse events from HTML structure (adapt to actual HTML)"""
        events = []

        # This is a template - actual selectors need to be updated
        # based on real ASM page structure
        event_containers = soup.find_all('div', class_='event-item')

        for container in event_containers:
            event = {
                'name': self.safe_extract(container, 'h3', 'title'),
                'date_range': self.safe_extract(container, 'time'),
                'location': self.safe_extract(container, 'span', 'location'),
                'url': self.extract_url(container),
                'scraped_at': datetime.now().isoformat()
            }
            events.append(event)

        return events

    def safe_extract(self, element, tag, class_name=None):
        """Safely extract text from HTML element"""
        try:
            if class_name:
                found = element.find(tag, class_=class_name)
            else:
                found = element.find(tag)
            return found.text.strip() if found else None
        except AttributeError:
            return None

    def extract_url(self, element):
        """Extract event URL from element"""
        try:
            link = element.find('a', href=True)
            if link:
                href = link['href']
                return href if href.startswith('http') else f"{self.base_url}{href}"
        except:
            return None

    def extract_location(self, location_data):
        """Extract location from various formats"""
        if isinstance(location_data, dict):
            return location_data.get('name') or location_data.get('address', {}).get('addressLocality')
        return str(location_data)

    def save_events(self, events, filename='asm_events.json'):
        """Save events to JSON file"""
        with open(filename, 'w') as f:
            json.dump(events, f, indent=2)
        print(f"Saved {len(events)} events to {filename}")

    def run(self):
        """Main execution method"""
        print("Fetching ASM events...")
        soup = self.fetch_events_page()

        if soup:
            events = self.extract_event_data(soup)
            if events:
                self.save_events(events)
                return events
            else:
                print("No events found. Page structure may have changed.")

        return []

# Usage
if __name__ == "__main__":
    scraper = ASMEventScraper()
    events = scraper.run()

    # Display events
    for event in events:
        print(f"\n{event.get('name')}")
        print(f"  Date: {event.get('start_date')} - {event.get('end_date')}")
        print(f"  Location: {event.get('location')}")
        print(f"  URL: {event.get('url')}")
```

### RSS Feed Reader for ASM Journals

```python
"""
ASM Journal RSS Feed Reader
Monitors ASM journals for infectious disease content
"""

import feedparser
import re
from datetime import datetime

class ASMJournalMonitor:
    def __init__(self):
        self.feeds = {
            'Journal of Clinical Microbiology': 'https://journals.asm.org/rss/journal_jcm.xml',
            'Antimicrobial Agents and Chemotherapy': 'https://journals.asm.org/rss/journal_aac.xml',
            'Clinical Microbiology Reviews': 'https://journals.asm.org/rss/journal_cmr.xml',
            'Infection and Immunity': 'https://journals.asm.org/rss/journal_iai.xml',
        }

        self.infectious_disease_keywords = [
            'infectious disease', 'pathogen', 'antimicrobial resistance',
            'AMR', 'antibiotic', 'viral infection', 'bacterial infection',
            'fungal infection', 'pandemic', 'epidemic', 'outbreak',
            'clinical trial', 'diagnostic', 'therapeutics'
        ]

    def fetch_feed(self, url):
        """Fetch and parse RSS feed"""
        try:
            return feedparser.parse(url)
        except Exception as e:
            print(f"Error fetching feed {url}: {e}")
            return None

    def is_relevant(self, entry):
        """Check if article is relevant to infectious diseases"""
        text = f"{entry.title} {entry.summary}".lower()
        return any(keyword.lower() in text for keyword in self.infectious_disease_keywords)

    def monitor_all_feeds(self):
        """Monitor all configured RSS feeds"""
        relevant_articles = []

        for journal_name, feed_url in self.feeds.items():
            print(f"\nChecking {journal_name}...")
            feed = self.fetch_feed(feed_url)

            if feed and feed.entries:
                for entry in feed.entries:
                    if self.is_relevant(entry):
                        article = {
                            'journal': journal_name,
                            'title': entry.title,
                            'link': entry.link,
                            'published': entry.get('published', 'Unknown'),
                            'summary': entry.summary[:200] + '...',
                            'checked_at': datetime.now().isoformat()
                        }
                        relevant_articles.append(article)

        return relevant_articles

    def display_articles(self, articles):
        """Display relevant articles"""
        print(f"\n{'='*80}")
        print(f"Found {len(articles)} relevant articles")
        print(f"{'='*80}\n")

        for article in articles:
            print(f"Journal: {article['journal']}")
            print(f"Title: {article['title']}")
            print(f"Published: {article['published']}")
            print(f"Link: {article['link']}")
            print(f"Summary: {article['summary']}")
            print("-" * 80)

# Usage
if __name__ == "__main__":
    monitor = ASMJournalMonitor()
    articles = monitor.monitor_all_feeds()
    monitor.display_articles(articles)
```

---

## 11. Contact Information

### ASM Support
- **Website:** https://asm.org
- **General Inquiries:** service@asmusa.org
- **Phone:** (202) 737-3600
- **Address:** 1752 N St. NW, Washington, D.C. 20036

### Specific Departments
- **Webinars:** webinars@blueskyelearn.com
- **Journal Subscriptions:** ejournals@asmusa.org
- **ASMCUE:** ASMCUE@asmusa.org
- **Membership:** service@asmusa.org

### Social Media
- **Twitter/X:** @ASMicrobiology
- **Conference Hashtags:** #IMARI26, #ASMMicrobe, #ASMCUE

---

## 12. Conclusions

The American Society for Microbiology maintains a comprehensive and well-organized digital presence with substantial content relevant to infectious disease research and clinical practice. However, **programmatic access to event and webinar data is not officially supported**.

### Key Takeaways:

1. **Events and webinars lack structured data feeds** - No RSS, iCal, or API available
2. **Journal content is well-supported** - 15 journals with RSS feeds for current issues and latest articles
3. **Web scraping is necessary** for automated event monitoring
4. **Third-party platforms provide alternatives** - Sched.com, 10times.com, NCBI conferences
5. **Partnership approach recommended** - Contact ASM for official data access

### Best Path Forward:

1. Implement web scraping for event pages (maintenance required)
2. Subscribe to journal RSS feeds for research updates
3. Monitor third-party aggregators for event announcements
4. Contact ASM to request API/feed development
5. Consider community-driven data aggregation

### Infectious Disease Relevance:

ASM provides extensive infectious disease content through:
- **IMARI conference** - Dedicated to antimicrobial resistance
- **ASM Health track** - Clinical and public health microbiology
- **Clinical Infections & Vaccines** - 8 subtracks covering ID topics
- **220+ diagnostic resources** - Largest content category
- **33 CPHM webinars** - Ongoing educational content
- **Key journals** - JCM, AAC, CMR focused on clinical microbiology

---

**Report Prepared By:** Research Analyst Agent
**Date:** January 14, 2026
**Next Review:** Recommend quarterly updates as ASM may add new features
