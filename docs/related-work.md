# Related work and project scope

Terminology-aware machine translation is an established research area. This project
packages a narrow, reproducible operating pattern rather than claiming that glossary
conditioning itself is new.

- The WMT25 Terminology Translation Task evaluates no terminology, proper terminology,
  and random terminology in IT and finance translation. Its findings report that proper
  terminology improves terminology accuracy and often overall translation quality.
  - https://aclanthology.org/2025.wmt-1.30/
  - https://github.com/wmt-conference/wmt25-terminology
- T-Ragx combines local LLM translation with translation memory, glossaries, and tuned
  models. GlossaryRAG Translate has a smaller scope: model-neutral exact glossary
  retrieval, structured prompt construction, and reproducible causal comparison without
  requiring model fine-tuning.
  - https://pypi.org/project/t-ragx/
- TICO-19 supplies a CC0 medical/public-health benchmark and multilingual terminology,
  enabling evaluation outside the WMT IT and finance domains.
  - https://tico-19.github.io/

The practical contribution is a small dependency-light package that organizations can
connect to their own termbase and private OpenAI-compatible model endpoint, together with
public benchmark adapters and paired evaluation reports.
