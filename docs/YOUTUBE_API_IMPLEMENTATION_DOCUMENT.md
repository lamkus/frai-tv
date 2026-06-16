# YouTube API Implementation Document
## remAIke Channel Manager - API Client Documentation

**Company:** skillbox.nrw GmbH  
**Contact:** Lars Malkus (contact@frai.tv)  
**Date:** December 28, 2025  
**API Project ID:** 827191956003  
**YouTube Channel:** @remAIke_IT (https://youtube.com/@remAIke_IT)

---

## 1. Executive Summary

The **remAIke Channel Manager** is an internal Node.js command-line tool developed by skillbox.nrw GmbH for managing the YouTube channel @remAIke_IT. This channel serves as a digital archive for public domain classic films from 1890-1960.

**Purpose:** Efficient batch management of 130+ video metadata and playlist organization.

**Access:** Internal use only - no public access, no external users.

---

## 2. Organization Overview

### 2.1 Company Information
- **Legal Entity:** skillbox.nrw GmbH
- **Address:** Im Springen 2, 58791 Werdohl, Germany
- **Website:** https://remaike.it
- **Media Portal:** https://frai.tv
- **Industry:** Media Production / Digital Film Archive

### 2.2 YouTube Presence
- **Channel:** @remAIke_IT
- **URL:** https://youtube.com/@remAIke_IT
- **Content:** Public Domain Classic Films (1890-1960)
- **Current Library:** 130+ videos
- **Categories:** Silent Films, Early Cinema, Classic Animation, Film Noir

---

## 3. API Client Architecture

### 3.1 Technical Stack
```
┌─────────────────────────────────────────────┐
│           remAIke Channel Manager           │
│              (Node.js CLI Tool)             │
├─────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │   OAuth 2.0 │  │  YouTube Data API   │  │
│  │   Handler   │  │       v3            │  │
│  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────┤
│              Local Database                 │
│         (Video Metadata Cache)              │
└─────────────────────────────────────────────┘
```

### 3.2 Technology Details
- **Runtime:** Node.js v20+
- **API Library:** googleapis (official Google API client)
- **Authentication:** OAuth 2.0 with offline access (refresh tokens)
- **Storage:** Local JSON files for metadata caching
- **Deployment:** Local development machine only

---

## 4. YouTube API Services Used

### 4.1 Endpoints and Quota Costs

| Endpoint | Method | Quota Cost | Use Case |
|----------|--------|------------|----------|
| `videos.list` | GET | 1 unit | Retrieve video metadata |
| `videos.update` | PUT | 50 units | Update titles, descriptions, tags |
| `playlists.list` | GET | 1 unit | List existing playlists |
| `playlists.insert` | POST | 50 units | Create new playlists |
| `playlistItems.list` | GET | 1 unit | List playlist contents |
| `playlistItems.insert` | POST | 50 units | Add videos to playlists |

### 4.2 Scopes Requested
```
https://www.googleapis.com/auth/youtube
https://www.googleapis.com/auth/youtube.force-ssl
```

---

## 5. Feature Documentation

### 5.1 SEO Optimization Module

**Purpose:** Batch update video metadata for improved discoverability.

**Workflow:**
1. Fetch current metadata via `videos.list`
2. Generate optimized titles, descriptions, and tags
3. Apply updates via `videos.update`

**Data Modified:**
- Video titles (localized for DE/EN)
- Video descriptions (structured format with timestamps)
- Tags (SEO-optimized keywords)
- Category assignment

**Example Update:**
```
Before: "Old Film 1920"
After:  "The Kid (1921) | Charlie Chaplin Classic | Full Movie HD | Public Domain"
```

### 5.2 Playlist Management Module

**Purpose:** Organize videos into thematic collections.

**Planned Playlists:**
- "Charlie Chaplin Collection"
- "Buster Keaton Classics"
- "Film Noir Essentials"
- "Vintage Animation (Fleischer/Van Beuren)"
- "Silent Film Era Masterpieces"

**Workflow:**
1. Check existing playlists via `playlists.list`
2. Create missing playlists via `playlists.insert`
3. Assign videos via `playlistItems.insert`

### 5.3 Metadata Audit Module

**Purpose:** Ensure consistency across all video metadata.

**Checks Performed:**
- Title format compliance
- Description structure validation
- Tag completeness
- Thumbnail presence
- Category accuracy

---

## 6. Data Handling

### 6.1 Data Retrieved from YouTube API
- Video IDs and metadata
- Playlist IDs and contents
- Channel statistics (own channel only)

### 6.2 Data Storage
- **Location:** Local machine only
- **Retention:** 30-90 days (cache refresh)
- **No cloud storage** of YouTube data
- **No sharing** with third parties

### 6.3 Data Display
- Internal CLI output only
- No public-facing interface
- No embedding on external websites

---

## 7. Authentication Flow

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│   User       │     │  Google OAuth   │     │  YouTube     │
│   (Admin)    │     │     Server      │     │    API       │
└──────┬───────┘     └────────┬────────┘     └──────┬───────┘
       │                      │                     │
       │  1. Start Auth       │                     │
       │─────────────────────>│                     │
       │                      │                     │
       │  2. Login + Consent  │                     │
       │<─────────────────────│                     │
       │                      │                     │
       │  3. Auth Code        │                     │
       │─────────────────────>│                     │
       │                      │                     │
       │  4. Access Token     │                     │
       │<─────────────────────│                     │
       │                      │                     │
       │  5. API Request      │                     │
       │──────────────────────────────────────────>│
       │                      │                     │
       │  6. Response         │                     │
       │<──────────────────────────────────────────│
```

### 7.1 Token Management
- Initial authorization: Manual (one-time)
- Token storage: Local encrypted file
- Token refresh: Automatic via googleapis library
- Token revocation: Available via Google Account settings

---

## 8. Quota Usage Analysis

### 8.1 Current Daily Usage (Estimated)
| Operation | Count | Quota/Op | Total |
|-----------|-------|----------|-------|
| videos.list | 130 | 1 | 130 |
| videos.update | 50 | 50 | 2,500 |
| playlists.list | 5 | 1 | 5 |
| playlists.insert | 2 | 50 | 100 |
| playlistItems.insert | 30 | 50 | 1,500 |
| **Daily Total** | | | **~4,235** |

### 8.2 Quota Increase Justification
- Current limit: 10,000 units/day
- Peak usage (full library update): ~8,000 units
- Requested: 50,000 units/day
- Reason: Allow complete library SEO updates in single session

### 8.3 Growth Projection
| Timeframe | Videos | Est. Quota Need |
|-----------|--------|-----------------|
| Current | 130 | 8,000/day |
| 6 months | 200 | 12,000/day |
| 12 months | 300 | 18,000/day |

---

## 9. Compliance

### 9.1 YouTube Terms of Service
- ✅ Only accessing own channel data
- ✅ No automated content uploads
- ✅ No scraping of other channels
- ✅ No monetization of API access
- ✅ Respecting rate limits

### 9.2 Data Protection (GDPR/DSGVO)
- No personal user data collected
- No viewer tracking beyond YouTube Analytics
- All data processing within EU

### 9.3 Content Policy
- All uploaded content is verified Public Domain
- Films from 1890-1960 with expired copyrights
- No copyrighted material

---

## 10. Screenshots / CLI Output Examples

### 10.1 SEO Update Command
```bash
$ node youtube_studio_bot.mjs seo --limit=5

🤖 YouTube Studio Bot - SEO Optimization
════════════════════════════════════════

📊 Fetching videos from channel @remAIke_IT...
✅ Found 130 videos

📝 Processing video 1/5: FG-vqRH5Cg4
   Title: "Chaplin Marathon" → "Charlie Chaplin Film Festival | 8 Classic Shorts | Silent Comedy"
   Tags: +15 SEO keywords added
   ✅ Updated successfully

📝 Processing video 2/5: Qm3K0-XL46Q
   Title: "Kirby Collection" → "Kirby's Fairytale Classics | Vintage Animation Collection"
   Tags: +12 SEO keywords added
   ✅ Updated successfully

[...]

════════════════════════════════════════
✅ SEO update complete: 5/5 videos processed
   Quota used: 255 units
```

### 10.2 Playlist Creation Command
```bash
$ node youtube_studio_bot.mjs playlists

🎬 Playlist Manager
════════════════════════════════════════

📋 Existing playlists: 3
📋 Creating new playlist: "Film Noir Collection"
   ✅ Created: PLxxxxx
   Adding 12 videos...
   ✅ All videos added

════════════════════════════════════════
✅ Playlist management complete
   Quota used: 650 units
```

---

## 11. Contact Information

**Technical Contact:**
- Name: Lars Malkus
- Email: contact@frai.tv
- Role: Managing Director / Developer

**Company:**
- skillbox.nrw GmbH
- Im Springen 2
- 58791 Werdohl
- Germany

**YouTube Channel:**
- https://youtube.com/@remAIke_IT

**Websites:**
- https://remaike.it (Company)
- https://frai.tv (Media Portal)

---

## 12. Appendix

### A. API Client Source Repository
Internal GitLab repository (not public)

### B. Dependencies
- googleapis: ^140.0.0
- playwright: ^1.40.0 (for YouTube Studio automation fallback)

### C. Version History
- v1.0 (2025-10): Initial release
- v1.1 (2025-11): Added playlist management
- v1.2 (2025-12): SEO optimization improvements

---

*Document prepared for YouTube API Services quota increase request*
*skillbox.nrw GmbH © 2025*
