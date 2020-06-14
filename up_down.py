import numpy as np

import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff


# some variables that needs to be defined
plot_bgcolor = "XXXXX"
paper_bgcolor = "XXXXX"
font = "XXXXX"
xaxis = "XXX"
yaxis = "XXXX"
yaxis2 = "XXXX"


data_df = """dataframe that has spy returns and up_down ratio"""
data_df = data_df.sort_values(by='tradedate', ascending=True)

# calculate daily price moves
data_df.loc[:, 'change'] = data_df.groupby('ticker').close.pct_change(periods=1)
# first row is now NA, remove the row
data_df.dropna(how='any', inplace=True)

# assign value = 1 for all the names that were up
data_df.loc[:, 'up'] = np.where(data_df.change >= 0, 1, 0)

# count total number of tickers traded each day to find the up_ratio
data_df.loc[:, 'numberoftickers'] = data_df.groupby('tradedate')['ticker'].transform(len)
data_df.loc[:, 'total_up'] = data_df.groupby('tradedate')['up'].transform(sum)
data_df.loc[:, 'up_ratio'] = data_df.total_up/data_df.numberoftickers

# beacuse we care about spy returns against the up_ratio, we focus on spy
spy_df = data_df[data_df.ticker=='SPY']

# calculate 5 days sma
spy_df.loc[:, 'up_ratio_sma5'] = spy_df['up_ratio'].rolling(window=5).mean()

# calculate 1 day, 5 day and 10 day returns on spy
spy_df.loc[:, 'return'] = spy_df.change + 1
spy_df.loc[:, '1dayreturn'] = spy_df.change.shift(-1)
spy_df.loc[:,'5dayreturn'] = spy_df['return'].rolling(5).apply(lambda x:np.prod(x)-1).shift(-5)
spy_df.loc[:,'10dayreturn'] = spy_df['return'].rolling(10).apply(lambda x:np.prod(x)-1).shift(-10)



# plot the 5 day distributions against the rolling 5 day average of up_ratio

plots = []

# fig 1
fig0 = px.scatter(spy_df, x="up_ratio", y="1dayreturn", trendline="lowess")
fig0.update_layout(title= {'text': f'1day returns against up_ratio',
                           'xanchor': 'center', 'x': 0.5
                          }
                  )
plots.append(fig0)

# fig 1
fig1 = px.scatter(spy_df, x="up_ratio_sma5", y="5dayreturn", trendline="lowess")
fig1.update_layout(title= {'text': f'5day returns against 5day SMA up_ratio',
                           'xanchor': 'center', 'x': 0.5
                          }
                  )
plots.append(fig1)

# fig 2
fig2 = px.histogram(spy_df, x="up_ratio_sma5", y="5dayreturn", histfunc='avg')
fig2.update_layout(title= {'text': f'5day returns against 5day SMA up_ratio',
                           'xanchor': 'center', 'x': 0.5
                          }
                  )

plots.append(fig2)

# take the bottom 10 and 90 percentile
q1 = spy_df.up_ratio_sma5.quantile(0.10)
q9 = spy_df.up_ratio_sma5.quantile(0.90)
q1_data = spy_df.where(spy_df.up_ratio_sma5<=q1)
q9_data = spy_df.where(spy_df.up_ratio_sma5>=q9)

# drop all the NA
spy_df.dropna(how='any', inplace=True)
q1_data.dropna(how='any', inplace=True)
q9_data.dropna(how='any', inplace=True)


# fig 3
hist_data = [spy_df['5dayreturn'], q1_data['5dayreturn'], q9_data['5dayreturn'], q1_data['10dayreturn'], q9_data['10dayreturn']]
group_labels = ['0 percentile',
                '5 day returns distribution (10 %-ile)',
                '5 day returns distribution (90%-ile)',
                '10 day returns distribution (10%-ile)',
                '10 day returns distribution (90%-ile)'
               ]
fig3 = ff.create_distplot(hist_data, group_labels, bin_size=.2,  histnorm='probability density')
fig3.update_layout(title= {'text': f'5 day returns distributions for up_ratio at different percentile',
                           'xanchor': 'center', 'x': 0.5
                          }
                  )

plots.append(fig3)


for i in range(len(plots)):
    # uncomment the below lines if you need to add your custom formatting
    # plots[i].update_layout(
    #     showlegend=True,
    #     plot_bgcolor=plot_bgcolor,
    #     paper_bgcolor=paper_bgcolor,
    #     xaxis=xaxis,
    #     yaxis=yaxis,
    #     font=font
    # )
    # plots[i] = plots[i]
    plots[i].show()


# figure 4 with statistics table for all daily returns
table = spy_df[['up_ratio_sma5', '1dayreturn', '5dayreturn', '10dayreturn']].describe()
table = table.reset_index()
table = table.round(3)

headers = table.columns.to_list()
table = go.Table(
    header={'values': [f'<b>{i}</b>' for i in headers],
            'line_color': plot_bgcolor, 'fill_color': plot_bgcolor, 'align': 'center', 'font': font
           },
    cells={'values': table.T, 'line_color':plot_bgcolor, 'fill_color': plot_bgcolor, 'align':'center',  'font':font
          }
    )

fig4 = go.Figure(data=table)
fig4.show()


# figure 5 with statistics table for 10 percentile
table = q1_data[['up_ratio_sma5', '1dayreturn', '5dayreturn', '10dayreturn']].describe()
table = table.reset_index()
table = table.round(3)

headers = table.columns.to_list()
table = go.Table(
    header={'values': [f'<b>{i}</b>' for i in headers],
            'line_color': plot_bgcolor, 'fill_color': plot_bgcolor, 'align': 'center', 'font': font
           },
    cells={'values': table.T, 'line_color':plot_bgcolor, 'fill_color': plot_bgcolor, 'align':'center',  'font':font
          }
    )

fig5 = go.Figure(data=table)
fig5.show()



# figure 6 with statistics table for 90 percentile
table = q9_data[['up_ratio_sma5', '1dayreturn', '5dayreturn', '10dayreturn']].describe()
table = table.reset_index()
table = table.round(3)

headers = table.columns.to_list()
table = go.Table(
    header={'values': [f'<b>{i}</b>' for i in headers],
            'line_color': plot_bgcolor, 'fill_color': plot_bgcolor, 'align': 'center', 'font': font
           },
    cells={'values': table.T, 'line_color':plot_bgcolor, 'fill_color': plot_bgcolor, 'align':'center',  'font':font
          }
    )

fig6 = go.Figure(data=table)
fig6.show()


q05 = spy_df.up_ratio_sma5.quantile(0.05)
q05_data = spy_df.where(spy_df.up_ratio_sma5<=q05)
# figure 6 with statistics table for 95 percentile
table = q05_data[['up_ratio_sma5', '1dayreturn', '5dayreturn', '10dayreturn']].describe()
table = table.reset_index()
table = table.round(3)

headers = table.columns.to_list()
table = go.Table(
    header={'values': [f'<b>{i}</b>' for i in headers],
            'line_color': plot_bgcolor, 'fill_color': plot_bgcolor, 'align': 'center', 'font': font
           },
    cells={'values': table.T, 'line_color':plot_bgcolor, 'fill_color': plot_bgcolor, 'align':'center',  'font':font
          }
    )

fig6 = go.Figure(data=table)
fig6.show()