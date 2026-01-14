# NIH VideoCast Data Sources Research
**Research Date:** January 14, 2026
**Platform:** videocast.nih.gov

## Executive Summary

NIH VideoCast provides RSS feeds for accessing event data but does not appear to offer public iCal/ICS calendar subscriptions or a formal REST API. The platform uses standard RSS 2.0 XML format with custom namespaces for event metadata. There are 14,000+ archived events and 67 upcoming events currently listed.

---

## 1. Available RSS Feeds

### General Event Feeds

#### Upcoming Events Feed
- **URL:** `https://videocast.nih.gov/rss/UpcomingEvents.asp`
- **Purpose:** Live and scheduled future events
- **Format:** RSS 2.0 XML
- **Update Frequency:** TTL 20 minutes

#### Past Events Feed (All Categories)
- **URL:** `https://videocast.nih.gov/rss/PastEvents.asp`
- **Purpose:** Recorded/archived content across all categories
- **Format:** RSS 2.0 XML

#### Combined Feed
- **URL:** `https://videocast.nih.gov/rss/all.asp`
- **Purpose:** Both upcoming and archived events
- **Format:** RSS 2.0 XML

---

## 2. RSS Feed Data Structure

### Feed-Level Metadata
```xml
<channel>
  <title>Videocast Upcoming Events</title>
  <link>https://videocast.nih.gov/</link>
  <description>The National Institutes of Health</description>
  <language>en-us</language>
  <ttl>20</ttl>
  <image>
    <url>[Logo URL]</url>
    <width>88</width>
    <height>31</height>
  </image>
```

### Event Item Elements

| XML Element | Data Type | Description | Example Format |
|-------------|-----------|-------------|----------------|
| `<title>` | String | Event name | Text string |
| `<link>` | URL | Video/event page | `https://videocast.nih.gov/watch=[ID]` |
| `<guid>` | String | Unique identifier | `[ID]@https://videocast.nih.gov` |
| `<description>` | HTML | Full event details including speaker info, objectives | HTML-encoded text with `&lt;`, `&gt;`, `&quot;` |
| `<author>` | String | Air date/time | `Wed, 13 May 2026 18:00:00 GMT` |
| `<pubDate>` | RFC 2822 | Publication timestamp | `Tue, 13 Jan 2026 20:03:00 GMT` |
| `<category>` | String | Topic classification | "Health", "Immunology", etc. |
| `<Videocast:AirDate>` | RFC 2822 | Original broadcast time (custom namespace) | GMT timestamp |

### Date Format
- **Standard:** RFC 2822 format
- **Pattern:** `Day, DD Mon YYYY HH:MM:SS GMT`
- **Example:** `Wed, 15 Jan 2025 13:00:00 GMT`

---

## 3. Category-Specific RSS Feeds

### URL Pattern
`https://videocast.nih.gov/rss/PastEvents.asp?c=[CATEGORY_ID]`

### Infectious Disease & Related Categories

#### Confirmed Category IDs

| Category Name | Category ID | RSS Feed URL |
|---------------|-------------|--------------|
| **Immunology** | 28 | `https://videocast.nih.gov/rss/PastEvents.asp?c=28` |
| **John R. LaMontagne - Infectious Diseases** | 16 | `https://videocast.nih.gov/rss/PastEvents.asp?c=16` |
| **Neuroscience** | 16 | `https://videocast.nih.gov/rss/PastEvents.asp?c=16` |
| **DNA Repair** | 5 | `https://videocast.nih.gov/rss/PastEvents.asp?c=5` |
| **Stem Cell** | 29 | `https://videocast.nih.gov/rss/PastEvents.asp?c=29` |
| **Proteomics** | 36 | `https://videocast.nih.gov/rss/PastEvents.asp?c=36` |
| **Bioethics** | 22 | `https://videocast.nih.gov/rss/PastEvents.asp?c=22` |
| **Lectures** | 124 | `https://videocast.nih.gov/rss/PastEvents.asp?c=124` |
| **NIH Director's Seminars** | 25 | `https://videocast.nih.gov/rss/PastEvents.asp?c=25` |
| **Clinical Center Grand Rounds** | 27 | `https://videocast.nih.gov/rss/PastEvents.asp?c=27` |
| **WALS - Wednesday Afternoon Lectures** | 3 | `https://videocast.nih.gov/rss/PastEvents.asp?c=3` |
| **ORS and ORF (NIH Only)** | 204 | `https://videocast.nih.gov/rss/PastEvents.asp?c=204` |

### Additional Relevant Categories (IDs not confirmed)

Based on Past Events page listings:
- **James C. Hill - HIV/AIDS Research**
- **Joseph J. Kinyoun - Infection and Immunity**
- **David E. Barmes - Global Health**
- **National Institute of Allergy and Infectious Diseases** (NIAID advisory content)
- **COVID-19** (dedicated pandemic archive)
- **Health Disparities**

### Category Feed Characteristics
- **Format:** RSS 2.0 XML with custom `Videocast:` namespace
- **Ordering:** Chronological (newest first)
- **Update Interval:** TTL 20 minutes
- **Sample Size:** ~20 items per feed
- **Date Range:** Multi-year archives (example: Immunology feed spans 2019-2025)

---

## 4. iTunes/Podcast RSS Feeds

### Video Podcasts
- **Title:** "National Institutes of Health - Video Podcasts"
- **Category:** Science & Medicine
- **iTunes Link:** `http://phobos.apple.com/WebObjects/MZStore.woa/wa/viewPodcast?id=280196883`
- **Format:** Video podcast compatible with iTunes/Apple Podcasts

### Audio Podcasts
- **Title:** "National Institutes of Health - Audio Podcasts"
- **Category:** Science & Medicine
- **iTunes Link:** `http://phobos.apple.com/WebObjects/MZStore.woa/wa/viewPodcast?id=280416633`
- **Format:** Audio-only podcast

### iTunes RSS Feed Page
- **URL:** `https://videocast.nih.gov/rss/itunes/`
- **Note:** Links to iTunes Store rather than direct RSS XML URLs

---

## 5. Event Listing Page Structure

### Upcoming Events Page
- **URL:** `https://videocast.nih.gov/FutureEvents`
- **Current Count:** 67 upcoming events

#### Data Fields Displayed
1. **Title** - Event name with "Read more" links
2. **Date** - Format: Day, Month DD, YYYY
3. **Time** - Start and end times in Eastern Time (ET)
4. **Access Level** - Public, "NIH Only," or "HHS Only" designations

#### Features
- DataTable interface with sorting capabilities
- Chronological organization
- No visible category filters in the interface
- Individual event pages accessible via links

#### URL Pattern for Individual Events
- Live/Upcoming: `https://videocast.nih.gov/summary.asp?live=[EVENT_ID]`
- Archived: `https://videocast.nih.gov/watch=[EVENT_ID]`

### Past Events Page
- **URL:** `https://videocast.nih.gov/PastEvents`
- **Total Archive:** 13,981 events (as of January 2026)
- **Pagination:** 1,394 pages of results
- **Filtering:** Category-based filtering available

---

## 6. iCal/ICS Calendar Subscriptions

### Findings: NO ICAL SUPPORT FOUND

**Status:** NIH VideoCast does NOT appear to offer:
- iCal/ICS calendar subscription feeds
- Calendar export functionality on individual event pages
- "Add to Calendar" buttons or links
- Calendar API endpoints

### Alternative Calendar Options

#### NIH Calendar of Events
- **URL:** `https://calendar.nih.gov/`
- **Status:** Separate NIH calendar system
- **Integration:** No confirmed integration with VideoCast
- **Calendar Export:** Not confirmed in research

#### Event-Level Calendar Export
Individual event pages were examined and **no calendar export functionality was found**. Event pages include:
- Video player and streaming information
- Download options for video files (various bitrates)
- Caption/transcript downloads
- Feedback forms
- **No calendar integration tools**

---

## 7. API Endpoints

### Findings: NO PUBLIC API DOCUMENTED

**Status:** No formal REST API or programmatic access points were identified beyond RSS feeds.

### Available Data Access Methods
1. **RSS Feeds** - Standard XML parsing (primary method)
2. **Web Scraping** - Event listing pages (not recommended)
3. **Direct Video URLs** - Pattern: `https://videocast.nih.gov/watch=[ID]`

### URL Patterns Identified

| Resource Type | URL Pattern | Parameters |
|---------------|-------------|------------|
| RSS - Upcoming | `/rss/UpcomingEvents.asp` | None |
| RSS - Past Events | `/rss/PastEvents.asp` | `?c=[CATEGORY_ID]` |
| RSS - All Events | `/rss/all.asp` | None |
| Event Summary | `/summary.asp` | `?live=[EVENT_ID]` |
| Video Watch | `/watch` | `=[EVENT_ID]` or `?live=[EVENT_ID]` |
| Live Video | `/livew.asp` | `?live=[EVENT_ID]` |
| Past Events List | `/PastEvents` | `?c=[CATEGORY_ID]` |
| Podcasts | `/Podcasts.asp` | `?c=[CATEGORY_ID]` |
| Search | `/Search` | Query parameters not documented |

---

## 8. Relevant Events & Content for Disease Research

### Current Upcoming Events (January 2026)

#### Infectious Disease & Immunology Events
1. **NIH-FDA Immunology Interest Group (IIG) seminar series**
   - Dates: January 14, 21, 28; February 4, 2026
   - Weekly series

2. **Demystifying Medicine - The Epidemic That Won't Quit: Unraveling the HIV Crisis**
   - Date: January 20, 2026
   - Topic: HIV/AIDS research

3. **70th Office of AIDS Research Advisory Council Meeting**
   - Date: January 29, 2026
   - Topic: HIV/AIDS policy and research

4. **Demystifying Medicine Series - Emerging and Re-Emerging Infectious Diseases: A Perpetual Challenge**
   - Presenter: Dr. Anthony Fauci (former NIAID Director)
   - Recent presentation (January 7, 2025)
   - Topics: Pandemic preparedness, disease emergence

### Notable Past Event Series

#### COVID-19 Content
- **NIH-FDA COVID-19 Lecture Series** - Multiple presentations on:
  - Coronavirus cell entry mechanisms
  - Genomic surveillance (SARS-CoV-2, mpox)
  - Vaccine development
  - Pandemic response

#### Pandemic & Preparedness
- Pandemic Influenza research
- SARS preparedness
- Bioterrorism response
- Emerging infectious diseases

#### Specialized Topics
- Division of Microbiology and Infectious Diseases Subcommittee meetings
- Clinical Center Grand Rounds (including infectious disease topics)
- LaMontagne Lecture Series (vaccines, pandemic response)

---

## 9. Search & Discovery

### Search Page
- **URL:** `https://videocast.nih.gov/Search`
- **Features:** Full-text search across event archive
- **Search Parameters:** Not fully documented

### Recommended Search Keywords for Disease Research
- "infectious disease"
- "virology"
- "immunology"
- "global health"
- "pandemic"
- "vaccine"
- "HIV/AIDS"
- "influenza"
- "coronavirus"
- "emerging diseases"

---

## 10. Technical Implementation Notes

### RSS Feed Consumption Best Practices

#### Polling Frequency
- **Recommended:** Respect TTL of 20 minutes
- **Minimum Interval:** 15-20 minutes
- **Upcoming Events:** Check hourly or daily depending on needs

#### XML Parsing Considerations
1. **HTML Entities:** Descriptions contain HTML-encoded content (`&lt;`, `&gt;`, `&quot;`)
2. **Custom Namespace:** Handle `Videocast:AirDate` element
3. **Date Parsing:** RFC 2822 format parsing required
4. **Character Encoding:** UTF-8

#### Feed Reliability
- **Government Site:** High reliability (.gov domain)
- **HTTPS:** Secure connections required
- **Uptime:** Generally stable but subject to government shutdowns
- **Update Consistency:** Regular updates, TTL indicates 20-minute cache

### Sample RSS Entry Structure
```xml
<item>
  <title>NIH-FDA Immunology Interest Group (IIG) seminar series</title>
  <link>https://videocast.nih.gov/watch=57201</link>
  <guid>57201@https://videocast.nih.gov</guid>
  <description>&lt;p&gt;Speaker: Jakob von Moltke&lt;/p&gt;</description>
  <author>Wed, 15 Jan 2025 13:00:00 GMT</author>
  <pubDate>Tue, 13 Jan 2026 20:03:00 GMT</pubDate>
  <category>Health</category>
  <Videocast:AirDate>Wed, 15 Jan 2025 13:00:00 GMT</Videocast:AirDate>
</item>
```

### Integration Recommendations

#### For Event Aggregation Systems
1. **Primary Data Source:** RSS feeds (most reliable)
2. **Polling Strategy:** Daily check of UpcomingEvents.asp
3. **Category Filtering:** Subscribe to specific category feeds (c=28 for Immunology, c=16 for Infectious Diseases)
4. **Deduplication:** Use GUID field for unique event tracking
5. **Date Handling:** Parse both `<author>` (air date) and `<pubDate>` (publication date)

#### For Calendar Integration
Since iCal is not available:
1. Parse RSS feeds
2. Convert to iCal format programmatically
3. Generate custom calendar feeds
4. Update calendar entries based on RSS TTL

#### For Content Discovery
1. **Keyword Monitoring:** Parse descriptions for disease-related terms
2. **Category Subscriptions:** Monitor specific category feeds
3. **Title Matching:** Filter by event series names (e.g., "Demystifying Medicine", "LaMontagne Lecture")

---

## 11. Limitations & Gaps

### Missing Features
1. **No iCal/ICS Support** - Calendar subscriptions not available
2. **No Public API** - RSS feeds only programmatic access
3. **Limited Category Documentation** - Not all category IDs publicly listed
4. **No Advanced Filters** - RSS feeds are category-based only
5. **No Event Status Updates** - Cancellations/rescheduling not reflected in RSS metadata
6. **Access Restrictions** - Some content marked "NIH Only" or "HHS Only"

### Data Quality Notes
1. **Category Breadth:** "Health" is used as catch-all category in some feeds
2. **Description Formatting:** HTML entities require parsing
3. **Time Zone:** All times in GMT/ET depending on context
4. **Update Lag:** RSS may not reflect real-time changes

---

## 12. Recommended Data Sources for Integration

### Priority 1: Essential Feeds
1. **Upcoming Events:** `https://videocast.nih.gov/rss/UpcomingEvents.asp`
2. **Immunology:** `https://videocast.nih.gov/rss/PastEvents.asp?c=28`
3. **Infectious Diseases:** `https://videocast.nih.gov/rss/PastEvents.asp?c=16`

### Priority 2: Supplementary Feeds
4. **All Events:** `https://videocast.nih.gov/rss/all.asp`
5. **NIH Director's Seminars:** `https://videocast.nih.gov/rss/PastEvents.asp?c=25`
6. **Clinical Center Grand Rounds:** `https://videocast.nih.gov/rss/PastEvents.asp?c=27`
7. **WALS:** `https://videocast.nih.gov/rss/PastEvents.asp?c=3`

### Priority 3: Monitoring Sources
8. **Main RSS Page:** `https://videocast.nih.gov/rss/` (for discovering new categories)
9. **Search Interface:** `https://videocast.nih.gov/Search` (for keyword-based discovery)
10. **Future Events Page:** `https://videocast.nih.gov/FutureEvents` (for browsing)

---

## 13. Contact & Support

### NIH VideoCast Support
- **Main Site:** `https://videocast.nih.gov/`
- **FAQ:** `https://videocast.nih.gov/Faq`
- **Support Link:** Available on main site
- **YouTube Channel:** `youtube.com/nihvcast` (1,129 videos)

### Related Resources
- **NLM RSS Feeds:** `https://www.nlm.nih.gov/listserv/rss_podcasts.html`
- **NIH Grants Podcasts:** `https://grants.nih.gov/news-events/podcasts/info-on-rss-and-podcasts`
- **NIH Calendar:** `https://calendar.nih.gov/`

---

## 14. Data Format Examples

### RSS Feed Headers (Typical Response)
```
Content-Type: text/xml; charset=utf-8
Server: Microsoft-IIS/10.0
Cache-Control: public
```

### Event Categories Found
Based on research, confirmed and suspected categories:
- Immunology (c=28)
- Infectious Diseases (c=16)
- Neuroscience (c=16)
- DNA Repair (c=5)
- Stem Cell (c=29)
- Proteomics (c=36)
- Bioethics (c=22)
- Lectures (c=124)
- NIH Director's Seminars (c=25)
- Clinical Center Grand Rounds (c=27)
- WALS (c=3)
- ORS and ORF - NIH Only (c=204)
- HIV/AIDS Research (ID unknown)
- Infection and Immunity (ID unknown)
- Global Health (ID unknown)
- COVID-19 (ID unknown)
- Health Disparities (ID unknown)

---

## 15. Summary & Recommendations

### Key Findings
1. **RSS Feeds Available:** Comprehensive RSS 2.0 XML feeds for upcoming and past events
2. **No iCal Support:** Calendar subscriptions not available natively
3. **No Public API:** RSS feeds are the primary programmatic access method
4. **Rich Metadata:** Event descriptions include presenter info, objectives, air dates
5. **Category System:** Topic-based filtering via URL parameters
6. **Update Frequency:** 20-minute TTL on feeds
7. **Large Archive:** 14,000+ events spanning years

### Best Integration Approach
For a seminar tracking system focused on infectious disease, virology, immunology, and global health:

1. **Poll Primary Feeds Daily:**
   - UpcomingEvents.asp for new scheduled events
   - Category-specific feeds (c=28, c=16) for topic filtering

2. **Parse RSS to Extract:**
   - Event title, description, air date, category
   - Speaker information from description field
   - Unique event ID from GUID/link

3. **Build Custom Calendar Layer:**
   - Convert RSS data to iCal format
   - Generate calendar subscription feeds
   - Provide email notifications for new events

4. **Keyword Filtering:**
   - Monitor descriptions for: "infectious disease", "virology", "immunology", "vaccine", "pandemic", "global health"
   - Flag relevant event series: "Demystifying Medicine", "LaMontagne Lecture", "IIG seminar"

5. **Handle Edge Cases:**
   - Parse HTML entities in descriptions
   - Handle "NIH Only" restricted content
   - Track event status changes via description updates

---

## Research Sources

- [NIH VideoCasting - RSS Feeds](https://videocast.nih.gov/rss/)
- [NIH VideoCast iTunes RSS Feeds](https://videocast.nih.gov/rss/itunes/)
- [NIH VideoCasting - Upcoming Events](https://videocast.nih.gov/FutureEvents)
- [NIH VideoCasting - Past Events](https://videocast.nih.gov/PastEvents)
- [NIH VideoCast](https://videocast.nih.gov/)
- [NLM RSS Feeds for News and Webcasts](https://www.nlm.nih.gov/listserv/rss_podcasts.html)

---

**End of Research Report**
