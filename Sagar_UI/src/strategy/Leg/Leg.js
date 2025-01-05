import "./Leg.css";
import { Label } from "../../common/Label";
import { InputText } from "../../common/InputText";
import { OptionButtonsWithId } from "../../common/OptionButtonsWithId";
import { SelectDD } from "../../common/SelectDD";
import { SelectDDWithKeyIndex } from "../../common/SelectDDWithKeyIndex";
import { pointPercentOptions, plusMinusOptions } from "../../common/common";
import {
  expiryOptions,
  strikeTypeOptions,
  strikeSelectionCriteriaOptions,
  trailingOptions,
  momentumOptions,
} from "./LegOptions";

const Leg = (props) => {
  //console.log(props);
  const { removeLeg, leg, onChangeLegs } = props;

  const onChangeLeg = (fieldName, fieldValue) => {
    // console.log("fieldname -", fieldName);
    // console.log("fieldvlaue -", fieldValue);
    // console.log("leg.id", leg.id);
    onChangeLegs(leg.id, fieldName, fieldValue);
  };

  const positionOptions = [
    {
      inputName: `position${leg.id}`,
      inputId: `position-buy${leg.id}`,
      inputLabel: "Buy",
      fieldName: "position",
      fieldValue: "buy",
    },
    {
      inputName: `position${leg.id}`,
      inputId: `position-sell${leg.id}`,
      inputLabel: "Sell",
      fieldName: "position",
      fieldValue: "sell",
    },
  ];

  const optionTypeOptions = [
    {
      inputName: `option_type${leg.id}`,
      inputId: `option_type_call${leg.id}`,
      inputLabel: "Call",
      fieldName: "option_type",
      fieldValue: "call",
    },
    {
      inputName: `option_type${leg.id}`,
      inputId: `option_type_put${leg.id}`,
      inputLabel: "Put",
      fieldName: "option_type",
      fieldValue: "put",
    },
  ];

  return (
    <div className="box-content-fill">
      <div className="leg box card">
        {removeLeg && (
          <div className="flex-row">
            <div className="leg-no">
              <div>
                <button
                  className="btn remove-leg"
                  onClick={() => removeLeg(leg.id)}
                >
                  Remove Leg
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="flex-row">
          <div className="cell">
            <div>
              <Label caption="Total Lot" />
            </div>
            <div className="input-group input-group-sm">
              <InputText
                name="lots"
                value={leg.lots}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="cell">
            <div>
              <label className="field-label" htmlFor={`position${props.srNo}`}>
                Position
              </label>
            </div>
            <div>
              <OptionButtonsWithId
                options={positionOptions}
                selectedValue={leg.position}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="cell">
            <div>
              <label
                className="field-label"
                htmlFor={`optionType${props.srNo}`}
              >
                Option Type
              </label>
            </div>
            <div>
              <OptionButtonsWithId
                options={optionTypeOptions}
                selectedValue={leg.option_type}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="cell">
            <div>
              <Label caption="Expiry" />
            </div>
            <div>
              <SelectDD
                fieldName="expiry"
                selectedValue={leg.expiry}
                options={expiryOptions}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="cell">
            <div>
              <Label caption="No. of Reentry" />
            </div>
            <div className="input-group input-group-sm">
              <InputText
                name="no_of_reentry"
                value={leg.no_of_reentry}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
        </div>
        <div className="flex-row">
          <div className="cell">
            <div>
              <Label caption="Strike Selection Criteria" />
            </div>
            <div>
              <SelectDD
                fieldName="strike_selection_criteria"
                selectedValue={leg.strike_selection_criteria}
                options={strikeSelectionCriteriaOptions}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          {leg.strike_selection_criteria === "strike" && (
            <div className="cell">
              <div>
                <Label caption="Strike Type" />
              </div>
              <div>
                <SelectDDWithKeyIndex
                  fieldName="strike_type"
                  selectedValue={leg.strike_type}
                  options={strikeTypeOptions}
                  callbackFunction={onChangeLeg}
                />
              </div>
            </div>
          )}
          {leg.strike_selection_criteria === "closestpremium" && (
            <div className="cell">
              <div>
                <Label caption="Closest Premium" />
              </div>
              <div className="input-group input-group-sm">
                <InputText
                  name="closest_premium"
                  value={leg.closest_premium}
                  callbackFunction={onChangeLeg}
                />
              </div>
            </div>
          )}
          {leg.strike_selection_criteria === "straddlewidth" && (
            <div className="cell">
              <div>
                <Label caption="Straddle Width" />
              </div>
              <div className="cell align-bottom">
                <div>
                  <Label caption="[ ATM Strike" />
                </div>
                <div>
                  <SelectDD
                    fieldName="straddle_width_sign"
                    selectedValue={leg.straddle_width_sign}
                    options={plusMinusOptions}
                    callbackFunction={onChangeLeg}
                  />
                </div>
                <div>
                  <Label caption="(" />
                </div>
                <div>
                  <div className="input-group input-group-sm">
                    <InputText
                      name="straddle_width_value"
                      value={leg.straddle_width_value}
                      callbackFunction={onChangeLeg}
                    />
                  </div>
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
                <Label caption="% of ATM Strike" />
              </div>
              <div className="cell align-bottom">
                <div>
                  <SelectDD
                    fieldName="percent_of_atm_strike_sign"
                    selectedValue={leg.percent_of_atm_strike_sign}
                    options={plusMinusOptions}
                    callbackFunction={onChangeLeg}
                  />
                </div>
                <div>
                  <div className="input-group input-group-sm">
                    <InputText
                      name="percent_of_atm_strike_value"
                      value={leg.percent_of_atm_strike_value}
                      callbackFunction={onChangeLeg}
                    />
                  </div>
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
                <Label caption="Atm Straddle Premium %" />
              </div>
              <div className="input-group input-group-sm">
                <InputText
                  name="atm_straddle_premium"
                  value={leg.atm_straddle_premium}
                  callbackFunction={onChangeLeg}
                />
              </div>
            </div>
          )}
        </div>
        <div className="flex-row traling-options-row">
          <div className="cell">
            <div>
              <Label caption="Stop Loss" />
            </div>
            <div className="with-sign">
              <div className="input-group input-group-sm">
                <InputText
                  name="strike_selection_criteria_stop_loss"
                  value={leg.strike_selection_criteria_stop_loss}
                  callbackFunction={onChangeLeg}
                />
              </div>
              <div className="sign">
                <SelectDD
                  fieldName="strike_selection_criteria_stop_loss_sign"
                  selectedValue={leg.strike_selection_criteria_stop_loss_sign}
                  options={pointPercentOptions}
                  callbackFunction={onChangeLeg}
                />
              </div>
            </div>
          </div>
          <div className="cell">
            <div>
              <Label caption="Trailing Options" />
            </div>
            <div>
              <SelectDD
                fieldName="strike_selection_criteria_trailing_options"
                selectedValue={leg.strike_selection_criteria_trailing_options}
                options={trailingOptions}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="flex-row">
            <div className="cell">
              <div>
                <Label caption="If profit reaches" />
              </div>
              <div className="input-group input-group-sm">
                <InputText
                  name="strike_selection_criteria_profit_reaches"
                  value={leg.strike_selection_criteria_profit_reaches}
                  callbackFunction={onChangeLeg}
                />
              </div>
            </div>
            <div className="cell">
              <div>
                <Label caption="Lock profit" />
              </div>
              <div className="with-sign">
                <div className="input-group input-group-sm">
                  <InputText
                    name="strike_selection_criteria_lock_profit"
                    value={leg.strike_selection_criteria_lock_profit}
                    callbackFunction={onChangeLeg}
                  />
                </div>
                <div>
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
          {leg.strike_selection_criteria_trailing_options === "lockntrail" && (
            <div className="flex-row">
              <div className="cell">
                <div>
                  <Label caption="For every increase in profit by" />
                </div>
                <div className="input-group input-group-sm">
                  <InputText
                    name="strike_selection_criteria_increase_in_profit"
                    value={leg.strike_selection_criteria_increase_in_profit}
                    callbackFunction={onChangeLeg}
                  />
                </div>
              </div>
              <div className="cell">
                <div>
                  <Label caption="Trail profit by" />
                </div>
                <div className="with-sign">
                  <div className="input-group input-group-sm">
                    <InputText
                      name="strike_selection_criteria_trail_profit"
                      value={leg.strike_selection_criteria_trail_profit}
                      callbackFunction={onChangeLeg}
                    />
                  </div>
                  <div>
                    <SelectDD
                      fieldName="strike_selection_criteria_trail_profit_sign"
                      selectedValue={
                        leg.strike_selection_criteria_trail_profit_sign
                      }
                      options={pointPercentOptions}
                      callbackFunction={onChangeLeg}
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
              <Label caption="Roll Strike" />
            </div>
            <div className="input-group input-group-sm">
              <InputText
                name="roll_strike"
                value={leg.roll_strike}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="cell">
            <Label caption="New Strike Type" />
            <div>
              <SelectDDWithKeyIndex
                fieldName="roll_strike_strike_type"
                selectedValue={leg.roll_strike_strike_type}
                options={strikeTypeOptions}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
        </div>
        <div className="flex-row traling-options-row">
          <div className="cell">
            <div>
              <Label caption="Stop Loss" />
            </div>
            <div className="with-sign">
              <div className="input-group input-group-sm">
                <InputText
                  name="roll_strike_stop_loss"
                  value={leg.roll_strike_stop_loss}
                  callbackFunction={onChangeLeg}
                />
              </div>
              <div className="sign">
                <SelectDD
                  fieldName="roll_strike_stop_loss_sign"
                  selectedValue={leg.roll_strike_stop_loss_sign}
                  options={pointPercentOptions}
                  callbackFunction={onChangeLeg}
                />
              </div>
            </div>
          </div>
          <div className="cell">
            <Label caption="Trailing Options" />
            <div>
              <SelectDD
                fieldName="roll_strike_trailing_options"
                selectedValue={leg.roll_strike_trailing_options}
                options={trailingOptions}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="flex-row">
            <div className="cell">
              <div>
                <Label caption="If profit reaches" />
              </div>
              <div className="input-group input-group-sm">
                <InputText
                  name="roll_strike_profit_reaches"
                  value={leg.roll_strike_profit_reaches}
                  callbackFunction={onChangeLeg}
                />
              </div>
            </div>
            <div className="cell">
              <div>
                <Label caption="Lock profit" />
              </div>
              <div className="with-sign">
                <div className="input-group input-group-sm">
                  <InputText
                    name="roll_strike_lock_profit"
                    value={leg.roll_strike_lock_profit}
                    callbackFunction={onChangeLeg}
                  />
                </div>
                <div>
                  <SelectDD
                    fieldName="roll_strike_lock_profit_sign"
                    selectedValue={leg.roll_strike_lock_profit_sign}
                    options={pointPercentOptions}
                    callbackFunction={onChangeLeg}
                  />
                </div>
              </div>
            </div>
          </div>
          {leg.roll_strike_trailing_options === "lockntrail" && (
            <div className="flex-row">
              <div className="cell">
                <div>
                  <Label caption="For every increase in profit by" />
                </div>
                <div className="input-group input-group-sm">
                  <InputText
                    name="roll_strike_increase_in_profit"
                    value={leg.roll_strike_increase_in_profit}
                    callbackFunction={onChangeLeg}
                  />
                </div>
              </div>
              <div className="cell">
                <div>
                  <Label caption="Trail profit by" />
                </div>
                <div className="with-sign">
                  <div className="input-group input-group-sm">
                    <InputText
                      name="roll_strike_trail_profit"
                      value={leg.roll_strike_trail_profit}
                      callbackFunction={onChangeLeg}
                    />
                  </div>
                  <div>
                    <SelectDD
                      fieldName="roll_strike_trail_profit_sign"
                      selectedValue={leg.roll_strike_trail_profit_sign}
                      options={pointPercentOptions}
                      callbackFunction={onChangeLeg}
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
            <div>
              <SelectDD
                fieldName="simple_momentum_range_breakout"
                selectedValue={leg.simple_momentum_range_breakout}
                options={momentumOptions}
                callbackFunction={onChangeLeg}
              />
            </div>
          </div>
          <div className="cell">
            {leg.simple_momentum_range_breakout === "sm" && (
              <>
                <div>
                  <Label caption="Simple Momentum" />
                </div>
                <div className="cell align-bottom">
                  <div>
                    <SelectDD
                      fieldName="simple_momentum_direction"
                      selectedValue={leg.simple_momentum_direction}
                      options={plusMinusOptions}
                      callbackFunction={onChangeLeg}
                    />
                  </div>
                  <div className="input-group input-group-sm">
                    <InputText
                      name="simple_momentum"
                      value={leg.simple_momentum}
                      callbackFunction={onChangeLeg}
                    />
                  </div>
                  <div>
                    <SelectDD
                      fieldName="simple_momentum_sign"
                      selectedValue={leg.simple_momentum_sign}
                      options={pointPercentOptions}
                      callbackFunction={onChangeLeg}
                    />
                  </div>
                </div>
              </>
            )}
            {leg.simple_momentum_range_breakout === "rb" && (
              <>
                <div>
                  <Label caption="Range Breakout" />
                </div>
                <div className="input-group input-group-sm">
                  <InputText
                    name="range_breakout"
                    value={leg.range_breakout}
                    callbackFunction={onChangeLeg}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Leg;
