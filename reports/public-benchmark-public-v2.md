# Public benchmark results

This report evaluates the same source records with no glossary and with the
correct matched glossary. WMT25 studies additionally include benchmark-provided
random terminology as a negative control. Dataset text is not redistributed.

## Runtime

- Model: `Qwen/Qwen3-8B`
- Model revision: `b968826d9c46dd6066d109eabc6255188de91218`
- Runtime: `vLLM 0.23.0`
- Hardware: `one NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition GPU`
- Paired bootstrap samples: 1000

## Scores

| Study | Mode | Records | BLEU | chrF | Terminology success | Mean latency |
|---|---:|---:|---:|---:|---:|---:|
| Medical en-ru | no_term | 500 | 25.07 | 54.21 | 49.8% | 1.838s |
| Medical en-ru | proper | 500 | 25.63 | 54.53 | 61.2% | 1.819s |
| Medical en-es-LA | no_term | 500 | 48.69 | 72.89 | 85.5% | 1.574s |
| Medical en-es-LA | proper | 500 | 48.11 | 72.57 | 94.9% | 1.568s |
| Medical en-zh | no_term | 500 | 51.19 | 52.36 | 44.3% | 1.066s |
| Medical en-zh | proper | 500 | 49.48 | 51.84 | 62.9% | 1.095s |
| IT en-de | no_term | 500 | 33.15 | 61.89 | 38.8% | 0.729s |
| IT en-de | proper | 500 | 38.51 | 67.99 | 89.6% | 0.723s |
| IT en-de | random | 500 | 37.23 | 65.99 | 43.4% | 0.723s |
| IT en-es | no_term | 500 | 44.44 | 66.93 | 47.2% | 0.661s |
| IT en-es | proper | 500 | 50.00 | 72.09 | 88.0% | 0.663s |
| IT en-es | random | 500 | 47.29 | 69.76 | 48.7% | 0.658s |
| IT en-ru | no_term | 500 | 25.53 | 57.55 | 33.9% | 0.680s |
| IT en-ru | proper | 500 | 32.91 | 64.30 | 82.0% | 0.680s |
| IT en-ru | random | 500 | 29.67 | 61.39 | 33.9% | 0.677s |
| Finance en-zh | no_term | 10 | 38.31 | 34.40 | 36.7% | 73.533s |
| Finance en-zh | proper | 10 | 47.85 | 42.20 | 86.9% | 73.899s |
| Finance en-zh | random | 10 | 41.40 | 36.91 | 38.9% | 73.597s |
| Finance zh-en | no_term | 10 | 27.26 | 70.17 | 47.2% | 85.471s |
| Finance zh-en | proper | 10 | 33.31 | 73.25 | 83.7% | 84.751s |
| Finance zh-en | random | 10 | 28.09 | 71.07 | 49.8% | 87.316s |

## Proper glossary effect versus no glossary

Positive values favor the correct glossary. Deltas are paired means of
per-record scores; intervals are 95% bootstrap confidence intervals over
source records. The score table above reports corpus-level BLEU and chrF.

| Study | Paired records | BLEU delta [95% CI] | chrF delta [95% CI] | Terminology-success delta [95% CI] |
|---|---:|---:|---:|---:|
| Medical en-ru | 500 | +0.93 [+0.14, +1.78] | +0.01 [-0.70, +0.77] | +11.8% [+9.5%, +14.4%] |
| Medical en-es-LA | 500 | -0.81 [-1.74, +0.06] | -0.60 [-1.13, -0.11] | +9.9% [+7.8%, +12.3%] |
| Medical en-zh | 500 | -1.39 [-2.23, -0.47] | -0.26 [-1.09, +0.62] | +20.0% [+16.9%, +23.3%] |
| IT en-de | 500 | +6.03 [+4.27, +7.62] | +8.76 [+7.45, +10.08] | +50.0% [+46.0%, +54.5%] |
| IT en-es | 500 | +8.45 [+6.58, +10.21] | +7.50 [+6.27, +8.74] | +40.3% [+36.1%, +44.7%] |
| IT en-ru | 500 | +10.80 [+8.88, +12.77] | +9.83 [+8.26, +11.42] | +47.1% [+42.6%, +51.5%] |
| Finance en-zh | 10 | +11.02 [+8.84, +13.14] | +9.13 [+7.00, +11.18] | +51.0% [+47.8%, +54.1%] |
| Finance zh-en | 10 | +6.77 [+4.11, +9.85] | +3.60 [+2.22, +5.27] | +37.0% [+33.3%, +41.0%] |

## Findings

- Correct matched terminology improved terminology success in all 8 studies. The paired mean gain ranged from +9.9 to +51.0 percentage points, and every 95% interval remained above zero.
- For paired per-record chrF, 5 studies had an entirely positive 95% interval, 1 had an entirely negative interval, and 2 crossed zero. Terminology gains therefore do not guarantee a general-quality gain in every domain and language.
- The largest absolute change in mean request latency was 0.719 seconds, indicating that matched glossary rows added little generation latency in this reference run.
- Proper terminology outperformed the random-term control in the WMT25 IT and finance studies, supporting an effect from the correct mappings rather than from merely adding extra prompt text.

## Interpretation rules

- Terminology success is the primary measure of whether an organization termbase
  is followed; BLEU and chrF monitor overall reference similarity.
- A glossary is considered beneficial when terminology success improves without a
  material general-quality regression. Results can vary by model and domain.
- Random terminology is a negative control, not a valid operating configuration.
- WMT25 data are CC BY-NC 4.0 and are downloaded from upstream for evaluation only.
