# GlossaryRAG Translate

[English](README.md)

**모델을 다시 학습하지 않고 조직의 용어 기준을 LLM 번역에 반영합니다.**

GlossaryRAG Translate는 CSV·TSV·JSONL·TBX 용어사전을 색인하고, 입력 원문에
실제로 등장한 용어만 검색하여 로컬 번역 LLM에 구조화된 참고 정보로 전달하는
오픈소스 패키지입니다.

번역 회사, 공공기관, 법률·의료기관, 제조사처럼 자체 번역 기준이나 표준 용어를
관리하는 조직에서 사용할 수 있습니다.

## 주요 기능

- Trie 기반의 빠른 정확 일치 검색
- 영문 단어 내부의 오탐 방지와 일반적인 굴절형 지원
- 중첩 용어의 최장 일치 처리
- CSV, TSV, JSONL, TBX 용어사전 지원
- 조직별 용어 우선순위 지원
- 로컬 vLLM 등 OpenAI 호환 엔드포인트 연동
- 사전 미적용·정상 사전·무작위 사전 비교 평가
- BLEU, chrF, 용어 재현 성공률 및 쌍체 신뢰구간 산출
- 의료·IT·금융 공개 데이터 평가 어댑터
- Hugging Face 용어 검색·프롬프트 확인 데모

비공개 모델, 내부 데이터, API 키, 조직 용어사전은 포함하지 않습니다.

## 설치

```bash
git clone https://github.com/OWNER/glossaryrag-translate.git
cd glossaryrag-translate
python -m venv .venv
source .venv/bin/activate
pip install -e '.[eval]'
```

## 용어 검색

```bash
glossaryrag match \
  --glossary examples/glossary.csv \
  --text 'The data controller records the purpose of processing personal data.'
```

## 로컬 LLM 번역

```bash
glossaryrag translate \
  --glossary examples/glossary.csv \
  --text 'The data controller records the purpose of processing personal data.' \
  --source-lang English \
  --target-lang Spanish \
  --domain privacy \
  --base-url http://127.0.0.1:8000 \
  --model Qwen/Qwen3-8B
```

전체 설치·데이터 준비·평가 명령은 [영문 README](README.md)에 정리되어 있습니다.
공개 시험의 모델 리비전과 추론 조건은
[기준 실행 환경](docs/reference-runtime.md)에 고정되어 있습니다.

## 공개 평가 구성

| 분야 | 공개 데이터 | 평가 목적 |
|---|---|---|
| 의료·공중보건 | TICO-19 | 다국어 의료 용어 반영 효과 |
| 정보기술 | WMT25 Terminology Track 1 | 정상·무작위·미적용 사전 비교 |
| 금융 | WMT25 Terminology Track 2 | 장문·대규모 사전 환경의 효과 |

최종 공개 보고서는 동일한 원문을 사전 미적용과 정상 사전 적용 조건에서 번역하고,
일반 번역 품질과 용어 재현 성공률을 함께 비교합니다. 공개 데이터 원문은 저장소에
재배포하지 않고 공식 출처에서 내려받습니다.

## 운영 원칙

- 용어사전은 모델 가중치와 분리하여 독립적으로 갱신합니다.
- 전체 사전을 프롬프트에 넣지 않고 원문과 일치한 항목만 전달합니다.
- 기밀 원문과 사전은 조직 내부의 모델 엔드포인트에서 처리합니다.
- BLEU만으로 효과를 판단하지 않고 chrF와 용어 성공률을 함께 확인합니다.

자세한 운영 절차는 [기관 도입 가이드](docs/organization-adoption.md)를 참고하십시오.

## 라이선스

코드는 Apache-2.0입니다. 공개 평가 데이터와 모델은 각각의 원 라이선스를 따릅니다.
TICO-19는 CC0이며, WMT25 평가 자료는 CC BY-NC 4.0입니다.
