# Technical Comparison of Stop Loss Mechanisms: Live Trading vs Backtesting

## Live Trading Implementation

### Key Methods:
1. `leg_place_order`: Places the initial order and sets up the stop loss.
2. `calculate_mtm`: Continuously monitors the position and P&L.

### Process Flow:
1. Entry Selection:
   ```python
   if self.selection_criteria()
      #selection Criteria
   elif self.strategy_type == 'range_breakout':
       # Wait for breakout
   elif self.strategy_type == 'simple_momentum':
       # Wait for momentum
   ```



2. Order Placement and Stop Loss Setup:
   ```python
   def leg_place_order(self):
       # Place the initial market order
       order_id = self.xts.place_market_order(...)
       
       # Wait for order completion confirmation from the order socket
       self.trade_data_event.wait()
       
       # Once the initial order is confirmed, calculate and place the stop loss order
       sl_price = self.entry_price - self.stop_loss if self.transaction_type == 'buy' else self.entry_price + self.stop_loss
       sl_order_id = self.xts.place_SL_order(sl_price, ...)
   ```
In the live environment, it's crucial to wait for the confirmation of the initial order execution before placing the stop loss order. This ensures that we have the correct entry price and that the position is actually open before setting up the stop loss.

3. Continuous Monitoring:
   ```python
   def calculate_mtm(self):
       # Calculate P&L
       self.stoploss_trail()
   ```


   ```

### Stop Loss Execution:
- A separate stop loss order is placed with the broker's system.
- This order remains active and is triggered automatically if the price reaches the stop loss level.
- For trailing stop losses, the order is modified in real-time as the price moves favorably.
- The execution is handled by the broker's system, ensuring quick response to market movements.

## Backtesting Implementation

### Key Methods:
1. `backtest_selection`: Processes data day by day.
2. `stoploss_tracker`: Monitors price movement and simulates stop loss hits.

### Process Flow:
1. Data Processing:
   ```python
   for date in self.dates:
       self.backtest_selection()
   ```

2. Strike Selection:
   ```python
   self.strike_selection_criteria()
   ```

3. Entry Determination:
   ```python
   if self.strategy_type == 'regular':
       entry = True
   elif self.strategy_type == 'range_breakout':
       # Check for breakout
   elif self.strategy_type == 'simple_momentum':
       # Check for momentum
   ```

4. Stop Loss Calculation:
   ```python
   self.sl = self.entry_price - self.stop_loss if self.transaction_type == 'buy' else self.entry_price + self.stop_loss
   ```

5. Stop Loss Tracking:
   ```python
   def stoploss_tracker(self):
       if self.current_price <= self.sl:  # For 'buy'
           # Close position
           # Record trade
           # Check for reentry
   ```

6. Trailing Stop Loss:
   ```python
   if self.trailing_sl == 'lock':
       # Lock in profit at certain levels
   elif self.trailing_sl == 'lock_and_trail':
       # Lock and continue trailing
   ```

### Stop Loss Execution:
- The `stoploss_tracker` method simulates the stop loss execution.
- It checks each price point in the historical data against the stop loss level.
- When the price crosses the stop loss level, it simulates closing the position.
- For trailing stop losses, it adjusts the stop loss level based on price movements before checking for triggers.
- The execution is instantaneous in the simulation, assuming perfect order fills at the stop loss price.


## Stop Loss Execution Details

### Live Trading Execution
In the live trading scenario (`LegBuilder.py`), the stop loss execution happens as follows:

1. Initial Order Placement:
   ```python
   def leg_place_order(self):
       # Place the initial market order
       self.xts.place_market_order(...)
       self.trade_data_event.wait()

       # Calculate and place the stop loss order
       sl_price = self.entry_price - self.stop_loss if self.transaction_type == 'buy' else self.entry_price + self.stop_loss
       self.xts.place_SL_order(sl_price, ...)
   ```

2. Continuous Monitoring:
   ```python
   def calculate_mtm(self):
       # Get the latest market price
       current_price = self.xts.get_ltp(self.instrument)

       # Calculate P&L
       self.unrealized_mtm = (current_price - self.entry_price) * self.qty if self.transaction_type == 'buy' else (self.entry_price - current_price) * self.qty

       # Check for stop loss hit (handled by broker's system)
       # Adjust trailing stop loss if enabled
       self.stoploss_trail()
   ```

3. Trailing Stop Loss Adjustment:
   ```python
   def stoploss_trail(self):
       if self.trailing_sl_enabled and self.unrealized_mtm > self.trailing_sl_trigger:
           new_sl_price = calculate_new_sl_price()
           self.xts.modify_SL_order(new_sl_price, ...)
   ```

The actual stop loss execution is handled by the broker's system. When the market price hits the stop loss price, the broker automatically triggers the stop loss order,
sending the signal from OrderSocket to Leg and closing the position.

### Backtesting Execution
In the backtesting scenario (`LegBuilder.py` in the backtest folder), the stop loss execution is simulated:

1. Data Processing and Stop Loss Tracking:
   ```python
   def backtest_selection(self, date):
       for time, price in self.price_data[date].items():
           if self.in_position:
               self.stoploss_tracker(price)
           # ... other logic for entry, etc.
   ```

2. Stop Loss Simulation:
   ```python
   def stoploss_tracker(self, current_price):
       if (self.transaction_type == 'buy' and current_price <= self.sl) or \
          (self.transaction_type == 'sell' and current_price >= self.sl):
           # Simulate closing the position
           self.close_position(current_price)
           self.record_trade()
           self.in_position = False
   ```


In backtesting, the stop loss execution is simulated by checking each price point against the stop loss level. When the price crosses the stop loss, the position is immediately closed in the simulation, assuming perfect execution.

## Key Technical Differences

1. Data Handling:
   - Live: Uses real-time data streams that gets fed to individual legs using publisher subscriber model from MarketSocket
   - Backtest: Processes historical data in batches from database

2. Order Execution:
   - Live: Interacts with actual trading system (`self.xts.place_market_order()`)
   - Live: Places actual stop loss orders with the broker after entry confirmation.
   - Backtest: Simulates order execution based on historical data received from the database
   - Backtest: Simulates stop loss levels without placing orders, set up immediately after simulated entry.


3. Stop Loss Implementation:
   - Live: Places actual stop loss orders (`self.xts.place_SL_order()`)
   - Backtest: Simulates stop loss hits in `stoploss_tracker()

4. Execution Speed:
   - Live: Subject to market conditions and broker's execution speed
   - Backtest: Assumes instantaneous execution at specified price

5. Price Gaps:
   - Live: May execute at a different price if there's a gap in the market
   - Backtest: It assumes perfect execution

6. Error Handling:
   - Live: It may encounter delayed execution, order failures due to technical reasons 
   - Backtest: Assumes perfect execution

7. Reentries:
   - Live: Requires additional logic and order management for reentry
   - Backtest: Can easily simulate reentries after stop loss hits

8. Communication Required:
   - Live: Requires constant communication with the broker to update orders
   - Backtest: Can implement more complex trailing logic without real-world constraints

These differences in execution highlight why separate implementations are necessary for live trading and backtesting, despite the similar core logic.

