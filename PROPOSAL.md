<!-- markdownlint-disable MD024 -->
# BookMyPlayer — UI Changes for 5 AI Features

**Ansh Baheti** · AI Internship Assignment
**Live Demo:** <https://techcodie.github.io/bookmyplayer-mockups/>

> The Live Demo is an interactive HTML page showing each of the 5 proposed AI features as annotated UI mockups on top of the BookMyPlayer interface. Every change is marked with a numbered callout (①②③…) and explained inline — so you can see exactly *what* changes on screen and *why*.

This doc is the short companion: the **UI changes** and **how I'd implement** each one in bullet form. Detailed reasoning lives in the Live Demo callouts.

---

## 01 · AI Video Skill Analysis

### UI changes

- New analysis screen: video player with AI pose skeleton overlay (red joints mark issues)
- Clickable timestamped issue list — jumps the video to that frame, shows AI confidence %
- Skill score + peer percentile (e.g. "78 — Top 22% of U18 in Mumbai")
- Auto-matched drills targeting the session's weakest metric
- "Book a coach for these gaps" CTA at the bottom

**How I'd implement**

- MediaPipe for pose estimation (runs on-device, low GPU cost)
- PyTorch for the sport-specific skill model
- OpenCV for frame extraction and preprocessing

---

## 02 · WhatsApp AI Engagement

### UI changes

- Branded chat with clear "auto-reply by AI" tag (transparency)
- Proactive first message when a user views an academy on the site but doesn't inquire
- Replies pull live data (slots, coach, fees) — no generic responses
- Booking confirmation rendered as a structured card, not free text
- Academy dashboard shows the full thread + AI intent score

**How I'd implement**

- WhatsApp Business API as the channel
- Claude API + RAG over academy data for grounded replies
- Deterministic workflow for booking & reminders (never let the LLM book)

---

## 03 · AI Lead Scoring & Academy Intelligence

### UI changes

- New academy dashboard view: leads sorted High / Medium / Low
- Numeric score + 🔥 tier badge per lead
- "Why this score" chips visible inline ("4 videos watched · compared 3 academies")
- AI nudge card with quantified suggestion ("reply <1h → +22% conversion")
- One-click filter to focus on high-intent leads only

**How I'd implement**

- XGBoost trained on behavioral logs (views, repeat visits, profile completion)
- SHAP values to surface the top features behind each score (explainability)
- scikit-learn for feature engineering and evaluation pipelines

---

## 04 · AI-Personalized Feed

### UI changes

- Dynamic homepage headline per user ("Sharpen your cover drive" vs "Quick reflexes for matchday")
- Academy cards ranked by % fit, not just rating
- Drills surface based on the user's last video analysis
- Tournaments show eligibility ("You qualify") and urgency ("3 days left")
- Same template, different content per user

**How I'd implement**

- pgvector at the start (simple, cheap)
- OpenAI embeddings of user behavior + content
- Ranking layer trained on engagement signals
- Migrate to Pinecone once retrieval latency matters

---

## 05 · AI Co-Pilot for Academies

### UI changes

- Weekly AI briefing card framed in rupees ("3 leads dropped — ~₹36k impact")
- AI-drafted reply box with Send / Edit / Regenerate buttons
- Profile improvement checklist with expected lift on each item ("+2.3× inquiries")
- Inquiry heatmap (day × hour) so academies know when to be online
- Long-tail tactical nudges feed (waitlists, photo pinning, promo timing)

**How I'd implement**

- Claude API for briefings and reply drafts
- RAG over academy's own data (every output cites their numbers)
- Weekly batch analytics pipeline (real-time isn't needed at the start)

---

## Suggested build order

1. **Video Analysis** — highest defensibility, start narrow (one sport)
2. **Lead Scoring** — quickest academy ROI, can be built in parallel
3. **WhatsApp AI** — best after Lead Scoring so the bot prioritizes correctly
4. **Personalized Feed** — needs the behavior data the first three generate
5. **Academy Co-Pilot** — sits on top of all four

---

**Mockups:** <https://techcodie.github.io/bookmyplayer-mockups/>
**Source:** <https://github.com/techcodie/bookmyplayer-mockups>
