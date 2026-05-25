# BookMyPlayer — AI Feature Proposal

**Submitted by:** Ansh Baheti
**For:** AI Internship Assignment
**Live mockups:** https://techcodie.github.io/bookmyplayer-mockups/

---

## Approach

I spent time exploring BookMyPlayer before writing this. Some of what follows is observation, some of it is informed guessing — I haven't seen the internal data yet, so I want to be upfront that this is an outsider's view, written by someone who would genuinely love to work on this product.

From what I can see, the platform already does the hard part well — it connects players and parents to academies, and it has built real coverage across sports. The opportunity I would focus on, if I joined, is the layer on top of this. The layer that decides:

- whether users come back next week, not just today
- whether academies actually convert the leads they get
- whether AI becomes the core of the product, not a small feature on the side

These three things are connected. If users don't come back, academies don't get leads. If academies don't convert leads, they leave the platform. And if AI is just a side feature, neither side improves over time.

So instead of treating AI as a list of features to add, I would treat it as the connective layer between **user engagement, player growth, and academy revenue.**

This document describes five AI systems I'd want to explore — with visual mockups for each at the link above.

---

## The five AI systems

Each section below maps to one screen in the live mockup. Numbered callouts (①②③④⑤) in the mockup are explained inline here.

| # | Feature | Side | What it does |
|---|---------|------|--------------|
| 01 | AI Video Skill Analysis | Player | Frame-by-frame skill report in 60s |
| 02 | WhatsApp AI Engagement | Player | Books trials inside WhatsApp |
| 03 | Lead Scoring & Intelligence | Academy | Ranks every inquiry with reasons |
| 04 | Personalized Feed | Player | Homepage adapts to user's sport & history |
| 05 | Academy Co-Pilot | Academy | Weekly AI briefings + reply drafts |

---

## 01 · AI Video Skill Analysis  *(flagship)*

**Pitch.** A player uploads a 30-second clip. The system returns a frame-by-frame breakdown — posture, balance, timing, technique — within 60 seconds, mapped to drills and academies.

**Why this one first.** Most features (recommendations, personalized feeds, WhatsApp, lead scoring) can be copied by competitors. AI-based sports video analysis is genuinely difficult to build well, and currently no Indian sports platform is doing it properly. It also:

- Gives users a reason to come back regularly
- Creates strong engagement loops
- Generates unique sports-performance data
- Creates viral sharing opportunities
- Becomes the base for later talent scouting

**What the mockup shows:**

- ① **Pose-overlay video** — skeleton drawn on the player's clip; red joints mark issues. Makes the AI verdict visible, not just a number.
- ② **Timestamped issue list** — every flagged event is clickable and jumps the video to that frame. Confidence % is shown so the user can judge the AI.
- ③ **Skill score with peer percentile** — "78" alone is meaningless. "Top 22% of U18 in Mumbai" turns it into a benchmark and drives competitive return visits.
- ④ **Drills auto-matched to weakness** — not generic drills; the two that target this session's weakest metric. Closes the loop: diagnosis → fix.
- ⑤ **Coach booking CTA** — converts the AI insight into academy revenue in one tap.

**Tech I'd explore.** MediaPipe for pose estimation (efficient on-device), PyTorch for custom sports-movement models trained on Indian footage, OpenCV for frame extraction and preprocessing.

**Business impact.** Higher retention, viral sharing of skill scores, a proprietary data moat that compounds with every uploaded clip.

---

## 02 · WhatsApp AI Engagement

**Pitch.** Indian parents live on WhatsApp. The bot continues the conversation after the user leaves the website — qualifies intent, books trials, sends reminders. Hands off to a human only when AI confidence drops.

**Why it matters.** Right now, once users leave the website, communication usually stops — and that's where many inquiries and trial bookings are probably getting lost.

**What the mockup shows:**

- ① **Branded auto-reply identity** — "auto-reply by AI" is transparent. Parents see immediately who they're talking to. Builds trust, avoids the "fake human" creepiness.
- ② **Proactive re-engagement** — triggered when a user views an academy on the site but doesn't inquire. Catches drop-offs in the most-used app in India.
- ③ **Grounded, specific replies** — slot count, coach name, time options pulled from the academy database via RAG. No hallucination.
- ④ **Booking as a structured card** — confirmation isn't free-text; it's a rendered card the parent can show at the gate. The reminder is scheduled deterministically.
- ⑤ **Three-stage pipeline** — intent → retrieval → action. Each stage is logged so failures can be debugged exactly where they happened.
- ⑥ **Academy gets the thread + intent score** — connects to Feature 03: academies don't get a raw message, they get a triaged lead with full conversation history.

**Tech I'd explore.** WhatsApp Business API for the channel (already native to how Indian users communicate), Claude API + RAG over the academy database for grounded responses, and deterministic workflows for the booking and reminder steps. Never let the LLM book a slot.

**Business impact.** Higher inquiry-to-conversion, dramatically faster response times, better academy trust because pre-qualified leads land in the dashboard.

---

## 03 · AI Lead Scoring & Academy Intelligence

**Pitch.** Every inquiry looks the same in a form. Behaviorally, a parent who watched four videos and compared three academies is nothing like one who bounced after eight seconds. This view ranks every lead — with reasons academies can trust.

**The problem this solves.** One of the biggest academy-side problems is that every inquiry looks similar on the surface. Serious parents and casual browsers submit the same form. Academies waste time on tire-kickers and miss the high-intent ones.

**What the mockup shows:**

- ① **Tier filters (High / Medium / Low)** — academies focus their day on the nine high-intent leads, not 42 mixed ones. One-click filter.
- ② **Lead profile context** — parent vs. player, age, neighborhood — surfaced inline so the academy can personalize the reply.
- ③ **Numeric score + tier badge** — "94" with a 🔥 badge anchors urgency. Color-coded so it's scannable from across the room.
- ④ **Why-this-score chips** — the biggest unlock. "4 videos watched · 3 academies compared · Profile 100%". Academies trust the number because they see the evidence.
- ⑤ **AI nudge card** — quantified behavior change suggestion. Not "reply faster" but "replying within 1hr lifts conversion ~22%". Drives action.

**Tech I'd explore.** XGBoost on behavioral and tabular data (works well, easy to explain to academies), scikit-learn for feature-engineering and evaluation pipelines, SHAP values to surface the top features behind each score. Explainability is the differentiator — show *why*, not just the score.

**Business impact.** Higher academy ROI, better conversion rates, reduced wasted leads, stronger academy trust in the platform. Natural path to a paid Premium tier in Phase 2.

---

## 04 · AI-Personalized Feed & Homepage

**Pitch.** Today every user sees the same homepage. The cricket batter and the football goalkeeper should land on what feels like two different apps — even though the template is the same. Powered by behavior embeddings.

**Why it matters.** Right now, every user sees the same homepage, which is a missed opportunity. The platform should feel less like a directory and more like a system that understands the user personally.

**What the mockup shows** *(side-by-side comparison of two users on the same homepage)*:

- ① **Dynamic headline per user** — "Sharpen your cover drive" vs. "Quick reflexes for matchday". Generated from the user's recent activity + sport, not a template variable.
- ② **Academies ranked by fit %** — "98% fit" makes the ranking transparent. Different users see different academies first.
- ③ **Drills tied to last analysis** — connects to Feature 01. The homepage knows your weakest metric and surfaces drills against it.
- ④ **Tournaments with eligibility** — "You qualify" + "3 days left". Relevance + urgency, not just a list of every event in Mumbai.
- ⑤ **Embedding-based ranking pipeline** — behavior → vector → ranked content. Cheap on pgvector at start, scales to Pinecone when latency matters.

**Tech I'd explore.** pgvector initially (simpler and more cost-efficient at small scale), Pinecone as scale grows, OpenAI embedding models combined with a ranking layer trained on user behavior patterns.

**Business impact.** Longer sessions, more clicks, better academy visibility — especially for long-tail academies that don't get matched by simple rating sorts.

---

## 05 · AI Co-Pilot for Academies

**Pitch.** Most AI is built for players. This one is the reason academies stay on the platform: a weekly AI briefing, ready-to-send replies, and profile improvements — all grounded in their own data.

**Why it matters.** BookMyPlayer's actual business depends on academies. So academies should have their own AI-powered system, not just be the recipients of player-side features.

**What the mockup shows:**

- ① **Weekly AI briefing with revenue framing** — not "your reply time is slow" but "this cost you ₹36,000". Talks the academy's language: rupees.
- ② **AI-drafted reply with one-click send** — removes the biggest blocker (writing the reply). Academy stays in control: approve, edit, or regenerate.
- ③ **Profile improvements with quantified lift** — every suggestion includes the expected outcome ("2.3× more inquiries"). Turns a checklist into a business case.
- ④ **Inquiry heatmap** — tells the academy when to be online. Visual, immediate. Solves a real operational problem.
- ⑤ **Long-tail suggestions feed** — smaller tactical nudges always visible: waitlists, photo pinning, promo timing. Keeps the Co-Pilot useful between weekly briefings.

**Tech I'd explore.** Claude API for reply drafts and weekly briefings (strong reasoning, contextual understanding), RAG over the academy's own data so outputs are grounded and personalized, weekly batch analytics pipelines (real-time isn't needed at the start).

**Business impact.** Stronger academy retention, a clear path to a paid Premium AI subscription, and a compounding marketplace moat — competitors can copy listings, not the AI relationship.

---

## Suggested build order

| Order | Feature | Why this position |
|-------|---------|-------------------|
| 1 | Video Skill Analysis | Start narrow on one sport (e.g. cricket batting). Get the pose pipeline + skill scoring working before going wide. |
| 2 | Lead Scoring | Quickest academy ROI. XGBoost on existing behavioral logs — can be built in parallel with Video Analysis. |
| 3 | WhatsApp AI | Best built after Lead Scoring is live so the bot can prioritize high-intent conversations. |
| 4 | Personalized Feed | Needs enough behavior data to be useful — gets stronger once the first three features have been generating signals. |
| 5 | Academy Co-Pilot | Built on top of all four. The briefing pulls from lead scores, WhatsApp logs, and homepage analytics. Most valuable once the data layer exists. |

---

## Outcomes I'd want to see

- **Repeat visit rate · +20%** — proxy for Video Analysis and Feed working
- **Video uploads per user · 3+/month** — engagement loop is closing
- **High-intent reply time · under 1 hour** — Lead Scoring + WhatsApp working together
- **Trial → booking conversion · +15%** — hard business outcome; what academies care about
- **Academy 6-month retention · +10pp** — Co-Pilot creating real switching cost

---

## Principles I'd build by

**Both sides of the marketplace should win.** Every AI feature should improve player experience AND academy outcomes. If only one side wins, the other leaves.

**Data > model.** Most AI systems fail because of poor event tracking, feature engineering, and data quality — not because the model is bad. I'd invest in instrumentation first.

**Ship narrow before wide.** One sport, one workflow, one loop — properly. Then scale. Avoid the "broad but shallow" trap.

**Defensibility comes from data.** Features can be copied. Sports-performance datasets, movement analysis, engagement patterns, and conversion intelligence become long-term advantages.

---

## Closing

If I had the opportunity to work on BookMyPlayer, I wouldn't treat AI as a side feature added onto the platform. I'd treat it as the layer that decides whether the platform becomes a one-time sports directory, or a sports ecosystem users continuously return to and academies genuinely depend on.

The five systems above are the direction I'd want to explore. Video Analysis would be the long-term differentiator. WhatsApp engagement would improve conversions. Lead Scoring would improve academy trust. Personalized Feeds would improve engagement. The Academy Co-Pilot would strengthen the marketplace long-term.

I'd rather build one of these systems really well than five superficially. That's the approach I'd want to bring to the team.

---

**Mockups:** https://techcodie.github.io/bookmyplayer-mockups/
**Source:** https://github.com/techcodie/bookmyplayer-mockups
**Contact:** Ansh Baheti
