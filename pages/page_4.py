# Contents of ~/my_app/pages/page_4.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

from main_page import get_data_from_excel
from pages.page_2 import aggrid_df

st.markdown("# Page 3:M1_M3εζ π")
st.sidebar.markdown("# Page 3:M1_M3εζ π")

df1, df2 = get_data_from_excel(filename="B_ROLLRATE_2M")
multipage = st.sidebar.radio("ιζ©εζη»΄εΊ¦", ('ζ΄δ½', 'ζΆι΄η»΄εΊ¦', 'δΊ§εη»΄εΊ¦', 'ζ¬θ‘εζ'))


def select_sjdf(data, prodt_l5_up=None, prodt_l5=None, LOANSTATUS=None, group=None, index_=None):
    indexs = ['REPORT_DT']
    if index_ is not None:
        indexs.append(index_)
    sql = "DELQ_hx==1"
    if prodt_l5_up is not None:
        sql = sql + " & prodt_l5_up == @prodt_l5_up"
    if prodt_l5 is not None:
        sql = sql + " & prodt_l5 == @prodt_l5"
    if LOANSTATUS is not None:
        sql = sql + " & LOANSTATUS == @LOANSTATUS"
    if group is not None:
        sql = sql + " & brh_group_2022 == @group"
    df_selection = data.query(sql)
    result_data = pd.pivot_table(df_selection,
                                 index=indexs,
                                 columns=['DELQ_hx_n2'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    m1_m3_data = result_data.div(result_data.sum(axis=1), axis=0)[[3]]
    m1_m3_data.columns = ['M1-M3']

    return m1_m3_data


def select_cpdf(data, start_time, end_time, prodt_select, LOANSTATUS, group=None):
    # εδΊ§εδΈθ―εζ
    if group is None:
        df_selection = data.query(
            "REPORT_DT >= @start_time & REPORT_DT <= @end_time & LOANSTATUS == @LOANSTATUS & "
            "DELQ_hx==1")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & REPORT_DT >= @start_time & REPORT_DT <= @end_time & "
            "LOANSTATUS == @LOANSTATUS & DELQ_hx==1")
    result_data = pd.pivot_table(df_selection,
                                 index=prodt_select,
                                 columns=['DELQ_hx_n2'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    m1_m3_data = result_data.div(result_data.sum(axis=1), axis=0)[[3]]
    m1_m3_data.columns = ['M1-M3']
    return m1_m3_data


def select_bhdf(data, start_time, end_time, LOANSTATUS, index_select):
    # εζ―θ‘δΈθ―εζ
    df_selection = data.query("DELQ_hx == 1 & REPORT_DT >= @start_time & REPORT_DT <= @end_time "
                              "& LOANSTATUS == @LOANSTATUS")
    # δ½ι’γδΈθ―
    if index_select == 'sub_brh_name':
        select_pt_name = st.selectbox("ιζ©δΊ§εεζ",
                                      ['ε¨ι¨', 'δΈͺδΊΊιζΏζΆθ΄Ήθ΄·ζ¬Ύ', 'δΈͺδΊΊη»θ₯ζ§θ΄·ζ¬Ύ', 'δΈͺδΊΊδ½ζΏζΆθ΄Ήθ΄·ζ¬Ύ'])
        if select_pt_name == 'ε¨ι¨':
            pass
        else:
            df_selection = df_selection[df_selection['prodt_l5_up'] == select_pt_name]
        pg_title = "εζ―θ‘{}M1-M3ζ»ε¨η".format(select_pt_name)
    else:
        pg_title = "{}M1-M3ζ»ε¨η".format(index_select)
    result_data = pd.pivot_table(df_selection,
                                 index=index_select,
                                 columns=['DELQ_hx_n2'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    m1_m3_data = result_data.div(result_data.sum(axis=1), axis=0)[[3]]
    m1_m3_data.columns = ['m1-m3']
    ye_data = result_data[[3]]  ##
    ye_data.columns = ['θ΄·ζ¬Ύδ½ι’']
    bf_sysdata = pd.concat([m1_m3_data, ye_data], axis=1)

    bf_sysdata.reset_index(inplace=True)
    aggrid_df(bf_sysdata)
    fig1 = go.Bar(x=bf_sysdata[index_select],
                  y=bf_sysdata['θ΄·ζ¬Ύδ½ι’'],
                  name='θ΄·ζ¬Ύδ½ι’')

    fig2 = go.Scatter(x=bf_sysdata[index_select],
                      y=bf_sysdata['m1-m3'],
                      mode="lines+markers+text",
                      text=bf_sysdata['m1-m3'].apply(lambda x: format(x, '.2%')),
                      yaxis="y2",
                      name='m1-m3')
    datas = [fig1, fig2]
    layout = go.Layout(title=pg_title,
                       xaxis=dict(tickangle=-45),
                       yaxis=dict(title="θ΄·ζ¬Ύδ½ι’"),
                       yaxis2=dict(title="m1-m3", overlaying="y", side="right", tickformat='2%'),
                       )
    fig = go.Figure(data=datas, layout=layout)
    st.plotly_chart(fig)
    ## δΈι»εζ ['sub_brh_name', 'prodt_l5_up', 'prodt_l5', 'prodt_l6_up'],
    sub_brh_name = st.selectbox("δΈι»ζ―θ‘εζ",
                                data["sub_brh_name"].unique())
    cp_type = st.selectbox("ιζ©δΊ§εη­ηΊ§",
                           ('prodt_l5', 'prodt_l6_up', 'prodt_l5_up'))
    df2_selection = df_selection.query("sub_brh_name == @sub_brh_name")
    result_data2 = pd.pivot_table(df2_selection,
                                  index=cp_type,
                                  columns=['DELQ_hx_n2'],
                                  values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                  aggfunc=[np.sum])
    result_data2.columns = result_data2.columns.droplevel([0, 1])
    m1_m3_data_2 = result_data2.div(result_data2.sum(axis=1), axis=0)[[3]]
    m1_m3_data_2.columns = ['m1-m3']
    ye_data_2 = result_data2[[3]]
    ye_data_2.columns = ['θ΄·ζ¬Ύδ½ι’']
    bf_sysdata_2 = pd.concat([m1_m3_data_2, ye_data_2], axis=1)
    bf_sysdata_2.reset_index(inplace=True)
    bf_sysdata_2.fillna(0, inplace=True)
    datas_2 = [go.Bar(x=bf_sysdata_2[cp_type],
                      y=bf_sysdata_2['θ΄·ζ¬Ύδ½ι’'],
                      text=bf_sysdata_2['θ΄·ζ¬Ύδ½ι’'].round(),
                      textposition='outside',
                      name='θ΄·ζ¬Ύδ½ι’'),
               go.Scatter(x=bf_sysdata_2[cp_type],
                          y=bf_sysdata_2['m1-m3'],
                          mode='lines+markers+text',
                          text=bf_sysdata_2['m1-m3'].apply(lambda x: format(x, '.2%')),
                          line=dict(color="Crimson"),
                          yaxis="y2",
                          name='m1-m3')]
    layout2 = go.Layout(title="{} {} η»΄εΊ¦M1-M3εΎ".format(sub_brh_name, cp_type),
                        xaxis=dict(title=cp_type),
                        yaxis=dict(title="θ΄·ζ¬Ύδ½ι’"),
                        yaxis2=dict(title="M1-M3", overlaying="y", side="right",tickformat='2%'),
                        )
    fig2 = go.Figure(data=datas_2, layout=layout2)
    st.plotly_chart(fig2)


if multipage == 'ζ΄δ½':
    st.info('ζ¬θ‘M1-M3ζ΄δ½ζ°ζ?')
    st.dataframe(df1)
    st.info('ε¨θ‘M1-M3ζ΄δ½ζ°ζ?')
    st.dataframe(df2)

if multipage == 'ζΆι΄η»΄εΊ¦':
    # δΎ§θΎΉζ 
    st.sidebar.header("θ―·ε¨θΏιη­ι:")
    prodt_l5_up = st.sidebar.multiselect(
        "δΊ§εη±»εprodt_l5_up:",
        options=df2["prodt_l5_up"].unique(),
        default=df2["prodt_l5_up"].unique()
    )
    prodt_l5 = st.sidebar.multiselect(
        "δΊ§εη±»εprodt_l5:",
        options=df2["prodt_l5"].unique(),
        default=df2["prodt_l5"].unique()
    )
    LOANSTATUS = st.sidebar.multiselect(
        "θ΄·ζ¬ΎηΆζ:",
        options=df2["LOANSTATUS"].unique(),
        default=['FS01']
    )
    # ειη¬¦
    st.markdown("""---""")

    bh_select = select_sjdf(df1, prodt_l5_up, prodt_l5, LOANSTATUS, group=None)
    st.info('ζ¬θ‘ {} M1-M3ζ»ε¨ηζ΄δ½ζε΅'.format(prodt_l5_up))
    st.table(bh_select)
    bz_select = select_sjdf(df2, prodt_l5_up, prodt_l5, LOANSTATUS, group='η¬¬δΈη»')
    st.info('ζ¬η» {} M1-M3ζ»ε¨ηζ΄δ½ζε΅'.format(prodt_l5_up))
    st.table(bz_select)
    qh_select = select_sjdf(df2, prodt_l5_up, prodt_l5, LOANSTATUS, group=None)
    st.info('ε¨θ‘ {} M1-M3ζ»ε¨ηζ΄δ½ζε΅'.format(prodt_l5_up))
    st.table(qh_select)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bh_select.index,
                             y=bh_select['M1-M3'],
                             mode='lines+markers+text',
                             text=bh_select['M1-M3'].apply(lambda x: format(x, '.2%')),
                             line=dict(color="Crimson"),
                             name='ζ¬θ‘'))
    fig.add_trace(go.Scatter(x=bz_select.index,
                             y=bz_select['M1-M3'],
                             mode='lines+markers+text',
                             line=dict(color="MediumPurple"),
                             name='ζ¬η»'))
    fig.add_trace(go.Scatter(x=qh_select.index,
                             y=qh_select['M1-M3'],
                             mode='lines+markers+text',
                             line=dict(color="Blue"),
                             name='ε¨θ‘'))
    fig.update_layout(width=800,
                      height=500,  # ζΉεζ΄δΈͺfigureηε€§ε°
                      title_text="δΊ§ε {} ε¨θ‘γζ¬η»γζ¬θ‘M1-M3ζ»ε¨η".format(prodt_l5_up),
                      xaxis=dict(tickformat="%Y-%m"),
                      yaxis=dict(tickformat='2%'),
                      )
    st.plotly_chart(fig)
    # ειη¬¦
    st.markdown("""---""")
    st.markdown("### ε―Ήε¨θ‘γζ¬η»εζ¬θ‘δΈͺδΊΊιζΏζΆθ΄ΉγδΈͺδΊΊη»θ₯ζ§θ΄·ζ¬ΎεδΈͺδΊΊδ½ζΏζΆθ΄Ήθ΄·ζ¬ΎδΈε‘M1-M3ζ»ε¨ηθΏθ‘ε±η€Ί")
    # ε―Ήε¨θ‘γζ¬η»εζ¬θ‘δΈͺδΊΊιζΏζΆθ΄ΉγδΈͺδΊΊη»θ₯ζ§θ΄·ζ¬ΎεδΈͺδΊΊδ½ζΏζΆθ΄Ήθ΄·ζ¬ΎδΈε‘M1-M3ζ»ε¨ηθΏθ‘ε±η€Ί
    select_name = st.selectbox("ιζ©εζζ η",
                               ['ζ¬θ‘', 'ε¨θ‘', 'ζ¬η»'])
    if select_name == 'ζ¬θ‘':
        select_bh = select_sjdf(df1, index_='prodt_l5_up')
    elif select_name == 'ζ¬η»':
        select_bh = select_sjdf(df2, group='η¬¬δΈη»', index_='prodt_l5_up')
    else:
        select_bh = select_sjdf(df2, index_='prodt_l5_up')
    select_bh.reset_index(inplace=True)
    select_bh['M1-M3'] = select_bh['M1-M3'].fillna(0)
    fig = px.line(select_bh,
                  x='REPORT_DT',
                  y='M1-M3',
                  text=select_bh['M1-M3'].apply(lambda x: format(x, '.2%')),
                  color='prodt_l5_up',
                  title="δΈͺδΊΊιζΏζΆθ΄ΉγδΈͺδΊΊη»θ₯ζ§θ΄·ζ¬ΎεδΈͺδΊΊδ½ζΏζΆθ΄Ήθ΄·ζ¬ΎδΈε‘M1-M3ζ»ε¨η"
                  )
    fig.update_layout(height=500, width=800,
                      yaxis=dict(tickformat='2%'),
                      xaxis=dict(
                          tickangle=-45,
                          type='category')
                      )
    st.plotly_chart(fig)
if multipage == 'δΊ§εη»΄εΊ¦':
    # δΎ§θΎΉζ 
    st.sidebar.header("θ―·ε¨θΏιη­ι:")
    options = sorted((df2['REPORT_DT']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("θ―·ιζ©ζ₯εεΉ΄ζεΊι΄οΌ",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    prodt_select = st.sidebar.selectbox('ιζ©δΊ§εεη±»ηζ ε', ('prodt_l5_up', 'prodt_l5'))
    st.markdown('#### ζ₯εεΊι΄ {} θ³ {} εδΊ§εM1-M3εζ'.format(start_time, end_time))
    LOANSTATUS = st.sidebar.multiselect(
        "θ΄·ζ¬ΎηΆζ:",
        options=df2["LOANSTATUS"].unique(),
        default=['FS01']
    )
    # ειη¬¦
    st.markdown("""---""")

    bh_select = select_cpdf(df1, start_time, end_time, prodt_select, LOANSTATUS, group=None)
    st.info('ζ¬θ‘ {} θ³ {} εδΊ§εM1-M3ζ΄δ½ζε΅'.format(start_time, end_time))
    st.table(bh_select)
    bz_select = select_cpdf(df2, start_time, end_time, prodt_select, LOANSTATUS, group='η¬¬δΈη»')
    st.info('ζ¬η» {} θ³ {} εδΊ§εM1-M3ζ΄δ½ζε΅'.format(start_time, end_time))
    st.table(bz_select)
    qh_select = select_cpdf(df2, start_time, end_time, prodt_select, LOANSTATUS, group=None)
    st.info('ε¨θ‘ {} θ³ {} εδΊ§εM1-M3ζ΄δ½ζε΅'.format(start_time, end_time))
    st.table(qh_select)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=bh_select.index,
                         y=bh_select['M1-M3'],
                         text=bh_select['M1-M3'].apply(lambda x: format(x, '.2%')),
                         textposition='outside',
                         name='ζ¬θ‘'))
    fig.add_trace(go.Bar(x=bz_select.index,
                         y=bz_select['M1-M3'],
                         text=bz_select['M1-M3'].apply(lambda x: format(x, '.2%')),
                         textposition='outside',
                         name='ζ¬η»'))
    fig.add_trace(go.Bar(x=qh_select.index,
                         y=qh_select['M1-M3'],
                         text=qh_select['M1-M3'].apply(lambda x: format(x, '.2%')),
                         textposition='outside',
                         name='ε¨θ‘'))
    fig.update_layout(width=800,
                      height=500,  # ζΉεζ΄δΈͺfigureηε€§ε°
                      title_text=' {} θ³ {} εδΊ§εM1-M3ζ΄δ½ζε΅'.format(start_time, end_time),
                      xaxis=dict(tickformat="%Y-%m"),
                      yaxis=dict(title="M1-M3", overlaying="y", tickformat='2%'),
                      )
    st.plotly_chart(fig)
if multipage == 'ζ¬θ‘εζ':
    # ζΊζγδΊ§εγη»΄εΊ¦εζ
    st.sidebar.header("θ―·ε¨θΏιη­ι:")
    options = sorted((df1['REPORT_DT']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("θ―·ιζ©ζ₯εεΉ΄ζεΊι΄οΌ",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    LOANSTATUS = st.sidebar.multiselect(
        "θ΄·ζ¬ΎηΆζ:",
        options=df1["LOANSTATUS"].unique(),
        default=['FS01']
    )
    index_select = st.sidebar.selectbox(
        "η»΄εΊ¦ιζ©:",
        options=['sub_brh_name', 'prodt_l5_up', 'prodt_l5', 'prodt_l6_up'],
    )

    st.markdown('#### ζ₯εεΊι΄ {} θ³ {} ε{}M1-M3εζ'.format(start_time, end_time,index_select))
    bf_sysdata = select_bhdf(df1, start_time, end_time, LOANSTATUS, index_select)
