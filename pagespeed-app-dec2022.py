# Libraries
import pandas as pd
import plotly.express as px
import streamlit as st

# Page configuration
st.set_page_config(layout="wide")

# Sitebar
with st.sidebar:
    st.write('''
        ### About the data
        Explore the pagespeed performance data for 10 websites that has been created by AKQA Denmark.

        The dataset contains observations from the Google PageSpeed API on the Lighthouse performance scores for ~700 tested urls as well as insights into technical opportunities which are likely to increase speed performance.

        Use the drop-down menu above the graphs to select specific websites, compare individual sites against each other or view global trends.

        **Note**: *The dataset in this app may be biased towards certain page types. For example, the observations on the Dr. Oetker (uk) website contains a very large proportion of recipe pages which strongly influences the trends. See the presentation on Pagespeed Performance for insights on a smaller, but more unbiased dataset.*
    ''')

# Data import
@st.cache
def import_csv(file):
    df = pd.read_csv(file)
    df['Domain'] = df['Address'].str.extract('//(www\.){0,1}(.*?)/')[1]
    return df

file = "pagespeed_larger_sample.csv"
pagespeed = import_csv(file)

# Filter 'en.horten.dk' domain away
pagespeed = pagespeed[pagespeed['Domain'] != 'en.horten.dk']

# Title
st.write('### Pagespeed Performance Review')

# Filtering-widget for domains ~~ Use output in ifelse for plotting of graphs
domains = st.multiselect(
    label="**Select domains**",
    options=pagespeed['Domain'].unique()
)

# ~~~ [SECTON] Pagespeed performance 

# Pagespeed performance score [GRAPH]
if len(domains) == 0:
    scores_plot = px.histogram(
        data_frame=pagespeed, 
        x='Performance Score', 
        nbins=50, 
        range_x=[0,100],
        marginal='rug',
        color_discrete_sequence=px.colors.qualitative.Dark2
    )
    scores_plot.update_layout(
        margin=dict(l=50, r=25, t=35, b=50),
        plot_bgcolor='white'
    )
    scores_plot.update_xaxes(showline=True, linecolor='lightgrey', mirror=True)
    scores_plot.update_yaxes(showline=True, linecolor='lightgrey', mirror=True)
    st.plotly_chart(scores_plot, use_container_width=True)
else:
    scores_plot = px.histogram(
        data_frame=pagespeed[pagespeed['Domain'].isin(domains)], 
        x='Performance Score', 
        color='Domain',
        nbins=50, 
        marginal='rug', 
        range_x=[0,100], 
        color_discrete_sequence=px.colors.qualitative.Dark2
    )
    scores_plot.update_layout(
        margin=dict(l=50, r=25, t=35, b=50),
        plot_bgcolor='white'
    )
    scores_plot.update_xaxes(showline=True, linecolor='lightgrey', mirror=True)
    scores_plot.update_yaxes(showline=True, linecolor='lightgrey', mirror=True)
    st.plotly_chart(scores_plot, use_container_width=True)


# ~~~ [SECTION] Opportunities

left_col, right_col = st.columns(2)

# Opportunities [DATA PREP]
columns = [
    'Address',
    'Domain',
    'Eliminate Render-Blocking Resources Savings (ms)',
    'Defer Offscreen Images Savings (ms)',
    'Efficiently Encode Images Savings (ms)',
    'Properly Size Images Savings (ms)',
    'Minify CSS Savings (ms)',
    'Minify JavaScript Savings (ms)',
    'Reduce Unused CSS Savings (ms)',
    'Reduce Unused JavaScript Savings (ms)',
    'Serve Images in Next-Gen Formats Savings (ms)',
    'Enable Text Compression Savings (ms)',
    'Preconnect to Required Origins Savings (ms)',
    'Server Response Times (TTFB) (ms)',
    'Multiple Redirects Savings (ms)',
    'Preload Key Requests Savings (ms)',
    'Use Video Format for Animated Images Savings (ms)'
]

pagespeed_opportunities = pagespeed[columns]
pagespeed_opportunities_longer = pd.melt(
    frame=pagespeed_opportunities, id_vars=['Address', 'Domain'], var_name="Opportunity", value_name="Time savings (ms)"
)
pagespeed_opportunities_longer['Opportunity'] = pagespeed_opportunities_longer['Opportunity'].str.replace("Savings \(ms\)", "")
pagespeed_opportunities_longer['Opportunity'] = pagespeed_opportunities_longer['Opportunity'].str.replace("Savings \(Bytes\)", "")

# Opportunities [SUMMARY GRAPH]
with left_col: 
    if len(domains) == 0:
        opportunities_summary = pagespeed_opportunities_longer.groupby('Opportunity').agg('mean').reset_index(col_level=0)
        opportunities_summary.columns = ['Opportunity', 'Mean Savings (ms)']
        opportunities_summary = opportunities_summary.sort_values('Mean Savings (ms)', ascending=False)
        opportunities_stat_plot = px.bar(
            data_frame=opportunities_summary,
            x='Opportunity',
            y='Mean Savings (ms)',
            labels={
                'Opportunity': '',
                'Mean Savings (ms)': 'Average Savings (ms)'
            },
            color_discrete_sequence=px.colors.qualitative.Dark2,
            height=600
            )
        opportunities_stat_plot.update_layout(margin=dict(l=50, r=50, t=35, b=250), plot_bgcolor='white')
        opportunities_stat_plot.update_xaxes(showline=True, linecolor='lightgrey', mirror=False)
        opportunities_stat_plot.update_yaxes(showgrid=True, gridcolor='lightgrey')
        st.plotly_chart(opportunities_stat_plot, use_container_width=True)
    else:
        opportunities_summary = pagespeed_opportunities_longer[pagespeed_opportunities_longer['Domain'].isin(domains)].groupby('Opportunity').agg('mean').reset_index(col_level=0)
        opportunities_summary.columns = ['Opportunity', 'Mean Savings (ms)']
        opportunities_summary = opportunities_summary.sort_values('Mean Savings (ms)', ascending=False)
        opportunities_stat_plot = px.bar(
            data_frame=opportunities_summary,
            x='Opportunity',
            y='Mean Savings (ms)',
            labels={
                'Opportunity': '',
                'Mean Savings (ms)': 'Average Savings (ms)'
            },
            color_discrete_sequence=px.colors.qualitative.Dark2,
            height=600
            )
        opportunities_stat_plot.update_layout(margin=dict(l=50, r=50, t=35, b=250), plot_bgcolor='white')
        opportunities_stat_plot.update_xaxes(showline=True, linecolor='lightgrey', mirror=False)
        opportunities_stat_plot.update_yaxes(showgrid=True, gridcolor='lightgrey')
        st.plotly_chart(opportunities_stat_plot, use_container_width=True)




# Opportunities [DISTRIBUTION GRAPH]
with right_col:
    if len(domains) == 0:
        opportunities_dist_plot = px.scatter(
            data_frame=pagespeed_opportunities_longer.sort_values('Opportunity', ascending=True),
            y='Time savings (ms)',
            x='Opportunity',
            labels={
                'Opportunity': '',
                'Time savings (ms)': 'Savings per URL (ms)'
            },
            opacity=0.3,
            log_y=True,
            color_discrete_sequence=px.colors.qualitative.Dark2,
            height=600
            )
        opportunities_dist_plot.update_layout(margin=dict(l=50, r=50, t=35, b=250), plot_bgcolor='white')
        opportunities_dist_plot.update_xaxes(
            showline=True, linecolor='lightgrey', mirror=False,
            showgrid=True, gridcolor='lightgrey'
            )
        opportunities_dist_plot.update_yaxes(showgrid=True, gridcolor='lightgrey')
        st.plotly_chart(opportunities_dist_plot, use_container_width=True)
    else:
        opportunities_dist_plot = px.scatter(
            data_frame=pagespeed_opportunities_longer[pagespeed_opportunities_longer['Domain'].isin(domains)].sort_values('Opportunity', ascending=True),
            y='Time savings (ms)',
            x='Opportunity',
            labels={
                'Opportunity': '',
                'Time savings (ms)': 'Savings per URL (ms)'
            },
            opacity=0.3,
            log_y=True,
            color_discrete_sequence=px.colors.qualitative.Dark2,
            height=600
            )
        opportunities_dist_plot.update_layout(margin=dict(l=50, r=50, t=35, b=250), plot_bgcolor='white')
        opportunities_dist_plot.update_xaxes(
            showline=True, linecolor='lightgrey', mirror=False,
            showgrid=True, gridcolor='lightgrey'
            )
        opportunities_dist_plot.update_yaxes(showgrid=True, gridcolor='lightgrey')
        st.plotly_chart(opportunities_dist_plot, use_container_width=True)
