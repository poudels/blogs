# %reset

import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go


# some variables that needs to be defined
plot_bgcolor = "XXXXX"
paper_bgcolor = "XXXXX"
font = "XXXXX"
xaxis = "XXX"
yaxis = "XXXX"
yaxis2 = "XXXX"


historicalPrices = """ dataframe with tradedate and spy closing prices for 2010-01-01 and 2020-01-01 """
# historicalPrices.sort_values(by='tradedate', ascending=True, inplace=True)

putCallRatio = """ dataframe with equities put call ratio for 2010-01-01 and 2020-01-01"""
# putCallRatio.sort_values(by='tradedate', ascending=True, inplace=True)

# combine put call ratio with historical prices
data_df = pd.merge(historicalPrices, putCallRatio, on='tradedate')
# data_df.sort_values(by=['ticker', 'tradedate'], inplace=True)

# calculate returns for different time periods.. e.g. 2dayreturn, 5dayreturn, 10dayreturn
data_df['pct'] = data_df.close.pct_change(periods=1)
data_df.loc[:, '1dayreturn'] = data_df['pct'].shift(-1)
data_df.loc[:, '2dayreturn'] = data_df['pct'].rolling(2).sum().shift(-2)
data_df.loc[:, '5dayreturn'] = data_df['pct'].rolling(5).sum().shift(-5)
data_df.loc[:, '10dayreturn'] = data_df['pct'].rolling(10).sum().shift(-10)

# drop columns with missing data
data_df.dropna(how='any', inplace=True)

# take 90th percentile data and returns
eqt_pc_quantile = data_df.eqt_pc.quantile(0.9)

data_df_eqt = data_df.where(data_df.eqt_pc >= eqt_pc_quantile)
_ = data_df_eqt  # reassigning data_df to a easier name
_.dropna(how='any', inplace=True)


# figures
# figure 1 for return distribution
fig = go.Figure()
trace0 = data_df['1dayreturn']
trace1 = _['1dayreturn']
trace3 = _['2dayreturn']
trace5 = _['5dayreturn']
trace7 = _['10dayreturn']

hist_data = [trace7, trace5, trace3, trace1, trace0]
group_labels = ['10 day returns (90%-ile)', '5 day returns (90-%ile)',
                '2 day returns (90-%ile)', '1 day returns (90-%ile)',
                '1 day returns (0-%ile)'
               ]

fig = ff.create_distplot(hist_data, group_labels, bin_size=.2,  histnorm='probability density')
fig.update_layout(title={'text': f'Returns with Equity PC Ratio at 90th Percentile ({eqt_pc_quantile})',
                         'xanchor': 'center', 'x': 0.5
                         },
                  xaxis_title='returns', yaxis_title='probability',
                  showlegend=True, autosize=True,
                  plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, font=font, xaxis=xaxis, yaxis=yaxis,
                  legend_orientation='h'
                  )
fig.update_xaxes(range=[-0.15, 0.15])
fig.show()

# figure 2 for spy closing prices overlaid with equities pc at 95 percentile
ninetyfive_percentile = data_df_eqt.eqt_pc.quantile(0.95)
__ = data_df_eqt[data_df_eqt['eqt_pc'] >= ninetyfive_percentile]

fig = go.Figure()
fig.add_trace(
    go.Scatter(x=__.tradedate, y=__.eqt_pc, yaxis="y2",
               mode='markers', name="PC ratio",
               marker={'size': 6, 'color': __.eqt_pc, 'colorscale': "Viridis"}
               ))
#
fig.add_trace(
    go.Scatter(x=data_df_eqt.tradedate, y=data_df_eqt.close,
               yaxis="y", mode='lines', name="SPY Close",
               line={'width': 4, 'color': 'goldenrod'}
               ))

fig.add_shape(
    type="line",
    x0=data_df_eqt.tradedate.min(), y0=ninetyfive_percentile,
    x1=data_df_eqt.tradedate.max(), y1=ninetyfive_percentile,
    line=dict(color="lightgreen", width=3))

fig.update_shapes(dict(xref='x', yref='y2'))
fig.update_layout(title={'text': f'95 percentile equities Put Call Ratio overlaid with SPY', 'xanchor': 'center', 'x': 0.5
                         },
                  plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, xaxis=xaxis, yaxis=yaxis, font=font, yaxis2=yaxis2,
                  showlegend=True
                  )

fig.update_shapes(dict(xref='x', yref='y2'))
fig.update_xaxes(matches='x')

x_annotate = data_df_eqt.tradedate.max()
pc_ratio_annotate = "95 %ile"

fig.add_annotation(x=x_annotate, y=ninetyfive_percentile,
                   xref="x", yref="y2", text=f"{pc_ratio_annotate} ",
                   showarrow=True,
                   font=dict(
                       color="white",
                       size=18
                   ),
                   align="center",
                   arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#636363",
                   ax=40, ay=40,
                   bordercolor="#c7c7c7", borderwidth=0,  borderpad=0,
                   bgcolor=plot_bgcolor,
                   opacity=0.8
                   )
fig.show()


# figure 3 with statistics table
table = _[['eqt_pc', '1dayreturn', '2dayreturn', '5dayreturn', '10dayreturn']].describe()
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

fig = go.Figure(data=table)
fig.show()