# Hybrid failure analysis

Historical analysis of the first-stage hybrid follows. The subsequent multilingual reranker reaches 25/40 Top-1 (15 failures) with the same 1/10 hard accuracy. See [tuning_notes.md](tuning_notes.md) for the retained change, four gains and one regression, and [failed_queries.txt](failed_queries.txt) for current expected/retrieved messages and scores. The descriptions below retain the original experiment's evidence rather than substituting later rankings.

Initial analysis was performed before modifying retrieval code, using the frozen 40-query report archived in `tuning/before/hybrid.json`. All 19 initial Top-1 failures are listed below. Live read-only diagnostics confirmed that **every expected target was eligible** after metadata filtering; listed target ranks are among all eligible messages, not just the saved top three.

The initial result was **21/40 (52.5%) overall**, **1/10 (10%) hard**, gap **+42.5 percentage points**, and Recall@3 **25/40 (62.5%)**. After the retained general message-type change: **22/40 (55%) overall**, **1/10 (10%) hard**, gap **+45 pp**, Recall@3 **25/40 (62.5%)**. Q038 is fixed; all other initial failures remain. No previously correct Top-1 query was lost.

Classifications identify a likely primary cause; they are not proofs from isolated causal ablations. Several errors have secondary causes described in the evidence. Scores below are the initial retrieved message scores, not probabilities.

## Primary classifications

| Reason | Initial failures |
| --- | ---: |
| embedding semantic failure | 10 |
| context-window issue | 5 |
| person parsing problem | 0 |
| time parsing problem | 0 |
| lexical noise | 2 |
| wrong metadata weighting | 1 |
| ambiguous ground truth | 0 |
| other | 1 |

No target was demonstrably invalid. Q001 has some underspecification (earlier cost explanations could also answer the wording), but that does not justify changing its expected ID. The other intended targets are supported by their original messages and local conversation; none was replaced with a neighboring question, proposal, or update.

## Every initial failure

### Q001 ? embedding semantic failure

**Query:** What made a seaside holiday unaffordable?

Category: semantic; hard: True; initial expected rank: 195; final state: **still incorrect**.

**Expected MSG_000600** ? Ishita Patel, 2026-03-23T19:03:05+05:30

> Goa rejected for this break because total exceeds our cap

**Retrieved MSG_000594** ? Aarav Sharma, 2026-03-23T18:43:34+05:30

> Could postpone to December instead?

Initial hit scores: hybrid_score=0.2369, semantic_score=0.4105, contextual_score=0.2664, lexical_score=0.0000.

The intended cost-based rejection scores below postponement and earlier price discussion. The model does not bridge seaside/Goa and unaffordable/exceeds cap well. The question is broad enough that an earlier cost explanation is also plausible, but the labelled rejection is supported and is not invalid.

### Q002 ? embedding semantic failure

**Query:** Who worried about feeling nauseous during consecutive coach rides?

Category: semantic; hard: True; initial expected rank: 69; final state: **still incorrect**.

**Expected MSG_000291** ? Ananya Verma, 2026-03-12T19:37:44+05:30

> overnight buses do back to back honge? motion sickness hoti hai mujhe

**Retrieved MSG_003767** ? Meera Nair, 2026-07-26T17:18:47+05:30

> ohhh yes. copied assumption from yesterday's exercise

Initial hit scores: hybrid_score=0.2686, semantic_score=0.4480, contextual_score=0.3159, lexical_score=0.0060.

An unrelated repeated debugging reply outranks the explicit motion-sickness concern. Target original cosine is 0.3468 versus 0.4480 for the hit. Food/compiler interruptions also dilute the target context; neither sender nor time is constrained.

### Q003 ? embedding semantic failure

**Query:** What condition would force us to call off the Himalayan vacation?

Category: semantic; hard: True; initial expected rank: 57; final state: **still incorrect**.

**Expected MSG_000436** ? Aditya Joshi, 2026-03-17T21:45:40+05:30

> If roads look unsafe we cancel, no heroic driving plan

**Retrieved MSG_000852** ? Rohan Mehta, 2026-04-02T19:33:35+05:30

> I saw another Goa deal but ignoring it. We already chose the hills

Initial hit scores: hybrid_score=0.3549, semantic_score=0.5286, contextual_score=0.4760, lexical_score=0.0165.

The hit is about choosing the hills, not a condition for cancelling. Topical similarity dominates the conditional meaning of unsafe roads; the labelled cancellation condition is present and valid.

### Q004 ? embedding semantic failure

**Query:** What extra software would the panel's computer need for the phone app?

Category: semantic; hard: True; initial expected rank: 61; final state: **still incorrect**.

**Expected MSG_001154** ? Ishita Patel, 2026-04-14T18:36:48+05:30

> Flutter would mean emulator setup on judging laptop

**Retrieved MSG_001061** ? Ishita Patel, 2026-04-10T20:09:58+05:30

> Flutter app could look nice, camera upload simple

Initial hit scores: hybrid_score=0.2674, semantic_score=0.4789, contextual_score=0.2222, lexical_score=0.1102.

The hit proposes a mobile app but does not answer what must be installed. The model misses panel computer/judging laptop and extra software/emulator. Adjacent Firebase and QR suggestions further dilute context.

### Q005 ? embedding semantic failure

**Query:** What accessibility improvement was requested for the success indicator?

Category: semantic; hard: True; initial expected rank: 204; final state: **still incorrect**.

**Expected MSG_001602** ? Meera Nair, 2026-05-03T18:51:28+05:30

> approved colour needs text also, don't rely only on green

**Retrieved MSG_003222** ? Meera Nair, 2026-07-06T21:07:00+05:30

> [PDF] draft volunteer orientation session checklist, still needs review

Initial hit scores: hybrid_score=0.2920, semantic_score=0.4104, contextual_score=0.4203, lexical_score=0.0063.

The requested colour-independent status indicator is explicit in the target. An unrelated checklist wins; the accessibility concept is not linked to adding text beside green. Nearby laptop chatter does not supply that missing meaning.

### Q007 ? lexical noise

**Query:** Why was the outdoor picnic abandoned?

Category: semantic; hard: True; initial expected rank: 28; final state: **still incorrect**.

**Expected MSG_003426** ? Ananya Verma, 2026-07-14T21:10:16+05:30

> Rain and permission both uncertain. Dropping lawn

**Retrieved MSG_003214** ? Aditya Joshi, 2026-07-06T20:22:31+05:30

> college lawn picnic? practically free venue

Initial hit scores: hybrid_score=0.3670, semantic_score=0.6255, contextual_score=0.2898, lexical_score=0.2331.

An earlier picnic proposal wins with lexical 0.2331 and original cosine 0.6255; the rejection has lexical 0.0012 and original cosine 0.2974. Shared topic wording reinforces the wrong decision stage. Unrelated coding replies occupy three of the four target neighbors.

### Q008 ? lexical noise

**Query:** Why did the birthday girl prefer chatting over a game at the alley?

Category: semantic; hard: True; initial expected rank: 5; final state: **still incorrect**.

**Expected MSG_003330** ? Meera Nair, 2026-07-10T19:29:49+05:30

> Skip bowling too, I want time to talk anyway

**Retrieved MSG_003619** ? Kabir Khan, 2026-07-21T20:56:55+05:30

> [Image] tragic attempt at a homemade birthday card

Initial hit scores: hybrid_score=0.2547, semantic_score=0.3118, contextual_score=0.3002, lexical_score=0.2027.

The birthday-card hit has lexical 0.2027 against 0.0046 for the target; its original semantic score is actually lower (0.3118 versus 0.3253). Birthday wording helps a distractor beat the explicit preference for talking rather than bowling. The short window does not establish the birthday-girl role.

### Q009 ? embedding semantic failure

**Query:** How much of our holiday allowance was reserved for unforeseen expenses rather than souvenirs?

Category: semantic; hard: True; initial expected rank: 63; final state: **still incorrect**.

**Expected MSG_000700** ? Ishita Patel, 2026-03-28T20:47:26+05:30

> 8700 ceiling includes a 700 emergency buffer, not shopping

**Retrieved MSG_000856** ? Ishita Patel, 2026-04-02T19:49:04+05:30

> Budget unchanged. Any optional activity comes out of personal spending

Initial hit scores: hybrid_score=0.3371, semantic_score=0.5203, contextual_score=0.4251, lexical_score=0.0309.

The hit discusses optional personal spending, not the numerical emergency reserve. The model does not reliably map unforeseen expenses/souvenirs to emergency buffer/shopping. The amount is explicit in the target.

### Q010 ? embedding semantic failure

**Query:** Why was the cheap coastal vacation clip misleading for people departing from our city?

Category: semantic; hard: True; initial expected rank: 117; final state: **still incorrect**.

**Expected MSG_000289** ? Meera Nair, 2026-03-12T19:31:15+05:30

> that reel starts from Mumbai, hum Indore mein hain

**Retrieved MSG_002778** ? Rohan Mehta, 2026-06-18T21:05:00+05:30

> local walk near home today, no big travel plan

Initial hit scores: hybrid_score=0.3151, semantic_score=0.4294, contextual_score=0.4696, lexical_score=0.0023.

An unrelated local walk beats the correction of a misleading reel. The previous reel and current departure-city correction are inside the allowed window, so increasing its size would not address the principal failure to combine these facts.

### Q011 ? context-window issue

**Query:** Where did we finally decide to go for the June trip, and what was the per-person limit?

Category: semantic; hard: False; initial expected rank: 75; final state: **still incorrect**.

**Expected MSG_000713** ? Ishita Patel, 2026-03-28T21:13:19+05:30

> Final decision: Manali, June 10-15, maximum Rs 8,700 each. Goa is dropped. Refundable rooms only; Aarav will collect Rs 2,000 each by April 2.

**Retrieved MSG_000854** ? Meera Nair, 2026-04-02T19:42:42+05:30

> [PDF] June hill-trip itinerary revision 3, with refund notes

Initial hit scores: hybrid_score=0.3118, semantic_score=0.5276, contextual_score=0.3000, lexical_score=0.1109.

The current message contains the complete final destination and cap, but three of its four neighbors are unrelated coding chatter. The itinerary PDF outranks it. Original cosine is also weak (0.3308); the event-date safeguard correctly avoids excluding the March decision because the trip is in June.

### Q012 ? context-window issue

**Query:** What backend and database did we finally choose for LostLoop?

Category: semantic; hard: False; initial expected rank: 6; final state: **still incorrect**.

**Expected MSG_001482** ? Sneha Iyer, 2026-04-27T20:42:09+05:30

> Locked for LostLoop: React with Vite in JavaScript, FastAPI on Python, and SQLite for storage. Plain CSS, local image files, no cloud dependency. Aarav handles UI; Kabir and I handle API and schema.

**Retrieved MSG_001598** ? Kabir Khan, 2026-05-03T18:40:00+05:30

> LostLoop now launches from the README on a fresh folder

Initial hit scores: hybrid_score=0.3479, semantic_score=0.4290, contextual_score=0.4975, lexical_score=0.1179.

The project launch update wins largely through contextual cosine (0.4975 versus 0.3320 for the locked stack). The final stack remains a complete valid answer. Similarity to the project thread is being confused with the identity and decision stage of the current message.

### Q015 ? context-window issue

**Query:** Was outside cake allowed, and what decoration rule came with it?

Category: semantic; hard: False; initial expected rank: 3; final state: **still incorrect**.

**Expected MSG_003434** ? Rohan Mehta, 2026-07-14T21:26:41+05:30

> Yes if we clean up; no decoration on walls

**Retrieved MSG_003433** ? Kabir Khan, 2026-07-14T21:24:18+05:30

> Cake allowed from outside?

Initial hit scores: hybrid_score=0.4891, semantic_score=0.7558, contextual_score=0.3862, lexical_score=0.4467.

The preceding question is selected instead of its answer. The labelled answer explicitly grants permission with cleanup and wall-decoration conditions; its window contains the question. This is answer anchoring, not missing context, and neighbor-only credit would conceal the error.

### Q016 ? embedding semantic failure

**Query:** What did the birthday actually cost once it was over, and was any buffer used?

Category: semantic; hard: False; initial expected rank: 8; final state: **still incorrect**.

**Expected MSG_003738** ? Ishita Patel, 2026-07-25T22:24:37+05:30

> Actual total 2900, equal shares 362.50. No buffer spent

**Retrieved MSG_003616** ? Ishita Patel, 2026-07-21T20:47:27+05:30

> Final birthday plan: July 25, 7-9 pm, Nukkad Cafe side room for all eight. Rs 2,400 snacks/drinks + Rs 500 chocolate cake = Rs 2,900 total, capped at Rs 3,000. Split Rs 362.50 each. No decorations purchase. Rohan reserves the room; Sneha collects the cake.

Initial hit scores: hybrid_score=0.3943, semantic_score=0.5559, contextual_score=0.5361, lexical_score=0.0603.

A planned budget beats the post-event actual total. The projected and actual totals happen to agree, but only the target confirms that no reserve was spent. Temporal/decision-stage semantics are lost; there is no explicit chat-date interval to parse.

### Q022 ? wrong metadata weighting

**Query:** What was Ishita's absolute spending limit when the Goa estimate first came in?

Category: person; hard: False; initial expected rank: 2; final state: **still incorrect**.

**Expected MSG_000287** ? Ishita Patel, 2026-03-12T19:24:43+05:30

> 10400 already, aur buffer? mera absolute limit 9000 hai

**Retrieved MSG_000286** ? Rohan Mehta, 2026-03-12T19:20:00+05:30

> Goa estimate: travel 4200, stay 2800, food 1800, local 1600 per head

Initial hit scores: hybrid_score=0.4385, semantic_score=0.5662, contextual_score=0.5710, lexical_score=0.2024.

The participant resolves correctly to Ishita, but a possessive spending-limit question receives only a 0.05 author bonus. Rohan's estimate wins over Ishita's own response. This is uncertain author intent, not name-recognition failure; filtering every possessive could incorrectly exclude someone else reporting a person's limit.

### Q023 ? embedding semantic failure

**Query:** How did Aarav say he would track everyone's trip contributions?

Category: person; hard: False; initial expected rank: 2; final state: **still incorrect**.

**Expected MSG_000715** ? Aarav Sharma, 2026-03-28T21:16:09+05:30

> I'll track the eight contributions in one sheet. No payments posted here.

**Retrieved MSG_000846** ? Aarav Sharma, 2026-04-02T19:10:00+05:30

> Trip update: all eight deposits marked received in our plan

Initial hit scores: hybrid_score=0.3588, semantic_score=0.4604, contextual_score=0.3555, lexical_score=0.0637.

The correct Aarav-only filter is already active. His later deposits-received update beats his earlier spreadsheet-tracking commitment. The expected message answers how; the hit answers whether collection is complete.

### Q027 ? context-window issue

**Query:** What name did Rohan suggest for our coding project?

Category: person; hard: False; initial expected rank: 15; final state: **still incorrect**.

**Expected MSG_001478** ? Rohan Mehta, 2026-04-27T20:28:28+05:30

> call it LostLoop? sounds like my coding life

**Retrieved MSG_000975** ? Rohan Mehta, 2026-04-08T08:16:34+05:30

> thanks for clarifying

Initial hit scores: hybrid_score=0.2665, semantic_score=0.3613, contextual_score=0.1776, lexical_score=0.0475.

The target naming suggestion has original cosine 0.3774 versus 0.3613 for an unrelated thanks reply, but its contextual cosine is clipped to zero. The correct Rohan-only filter is active. Concatenating prototype/storage chatter damages the naming suggestion's representation.

### Q031 ? context-window issue

**Query:** What decision did we make on March 28 about the trip destination and payments?

Category: time; hard: False; initial expected rank: 5; final state: **still incorrect**.

**Expected MSG_000713** ? Ishita Patel, 2026-03-28T21:13:19+05:30

> Final decision: Manali, June 10-15, maximum Rs 8,700 each. Goa is dropped. Refundable rooms only; Aarav will collect Rs 2,000 each by April 2.

**Retrieved MSG_000699** ? Ananya Verma, 2026-03-28T20:44:51+05:30

> Return June 15 morning works for me, checked family calendar

Initial hit scores: hybrid_score=0.3281, semantic_score=0.4212, contextual_score=0.3542, lexical_score=0.0000.

The March 28 filter is correct and retains the target. Unrelated coding neighbors dilute the final decision, while a return-date reply wins. Raw calendar wording may also distract similarity; this was tested separately rather than labelled a date-parser bug.

### Q032 ? embedding semantic failure

**Query:** What stack did we settle on in late April for LostLoop?

Category: time; hard: False; initial expected rank: 12; final state: **still incorrect**.

**Expected MSG_001482** ? Sneha Iyer, 2026-04-27T20:42:09+05:30

> Locked for LostLoop: React with Vite in JavaScript, FastAPI on Python, and SQLite for storage. Plain CSS, local image files, no cloud dependency. Aarav handles UI; Kabir and I handle API and schema.

**Retrieved MSG_001403** ? Ananya Verma, 2026-04-25T08:11:59+05:30

> there was another group there earlier

Initial hit scores: hybrid_score=0.3516, semantic_score=0.4720, contextual_score=0.3570, lexical_score=0.0000.

The April 21-30 filter is correct. An unrelated room-use reply wins despite zero lexical overlap. The target locked stack has original cosine only 0.2477. Raw date wording and weak decision paraphrasing are more plausible causes than incorrect date bounds.

### Q038 ? other

**Query:** What network maintenance notice did Meera forward last month?

Category: time; hard: False; initial expected rank: 2; final state: **fixed**.

**Expected MSG_003999** ? Meera Nair, 2026-08-06T08:10:07+05:30

> Forwarded: Campus network maintenance, 2026-08-06, service may be interrupted. Save work locally.

**Retrieved MSG_004277** ? Meera Nair, 2026-08-18T08:11:20+05:30

> maintenance notice tha na

Initial hit scores: hybrid_score=0.5758, semantic_score=0.5751, contextual_score=0.5538, lexical_score=0.3927.

Missing requested-message-type constraint: both candidates satisfy Meera and August, but the hit only mentions a notice. Its neighboring forward is by Rohan. The target is the actual forwarded warning by Meera; type metadata can distinguish this class without knowing topic words or expected IDs.

## General improvements and stopping point

1. **Retained: explicit message-type constraints.** Intersect the current message's stored type with existing author/date filters for clear forwarded-item or attachment requests. Do not infer type from a neighboring message. Unsupported/negated/alternative type requests remain unconstrained. This fixed Q038 without Top-1 regressions; independent fixtures also cover PDF, image, voice and URL requests and empty intersections.

2. **Tested and rejected: removing resolved metadata from similarity text.** Preserve sender/date filters, but encode and vectorize the remaining content. This recovered the naming suggestion but lost two other answers: 21/40 to 20/40, hard 1/10 unchanged. Recall@3 improved from 25/40 to 27/40. Broad removal is therefore not enabled; see `tuning_notes.md` and the archived trial patch.

3. **Next research step: an answer-aware local reranker.** A local query/current-message/context pair model could distinguish proposal from rejection, question from answer, and forecast from actual accounting. Candidate recall must be measured first: many hard targets are below top 50, so reranking the current top three cannot fix them. Use a pooled, sufficiently broad candidate set and report exact-target recall and latency. No new model was downloaded or tested here.

4. **Test bounded context selection and current-message emphasis on fresh data.** Within the existing two-neighbor/30-minute cap, select topic-consistent neighbors or retain separate query-to-current and query-to-neighbor evidence instead of flattening five messages. Evaluate short-answer and unrelated-neighbor cases separately; never promote a neighbor solely because the answer occurs in its window. Do not expand the window or use synthetic thread/conclusion annotations to recover these labels.

5. **Improve mixed-language semantics with independent evidence.** Compare a suitable local reranker or encoder on newly labelled English/Hinglish paraphrases, negations and numeric questions before changing the pinned model. Do not add hand-authored synonym mappings derived from these ten hard queries.

6. **Keep uncertain author intent conservative.** Possessive ownership is not always authorship. A broad author-role parser or explicit user filter is safer than increasing a bonus until one spending-limit query flips.

**Stop:** Two general candidates were tested; the beneficial type constraint is retained. The remaining 18 errors would invite query-word dictionaries, answer-stage heuristics tailored to this corpus, window/weight sweeps, or ambiguous-person filters chosen from the same small set. Further tuning should use a separate manually labelled development set and a held-out test set, split by thread/episode and grouping repeated targets to reduce leakage. Keep these 40 labels frozen as the historical benchmark. No held-out accuracy or hard-query improvement is claimed.
