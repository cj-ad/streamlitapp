# Contents of ~/my_app/pages/page_2.py
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

from main_page import get_data_from_excel

st.markdown("# Page 2：新发放贷款不良分析 ❄️")
st.sidebar.markdown("# Page 2 ：新发放贷款不良分析❄️")


def aggrid_df(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",
                                editable=True)
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True)


df1, df2 = get_data_from_excel(filename='B_14MOB_NONPERF_GEN')

multipage = st.sidebar.radio("选择分析维度", ('整体', '时间维度', '产品维度', '本行分析'))


def select_sjdf(data, start_time, end_time, prodt_l5_up, prodt_l5, group=None):
    if group is None:
        df_selection = data.query(
            "REPORT_DT >= @start_time & REPORT_DT <= @end_time & prodt_l5_up == @prodt_l5_up & prodt_l5 == @prodt_l5")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & REPORT_DT >= @start_time & REPORT_DT <= @end_time & prodt_l5_up == @prodt_l5_up & prodt_l5 == @prodt_l5")
    result_data = pd.pivot_table(df_selection,
                                 index='DATEBEG_M',
                                 values=['nonperf_delq_prin_balance_sum_w', 'LOAN_AMOUNT_W'],
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel(0)
    result_data['NONPERF_GEN_RATIO'] = result_data['nonperf_delq_prin_balance_sum_w'] / \
                                       result_data['LOAN_AMOUNT_W']
    return result_data


def select_cpdf(data, prodt_select, start_time, end_time, group=None):
    # 各产品不良分析
    if group is None:
        df_selection = data.query(
            "REPORT_DT >= @start_time & REPORT_DT <= @end_time")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & REPORT_DT >= @start_time & REPORT_DT <= @end_time")
    result_data = pd.pivot_table(df_selection,
                                 index=prodt_select,
                                 values=['nonperf_delq_prin_balance_sum_w', 'LOAN_AMOUNT_W'],
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel(0)
    result_data['NONPERF_GEN_RATIO'] = result_data['nonperf_delq_prin_balance_sum_w'] / \
                                       result_data['LOAN_AMOUNT_W']
    return result_data


def plt_ye_bl(df, x_lab, title=None):
    # 不良、余额图
    plt_data = df.copy()
    loan_sum = plt_data['LOAN_AMOUNT_W'].sum()
    nonperf_sum = plt_data['nonperf_delq_prin_balance_sum_w'].sum()
    nonperf_ratio = nonperf_sum / loan_sum
    index_m = max(plt_data.index) + 1
    plt_data.loc[index_m, 'sub_brh_name'] = '北京分行'
    plt_data.loc[index_m, 'LOAN_AMOUNT_W'] = loan_sum
    plt_data.loc[index_m, 'nonperf_delq_prin_balance_sum_w'] = nonperf_sum
    plt_data.loc[index_m, 'NONPERF_GEN_RATIO'] = nonperf_ratio

    fig1 = go.Bar(x=plt_data[x_lab],
                  y=plt_data['LOAN_AMOUNT_W'],
                  text=plt_data['LOAN_AMOUNT_W'].round(),
                  textposition='outside',
                  name='贷款余额')

    fig2 = go.Scatter(x=plt_data[x_lab],
                      y=plt_data['NONPERF_GEN_RATIO'],
                      mode="markers+lines+text",
                      text=plt_data['NONPERF_GEN_RATIO'].apply(lambda x: format(x, '.2%')),
                      yaxis="y2",
                      name='不良率')
    datas = [fig1, fig2]
    layout = go.Layout(title=title,
                       xaxis=dict(tickangle=-45, ),
                       yaxis=dict(title="贷款余额"),
                       yaxis2=dict(title="不良率", overlaying="y", side="right", tickformat='2%'),
                       )

    fig = go.Figure(data=datas, layout=layout)
    fig.update_layout(legend=dict(
        orientation="h",  # 控制水平显示
        yanchor="bottom",  # 分别设置xy轴的位置和距离大小
        y=1.02,
        xanchor="right",
        x=1
    ))
    st.plotly_chart(fig)


def select_bhdf(data, start_time, end_time, index_select):
    # 本行分析：各支行不良分析
    df_selection = data.query("DATEBEG_M >= @start_time & DATEBEG_M <= @end_time")
    result_data = pd.pivot_table(df_selection,
                                 index=index_select,
                                 values=['nonperf_delq_prin_balance_sum_w', 'LOAN_AMOUNT_W'],
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel(0)
    result_data['NONPERF_GEN_RATIO'] = result_data['nonperf_delq_prin_balance_sum_w'] / \
                                       result_data['LOAN_AMOUNT_W']

    bf_sysdata = result_data.reset_index()
    aggrid_df(bf_sysdata)
    if len(index_select) == 1:
        # 余额、不良
        title = '{}新发放贷款不良生产率'.format(index_select[0])
        plt_ye_bl(df=bf_sysdata, x_lab=index_select[0], title=title)
    if len(index_select) == 2:
        color_lab = index_select[1]

        for pg in bf_sysdata[color_lab].unique():
            title = '各支行{}新发放贷款不良生产率'.format(pg)
            plt_ye_bl(df=bf_sysdata[bf_sysdata[color_lab] == pg], x_lab=index_select[0],
                      title=title)

    ## 下钻分析 ['sub_brh_name', 'prodt_l5_up', 'prodt_l5', 'prodt_l6_up'],
    sub_brh_name = st.selectbox("下钻支行分析",
                                data["sub_brh_name"].unique())
    cp_type = st.selectbox("选择产品等级",
                           ('prodt_l5', 'prodt_l6_up', 'prodt_l5_up'))
    df2_selection = df_selection.query("sub_brh_name == @sub_brh_name")

    result_data2 = pd.pivot_table(df2_selection,
                                  index=cp_type,
                                  values=['nonperf_delq_prin_balance_sum_w', 'LOAN_AMOUNT_W'],
                                  aggfunc=[np.sum])
    result_data2.columns = result_data2.columns.droplevel(0)
    result_data2['NONPERF_GEN_RATIO'] = result_data2['nonperf_delq_prin_balance_sum_w'] / \
                                        result_data2['LOAN_AMOUNT_W']
    bf_sysdata_2 = result_data2.reset_index()

    datas_2 = [go.Bar(x=bf_sysdata_2[cp_type],
                      y=bf_sysdata_2['LOAN_AMOUNT_W'],
                      text=bf_sysdata_2['LOAN_AMOUNT_W'].round(),
                      textposition='outside',
                      name='贷款余额'),
               go.Scatter(x=bf_sysdata_2[cp_type],
                          y=bf_sysdata_2['NONPERF_GEN_RATIO'],
                          mode="markers+lines+text",
                          yaxis="y2",
                          text=bf_sysdata_2['NONPERF_GEN_RATIO'].apply(lambda x: format(x, '.2%')),
                          name='不良率')]
    layout2 = go.Layout(title="{} {} 维度不良率图".format(sub_brh_name, cp_type),
                        xaxis=dict(title=cp_type, tickangle=-45),
                        yaxis=dict(title="贷款余额"),
                        yaxis2=dict(title="不良率", overlaying="y", side="right", tickformat='2%'),
                        )
    fig2 = go.Figure(data=datas_2, layout=layout2)
    fig2.update_layout(legend=dict(
        orientation="h",  # 控制水平显示
        yanchor="bottom",  # 分别设置xy轴的位置和距离大小
        y=1.02,
        xanchor="right",
        x=1
    ))
    st.plotly_chart(fig2)


if multipage == '整体':
    st.info('本行新发放贷款不良整体情况')
    st.dataframe(df1)
    st.info('全行新发放贷款不良整体情况')
    st.dataframe(df2)

if multipage == '时间维度':
    # 侧边栏
    st.sidebar.header("请在这里筛选:")
    options = sorted((df2['REPORT_DT']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("请选择报告日期区间：",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    st.markdown('#### 分析报告日期区间 {} 至 {}'.format(start_time, end_time))

    prodt_l5_up = st.sidebar.multiselect(
        "产品类型prodt_l5_up:",
        options=df2["prodt_l5_up"].unique(),
        default=df2["prodt_l5_up"].unique()
    )
    prodt_l5 = st.sidebar.multiselect(
        "产品类型prodt_l5:",
        options=df2["prodt_l5"].unique(),
        default=df2["prodt_l5"].unique()
    )
    # 分隔符
    st.markdown("""---""")

    bh_select = select_sjdf(df1, start_time, end_time, prodt_l5_up, prodt_l5, group=None)
    st.info('本行 {} 新发放贷款不良整体情况'.format(prodt_l5_up))
    st.table(bh_select)
    bz_select = select_sjdf(df2, start_time, end_time, prodt_l5_up, prodt_l5, group='第一组')
    st.info('本组 {} 新发放贷款不良整体情况'.format(prodt_l5_up))
    st.table(bz_select)
    qh_select = select_sjdf(df2, start_time, end_time, prodt_l5_up, prodt_l5, group=None)
    st.info('全行 {} 新发放贷款不良整体情况'.format(prodt_l5_up))
    st.table(qh_select)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bh_select.index,
                             y=bh_select['NONPERF_GEN_RATIO'],
                             mode="markers+lines+text",
                             text=bh_select['NONPERF_GEN_RATIO'].apply(lambda x: format(x, '.2%')),
                             textposition="top center",
                             line=dict(color="Crimson"),
                             name='本行'))
    fig.add_trace(go.Scatter(x=bz_select.index,
                             y=bz_select['NONPERF_GEN_RATIO'],
                             mode='lines+markers',
                             line=dict(color="MediumPurple"),
                             name='本组'))
    fig.add_trace(go.Scatter(x=qh_select.index,
                             y=qh_select['NONPERF_GEN_RATIO'],
                             mode='lines+markers',
                             line=dict(color="Blue"),
                             name='全行'))
    fig.update_layout(width=800,
                      height=500,  # 改变整个figure的大小
                      title_text="{} 至 {} 区间不良率趋势".format(start_time, end_time),
                      yaxis=dict(tickformat='2%'),
                      xaxis=dict(
                          tickangle=-45,
                          type='category')
                      )
    st.plotly_chart(fig)
    # temp = issue_yearmonth_to_grade_level.stack().reset_index()
    # temp.columns = ['issue_yearmonth', 'grade_level_adj', 'ratio']

if multipage == '产品维度':
    st.sidebar.header("请在这里筛选:")

    options = sorted((df2['REPORT_DT']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("请选择报告年月区间：",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    prodt_select = st.sidebar.selectbox('选择产品分类的标准', ('prodt_l5_up', 'prodt_l5'))
    st.markdown('#### 报告区间 {} 至 {} 各产品不良率分析'.format(start_time, end_time))

    # 分隔符
    st.markdown("""---""")

    bh_cpselect = select_cpdf(df1, prodt_select, start_time, end_time, group=None)
    bz_cpselect = select_cpdf(df2, prodt_select, start_time, end_time, group='第一组')
    qh_cpselect = select_cpdf(df2, prodt_select, start_time, end_time, group=None)
    st.info('本行 {} 各产品不良率分析'.format(prodt_select))
    st.table(bh_cpselect)
    st.info('本组 {} 各产品不良率分析'.format(prodt_select))
    st.table(bz_cpselect)
    st.info('全行 {} 各产品不良率分析'.format(prodt_select))
    st.table(qh_cpselect)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=bh_cpselect.index,
                         y=bh_cpselect['NONPERF_GEN_RATIO'],
                         name='本行'))
    fig.add_trace(go.Bar(x=bz_cpselect.index,
                         y=bz_cpselect['NONPERF_GEN_RATIO'],
                         name='本组'))
    fig.add_trace(go.Bar(x=qh_cpselect.index,
                         y=qh_cpselect['NONPERF_GEN_RATIO'],
                         name='全行'))
    fig.update_layout(width=800,
                      height=500,  # 改变整个figure的大小
                      title_text="{}不良率分析".format(prodt_select)
                      )
    st.plotly_chart(fig)

if multipage == '本行分析':
    # 机构、产品、还款方式维度分析
    st.sidebar.header("请在这里筛选:")
    options = sorted((df1['DATEBEG_M']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("请选择放款年月区间：",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    # prodt_l5_up = st.sidebar.multiselect(
    #     "产品类型1:",
    #     options=df1["prodt_l5_up"].unique(),
    #     default=df1["prodt_l5_up"].unique()
    # )
    # prodt_l5 = st.sidebar.multiselect(
    #     "产品类型2:",
    #     options=df1["prodt_l5"].unique(),
    #     default=df1["prodt_l5"].unique()
    # )
    index_select = st.sidebar.multiselect(
        "维度选择:",
        options=['sub_brh_name', 'prodt_l5_up', 'prodt_l5', 'prodt_l6_up', 'prodt_no_desc'],
        default=['sub_brh_name', 'prodt_l6_up'],
    )
    st.markdown('#### 放款区间 {} 至 {} 各支行不良率分析'.format(start_time, end_time))
    bf_sysdata = select_bhdf(df1, start_time, end_time, index_select)
