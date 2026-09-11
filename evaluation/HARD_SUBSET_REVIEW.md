# Manual hard-subset review: initial freeze

Reviewed Q001-Q010 against the unchanged generated messages and their surrounding decision episodes before any retrieval implementation or scoring. All ten target IDs identify answer-bearing messages. The token intersections are empty under `OVERLAP.md`; both sides retain substantive content tokens. No target text was changed.

| Query | Target | Semantic connection and ambiguity check |
| --- | --- | --- |
| Q001 | MSG_000600 | Seaside holiday / Goa; unaffordable / total exceeds cap. This is the explicit rejection, not a tentative quote or savings proposal. |
| Q002 | MSG_000291 | Nausea during consecutive coach rides / motion sickness and back-to-back overnight buses. The symptom is in this message, and Ananya's sender identity answers who. Later rest-stop requests omit the symptom. |
| Q003 | MSG_000436 | Call off the Himalayan vacation / cancel if roads look unsafe. This is the cancellation condition, while nearby weather comments only raise concerns. |
| Q004 | MSG_001154 | Software needed for a phone app on the panel's computer / Flutter emulator setup on the judging laptop. Later mobile-client rejections do not specify that setup burden. |
| Q005 | MSG_001602 | Accessibility of a success indicator / approval requires text, not only green. The preceding status-card image is context; the target is the requested improvement. |
| Q006 | MSG_003418 | Dorm lounge restriction / hostel common room excludes outside students after 6. Later messages discuss the social consequence, but only this target states the restriction. |
| Q007 | MSG_003426 | Abandoning the outdoor picnic / dropping lawn because rain and permission are uncertain. The earlier monsoon concern is provisional and does not give the final rejection or both reasons. |
| Q008 | MSG_003330 | Birthday girl's preference for chatting over an alley game / Meera skips bowling because she wants time to talk. The adjacent cost calculation answers a different question. |
| Q009 | MSG_000700 | Allowance for unforeseen expenses instead of souvenirs / 700 emergency buffer, not shopping. The final trip ceiling alone omits the reserve amount. |
| Q010 | MSG_000289 | Misleading cheap vacation clip for the group's departure city / reel begins in Mumbai, group is in Indore. The preceding price claim does not explain the geographic mismatch. |

These are ordinary paraphrases of costs, health discomfort, safety, software setup, accessibility and event arrangements. None depends only on misspelling or inflection. Q004 was simplified during initial drafting to avoid an unnecessarily formal synonym. The checker retains topic words, names, quantities and negations; no exclusion was added to make any pair pass.

Context is legitimately needed to resolve references such as the vacation, birthday girl and status indicator. The target still contains the requested fact, rationale or instruction. Returning only an adjacent message, a thread summary, or a message naming an earlier alternative is not sufficient.

## Scope and limits

- All ten hard cases have primary category `semantic` and come from the authored decision discussions: five trip, two hackathon and three birthday. The hard subset does not measure zero-overlap person/time retrieval independently.
- The full set has 40 queries and 37 distinct targets. Each of the three final-decision messages has one semantic and one time query, deliberately weighting those important decisions twice. Future metrics must retain denominators of 40 overall and 10 hard; these are not 40 independent facts.
- The corpus has repeated background templates. Q017 was narrowed to May after finding identical exam forwards in April; Q024 and Q029 use sender/date constraints. Q036 explicitly asks for the first matching forward in August. These constraints are in the user query, not just hidden notes.
- Text-only zero-overlap excludes metadata and context from the token comparison. Metadata/context can provide useful clues to a future system; this is not a claim that the tasks have no shared information of any kind.
- Review was performed by the authoring assistant, not an independent human annotator. The labels are manually composed rather than generated from retrieval results. Independent review may reveal legitimate ambiguities; corrections must follow `label_changes.md`.
- No search model, ranking rule, retrieval result, accuracy, Recall@3 or benchmark comparison was produced during this phase.
