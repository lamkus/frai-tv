This is a critical finding. The current `robots.txt` in the worktree **blocks the live-retrieval/citation bots** (`ChatGPT-User`, `PerplexityBot`) — directly contradicting the GEO finding and the project's own stated strategy. The current metadata script also has problems (12 hashtags, `00:00` placeholder chapters that fail YouTube's ascending-order validation, no recordingDate, no localization). I have enough grounding. Here is the synthesis.

---

# remAIke.TV Deterministic Metadata & Features Schema (v1)

Evidence-anchored. Every field gives: **rule/format**, **why (finding)**, **priority**, **surface** (YouTube Data API v3 / Studio-only / Website). Citations reference the findings JSON by dimension.

Two metadata profiles run in parallel: **LONG-FORM** (flagship restorations + compilations) and **SHORTS** (cut from flagship). They are scored by separate models — never reuse packaging wholesale (algorithm finding: Shorts/long-form decoupled).

---

## 0. Load-bearing prerequisites (set these or everything downstream breaks)

| Field | Rule | Why | Pri | Surface |
|---|---|---|---|---|
| `defaultLanguage` (snippet) | REQUIRED, validated, non-blank. Set to actual spoken language (`de` for Wochenschau narration, `en` for English cartoons). Fail pipeline if blank/auto-detect-only. | Original language is the keystone for auto-dub eligibility/quality, caption accuracy, and viewer routing. Wrong source = garbled dubs served by default. (multilang) | **P0** | API |
| `defaultAudioLanguage` (snippet) | REQUIRED. Match the audio track's actual language. | Same keystone; routes correct base track. (multilang) | **P0** | API |
| Auto-dubbing channel toggle | EXPLICITLY set (Studio → Settings → Content → Automatic dubbing). Do NOT leave to default — it defaults **ON**. Decision per channel; log state. | Auto-dub is ON by default for all creators (27 langs, Feb 2026). Ignoring it = AI dubs served automatically. (multilang) | **P0** | Studio-only |
| Auto-dub eligibility pre-flag | Flag videos that will NOT dub: >120 min, music-only/no speech (Soundies!), undetectable language. | Soundies (51) and some compilations are music/no-speech → never dub. Don't expect tracks that can't generate. (multilang) | **P1** | pipeline |

---

## 1. Title

**Rule (LONG-FORM):**
- Hard cap **≤100 chars** (Studio enforced); **target 40–60 chars**.
- **Front-load the famous entity + emotional/curiosity hook in first ≤50 chars** (survives mobile truncation ~48–55). Validate primary-entity first-char index `< 55`; reject if entity only appears after char 60.
- Format: `{EntityName} {Hook} ({Year}) [{RestorationTag}]` — e.g. `Hindenburg Disaster — Last Footage (1937) | 8K Restored`.
- **Surface-aware variant logic:** search-skewed videos (entity+year queries) → keyword-forward; browse/suggested-skewed → curiosity/packaging-forward. Tag each video with dominant traffic source from Analytics and pick accordingly.
- **Accuracy guard (blocking):** reject any title whose claim isn't supported by transcript/chapters. Misleading titles are penalized + risk Dec-2024 misleading-metadata enforcement.

**Why:** 100-char hard limit; ~48–55 mobile truncation; front-loading correlates with rank (metadata). Famous-entity front-loading is the British Pathé win — canonical figures/disasters dominate; obscure-topic titles underperform ~500x (archival). Surface-specific titles (algorithm). Accuracy required (algorithm + thumbnails enforcement).

**Pri P0. Surface: API.** Title length is genuinely unsettled — default to 40–60 but treat "70–100 wins" as an A/B hypothesis only via Test & Compare, never the pipeline default.

**FIX in current script:** `${title} | 8K Restoration (${year})` buries the entity behind the original title and appends boilerplate that eats the mobile-visible window. Move RestorationTag to the end and guarantee entity is char-0.

---

## 2. Description

**Structure (deterministic 5 blocks):**

1. **Line 1 (≤125 chars, before "Show more" fold):** benefit/hook sentence containing primary entity + year, human-readable. Must contain the canonical brand string `remAIke.TV` once.
2. **Block 2 (2–3 sentences):** natural-language summary with 1–2 secondary keywords (synonyms, NOT repetition). **GEO value-add (template-insert):** ≥1 verifiable **statistic with cited source** + ≥1 short **attributed quotation** where relevant + ≥1 **outbound citation** to an authoritative source (e.g., the archive/Wikipedia entry). This is the same text auto-dub and auto-translate consume.
3. **Block 3 — Chapters** (see §5).
4. **Block 4 — Links/CTA:** subscribe link, frai.tv watch-page link (brand mirror), licensing/contact line for press re-users.
5. **Block 5 — Hashtags** (see §4).

**Hard rules:** total ≤5000 chars. Primary-keyword mentions capped at 1–2 (flag/reject if exact phrase repeats ≥3× or keyword density >3%). Prefer semantic variants over repetition.

**Why:** First ~150 chars are weighted + previewed; descriptions feed suggested-video matching (metadata). Keyword stuffing = zero search-rank correlation + spam risk (metadata). Quotations (~+41%), statistics (~+31–40%), cited sources (~+30–40%) measurably lift generative-engine citation; stuffing *reduces* it (GEO, peer-reviewed KDD). Brand string in description is the strongest AI-visibility predictor (~0.74 corr) (GEO/Ahrefs).

**Pri P0. Surface: API.**

**FIX:** current script dumps `00:00` placeholder chapters and a footer of editor notes into the live description — placeholders fail chapter validation; notes pollute the weighted first-fold region.

---

## 3. Tags

**Rule:** Auto-generate **5–8 tags max**. Always include: primary entity, channel brand `remAIke.TV` / `@remAIke_IT`, and 1–2 **common misspellings/variant spellings** (e.g. `Krtek`/`Maulwurf`, `Betty Boop`/`Bettie Boop`). Then stop. Hard-cap the field; no competitor-tag scraping, no keyword stuffing.

**Why:** YouTube official: tags "play a minimal role… primarily used to correct common spelling mistakes." 1.3M-video studies = weak/marginal correlation (metadata/algorithm). The channel already has 10× "too many tags" defects (project audit) — this rule fixes that.

**Pri P2. Surface: API.**

---

## 4. Hashtags

**Rule:** **3–5 hashtags total**, placed in description Block 5. **Order matters** — the 3 most relevant/engaging go FIRST (only the first 3 render as clickable links above the title). Include one brand hashtag. Hard guardrail at **60** (the real ignore-threshold), but never approach it.

**Why:** Only first 3 surface above title → order is functional. 60 is the real limit; the "15-hashtag cliff" is folklore (metadata, myth-busted). 3–5 preserves relevance.

**Pri P1. Surface: API (description field).**

**FIX:** current script emits up to **12 hashtags** (`tags.slice(0,12)`) plus 3–4 hardcoded ones — dilutes relevance and wastes the above-title slots. Cap at 5, order by relevance.

---

## 5. Chapters

**Rule (machine-validated, BLOCKING):**
- `≥3` timestamps; first line **exactly `0:00`**; strictly ascending; each gap `≥10s`; format `M:SS`/`H:MM:SS`.
- Chapter naming for compilations: **`{Entity} {Year}`** (e.g. `01:12 Churchill VE Day 1945`). Write the same entity+year strings into description Block 2.
- Generate from the real cut-list; **never publish `00:00` placeholders**.

**Why:** YouTube's exact published spec (metadata). Per-chapter deep-linking surfaces individual segments as Google "key moments" — each segment of an hour-long Wochenschau becomes independently discoverable by entity/year query (archival, high-leverage). Also supports "satisfied completion" self-service navigation (algorithm).

**Pri P0. Surface: API (description).**

**FIX:** current fallback writes six `00:00` lines → not ascending → chapters silently fail. Block publish when no real cut-list exists rather than emitting placeholders.

---

## 6. recordingDate & category

| Field | Rule | Why | Pri | Surface |
|---|---|---|---|---|
| `recordingDate` (snippet) | Set to the **original footage date** (the historical year/date), not upload date. ISO 8601. | Surfaces accurate historical provenance; reinforces entity+year discoverability for archival material. (archival entity strategy) | **P1** | API |
| `categoryId` | Wochenschau/newsreels → `25` News & Politics or `27` Education; cartoons → `1` Film & Animation; Soundies (music) → `10` Music (also Charts-eligible). Deterministic map by series. | Charts replaced Trending; Music/Podcast back-catalog is Charts-eligible — only category where Charts targeting is real. (algorithm) | **P1** | API |

---

## 7. Captions (the multilingual keystone after audio-lang)

**Rule:** For every video with speech, **upload a corrected native-language caption file (SRT)** — do not rely on raw auto-captions. Bake "upload corrected SRT" into the publish checklist. Skip for Soundies/music-only.

**Why:** A clean source caption is the prerequisite that unlocks viewer auto-translate into 100+ languages AND improves auto-dub accuracy (raw auto-captions 70–90%). (multilang) Community/crowdsourced captions are dead (Sept 2020) — must be creator-driven.

**Pri P1. Surface: API (captions.insert).**

---

## 8. Multi-language audio & localizations

| Feature | Rule | Why | Pri | Surface |
|---|---|---|---|---|
| Auto-dub QA (per high-traffic lang) | **Gated/blocking step:** preview auto-dub + review transcript for the channel's top target langs (esp. **German** — country DE). If robotic/wrong → disable that language or replace with custom track. | Dub is served **by default** based on viewer history; viewers have no global off-switch. A bad default dub tanks AVD in that language. (multilang) | **P0** | Studio-only |
| Custom dub override | To replace a bad auto-dub: **delete the auto-dub for that language FIRST**, then upload audio-only file (Studio → Languages → Add → Dub). Requires Advanced Features. | Custom tracks don't auto-generate; override requires delete-first. (multilang) | **P2** | Studio-only |
| Per-language AVD monitor | Track AVD per audio language; if a dubbed lang materially underperforms original → disable/replace. | Official "no discovery harm" is about the *original*; retention within a bad track still suffers. (multilang) | **P1** | API (Analytics) |
| `localizations` (titles/descriptions) | Add localized title+description for **top 3–5 audience languages** (DE/EN/FR already have locale files on the site). Don't promise a % lift. | Real discoverability hygiene under audio dubbing; the "+15% watch time" figure is unverified folklore. (multilang) | **P2** | API (videos.update localizations) |

---

## 9. Thumbnail

**Rule (generation linter, all blocking):**
- Resolution **1920×1080 or 3840×2160**, 16:9, width ≥640, **<2 MB**, prefer **PNG** for crisp text. (Not 1280×720 — that's the minimum baseline.)
- **≤3 words / ≤12–15 chars** of on-image text. Reject if exceeded.
- **≤3 focal visual elements**, single dominant focal point, enforced min luminance-contrast subject-vs-background.
- **Mobile legibility gate:** downscale to ~160×90 and check text readability before upload.
- **Truthfulness check (blocking):** thumbnail text/imagery must be supported by actual video content (critical for any news framing → Wochenschau).
- **Faces:** do NOT hardcode "always include a face." Make face vs. faceless a per-niche **A/B hypothesis** via Test & Compare.

**Selection rule:** generate up to **3 variants**, submit to native **Test & Compare**; keep the **watch-time-share winner — never the highest-CTR variant**. If a high-CTR variant has lower watch-time share, discard it. On "Inconclusive," keep default (order strongest variant first → it wins ties).

**Why:** Official 3840×2160 spec, 2MB limit (thumbnails). ≤3-words + high-contrast + ≤3-elements = mobile legibility where most viewing happens (thumbnails). Misleading thumbnails removed since Dec 2024 (thumbnails). Faces don't universally help — 300k-video study (thumbnails). Test & Compare optimizes **watch-time share over CTR** — the single load-bearing fact (thumbnails + algorithm).

**Pri P0 (spec/linter), P1 (Test & Compare loop). Surface: thumbnail upload = API; Test & Compare = Studio-only, desktop, long-form/public/non-MFK only.**

**Never** trigger a thumbnail replace purely because absolute CTR is below an arbitrary number (e.g. 5%) — segment by traffic source, compare only to same-video variants + channel median.

---

## 10. End screens, cards & playlists (session engine)

| Feature | Rule | Why | Pri | Surface |
|---|---|---|---|---|
| End screens | EVERY long-form upload gets an end screen pointing to **1 "next logical video"** (next chronological episode / same-entity follow-up) + best-fit playlist. | Session contribution is a real signal; binge paths capture new-viewer back-catalog binging. (algorithm) | **P0** | Studio-only (end screens not in public API) |
| Cards | Add 1–2 cards to high-retention related back-catalog videos at natural lulls. | Session continuation. (algorithm) | **P2** | API (limited) / Studio |
| Playlists | Auto-assign every video to ≥1 **tight topical playlist** by series+chronology (Betty Boop chrono, Wochenschau by year, etc. — schemas already exist in workspace). Build binge chains. | Playlists chain back-catalog for binge + session value; re-recommendation of old videos is real. (algorithm + archival) | **P1** | API (playlistItems.insert) |

---

## 11. Shorts profile (separate model)

**Rule:** Auto-cut **1–3 Shorts per flagship** from the most dramatic 15–45s archival moment (disaster / famous face / shocking reveal). Hook in first 1–2s, designed for **loop/replay + share**. Minimal reliance on description/tags. Distinct title/thumbnail — do NOT reuse long-form packaging. End-screen/pinned-comment link to the full long-form. Track via "traffic source: Shorts feed," not Shorts view count.

**Why:** Shorts ranked by separate model (swipe/loop/share) (algorithm). Shorts = cheap top-of-funnel awareness; weak long-form conversion; Shorts watch-time does NOT count toward the 4,000-hr long-form monetization threshold (archival). Don't chase Shorts volume as a KPI.

**Pri P1. Surface: API upload + Studio.**

---

## 12. Monetization gate (archival-specific, BLOCKING)

**Rule:** Every upload must populate ≥1 **added-value field** or publish is blocked:
(a) original commentary/historical context, (b) `restoration_applied` note (denoise/upscale/colorize), or (c) educational framing (dates/sources/significance) as on-screen lower-third **and** in description. Surface restoration in title/thumbnail (`4K Restored`, `Colorized 1937`). Avoid identical template narration across many videos (inauthentic-content trigger).

**Why:** Public-domain status does NOT grant monetization; reused-content policy bars footage "with no added value"; enforcement is **channel-level** (single biggest risk). AI restoration counts as the "substantive modification" the policy requires. (archival)

**Pri P0. Surface: pipeline gate + API metadata + Studio (on-screen).**

---

## 13. Community & cross-posting

| Feature | Rule | Why | Pri | Surface |
|---|---|---|---|---|
| Cadence | Fixed **weekly** publish cadence + auto-distribute each upload to socials + newsletter with the same entity-keyword title. | Documented British Pathé success factor. NOTE: cadence builds habit, it is NOT an algorithmic ranking signal (don't oversell it). (archival + algorithm myth) | **P1** | Website/external |
| Brand-mention seeding | Seed authentic, non-spammy `remAIke.TV` mentions + helpful answers on Reddit/Quora + history forums. Never buy/automate fake mentions. | Brand mentions (esp. YouTube + community platforms) are ~3× stronger AI-visibility predictors than backlinks; community platforms disproportionately cited. (GEO) | **P1** | External |
| "Archives Picks" appetizer track | Maintain a short best-of compilation track aimed at press/re-users with licensing/contact info in description. | Documented secondary discovery+revenue funnel. (archival) | **P2** | YouTube + Website |
| Brand-string consistency | Put canonical `remAIke.TV` / `@remAIke_IT` **verbatim** in every title, description, spoken intro (for transcript capture), and mirror exactly on every frai.tv page. | Strongest AI-citation predictor is the machine-extractable brand string in text. (GEO) | **P0** | API + Website |

---

## 14. frai.tv / GEO bridge

| Item | Rule | Why | Pri | Surface |
|---|---|---|---|---|
| **robots.txt — UNBLOCK retrieval bots** | **CRITICAL FIX.** Current worktree `robots.txt` (lines 46–50) `Disallow: /` for `ChatGPT-User` and `PerplexityBot` — these are the **live-citation** bots. Change to **Allow** OAI-SearchBot, ChatGPT-User, PerplexityBot, Claude search bots, Googlebot, Bingbot. Keep training-bot policy a *separate explicit* decision (may Disallow GPTBot/Google-Extended/ClaudeBot/CCBot to opt out of training — that has little citation downside). | Blocking the **search/retrieval** bots forfeits AI citation eligibility entirely. Blocking *training* bots is the only defensible block. Current file conflates them and kills the GEO strategy. (GEO, high-confidence) | **P0** | Website |
| Indexability CI gate | Every watch/catalog page must: return 200, be in XML sitemap, not noindex, not robots-blocked, have unique meta description + crawlable HTML body. CI fails build otherwise. NOTE: site is React SPA with no SSR (project) — crawlers may see empty HTML; this gate must verify **rendered** body text reaches crawlers (prerender/SSG the watch pages). | Google AI Overviews eligibility = standard indexability; no special file/markup needed. SPA-no-SSR is the actual blocker. (GEO + project) | **P0** | Website |
| VideoObject schema | Emit valid `VideoObject` (name, description, thumbnailUrl, uploadDate, duration, embedUrl, chapters via `Clip`/`SeekToAction`) per watch page. Values MUST match visible text. Validate in CI. | Earns traditional video rich results + clean machine-readable facts/transcripts. NOT a guaranteed AI booster — don't market it as one. (GEO, low-confidence on AI lift) | **P1** | Website |
| Recency / dateModified | Emit accurate `datePublished`/`dateModified` in markup + visible text. Genuinely refresh high-value series/Wochenschau archive pages on a schedule. No fake date-bumping. | Recently updated pages are crawled/cited disproportionately by AI engines. (GEO) | **P1** | Website |
| IndexNow on publish | POST every new/updated URL to IndexNow (key file already at root) on each deploy. Expect benefit for ChatGPT-Search/Copilot/Bing **only**. Verify site in Bing Webmaster Tools. | IndexNow feeds Bing-cluster (which ChatGPT Search/Copilot use). **Google does NOT support it** — set expectations. (GEO) | **P1** | Website |
| Wikimedia Commons + Wikipedia | Upload public-domain **source file to Commons** (rich Structured Data + categories). Separately link the restored YouTube version in the relevant Wikipedia article's **infobox/external-links** area (CTR ~2.47%), NOT as a buried inline reference (~0.03%). Commons does NOT embed YouTube. | Authority + AI-citation surface, not high-volume traffic (~0.9% overall CTR). Placement determines the 10–80× CTR gap. (archival) | **P2** | External |
| **Remove llms.txt as a "GEO win"** | Stop treating `llms.txt` as a citation lever. Keep only as near-zero-cost optional artifact. **Update MEMORY.md** which currently lists it as a GEO measure. | 137k-domain study: 97% of llms.txt files got zero AI-bot requests; Google explicitly won't support it. (GEO, high-confidence) | **P1** | Website + memory |

---

## DO NOT bother (debunked folklore — actively remove from pipeline/team guidance)

1. **The "15-hashtag cliff."** Real ignore-threshold is 60. The number 15 appears nowhere in policy. (current script's 12-hashtag dump is symptomatic over-engineering of the wrong field.)
2. **Keyword-stuffed tag lists / competitor-tag scraping.** Tags are misspelling insurance only; 5–8 max. (Reallocate to title/thumbnail/first-15-words.)
3. **Description keyword stuffing.** Zero search-rank correlation; risks spam flags AND reduces generative-engine citation.
4. **"Longer titles (70–100 chars) reliably win."** Unverified low-authority claim contradicting the two largest studies. Default 40–60; test long only via Test & Compare.
5. **Optimize-for-Trending-tab logic.** Trending page + Trending Now retired July 2025. Target personalized recs/search/Shorts + relevant Charts only.
6. **"Wait 24–48h before going public so the algorithm understands it."** False per YouTube. Publish when ready.
7. **The "24-hour make-or-break velocity window."** No kill switch; evergreen archival can sleep then resurge via seasonality/binging — build a back-catalog refresh job instead.
8. **"Maximize CTR at all costs / punchiest thumbnail always wins."** Ranking predicts watch time, not click prob; Test & Compare picks watch-time-share. A high-CTR/low-AVD variant is a NET NEGATIVE — reject it.
9. **"Always put a big emotional face in the thumbnail (+20–30% CTR)."** Single-vendor, uncorroborated; 300k-video study found parity. A/B it.
10. **"1280×720 is the recommended thumbnail resolution."** It's the minimum. Render 1920×1080 / 3840×2160.
11. **"More subscribers / consistent schedule is itself a ranking factor; one flop hurts the whole channel."** Ranking is video+audience-level. Cadence aids habit, not ranking. (Don't oversell weekly cadence as algorithmic.)
12. **"Longer compilations always win on raw watch time."** Satisfaction-weighted; padded long videos lose to tight high-retention ones. Curate compilations around famous-entity demand, not length.
13. **"Shorts will funnel watch time into long-form monetization."** Separate systems; Shorts watch-time doesn't count toward the 4,000-hr threshold. Shorts = awareness only.
14. **"Just upload public-domain footage as-is and monetize it."** Public-domain ≠ monetizable; needs added value or channel-level demonetization.
15. **GEO: llms.txt / special "AI files" / AI-specific markup / content "chunking" / schema as a guaranteed AI-citation booster.** None move Google AI surfaces; eligibility = normal indexability. Remove llms.txt from MEMORY.md's GEO list.
16. **"IndexNow speeds up Google/Gemini indexing."** Google doesn't support IndexNow. Bing-cluster only.
17. **"Translating titles/descriptions = +15% watch time" / "community will crowdsource translations."** The 15% figure is unsourced folklore (the proven driver is multi-language **audio**, 25%+); community contributions were killed in 2020.
18. **"Backlinks are the dominant AI-citation authority signal."** Backlinks ~0.22 corr vs brand/YouTube mentions ~0.66–0.74. Prioritize machine-extractable brand mentions.

---

## Three concrete code deltas in this worktree (highest ROI, ordered)

1. **`code/frontend/public/robots.txt` (P0):** flip `ChatGPT-User` and `PerplexityBot` from `Disallow: /` to `Allow: /`; add explicit `Allow` for `OAI-SearchBot`, `Googlebot`, `Bingbot`, Claude search bots; keep `GPTBot`/`CCBot`/`Google-Extended`/`ClaudeBot`/`Bytespider` as the *deliberate* training-opt-out block. This file currently sabotages the entire GEO bridge and contradicts the project's own documented strategy.
2. **`code/frontend/scripts/generate-youtube-metadata.mjs` (P0):** (a) cap hashtags at 5 ordered by relevance (currently 12); (b) never emit `00:00` placeholder chapters — block/skip when no real cut-list exists; (c) restructure description so the brand string + hook + entity+year are in line 1 (<125 chars) and editor "Notes" footer is removed from the live field; (d) move `| 8K Restoration` to the end so the entity is char-0 in the title.
3. **Add to the pipeline (P0):** required-and-validated `defaultLanguage`/`defaultAudioLanguage`, an explicit auto-dub channel-toggle decision + German-dub QA gate, and the added-value monetization gate.

Relevant files: `D:\remaike.TV\.claude\worktrees\exciting-golick\code\frontend\public\robots.txt`, `D:\remaike.TV\.claude\worktrees\exciting-golick\code\frontend\scripts\generate-youtube-metadata.mjs`, and the memory file `C:\Users\T1mbox\.claude\projects\D--remaike-TV\memory\project_geo_indexing.md` (llms.txt claim needs correction).