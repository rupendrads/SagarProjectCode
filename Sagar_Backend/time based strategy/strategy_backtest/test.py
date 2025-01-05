import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import pandas as pd
import datetime
import warnings
warnings.filterwarnings("ignore")

def create_pdf_report(data, strategy_name, strategy_df):
    pdf_file = f"{strategy_name}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title = f"Strategy Performance Report: {strategy_name}"
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total PnL', f"{data['total_pnl']:.2f}"],
        ['Total Winning Days', data['total_winning_days']],
        ['Total Losing Days', data['total_losing_days']],
        ['Average Profit Per Day', f"{data['average_profit_per_day']:.2f}"],
        ['Average Profit on Winning Days', f"{data['average_profit_on_winning_days']:.2f}"],
        ['Average Loss on Losing Days', f"{data['average_loss_on_losing_days']:.2f}"],
        ['Max Profit in Single Day', f"{data['max_profit_single_day']:.2f}"],
        ['Max Loss in Single Day', f"{data['max_loss_single_day']:.2f}"],
        ['Winning Percentage', f"{data['winning_percentage']:.2f}%"],
        ['Losing Percentage', f"{data['losing_percentage']:.2f}%"],
        ['Total Days Traded', data['total_days_traded']],
        ['Max Drawdown', f"{data['max_drawdown']:.2f}"],
        ['Drawdown Period', f"{data['drawdown_period'][0]} to {data['drawdown_period'][1]}"]
    ]
    
    table = Table(summary_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.palegreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))
    pnl_df = pd.DataFrame(list(data['daily_pnl'].items()), columns=['Date', 'PnL'])
    pnl_df.set_index('Date', inplace=True)
    
    plt.figure(figsize=(10, 5))
    pnl_df['PnL'].plot(kind='bar', color='skyblue')
    plt.title('Daily PnL')
    plt.ylabel('PnL')
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig("daily_pnl_chart.png")
    plt.close()
    
    elements.append(Image("daily_pnl_chart.png", width=500, height=250))
    elements.append(Spacer(1, 24))
    strategy_data = [strategy_df.columns.tolist()] + strategy_df.values.tolist()
    strategy_table = Table(strategy_data)
    strategy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(strategy_table)
    doc.build(elements)
    print(f"PDF created: {pdf_file}")

data = {'daily_pnl': {datetime.date(2021, 4, 5): 972.5, datetime.date(2021, 4, 6): -469.3699999999999, datetime.date(2021, 4, 7): -165.32000000000016, datetime.date(2021, 4, 8): -86.86999999999995, datetime.date(2021, 4, 9): 1151.25, datetime.date(2021, 4, 12): -460.61, datetime.date(2021, 4, 15): -352.48, datetime.date(2021, 4, 16): -455.0, datetime.date(2021, 4, 19): -200.6199999999999, datetime.date(2021, 4, 20): 1412.5, datetime.date(2021, 4, 22): 954.06, datetime.date(2021, 4, 23): -1107.81, datetime.date(2021, 4, 26): -237.5, datetime.date(2021, 4, 28): 651.87, datetime.date(2021, 4, 29): 1119.06, datetime.date(2021, 4, 30): 1098.44, datetime.date(2021, 5, 3): -744.6799999999998, datetime.date(2021, 5, 4): 1126.25, datetime.date(2021, 5, 5): -1118.75}, 'total_pnl': 3086.92, 'total_winning_days': 8, 'total_losing_days': 11, 'average_profit_per_day': 162.46947368421053, 'average_profit_on_winning_days': 1060.74125, 'average_loss_on_losing_days': -490.81909090909085, 'max_profit_single_day': 1412.5, 'max_loss_single_day': -1118.75, 'winning_percentage': 42.10526315789473, 'losing_percentage': 57.89473684210527, 'total_days_traded': 19, 'max_drawdown': -3263.71, 'drawdown_period': (datetime.date(2021, 4, 19), datetime.date(2021, 4, 30))}
strategy_df = pd.read_csv(r"C:\Users\pegas\OneDrive\Desktop\code review\Sagar_Backend\time based strategy\strategy_backtest\nifty_atm_sell\nifty_atm_sell_strategy_pnl_details.csv")
create_pdf_report(data, "nifty_atm_sell", strategy_df)