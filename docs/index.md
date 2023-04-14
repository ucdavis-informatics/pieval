# Pie ![pieval logo](img/pieVal_Logo_medium.png)Val

As much as 83% of biomedical information is locked away in clinical note data [1]. It is considered locked away because the inherently unstructured nature of note data presents unique challenges. First, the tools and processes necessary to work with unstructured data are specialized and complicated. However, the tooling is reaching a critical point of commoditization making text data processing more widely possible. Due to recent advances in compute architectures and associated software frameworks, Natural Language Processing (NLP), which originated as a subfield of computer science and linguistics and offers computational approaches to deal with digitized text, has started to enter the mainstream.  Tooling and frameworks will never mask the need for large volumes of gold lableled data which must be used to guide NLP development, sometimes as training data, and other times as evaluative data.  Labelling data is an expensive activity but with focused scope and a little innotation, we can minimize this cost to the extent possible.

PieVal, combining the words Python and Validation, is a web-based, secure, text data labelling tool designed for distributed annotation of sensitive data supporting document level annotations and captures binary and multi-class labels.  It is designed to be part of an iterative continuous improvement cycle by reframing the labelling process as an assertion test.  This reframing provides a consistent interface regardless of class number or project stage.  It also had the side effect of decreasing annotation time by an average of 50% compared with other tools; at an average of less than 30 seconds per document.  Additional features include the ability to directly test the impact of text enrichment strategies on both annotation times as well as downstream model performance. In real life, PieVal can also be used to validate any computational process on text data.  All of these benefits are primarily due to PieVal's framing as an assertion tester.  If you are clever about how you frame your assertions you can make PieVal capture ground truth in a number of circumstances.

---
## Key Features

- Secure (when served over HTTPS and secured by [Keycloak](https://www.keycloak.org))
  - Note that KeyCloak is a seperate service and is a networked dependency
- Gamified - This is accomplished primarily with a project leaderboard, allowing for friendly competitions.  Best if combined with incentives, like coffee cards. 
- Assertion tester - Rather than presenting the user with data and asking for an annotation, we present the user with data, an assertion (either human or machine generated) and ask them to Agree, Disagree, Review, or Pass.  The result is a consistent UI that does not change, no matter the task allowing users to become extremely efficient with the tool.
- Built in enrichment strategy testing.  By default the user is presented with a clipped, enriched, or otherwise modified version of the data designed to speed up both the annotation times and downstream ML training times simply by acting on less, more specific data, to the task.  Enriching in this way requires a framework to ensure the enrichement is effective.  PieVal can also present the unmodified data IF the annotator asks for it.  The ask is recorded with the annotation allowing you to measure how often the enrichment failed and required a 'full review' to annotate correctly.
- Annotation compliance - PieVal can be configured to send reminder emails to keep annotators engaged after defined periods of inactivity.
- Post annotation tooling to measure IntrA and IntER operator agreement statistics
- Supports both Filesystem and Database persistance strategies
  - The Filesystem strategy should only be used for development, demonstrations, and single user annotation capture
  - The DB strategy should be used when multiple concurrent annotators are expected

---
## How to use PieVal

PieVal is a webapp that can present sensitive data.  If you wish to use PieVal, please work with Bill Riedl to set up a VM to host the app with appropriate Authentication (via UCDHS active directory).  Once the app is set up and congifured, please read the [following about how to create and manage projects](README_project_management.md)

## References

1. Murdoch TB, Detsky AS. The Inevitable Application of Big Data to Health Care. JAMA 2013;309:1351--