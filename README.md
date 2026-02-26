# 📊 K-Valuation Band

삼성전자, SK하이닉스의 **PER·PBR 밸류에이션 밴드 차트**를 자동 생성하여 GitHub Pages로 제공합니다.

[🇺🇸 English version](./README_en.md)

👉 **실시간 차트 확인하기**:
- [한국어 버전](https://k-sunshine-log.github.io/k-valuation-band/)
- [영어 버전](https://k-sunshine-log.github.io/k-valuation-band/index_en.html)

## 밴드 차트란?

과거 일정 기간 동안의 PER(주가수익비율)과 PBR(주가순자산비율) 지표 기반으로 밴드 라인을 생성하여, 현재 주가의 밸류에이션 리스크 및 프리미엄(저평가/고평가) 위치를 시각화합니다.
실적(EPS/BPS) 발표 시점의 계단식 변동을 부드럽게 만들기 위해 120영업일(약 6개월) 이동평균을 적용한 **평활화(Smoothing) 기법**을 사용합니다.

### PER 밴드 기준
반도체 섹터의 특성상 이익 변동성(Cycle)이 커서, 과거 분포 대신 **증권사 리포트 표준에 기반한 고정 배수(Multiple)**를 적용합니다.
*   **삼성전자:** 8x, 10x, 12x, 15x, 20x
*   **SK하이닉스:** 5x, 8x, 12x, 15x, 20x

### PBR 밴드 기준
PBR은 자본 기반이므로 상대적으로 변동성이 적어, 최근 5년간 데이터의 **통계적 분포(분위수, Quantile)**를 기준으로 밴드를 그립니다.
| 분위수 | 색상 (라인업) | 해석 |
| --- | --- | --- |
| **10%** | 빨강 계열 (#FF6B6B) | 역사적 저평가 (바닥권) |
| **25%** | 주황 계열 (#FFB347) | 다소 저평가 |
| **50%** | 파랑 계열 (#87CEEB) | 과거 5년 평균 (중립) |
| **75%** | 연두 계열 (#77DD77) | 다소 고평가 |
| **90%** | 보라 계열 (#DDA0DD) | 역사적 고평가 (과열권) |

## 대상 종목

- 🏢 삼성전자 (005930)
- 💾 SK하이닉스 (000660)

## 기술 스택

- `pykrx` — KRX 주식 데이터 수집
- `matplotlib` — 밴드 차트 시각화
- `GitHub Actions` — 평일 자동 업데이트
- `GitHub Pages` — 정적 웹 호스팅

## 로컬 실행

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 자동 업데이트

GitHub Actions가 **매일 평일 20시 30분 (KST)** 자동으로 차트를 갱신합니다.
