---
name: observability-coverage
description: Model how relevant reality can become observable before evidence acquisition when source coverage, sampling frame, platform boundaries, or representation bias could materially change the conclusion. Use when a search engine, platform, database, sample, telemetry stream, review corpus, survey, or other observation channel may expose only part of the target reality. Do not use for obvious single-source lookups where the authoritative frame is already sufficient.
---

# Observability / Coverage

Use this skill inside an **Evidence Gap** when the current observation frame may not sufficiently cover the relevant reality.

Core principle:

> Search is an observation through a frame, not direct access to reality.

> Model the observation space before acquiring evidence.

> Precision cannot compensate for material coverage error.

## 1. Target Reality / Population

Define only as precisely as needed:

- What population, events, states, behaviors, documents, or phenomena are we trying to understand?
- What conclusion or decision will the evidence support?

Do not silently replace the target reality with the population that is easiest to observe.

## 2. Evidence Generation

Ask how the target reality would naturally produce observable traces.

Examples:

- official documents or databases;
- platform posts or discussions;
- transactions or conversions;
- telemetry or logs;
- reviews;
- interviews or surveys;
- experiments;
- physical measurements.

Different traces often represent different aspects of reality.

## 3. Evidence Habitats / Collections

Identify the collections where those traces can actually exist.

Do not assume one search engine indexes every relevant collection.

Do not assume one platform represents the whole target population.

## 4. Observation Frames

For each materially relevant source, ask:

- What portion of the target reality can enter this frame?
- What has little or no chance of entering?
- What inclusion mechanism selects observations into this frame?

Examples:

- Reddit discussion ≠ all potential users;
- Steam reviews ≠ the whole market;
- telemetry ≠ stated motivation;
- a web search index ≠ all publicly released documents.

## 5. Access / Retrieval Channels

Choose the channel that can actually observe each required frame:

- search engine;
- platform-native search;
- API;
- database;
- crawler;
- telemetry;
- survey;
- interview;
- experiment;
- manual inspection.

Optimize the frame/channel before over-optimizing the query.

## 6. Blind Spots and Representation Risk

Check only risks capable of changing the conclusion:

- under-coverage;
- platform population bias;
- self-selection;
- survivorship;
- geographic / language / demographic skew;
- algorithmic exposure;
- time-window bias;
- missing non-digital behavior.

Ask:

**Could the observed population systematically differ from the target population in a way that changes the current decision?**

## 7. Multi-frame strategy

If one frame is insufficient:

- combine complementary frames; or
- explicitly constrain the conclusion to the observed frame.

Do not add sources merely for completeness. Add a frame only if it observes a materially different part of reality or reduces a decision-relevant blind spot.

## 8. Exit

Once the observation space is sufficiently modeled:

- suitable traces already exist → `evidence-acquisition` for retrieval;
- traces do not yet exist → `evidence-acquisition` for measurement / instrumentation / survey / interview / experiment;
- required observation capability is missing → `capability-sourcing`;
- multiple materially different observation strategies remain → `decision-analysis`.

Stop when further frame analysis is unlikely to change the evidence strategy or conclusion scope.
