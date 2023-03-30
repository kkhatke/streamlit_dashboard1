from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Title
st.set_page_config(page_title='Dashboard',
                   page_icon=":globe_with_meridians:",
                   layout='wide')

# Creating cache


@st.cache_data
def get_data_from_excel():
    # DataFrame
    df = pd.read_excel("C:/Users/31697/Desktop/otlay schemes.xlsx", header=0)
    return df


df = get_data_from_excel()

# SideBars
st.sidebar.header('Please Select Filters :')
Year = st.sidebar.multiselect(
    "Select the Year:",
    options=df['year'].unique(),
    default=df['year'].unique()
)
Scheme_type = st.sidebar.multiselect(
    "Select the Scheme Type:",
    options=df['scheme_type'].unique(),
    default=df['scheme_type'].unique()
)

# filter data
df_filtered = df.query(
    "year==@Year & scheme_type == @Scheme_type"
)
df_show = df_filtered.sort_values(by='expenditure', ascending=False).head(10)

# MainPage
st.title(":bar_chart: DashBoard")
st.markdown('##')

# KPI's
total_expenditure = int(df_filtered['expenditure'].sum())
total_schemes = np.count_nonzero(df_filtered['scheme'].unique())

grouped_df = df.groupby(by=['scheme']).sum()[['expenditure']].reset_index()
max_row = grouped_df.loc[grouped_df['expenditure'].idxmax()]
most_funded_scheme = str(max_row['scheme'])
# KPI Layout
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.markdown("<h3 style='text-align: center; color: black;'>Total Schemes</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>Count : {total_schemes}</h4>", unsafe_allow_html=True)
    # st.subheader('Total Schemes')
    # st.subheader(f"Count : {total_schemes}")
with right_column:
    st.markdown("<h3 style='text-align: center; color: black;'>Total Expenditure</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{total_expenditure:,} Crores</h4>", unsafe_allow_html=True)
    # st.subheader('Total Expenditure')
    # st.subheader(f"{total_expenditure:,} Crores")
with middle_column:
    st.markdown("<h3 style='text-align: center; color: black;'>Most Funded Scheme</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{most_funded_scheme}</h4>", unsafe_allow_html=True)

st.markdown("---")

# Charts
# Chart 1
scheme_type_expenditure = df_filtered.groupby(by=['scheme_type']).sum()[
    ['expenditure']].sort_values(by='expenditure')

# Vertical Bar Chart
# fig_sch_typ_exp = px.bar(
#     scheme_type_expenditure,
#     x=scheme_type_expenditure.index,
#     y="expenditure",
#     orientation="v",
#     title="<b> Total Expenditure by Scheme type </b>",
#     color_discrete_sequence=["#7030a0"] * len(scheme_type_expenditure),
#     template="plotly_white",
#     text_auto=True,
# )
# fig_sch_typ_exp.update_traces(textfont_size=12,textfont=dict(
#         family="Arial Black"), textangle=0, textposition="outside", cliponaxis=False)
# fig_sch_typ_exp.update_layout(title_x=0.5/2)

# Pie Chart
fig_sch_typ_exp = px.pie(df_filtered, values='expenditure',
                         names='scheme_type', title='Total Expenditurre Share', hole=0.5, color_discrete_sequence=px.colors.sequential.Purp)
fig_sch_typ_exp.update_traces(textfont_size=12, textfont=dict(
    family="Arial Black"), textposition="inside")
fig_sch_typ_exp.update_layout(title_x=0.5/2, legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-0.15,
    xanchor="right",
    x=0.85
))


# Chart 2
top_schemes = df_filtered.groupby(by=['scheme']).sum()[['expenditure']].sort_values(
    by='expenditure', ascending=False).head(10).reset_index()
# fig_sch_exp = px.bar(
#     top_schemes,
#     x="expenditure",
#     y=top_schemes.index,
#     orientation="h",
#     title="<b> Top Schemes </b>",
#     color_discrete_sequence=["#0083BB"] * len(top_schemes),
#     template="plotly_white",
#     text_auto=True,
# )
# fig_sch_exp.update_traces(textfont_size=18)
# fig_sch_exp.update_layout(yaxis=dict(autorange="reversed"))

categories = top_schemes.to_dict('records')

# function for labels on bar


def horizontal_bar_labels(categories):
    subplots = make_subplots(
        rows=len(categories),
        cols=1,
        subplot_titles=[x["scheme"] for x in categories],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.4 / len(categories)),
    )
    subplots['layout'].update(
        width=550,
        plot_bgcolor='#fff',
    )

    # add bars for the categories
    for k, x in enumerate(categories):
        subplots.add_trace(dict(
            type='bar',
            orientation='h',
            y=[x["scheme"]],
            x=[x["expenditure"]],
            text=["{:,.0f}".format(x["expenditure"])],
            hoverinfo='text',
            textposition='auto',
            marker=dict(
                color="#7030a0",
            ),
        ), k+1, 1)

    # update the layout
    subplots['layout'].update(
        showlegend=False,
    )
    for x in subplots["layout"]['annotations']:
        x['x'] = 0
        x['xanchor'] = 'left'
        x['align'] = 'left'
        x['font'] = dict(
            size=12,
        )

    # hide the axes
    for axis in subplots['layout']:
        if axis.startswith('yaxis') or axis.startswith('xaxis'):
            subplots['layout'][axis]['visible'] = False

    # update the margins and size
    subplots['layout']['margin'] = {
        'l': 0,
        'r': 0,
        't': 50,
        'b': 0,
    }
    height_calc = 40 * len(categories)
    height_calc = max([height_calc, 350])
    subplots['layout']['height'] = height_calc
    subplots['layout']['width'] = height_calc

    return subplots


fig_sch_exp = horizontal_bar_labels(categories)
fig_sch_exp.update_layout(title_text="<b> Top Schemes </b>",
                          title_x=0.5, yaxis=dict(autorange="reversed"))

# Charts Layout
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_sch_typ_exp, use_container_width=False)
right_column.plotly_chart(fig_sch_exp, use_container_width=False)

# Hide Streamlit style
hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """

st.markdown(hide_st_style, unsafe_allow_html=True)

# Showing Dataframe
st.dataframe(df_show[['year', 'scheme_type', 'scheme',
             'expenditure']], use_container_width=True)