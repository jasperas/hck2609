# Synthetic messy HR document dataset

Fictional client: Vandenberg Logistics NV. All people, policies and numbers are invented.

## Contents
80 documents = 10 HR topics x 8 formats (10 samples per format):
01_emails (.eml), 02_sharepoint (.json item exports), 03_teams_messages (.json channel threads),
04_pdf, 05_powerpoint, 06_word, 07_excel, 08_wiki_markdown (.md, Confluence/Notion-style).

Each topic (parental leave, remote work, meal expenses, leave carry-over, IT onboarding, performance
reviews, sick leave, training budget, company car, bonus payout) appears once in every format, with
conflicting versions: current official, outdated-but-marked-final, unapproved draft, hearsay,
informal HR answer, and correct-but-incomplete.

## Files
- manifest.csv      : what participants get (doc_id, path, format)
- questions.csv     : 10 employee questions, correct answer, trustworthy and untrustworthy doc_ids
- ground_truth.csv  : per-document labels (variant, trust_label, stated vs correct value, metadata issues)

## Trust signals to exploit
Location (policy library vs team site vs archive), author role / whether the author left, version and
status fields (note: outdated docs say "Final"), document date vs next-review date, view counts,
draft watermark/headers, reactions and doubting replies in Teams, missing metadata (~30% of hearsay/partial docs).

## Ideas
1. Retrieval + ranking: given a question, return the most trustworthy document.
2. Trust score per document, evaluated against ground_truth.csv.
3. Conflict detection: flag topics where documents disagree.
