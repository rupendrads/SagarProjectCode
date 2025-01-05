import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import calendar
import os
import matplotlib.ticker as mtick
import seaborn as sns

class Analyzer:
    def __init__(self, tradebook_path):
        self.tradebook = pd.read_csv(tradebook_path)

    def preprocess_data(self):
        self.tradebook.drop('trades_per_day', axis=1, inplace=True)
        self.tradebook['date'] = pd.to_datetime(self.tradebook['entry_time'])

    def trades_count(self):
        winning_trades_count = 0
        losing_trades_count = 0
        return

    def calculate_daily_pnl(self):
        data = []
        tradebook_grp = self.tradebook.groupby('date')
        for date, grp in tradebook_grp:
            day_pnl = grp['pnl'].sum()
            data.append({'date': date, 'pnl': day_pnl})
        self.daily_pnl = pd.DataFrame(data)

    def calculate_daily_returns(self, capital=200000):
        self.daily_returns_df = self.daily_pnl.copy()
        self.daily_returns_df.pnl = self.daily_returns_df.pnl * 15
        self.daily_returns_df["pnl_pct"] = (self.daily_returns_df["pnl"] / capital) * 100
        self.daily_returns_df.to_csv('daily_returns.csv')
        daily_returns = self.daily_returns_df.copy()
        daily_returns['date'] = daily_returns['date'].dt.date
        daily_pnl = daily_returns.groupby('date')['pnl'].sum().reset_index()
        # daily_pnl.to_csv('daily_returns.csv',index=False)
        print(daily_pnl)
    def plot_monthly_heatmap(self, figsize=None):
        df = self.daily_returns_df.copy()
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year
        monthly_returns = df.groupby(['year', 'month'])['pnl_pct'].sum().reset_index()
        monthly_returns['month_name'] = monthly_returns['month'].apply(lambda x: calendar.month_abbr[x])
        month_order = [calendar.month_abbr[i] for i in range(1, 13)]
        monthly_returns['month_name'] = pd.Categorical(monthly_returns['month_name'], categories=month_order,
                                                       ordered=True)
        monthly_returns.sort_values(['year', 'month_name'], inplace=True)
        monthly_returns_pivot = monthly_returns.pivot(index='year', columns='month_name', values='pnl_pct')
        monthly_returns_pivot.columns = map(lambda x: str(x).upper(), monthly_returns_pivot.columns)
        monthly_returns_pivot.columns.name = None

        fig_height = len(monthly_returns_pivot) / 3
        if figsize is None:
            size = list(plt.gcf().get_size_inches())
            figsize = (size[0], size[1])
        figsize = (figsize[0], max([fig_height, figsize[1]]))
        fig, ax = plt.subplots(figsize=figsize)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        fig.set_facecolor('white')
        ax.set_facecolor('white')
        ax.set_title('      Monthly Returns (%)\n', fontsize=14, y=.995,
                     fontname="Arial", fontweight='bold', color='black')
        ax = sns.heatmap(monthly_returns_pivot, ax=ax, annot=True, center=0,
                         annot_kws={"size": 10},
                         fmt="0.2f", linewidths=0.5,
                         square=True, cbar=False, cmap="RdYlGn",
                         cbar_kws={'format': '%.0f%%'})
        ax.set_ylabel('Years', fontname="Arial",
                      fontweight='bold', fontsize=12)
        ax.yaxis.set_label_coords(-.1, .5)
        ax.tick_params(colors="#808080")
        plt.xticks(rotation=0, fontsize=10 * 1.2)
        plt.yticks(rotation=0, fontsize=10 * 1.2)
        try:
            plt.subplots_adjust(hspace=0, bottom=0, top=1)
        except Exception:
            pass
        try:
            fig.tight_layout(w_pad=0, h_pad=0)
        except Exception:
            pass
        plt.savefig("monthly_returns.png")
        plt.close(fig)

    def plot_drawdown_curve(self):
        self.daily_returns_df.reset_index(inplace=True)
        self.daily_returns_df["pnl_pct_cumulative"] = self.daily_returns_df["pnl_pct"].cumsum()
        capital = 200000
        cumulative_pnl = np.cumsum(self.daily_returns_df['pnl'])
        max_cumulative_pnl = np.maximum.accumulate(cumulative_pnl)
        self.daily_returns_df["drawdown"] = ((cumulative_pnl / max_cumulative_pnl) - 1) * 100
        self.daily_returns_df.set_index("date", inplace=True)
        plt.figure(figsize=(15, 10))
        plt.fill_between(self.daily_returns_df.index, self.daily_returns_df["drawdown"], color='red', alpha=0.5)
        fmt = '%.0f%%'
        yticks = mtick.FormatStrFormatter(fmt)
        plt.gca().yaxis.set_major_formatter(yticks)
        max_drawdown = self.daily_returns_df['drawdown'].min()
        yticks_values = [max_drawdown, 0]
        yticks_labels = [f"{round(max_drawdown, 2)}%", "0"]
        max_dd = abs(int(max_drawdown))
        start_dd_intrvl = max_dd // 2
        if start_dd_intrvl != 0:
            max_dd_ticks = [-1 * i for i in range(start_dd_intrvl, max_dd, start_dd_intrvl)]
            mad_dd_ticklabels = [f"-{round(x, 2)}%" for x in max_dd_ticks]
            yticks_values.extend(max_dd_ticks)
            yticks_labels.extend(mad_dd_ticklabels)
        x_freq = self.get_x_freq(self.daily_returns_df)
        date_ticks = pd.date_range(self.daily_returns_df.index.min(), self.daily_returns_df.index.max(), freq=x_freq)
        date_labels = date_ticks.strftime('%d %b-%y')
        if x_freq == "ME":
            date_labels = date_ticks.strftime('%b-%y')
        if x_freq == "Y":
            date_labels = date_ticks.strftime('%Y')
        plt.yticks(yticks_values, yticks_labels)
        plt.xticks(date_ticks, date_labels)
        plt.axhline(max_drawdown, color='red', linestyle='--', label='Max Drawdown')
        plt.axhline(0, color='black', linestyle='--', alpha=0.5)
        plt.xticks(rotation=25, fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(loc='lower left', bbox_to_anchor=(0, 0.1), fontsize=15)
        plt.xlabel("Date", fontsize=15)
        plt.ylabel("Drawdown(%)", fontsize=15)
        plt.title("Drawdown", fontsize=15)
        plt.grid(True, alpha=0.2)
        plt.savefig("dd_curve.png")
        plt.close()

    def get_x_freq(self, df: pd.DataFrame) -> str:
        """Returns frequency of date based on df"""
        n = len(df)
        if n > 800:
            freq = "YE"
        elif n > 250:
            freq = '3M'
        elif n > 150:
            freq = 'ME'
        elif 100 <= n < 150:
            freq = '20D'
        elif 50 <= n < 100:
            freq = '10D'
        elif 25 <= n < 50:
            freq = '5D'
        elif 10 <= n < 25:
            freq = '2D'
        else:
            freq = 'D'
        return freq

    def plot_pnl_curve(self):
        plt.figure(figsize=(15, 10))
        plt.fill_between(self.daily_returns_df.index, self.daily_returns_df["pnl_pct_cumulative"], color='green', alpha=0.5)
        plt.fill_between(self.daily_returns_df.index, 0, self.daily_returns_df["pnl_pct_cumulative"],
                         where=(self.daily_returns_df["pnl_pct_cumulative"] < 0), color='red', alpha=0.7)
        fmt = '%.0f%%'
        yticks = mtick.FormatStrFormatter(fmt)
        plt.gca().yaxis.set_major_formatter(yticks)
        max_pnl_pct_cumulative = self.daily_returns_df['pnl_pct_cumulative'].max()
        yticks_values = [max_pnl_pct_cumulative, 0]
        yticks_labels = [f"{round(max_pnl_pct_cumulative, 2)}%", "0"]
        max_pnl = int(max_pnl_pct_cumulative)
        start_pnl_intrvl = max_pnl // 6
        if start_pnl_intrvl != 0:
            pct_cumulative_ticks = [i for i in range(start_pnl_intrvl, max_pnl - start_pnl_intrvl, start_pnl_intrvl)]
            pct_cumulative_ticklabels = [f"{round(x, 2)}%" for x in pct_cumulative_ticks]
            yticks_values.extend(pct_cumulative_ticks)
            yticks_labels.extend(pct_cumulative_ticklabels)
        x_freq = self.get_x_freq(self.daily_returns_df)
        date_ticks = pd.date_range(self.daily_returns_df.index.min(), self.daily_returns_df.index.max(), freq=x_freq)
        date_labels = date_ticks.strftime('%d %b-%y')
        if x_freq == "ME":
            date_labels = date_ticks.strftime('%b-%y')
        if x_freq == "Y":
            date_labels = date_ticks.strftime('%Y')
        plt.yticks(yticks_values, yticks_labels)
        plt.xticks(date_ticks, date_labels)
        plt.axhline(0, color='black', linestyle='--', alpha=0.5)
        plt.axhline(max_pnl_pct_cumulative, color='green', linestyle='--', label='Max PnL(%)')
        plt.xticks(rotation=25, fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(loc='upper left', bbox_to_anchor=(0, 0.9), fontsize=15)
        plt.xlabel("Date", fontsize=15)
        plt.ylabel("P&L(%)", fontsize=15)
        plt.title("P&L", fontsize=15)
        plt.grid(True, alpha=0.2)
        plt.savefig("pnl_curve.png")
        plt.close()

    def plot_data(self):
        self.preprocess_data()
        self.calculate_daily_pnl()
        self.calculate_daily_returns()
        self.plot_monthly_heatmap()
        self.plot_drawdown_curve()
        self.plot_pnl_curve()