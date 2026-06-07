# pii-detector-messaging

> PII detection where generic tools fail: 160-char SMS, conversational text, partial identifiers, adversarial obfuscation. Hybrid regex + fine-tuned NER + LLM pipeline with compliance-weighted eval (false negatives cost 10x false positives). Open reference implementation.

## Why this exists

Try running Presidio or AWS Comprehend on a 160-character SMS that reads `dm me at j dot sinh, talk soon`. It misses the email reference entirely. So does spaCy's stock NER. So does most off-the-shelf PII tooling - they are optimised for the long-form documents enterprises classified ten years ago, not the conversational, abbreviated, deliberately obfuscated text that flows through messaging today.

That gap matters. Messaging is now where most regulated communication actually happens - SMS, MMS, WhatsApp, email bodies threaded with quoted replies. The PII that needs to be detected, redacted, or flagged in that channel does not look like the PII in a contract or an HR document. It is shorter. It is coded. People typing on phones at 11 PM do not write "my email address is firstname.lastname@example.com." They write "msg me, j at jsinh dot com." Generic detectors trained on legal corpora do not catch that, and retrofitting them with more regex eventually hits a wall.

I have spent years working in real-time communications and compliance-adjacent infrastructure. Every PII tool I have evaluated for messaging use cases has the same shape - built for documents, bolted onto messaging, brittle in the predictable places. So I am building one from the ground up for the messaging case, in the open, with the eval framework I wish those tools had shipped with.

## What this is (and is not)

A reference implementation. The goal is to demonstrate, on a real codebase with a real evaluation framework, how a messaging-aware PII detector should be built end-to-end. Three components:

1. **Regex layer** for the well-formed identifiers - conventionally-formatted emails, phone numbers, structured account references. Fast, cheap, catches the obvious 60-70%.
2. **Fine-tuned NER model** (DistilBERT or RoBERTa-base, depending on what survives the eval) for the patterned-but-context-dependent cases - names inside conversational sentences, partial addresses, indirect references.
3. **LLM fallback** for genuinely ambiguous edges - adversarial obfuscation, multi-turn references, novel patterns the NER has not seen. Slow, expensive, rare.

The interesting work is not in any single layer. It is in the routing logic between them, the compliance-weighted eval that decides whether the routing is correct, and the failure modes when two layers disagree.

This is *not* a production-ready library. Not yet, not by week 12, probably not ever - that is a different project with different priorities. It is not a drop-in Presidio replacement. It is not tied to any specific compliance regime; GDPR, HIPAA, and the EU AI Act all define PII differently, and reconciling that with your specific risk posture is the user's job to plug in on top of detection.

## The eval framework

The component I am building first, because everything else is meaningless without it.

Precision and recall mean different things in compliance contexts. A false negative on PII in a regulated message is a potential exposure event with regulatory teeth. A false positive is an annoying over-redaction someone in ops complains about on Slack. The asymmetry is roughly 10:1 in favour of recall for most messaging compliance use cases - not always, but often enough that aggregate F1 lies to you about whether a model is fit for purpose.

The eval framework tracks:

- Precision and recall **per entity type**, never aggregated into a single score
- Errors weighted by compliance severity, with configurable cost ratios (10:1 is the default, not the rule)
- Latency budgets and cost per 1,000 messages, because production teams will ask
- A held-out adversarial set with deliberate obfuscation - homoglyphs, leetspeak, deliberate spacing, the kinds of evasion patterns real users employ when they do not want to be detected

## Status

Day 0. The repo exists, the architecture is sketched, the eval set seed is being assembled. I am building this in public over roughly 12 weeks on top of a day job and a side project, so the cadence is *show your work* rather than *polished release schedule*. Expect early commits to be ugly. Expect things to change. Expect honest postmortems when something does not work - those are usually the more useful posts anyway.

The blog series tracking the build will be linked here once the first post is up.

## License

Apache License 2.0. See [LICENSE](./LICENSE).

## Author

[Jaspal Chauhan](https://github.com/jsinh) - engineer working in real-time communications, compliance, and applied ML. This project is independent personal work, not affiliated with any employer or organisation.