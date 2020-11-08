import random
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# First show that VIX has a premium built into it
def vix_premium():
    a = pd.read_excel(open('VIX.xlsx', 'rb'), sheet_name='Sheet4')
    a.dropna(how='any', inplace=True)

    # Create traces
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a['Date'], y=a['rVol_21'], name='rVol 30-d', mode='lines',
                             marker={'color': "mediumspringgreen"}))
    fig.add_trace(go.Scatter(x=a['Date'], y=a['VIX'], name='VIX', mode='lines',
                             marker={'color': "#ffa600"}))
    fig.add_trace(go.Bar(x=a['Date'], y=(a['VIX'] - a['rVol_21']), name='VIX-rVol', yaxis='y2',
                         marker={'color': "#665191"}))

    fig.update_layout(title={'text': f'Realized 30-d Vol vs VIX', 'xanchor': 'center', 'x': 0.5},
                      plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, xaxis=xaxis, yaxis=yaxis, font=font,
                      yaxis2=yaxis2
                      )
    fig.update_xaxes(matches='x')
    fig.update_yaxes(matches='y')

    fig.show()


def vrp_strategies():
    data = pd.read_excel(open('VIX.xlsx', 'rb'), sheet_name='Sheet5')
    data.dropna(how='any', inplace=True)
    res = backtest(data, initial_capital=100)
    out = res.get('out')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=out['Date'], y=out['VIX'], mode='lines', name='VIX', marker={'color': "#ffa600"}))
    fig.add_trace(go.Scatter(x=out['Date'], y=out['rVol_10_hist'], mode='lines', name='10-day realized vol',
                             marker={'color': "mediumspringgreen"}))
    fig.add_trace(go.Scatter(x=out['Date'], y=out['signal'], mode='lines', yaxis='y2', name='signal',
                             marker={'color': "#2f4b7c"}))

    fig.update_layout(title={'text': f'Realized 10-d Vol vs VIX', 'xanchor': 'center', 'x': 0.5},
                      plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, xaxis=xaxis, yaxis=yaxis, font=font,
                      yaxis2=yaxis2,
                      height=300
                      )
    fig.update_xaxes(matches='x')
    fig.show()

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=out['Date'], y=out['capital'], mode='lines', name='lines', marker={'color': 'white'}))

    fig3.update_layout(title={'text': f'Capital', 'xanchor': 'center', 'x': 0.5},
                       plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, xaxis=xaxis, yaxis=yaxis, font=font,
                       yaxis2=yaxis2
                       )
    fig3.update_xaxes(matches='x')
    fig3.show()


class Portfolio:
    def __init__(self, data, initial_capital=100):
        # initalize data
        # these are constants that won't change with iteration
        self.min_step = data.index.min()
        self.max_step = data.index.max()
        self.initial_capital = initial_capital

        # Portfolio components - these change with iteration
        self.step = data.index.min()
        self.data = data
        self.apply_signal()

    def apply_signal(self):
        # strategy I
        self.data.loc[:, 'signal1'] = np.where(self.data['VIX'] > self.data['rVol_10_hist'], -1, 1)

        # strategy II
        self.data.loc[:, 'VIX_rVol'] = self.data['VIX'] - self.data['rVol_10_hist']
        self.data.loc[:, 'VIX_rVol_sma'] = self.data['VIX_rVol'].rolling(5).mean()
        self.data['signal2'] = np.where(self.data['VIX_rVol_sma'] > 1, -1, 1)

        self.data.loc[:, 'signal'] = self.data['signal2']

    def __iter__(self):
        return self

    def __next__(self):
        if self.step <= self.max_step:
            self.calculate_pv()
            self.adjust_positions()

            # increase the counter
            self.step += 1
            return self.data
        else:
            raise StopIteration

    def adjust_positions(self):
        # if today's and yesterday's signal are the same, don't change your size.
        # if they are different, close yesterday's position and open a new one
        first_step = True if self.step == self.min_step else False
        if first_step:
            self.data.loc[self.step, 'VXX_qty'] = self.data.loc[self.step, 'signal'] * self.data.loc[
                self.step, 'capital'] / self.data.loc[self.step, 'VXX']
            self.data.loc[self.step, 'adjust_position'] = 1
        else:
            if self.data.loc[self.step, 'signal'] == self.data.loc[self.step - 1, 'signal']:
                self.data.loc[self.step, 'VXX_qty'] = self.data.loc[self.step - 1, 'VXX_qty']
                self.data.loc[self.step, 'adjust_position'] = 0

            else:  # you have to adjust potision
                self.data.loc[self.step, 'VXX_qty'] = self.data.loc[self.step, 'signal'] * self.data.loc[
                    self.step, 'capital'] / self.data.loc[self.step, 'VXX']
                self.data.loc[self.step, 'adjust_position'] = 1

    def calculate_pv(self):

        first_step = True if self.step == self.min_step else False
        ydays_vxx = self.data.loc[self.step, 'VXX'] if first_step else self.data.loc[self.step - 1, 'VXX']
        todays_vxx = self.data.loc[self.step, 'VXX']
        day_gain = 0 if first_step else self.data.loc[self.step - 1, 'VXX_qty'] * (todays_vxx - ydays_vxx)

        if first_step:
            self.data.loc[self.step, 'capital'] = self.initial_capital
        else:
            self.data.loc[self.step, 'capital'] = self.data.loc[self.step - 1, 'capital'] + day_gain


def backtest(data, initial_capital=100):
    # initialize a portfolio with an initial capital

    m = Portfolio(data, initial_capital)

    out = pd.DataFrame()
    for i in m:
        out = i
    if out.empty:
        return out.to_dict()

    final_capital = out.loc[out.index.max(), 'capital']
    total_return = (final_capital - initial_capital) / initial_capital

    holding_period = len(out.index)
    down_days = len(out[out['capital'] <= initial_capital])
    max_draw_down = (initial_capital - out['capital'].min()) / initial_capital
    max_return = (out['capital'].max() - initial_capital) / initial_capital
    adjust_position = out['adjust_position'].sum()
    start_date = out['Date'].min()
    end_date = out['Date'].max()
    #     print(out)
    return {'total_return': total_return,
            'holding_period': holding_period,
            'down_days': down_days,
            'max_draw_down': max_draw_down,
            'max_return': max_return,
            'adjust_position': adjust_position,
            'start_date': start_date,
            'end_date': end_date,
            'out': out
            }


if __name__ == "__main__":
    vix_premium()
    vrp_strategies()