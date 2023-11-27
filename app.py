import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
import sys, os, re
import plotly.express as px
from tqdm import tqdm
from tools import merge_dup_fund, save_excel
import altair as alt

# Path
script_path = sys.argv[0]
script_dir = os.path.dirname(script_path)
exe_dir = os.path.abspath(script_dir)
file_extension = os.path.splitext(sys.argv[0])[1]

if file_extension.lower() == '.exe':
    # .exe
    rawdata_path = exe_dir + "\\" + "data_raw"
    newdata_path = exe_dir + "\\" + "data_new"
    output_path = exe_dir
elif file_extension.lower() == '.py':
    # .py
    rawdata_path = r'C:\Users\JongHyeonPark\vogo-fund.com\HEDGE - 문서\04. PM\Weekly HF\data_raw'
    newdata_path = r'C:\Users\JongHyeonPark\vogo-fund.com\HEDGE - 문서\04. PM\Weekly HF\data_new'
    output_path = r'C:\Users\JongHyeonPark\vogo-fund.com\HEDGE - 문서\04. PM\Weekly HF'

ret_vogo = pd.read_excel(r'vogo_hedge_return.xlsx', header=1).iloc[:, :14]
ret_vogo.기준일 = pd.to_datetime(ret_vogo.기준일).dt.strftime('%Y-%m-%d')
ret_vogo.설정일 = pd.to_datetime(ret_vogo.설정일).dt.strftime('%Y-%m-%d')
ref_vogo = pd.read_excel(r'vogo_ref.xlsx', header=0, index_col=0)
ref_vogo = ref_vogo.apply(lambda x: x.str.replace(',', '').astype(float))

st.set_page_config(
    page_title="Test Page",
    layout="wide"
)

# 타이틀 추가
st.title("Test Page")

# 데이터 가져오기


st.button('abc')



list_date = [name[-13:-5] for name in os.listdir(newdata_path)][::-1]
options_date = st.selectbox(label='날짜 선택', options=list_date)
filepath_new = os.path.join(newdata_path, 'new_한국형 HF 주간보고_'+options_date+".xlsx")
df = pd.read_excel(filepath_new)

for index, row in df.iterrows():
    try:
        df.at[index, '설정일'] = pd.to_datetime(row['설정일'])
    except (TypeError, ValueError):
        print(f"Error in row {index}: Skipping the conversion for '설정일' column in this row.")
        continue

df[['설정이후', 'YOY', 'YTD', '1M', '1W']] = df[['설정이후', 'YOY', 'YTD', '1M', '1W']]*100

df_strategy_amt = pd.DataFrame(df.groupby('전략')['설정액'].sum().sort_values(ascending=False)).reset_index()
df_amc_amt = pd.DataFrame(df.groupby('운용사')['설정액'].sum().sort_values(ascending=False)).iloc[:49].reset_index()


# 전략별
chart_str = alt.Chart(
    data=df_strategy_amt,
    title='전략별 설정액'
).mark_bar().encode(
    x=alt.X('전략',
            axis=alt.Axis(labelColor='black')
            ).sort('-y'),
    y=alt.Y('설정액',
            axis=alt.Axis(labelColor='black')),
    color=alt.value('steelblue')
).interactive(
).configure_axis(
        labelFontSize=14
).properties(
    width=1600, height=400
)

st.altair_chart(chart_str)


# 운용사별
chart_amc = alt.Chart(
    data=df_amc_amt,
    title='운용사별 설정액 Top 50').mark_bar().encode(
    x=alt.X('운용사',
            axis=alt.Axis(labelColor='black')).sort('-y'),
    y=alt.Y('설정액',
            axis=alt.Axis(labelColor='black')),
    color=alt.condition(
        alt.datum.운용사 == '보고',
        alt.value('orange'),
        alt.value('steelblue')
    )
).interactive(
).configure_axis(
        labelFontSize=14
    ).properties(width=1600, height=400)


st.altair_chart(chart_amc)

list_amc = df.운용사.unique()

options_amc = st.multiselect(
    '운용사 선택',
    options=list_amc,
    default='보고'
)

df_filtered_amc = df[df['운용사'].isin(options_amc)]

list_strategy = df_filtered_amc.전략.unique()

options_strategy = st.multiselect(
    '전략 선택',
    options=list_strategy,
    default=list_strategy
)

df_filtered = df[(df['운용사'].isin(options_amc))&(df['전략'].isin(options_strategy))]

options_columns = st.multiselect(
    '칼럼 선택',
    options=df.columns,
    default=['펀드명', '설정일', '운용사','전략', '설정액', '설정액 증감', '설정이후', 'YOY', 'YTD', '1M', '1W']
)

tab1, tab2 = st.tabs(["Table", "VOGO"])
with tab1:
    col1, col2 = st.columns([1, 3])
    with col1:
        pie_amc = alt.Chart(df_filtered_amc).mark_arc(
            innerRadius=50
        ).encode(
            theta='설정액',
            color='전략'
        )
        st.altair_chart(pie_amc)
    with col2:
        st.dataframe(
            df_filtered[options_columns],
            height=int(len(df_filtered)*41.67),
            use_container_width=True,
            column_config={
                "설정일":st.column_config.DateColumn("설정일", format='YYYY-MM-DD', width="medium"),
                "펀드명":st.column_config.TextColumn("펀드명", width="large"),
                "설정액": st.column_config.NumberColumn("설정액", format="%.2f"),
                "설정액 증감": st.column_config.NumberColumn("설정액 증감", format="%.2f"),
                "설정이후": st.column_config.NumberColumn("설정이후", format="%.2f%%"),
                "YOY": st.column_config.NumberColumn("YOY", format="%.2f%%"),
                "YTD": st.column_config.NumberColumn("YTD", format="%.2f%%"),
                "1M": st.column_config.NumberColumn("1M", format="%.2f%%"),
                "1W": st.column_config.NumberColumn("1W", format="%.2f%%"),
            }

        )

with tab2:
    st.dataframe(
        ret_vogo[['기준일', '펀드코드', '펀드명', '설정일', '설정액', '순자산', '1주', '1개월', '3개월', '1년', '연초이후', '설정이후']],
        height=1050,
        column_config={
            "1주": st.column_config.NumberColumn("1W", format="%.2f%%"),
            "1개월": st.column_config.NumberColumn("1M", format="%.2f%%"),
            "3개월": st.column_config.NumberColumn("3M", format="%.2f%%"),
            "1년": st.column_config.NumberColumn("YOY", format="%.2f%%"),
            "연초이후": st.column_config.NumberColumn("YTD", format="%.2f%%"),
            "설정이후": st.column_config.NumberColumn("ITD", format="%.2f%%"),
        }
    )
    options_fund = st.selectbox(
        label='펀드 선택',
        options=ret_vogo.펀드명,
    )
    code = ret_vogo[ret_vogo['펀드명']==options_fund].펀드코드.values[0]
    ref = ref_vogo[code]
    df_cumret = pd.DataFrame(ref[ref != 0] / 1000 - 1)
    df_cumret.index = df_cumret.index.strftime('%Y-%m-%d')
    df_cumret = df_cumret.reset_index()
    df_cumret.columns = ['date', 'cumret']

    chart = alt.Chart(df_cumret).mark_area(
        line={"color": "grey"},
        #point=alt.OverlayMarkDef(filled=False, fill="white")
        color = alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="white", offset=0),
                alt.GradientStop(color="steelblue", offset=1)
            ]
        )
    ).encode(
        x=alt.X('date:T'),
        y=alt.Y('cumret:Q', axis=alt.Axis(format='%')),
        tooltip=[
            alt.Tooltip('date:T', format='%Y-%m-%d'),
            alt.Tooltip('cumret:Q', format='.2%')
        ]
    ).add_params(
        alt.selection_interval()
    )
    st.altair_chart(chart, theme='streamlit', use_container_width=True)




