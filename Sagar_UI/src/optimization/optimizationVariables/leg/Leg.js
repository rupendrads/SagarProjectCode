import { Label } from "../../../common/Label";
import { InputText } from "../../../common/InputText";
import { OptionButtonsWithId } from "../../../common/OptionButtonsWithId";
import { SelectDD } from "../../../common/SelectDD";
import { SelectDDWithKeyIndex } from "../../../common/SelectDDWithKeyIndex";
import {
  expiryOptions,
  strikeTypeOptions,
  strikeSelectionCriteriaOptions,
  trailingOptions,
  momentumOptions,
} from "../../../strategy/Leg/LegOptions";
import { pointPercentOptions, plusMinusOptions } from "../../../common/common";
import NoOfReentry from "./noOfReentry/NoOfReentry";
import StrikeSelectionClosestPremium from "./strikeSelectionClosestPremium/StrikeSelectionClosestPremium";
import StrikeSelectionStrike from "./strikeSelectionStrike/StrikeSelectionStrike";
import StraddleWidthValue from "./straddleWidthValue/StraddleWidthValue";
import PercentOfAtmStrikeValue from "./percentOfAtmStrikeValue/PercentOfAtmStrikeValue";
import AtmStraddlePremium from "./atmStraddlePremium/AtmStraddlePremium";
import StrikeSelectionStopLoss from "./strikeSelectionStopLoss/StrikeSelectionStopLoss";
import StrikeSelectionProfitReaches from "./strikeSelectionProfitReaches/StrikeSelectionProfitReaches";
import StrikeSelectionLockProfit from "./strikeSelectionLockProfit/StrikeSelectionLockProfit";
import StrikeSelectionIncreaseInProfit from "./strikeSelectionIncreaseInProfit/StrikeSelectionIncreaseInProfit";
import StrikeSelectionTrailProfit from "./strikeSelectionTrailProfit/StrikeSelectionTrailProfit";
import SimpleMomentum from "./simpleMomentum/SimpleMomentum";
import RangeBreakout from "./rangeBreakout/RangeBreakout";
import RollStrike from "./rollStrike/RollStrike";
import RollStrikeStopLoss from "./rollStrikeStopLoss/RollStrikeStopLoss";
import RollStrikeStrikeType from "./rollStrikeStrikeType/RollStrikeStrikeType";
import RollStrikeProfitReaches from "./rollStrikeProfitReaches/RollStrikeProfitReaches";
import RollStrikeLockProfit from "./rollStrikeLockProfit/RollStrikeLockProfit";
import RollStrikeIncreaseInProfit from "./rollStrikeIncreaseInProfit/RollStrikeIncreaseInProfit";
import RollStrikeTrailProfit from "./rollStrikeTrailProfit/RollStrikeTrailProfit";

const Leg = (props) => {
  const { leg, onChangeLegs } = props;
  //console.log(onChangeLegs);

  const positionOptions = [
    {
      inputName: `optimization-position${leg.id}`,
      inputId: `optimization-position-buy${leg.id}`,
      inputLabel: "Buy",
      fieldName: "position",
      fieldValue: "buy",
    },
    {
      inputName: `optimization-position${leg.id}`,
      inputId: `optimization-position-sell${leg.id}`,
      inputLabel: "Sell",
      fieldName: "position",
      fieldValue: "sell",
    },
  ];

  const optionTypeOptions = [
    {
      inputName: `optimization-option_type${leg.id}`,
      inputId: `optimization-option_type_call${leg.id}`,
      inputLabel: "Call",
      fieldName: "option_type",
      fieldValue: "call",
    },
    {
      inputName: `optimization-option_type${leg.id}`,
      inputId: `optimization-option_type_put${leg.id}`,
      inputLabel: "Put",
      fieldName: "option_type",
      fieldValue: "put",
    },
  ];

  const onChangeLeg = (fieldName, fieldValue) => {
    onChangeLegs(leg.id, fieldName, fieldValue);
  };

  const trailingOptionsCellStyle = {
    marginRight:
      leg.strike_selection_criteria_trailing_options === "lockntrail"
        ? "0px"
        : "20px",
  };

  return (
    <div className="box-content-fill">
      <div className="leg box card">
        <div className="flex-row">
          <div className="cell">
            <div>
              <Label caption="Total Lot" />
            </div>
            <div className="input-group input-group-sm" disabled>
              <InputText name="lots" value={leg.lots} />
            </div>
          </div>
          <div className="cell">
            <div>
              <label
                className="field-label"
                htmlFor={`optimization-position${props.srNo}`}
              >
                Position
              </label>
            </div>
            <div disabled>
              <OptionButtonsWithId
                options={positionOptions}
                selectedValue={leg.position}
              />
            </div>
          </div>
          <div className="cell">
            <div>
              <label
                className="field-label"
                htmlFor={`optimization-optionType${props.srNo}`}
              >
                Option Type
              </label>
            </div>
            <div disabled>
              <OptionButtonsWithId
                options={optionTypeOptions}
                selectedValue={leg.option_type}
              />
            </div>
          </div>
          <div className="cell">
            <div>
              <Label caption="Expiry" />
            </div>
            <div disabled>
              <SelectDD
                fieldName="expiry"
                selectedValue={leg.expiry}
                options={expiryOptions}
              />
            </div>
          </div>
          <div className="cell">
            <div className="flex-row min-max-interval">
              <div className="cell">
                <div>
                  <Label caption="No. of Reentry (+)" />
                </div>
                <NoOfReentry
                  min={leg.no_of_reentry.min}
                  max={leg.no_of_reentry.max}
                  interval={leg.no_of_reentry.interval}
                  onChangeNoOfReentry={onChangeLeg}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="flex-row">
          <div className="cell">
            <div>
              <Label caption="Strike Selection Criteria" />
            </div>
            <div disabled>
              <SelectDD
                fieldName="strike_selection_criteria"
                selectedValue={leg.strike_selection_criteria}
                options={strikeSelectionCriteriaOptions}
              />
            </div>
          </div>
          {leg.strike_selection_criteria === "strike" && (
            <div className="cell">
              <div className="flex-row min-max-interval">
                <div className="cell">
                  <div>
                    <Label caption="Strike Type (-20, +20)" />
                  </div>
                  <StrikeSelectionStrike
                    min={leg.strike_type.min}
                    max={leg.strike_type.max}
                    interval={leg.strike_type.interval}
                    onChangeStrikeSelectionStrike={onChangeLeg}
                  />
                </div>
              </div>
            </div>
          )}
          {leg.strike_selection_criteria === "closestpremium" && (
            <div className="cell">
              <div className="flex-row min-max-interval">
                <div className="cell">
                  <div>
                    <Label caption="Closest Premium (+)" />
                  </div>
                  <StrikeSelectionClosestPremium
                    min={leg.closest_premium.min}
                    max={leg.closest_premium.max}
                    interval={leg.closest_premium.interval}
                    onChangeStrikeSelectionClosestPremium={onChangeLeg}
                  />
                </div>
              </div>
            </div>
          )}
          {leg.strike_selection_criteria === "straddlewidth" && (
            <div className="cell">
              <div>
                <Label caption="Straddle Width (+)" />
              </div>
              <div className="cell align-bottom">
                <div>
                  <Label caption="[ ATM Strike" />
                </div>
                <div disabled>
                  <SelectDD
                    fieldName="straddle_width_sign"
                    selectedValue={leg.straddle_width_sign}
                    options={plusMinusOptions}
                  />
                </div>
                <div>
                  <Label caption="(" />
                </div>
                <div className="min-max-interval">
                  <StraddleWidthValue
                    min={leg.straddle_width_value.min}
                    max={leg.straddle_width_value.max}
                    interval={leg.straddle_width_value.interval}
                    onChangeStraddleWidthValue={onChangeLeg}
                  />
                </div>
                <div>
                  <Label caption="x ATM Straddle Price )]" />
                </div>
              </div>
            </div>
          )}
          {leg.strike_selection_criteria === "percentofatmstrike" && (
            <div className="cell">
              <div>
                <Label caption="% of ATM Strike (+)" />
              </div>
              <div className="cell align-bottom">
                <div disabled>
                  <SelectDD
                    fieldName="percent_of_atm_strike_sign"
                    selectedValue={leg.percent_of_atm_strike_sign}
                    options={plusMinusOptions}
                  />
                </div>
                <div className="min-max-interval">
                  <PercentOfAtmStrikeValue
                    min={leg.percent_of_atm_strike_value.min}
                    max={leg.percent_of_atm_strike_value.max}
                    interval={leg.percent_of_atm_strike_value.interval}
                    onChangePercentOfAtmStrikeValue={onChangeLeg}
                  />
                </div>
                <div>
                  <Label caption="x ATM Strike" />
                </div>
              </div>
            </div>
          )}
          {leg.strike_selection_criteria === "atmstraddlepremiumpercent" && (
            <div className="cell">
              <div>
                <Label caption="Atm Straddle Premium % (0.001, 100, 100)" />
              </div>
              <AtmStraddlePremium
                min={leg.atm_straddle_premium.min}
                max={leg.atm_straddle_premium.max}
                interval={leg.atm_straddle_premium.interval}
                onChangeAtmStraddlePremium={onChangeLeg}
              />
            </div>
          )}
        </div>
        <div className="flex-row traling-options-row">
          <div className="cell">
            <div>
              <Label caption="Stop Loss (+)" />
            </div>
            <div className="with-sign">
              <StrikeSelectionStopLoss
                min={leg.strike_selection_criteria_stop_loss.min}
                max={leg.strike_selection_criteria_stop_loss.max}
                interval={leg.strike_selection_criteria_stop_loss.interval}
                onChangeStrikeSelectionStopLoss={onChangeLeg}
              />
              <div className="sign" disabled>
                <SelectDD
                  fieldName="strike_selection_criteria_stop_loss_sign"
                  selectedValue={leg.strike_selection_criteria_stop_loss_sign}
                  options={pointPercentOptions}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="flex-row traling-options-row">
          <div className="cell">
            <div>
              <Label caption="Trailing Options" />
            </div>
            <div disabled>
              <SelectDD
                fieldName="strike_selection_criteria_trailing_options"
                selectedValue={leg.strike_selection_criteria_trailing_options}
                options={trailingOptions}
              />
            </div>
          </div>
          <div className="flex-row">
            <div className="cell" style={trailingOptionsCellStyle}>
              <div className="flex-row min-max-interval">
                <div className="cell">
                  <div>
                    <Label caption="If profit reaches (+)" />
                  </div>
                  <StrikeSelectionProfitReaches
                    min={leg.strike_selection_criteria_profit_reaches.min}
                    max={leg.strike_selection_criteria_profit_reaches.max}
                    interval={
                      leg.strike_selection_criteria_profit_reaches.interval
                    }
                    onChangeStrikeSelectionProfitReaches={onChangeLeg}
                  />
                </div>
              </div>
            </div>
            <div className="cell" style={trailingOptionsCellStyle}>
              <div className="flex-row min-max-interval">
                <div className="cell">
                  <div>
                    <Label caption="Lock profit (+)" />
                  </div>
                  <div className="with-sign">
                    <StrikeSelectionLockProfit
                      min={leg.strike_selection_criteria_lock_profit.min}
                      max={leg.strike_selection_criteria_lock_profit.max}
                      interval={
                        leg.strike_selection_criteria_lock_profit.interval
                      }
                      onChangeStrikeSelectionLockProfit={onChangeLeg}
                    />
                    <div disabled>
                      <SelectDD
                        fieldName="strike_selection_criteria_lock_profit_sign"
                        selectedValue={
                          leg.strike_selection_criteria_lock_profit_sign
                        }
                        options={pointPercentOptions}
                        callbackFunction={onChangeLeg}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          {leg.strike_selection_criteria_trailing_options === "lockntrail" && (
            <div className="flex-row">
              <div className="cell" style={trailingOptionsCellStyle}>
                <div className="flex-row min-max-interval">
                  <div className="cell">
                    <div>
                      <Label caption="For every increase in profit by (+)" />
                    </div>
                    <StrikeSelectionIncreaseInProfit
                      min={leg.strike_selection_criteria_increase_in_profit.min}
                      max={leg.strike_selection_criteria_increase_in_profit.max}
                      interval={
                        leg.strike_selection_criteria_increase_in_profit
                          .interval
                      }
                      onChangeStrikeSelectionIncreaseInProfit={onChangeLeg}
                    />
                  </div>
                </div>
              </div>
              <div className="cell" style={trailingOptionsCellStyle}>
                <div className="flex-row min-max-interval">
                  <div className="cell">
                    <div>
                      <Label caption="Trail profit by (+)" />
                    </div>
                    <div className="with-sign">
                      <StrikeSelectionTrailProfit
                        min={leg.strike_selection_criteria_trail_profit.min}
                        max={leg.strike_selection_criteria_trail_profit.max}
                        interval={
                          leg.strike_selection_criteria_trail_profit.interval
                        }
                        onChangeStrikeSelectionTrailProfit={onChangeLeg}
                      />
                      <div disabled>
                        <SelectDD
                          fieldName="strike_selection_criteria_trail_profit_sign"
                          selectedValue={
                            leg.strike_selection_criteria_trail_profit_sign
                          }
                          options={pointPercentOptions}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="flex-row">
          <div className="cell">
            <div>
              <Label caption="Roll Strike (+)" />
            </div>
            <RollStrike
              min={leg.roll_strike.min}
              max={leg.roll_strike.max}
              interval={leg.roll_strike.interval}
              onChangeRollStrike={onChangeLeg}
            />
          </div>
          <div className="cell">
            <Label caption="New Strike Type (-10, +10)" />
            <RollStrikeStrikeType
              min={leg.roll_strike_strike_type.min}
              max={leg.roll_strike_strike_type.max}
              interval={leg.roll_strike_strike_type.interval}
              onChangeRollStrikeStrikeType={onChangeLeg}
            />
          </div>
        </div>
        <div className="flex-row traling-options-row">
          <div className="cell">
            <div>
              <Label caption="Stop Loss (+)" />
            </div>
            <div className="with-sign">
              <RollStrikeStopLoss
                min={leg.roll_strike_stop_loss.min}
                max={leg.roll_strike_stop_loss.max}
                interval={leg.roll_strike_stop_loss.interval}
                onChangeRollStrikeStopLoss={onChangeLeg}
              />
              <div className="sign" disabled>
                <SelectDD
                  fieldName="roll_strike_stop_loss_sign"
                  selectedValue={leg.roll_strike_stop_loss_sign}
                  options={pointPercentOptions}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="flex-row traling-options-row">
          <div className="cell">
            <Label caption="Trailing Options" />
            <div disabled>
              <SelectDD
                fieldName="roll_strike_trailing_options"
                selectedValue={leg.roll_strike_trailing_options}
                options={trailingOptions}
              />
            </div>
          </div>
          <div className="flex-row">
            <div className="cell">
              <div>
                <Label caption="If profit reaches (+)" />
              </div>
              <RollStrikeProfitReaches
                min={leg.roll_strike_profit_reaches.min}
                max={leg.roll_strike_profit_reaches.max}
                interval={leg.roll_strike_profit_reaches.interval}
                onChangeRollStrikeProfitReaches={onChangeLeg}
              />
            </div>
            <div className="cell">
              <div>
                <Label caption="Lock profit (+)" />
              </div>
              <div className="with-sign">
                <RollStrikeLockProfit
                  min={leg.roll_strike_lock_profit.min}
                  max={leg.roll_strike_lock_profit.max}
                  interval={leg.roll_strike_lock_profit.interval}
                  onChangeRollStrikeLockProfit={onChangeLeg}
                />
                <div disabled>
                  <SelectDD
                    fieldName="roll_strike_lock_profit_sign"
                    selectedValue={leg.roll_strike_lock_profit_sign}
                    options={pointPercentOptions}
                  />
                </div>
              </div>
            </div>
          </div>
          {leg.roll_strike_trailing_options === "lockntrail" && (
            <div className="flex-row">
              <div className="cell">
                <div>
                  <Label caption="For every increase in profit by (+)" />
                </div>
                <RollStrikeIncreaseInProfit
                  min={leg.roll_strike_increase_in_profit.min}
                  max={leg.roll_strike_increase_in_profit.max}
                  interval={leg.roll_strike_increase_in_profit.interval}
                  onChangeRollStrikeIncreaseInProfit={onChangeLeg}
                />
              </div>
              <div className="cell">
                <div>
                  <Label caption="Trail profit by (+)" />
                </div>
                <div className="with-sign">
                  <RollStrikeTrailProfit
                    min={leg.roll_strike_trail_profit.min}
                    max={leg.roll_strike_trail_profit.max}
                    interval={leg.roll_strike_trail_profit.interval}
                    onChangeRollStrikeTrailProfit={onChangeLeg}
                  />
                  <div disabled>
                    <SelectDD
                      fieldName="roll_strike_trail_profit_sign"
                      selectedValue={leg.roll_strike_trail_profit_sign}
                      options={pointPercentOptions}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="flex-row">
          <div className="cell">
            <div>
              <Label caption="Simple Momentum / Range Breakout" />
            </div>
            <div disabled>
              <SelectDD
                fieldName="simple_momentum_range_breakout"
                selectedValue={leg.simple_momentum_range_breakout}
                options={momentumOptions}
              />
            </div>
          </div>
          <div className="cell">
            {leg.simple_momentum_range_breakout === "sm" && (
              <>
                <div>
                  <Label caption="Simple Momentum (+)" />
                </div>
                <div className="cell align-top">
                  <div disabled>
                    <SelectDD
                      fieldName="simple_momentum_direction"
                      selectedValue={leg.simple_momentum_direction}
                      options={plusMinusOptions}
                    />
                  </div>
                  <SimpleMomentum
                    min={leg.simple_momentum.min}
                    max={leg.simple_momentum.max}
                    interval={leg.simple_momentum.interval}
                    onChangeSimpleMomentum={onChangeLeg}
                  />
                  <div disabled>
                    <SelectDD
                      fieldName="simple_momentum_sign"
                      selectedValue={leg.simple_momentum_sign}
                      options={pointPercentOptions}
                    />
                  </div>
                </div>
              </>
            )}
            {leg.simple_momentum_range_breakout === "rb" && (
              <>
                <div>
                  <Label caption="Range Breakout (+)" />
                </div>
                <RangeBreakout
                  min={leg.range_breakout.min}
                  max={leg.range_breakout.max}
                  interval={leg.range_breakout.interval}
                  onChangeRangeBreakout={onChangeLeg}
                />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leg;
