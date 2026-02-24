"""
삼성전자·SK하이닉스 PER/PBR 밴드 차트 생성기

pykrx로 일별 PER/PBR/EPS/BPS 데이터를 수집하고,
분위수 기반 밴드 차트를 matplotlib으로 생성합니다.
"""

from pykrx import stock
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform
from matplotlib import rc
from datetime import datetime, timedelta, timezone
import numpy as np

# ── 한글 폰트 설정 ──
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    rc('font', family='Malgun Gothic')
elif platform.system() == 'Linux':
    rc('font', family='NanumGothic')  # GitHub Actions (Ubuntu) 환경 대응
plt.rcParams['axes.unicode_minus'] = False

# ── 다크 모드 스타일 적용 ──
plt.style.use('dark_background')

# ── 대상 종목 정보 ──
STOCK_INFO = {
    '005930': {'name': '삼성전자', 'name_en': 'Samsung Electronics'},
    '000660': {'name': 'SK하이닉스', 'name_en': 'SK Hynix'},
}

# ── 밴드 분위수 설정 (색상 포함) ──
# 낮은 분위수부터 높은 분위수 순서로 정렬
BAND_QUANTILE = [
    (0.10, '#FF6B6B', '10%'),  # 저평가 구간 (빨강 계열)
    (0.25, '#FFB347', '25%'),  # 약간 저평가 (주황)
    (0.50, '#87CEEB', '50%'),  # 중립 (스카이블루)
    (0.75, '#77DD77', '75%'),  # 약간 고평가 (연두)
    (0.90, '#DDA0DD', '90%'),  # 고평가 구간 (보라)
]

# ── 데이터 조회 기간 ──
DATA_YEAR_RANGE = 5


def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    pykrx를 사용해 종목의 일별 종가 + PER/PBR/EPS/BPS 데이터를 수집합니다.

    Args:
        ticker: 종목 코드 (예: '005930')
        start_date: 조회 시작일 (예: '20210101')
        end_date: 조회 종료일 (예: '20260224')

    Returns:
        종가, PER, PBR, EPS, BPS 컬럼을 포함하는 DataFrame
    """
    # 일별 OHLCV 데이터 (종가 포함)
    df_price = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
    if df_price.empty:
        print(f"[오류] {ticker} 가격 데이터를 가져올 수 없습니다.")
        return pd.DataFrame()

    # 일별 PER/PBR/EPS/BPS 데이터
    df_fundamental = stock.get_market_fundamental_by_date(start_date, end_date, ticker)
    if df_fundamental.empty:
        print(f"[오류] {ticker} 기본 지표 데이터를 가져올 수 없습니다.")
        return pd.DataFrame()

    # 종가와 기본지표 병합
    df = pd.merge(
        df_price[['종가']],
        df_fundamental[['PER', 'PBR', 'EPS', 'BPS']],
        left_index=True,
        right_index=True,
        how='inner'
    )

    # 유효하지 않은 행 제거 (PER/PBR이 0이거나 EPS/BPS가 0인 경우)
    df = df[(df['PER'] > 0) & (df['PBR'] > 0) & (df['EPS'] != 0) & (df['BPS'] != 0)]

    return df


def calculate_band_line(df: pd.DataFrame, metric: str, ticker: str) -> dict:
    """
    밴드 라인을 계산합니다.
    EPS/BPS의 120일 이동평균을 사용하여 계단식 그래프를 부드럽게(Smoothing) 처리합니다.
    PER 밴드는 종목별 고정 배수를 사용하며 PBR 밴드는 최근 5년 분위수를 사용합니다.

    Args:
        df: 종가, PER, PBR, EPS, BPS가 포함된 DataFrame
        metric: 'PER' 또는 'PBR'
        ticker: 종목코드

    Returns:
        밴드 라인을 담은 dict
    """
    multiple_col = metric
    base_col = 'EPS' if metric == 'PER' else 'BPS'

    # 기본 지표(EPS/BPS) 스무딩 처리 (120일 영업일 기준 약 6개월 이동평균)
    smoothed_base = df[base_col].rolling(window=120, min_periods=1).mean()

    band_data = {}

    if metric == 'PER':
        # 증권사 리포트 표준에 가까운 종목별 고정 배수 사용
        if ticker == '005930':  # 삼성전자
            multiples = [(8.0, '#FF6B6B', '8x'),
                         (10.0, '#FFB347', '10x'),
                         (12.0, '#87CEEB', '12x'),
                         (15.0, '#77DD77', '15x'),
                         (20.0, '#DDA0DD', '20x')]
        else:  # SK하이닉스
            multiples = [(5.0, '#FF6B6B', '5x'),
                         (8.0, '#FFB347', '8x'),
                         (12.0, '#87CEEB', '12x'),
                         (15.0, '#77DD77', '15x'),
                         (20.0, '#DDA0DD', '20x')]

        for val, color, label in multiples:
            band_line = smoothed_base * val
            band_data[label] = {
                'line': band_line,
                'multiple': val,
                'color': color,
            }
    else:
        # PBR 밴드는 분위수 기준 사용
        for quantile, color, label in BAND_QUANTILE:
            multiple = df[multiple_col].quantile(quantile)
            band_line = smoothed_base * multiple
            band_data[label] = {
                'line': band_line,
                'multiple': multiple,
                'color': color,
            }

    return band_data


def plot_band_chart(
    df: pd.DataFrame,
    ticker: str,
    metric: str,
    output_filename: str,
) -> None:
    """
    PER 또는 PBR 밴드 차트를 생성하고 PNG 파일로 저장합니다.

    Args:
        df: 종가, PER, PBR, EPS, BPS가 포함된 DataFrame
        ticker: 종목코드
        metric: 'PER' 또는 'PBR'
        output_filename: 저장할 파일명
    """
    stock_name = STOCK_INFO[ticker]['name']
    band_data = calculate_band_line(df, metric, ticker)

    fig, ax = plt.subplots(figsize=(14, 8))

    # 밴드 라인 그리기 (면적 색칠 포함)
    sorted_band = sorted(band_data.items(), key=lambda x: x[1]['multiple'])

    # 밴드 사이 영역 색칠 (투명도 적용)
    for i in range(len(sorted_band) - 1):
        label_low, data_low = sorted_band[i]
        label_high, data_high = sorted_band[i + 1]
        ax.fill_between(
            df.index,
            data_low['line'],
            data_high['line'],
            alpha=0.08,
            color=data_low['color'],
        )

    # 밴드 라인 그리기
    for label, data in sorted_band:
        ax.plot(
            df.index,
            data['line'],
            label=f"{metric} {data['multiple']:.1f}x ({label})",
            color=data['color'],
            linewidth=1.2,
            linestyle='--',
            alpha=0.85,
        )

    # 현재 주가 그리기 (굵은 실선)
    ax.plot(
        df.index,
        df['종가'],
        label=f'{stock_name} 주가',
        color='white',
        linewidth=2.0,
        alpha=0.95,
    )

    # 현재가 표시
    last_date = df.index[-1]
    last_price = df['종가'].iloc[-1]
    last_metric = df[metric].iloc[-1]

    ax.annotate(
        f'현재: {last_price:,.0f}원\n({metric} {last_metric:.1f}x)',
        xy=(last_date, last_price),
        xytext=(last_date - pd.Timedelta(days=120), last_price * 1.08),
        ha='center',
        color='white',
        fontweight='bold',
        fontsize=12,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#333333', edgecolor='white', alpha=0.8),
    )

    # 차트 꾸미기
    kst = timezone(timedelta(hours=9))
    now_str = datetime.now(kst).strftime('%Y-%m-%d %H:%M')

    ax.set_title(
        f'{stock_name} {metric} 밴드 차트',
        fontsize=18,
        fontweight='bold',
        color='white',
        pad=15,
    )
    ax.set_xlabel(f'날짜 ({now_str} KST 기준)', fontsize=12, color='#CCCCCC')
    ax.set_ylabel('주가 (원)', fontsize=12, color='#CCCCCC')
    ax.grid(True, linestyle=':', alpha=0.3, color='gray')

    # 범례 설정
    ax.legend(
        loc='upper left',
        fontsize=10,
        facecolor='#1a1a1a',
        edgecolor='#555555',
        framealpha=0.9,
    )

    # Y축 천단위 콤마 포맷
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

    # X축 날짜 포맷
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f'[완료] {output_filename} 생성 ({stock_name} {metric} 밴드)')


def main():
    """
    전체 종목에 대해 PER/PBR 밴드 차트를 생성합니다.
    """
    # 조회 기간 설정
    kst = timezone(timedelta(hours=9))
    end_date = datetime.now(kst).strftime('%Y%m%d')
    start_date = (datetime.now(kst) - timedelta(days=365 * DATA_YEAR_RANGE)).strftime('%Y%m%d')

    print(f'데이터 조회 기간: {start_date} ~ {end_date}')

    for ticker, info in STOCK_INFO.items():
        print(f'\n{"=" * 50}')
        print(f'{info["name"]} ({ticker}) 처리 중...')
        print(f'{"=" * 50}')

        # 데이터 수집
        df = fetch_stock_data(ticker, start_date, end_date)
        if df.empty:
            print(f'[건너뜀] {info["name"]} 데이터가 없습니다.')
            continue

        print(f'수집된 데이터: {len(df)}건 ({df.index[0].strftime("%Y-%m-%d")} ~ {df.index[-1].strftime("%Y-%m-%d")})')
        print(f'현재 PER: {df["PER"].iloc[-1]:.1f}x | PBR: {df["PBR"].iloc[-1]:.2f}x')
        print(f'현재 종가: {df["종가"].iloc[-1]:,}원')

        # 파일명 접두어 결정
        prefix = 'samsung' if ticker == '005930' else 'hynix'

        # PER 밴드 차트 생성
        plot_band_chart(df, ticker, 'PER', f'{prefix}_per_band.png')

        # PBR 밴드 차트 생성
        plot_band_chart(df, ticker, 'PBR', f'{prefix}_pbr_band.png')

    print(f'\n{"=" * 50}')
    print('모든 차트 생성 완료!')


if __name__ == '__main__':
    main()
