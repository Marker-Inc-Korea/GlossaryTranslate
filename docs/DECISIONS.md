# Project decisions

This file records decisions that should survive chat and OMX session boundaries. New
decisions should include the date, reason, and affected files or experiments.

## 1. Separate public project

**Decision:** Maintain GlossaryRAG Translate as an independent Git repository and OMX
work context.

**Reason:** The reusable glossary-translation method has a different audience,
licensing boundary, release cycle, and evidence standard from the private service that
motivated it. A separate repository prevents accidental commits of internal data or
deployment code.

**Constraint:** Relevant engineering knowledge may be summarized here, but private
data, private paths, organization glossary entries, credentials, and internal service
details must not be copied into this public repository.

## 2. Glossary data stays separate from model weights

**Decision:** Apply organization terminology at inference time rather than requiring
model retraining.

**Reason:** Organizations need to update terminology independently, compare glossary
versions, and use the same method with different compatible models.

## 3. Retrieve only source-matched entries

**Decision:** Index the glossary once and inject only entries matched in the current
source text.

**Reason:** Supplying the whole glossary wastes context, increases irrelevant signals,
and makes the experiment less representative of production use.

**Current behavior:** The retriever uses a reusable character Trie, longest-match
overlap resolution, ASCII word-boundary protection, and common English inflection
support.

## 4. Glossary rows are reference data, not commands

**Decision:** Serialize matched rows inside explicit delimiters as structured reference
data and instruct the model to use applicable terminology while translating the source.

**Reason:** A glossary mapping expresses a preferred term, not permission to execute
instructions that might appear in a source term, target term, note, or metadata field.

## 5. Keep the core model- and server-neutral

**Decision:** Depend on the OpenAI-compatible request contract rather than a specific
model or server package.

**Reason:** vLLM is the reproducible reference runtime, but adopters may use another
compatible local runtime. Hosted external APIs are not required by the package.

## 6. Evaluate paired conditions

**Decision:** Compare the same source records with the same model, revision, prompt
task, and decoding configuration in `no_term`, `proper`, and—when supported—`random`
conditions.

**Reason:** The design isolates the effect of correct terminology from record sampling,
model changes, and the effect of merely adding extra prompt text.

## 7. Report terminology and general quality together

**Decision:** Treat terminology success as the direct glossary-adherence measure while
also reporting BLEU and chrF.

**Reason:** Public experiments show that terminology adherence can improve even when a
general reference-similarity metric is flat or slightly lower. No single metric is
sufficient.

## 8. Preserve reproducibility metadata

**Decision:** Public reports must record model revision, runtime version, hardware,
dataset revision or source hashes, deterministic decoding settings, paired record
counts, and bootstrap configuration.

**Reason:** A score without its exact generation and data conditions cannot support a
credible open-source claim.

## 9. Do not redistribute restricted benchmark text

**Decision:** Download public evaluation data from upstream and publish aggregate
reports and permitted metadata only.

**Reason:** Code, model, and dataset licenses are separate. WMT25 content is used under
CC BY-NC 4.0 and is deliberately excluded from distribution bundles.

## 10. Current reference benchmark, not universal performance claim

**Decision:** Use the committed Qwen3-8B run as the current reference evidence without
claiming that its gains automatically transfer to every model, domain, language, or
glossary.

**Reason:** The eight committed studies demonstrate the method's usefulness and its
tradeoffs, but broader generalization requires additional paired experiments.
