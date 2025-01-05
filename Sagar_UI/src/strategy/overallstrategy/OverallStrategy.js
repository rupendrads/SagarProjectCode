import { OptionButtons } from "../../common/OptionButtons";
import { SelectDD } from "../../common/SelectDD";
import { InputText } from "../../common/InputText";
import { Label } from "../../common/Label";

export const OverallStrategy = (props) => {
  const { overallStrategy, onChangeOverallStrategy, children } = props;

  const strategyTypeValuesWithCaptions = [
    "intraday,Intraday",
    "btst,BTST",
    "positional,Positional",
  ];

  const underlyingValuesWithCaptions = [
    "spot,Spot",
    "futures,Futures",
    "impliedfutures,Implied Futures",
  ];

  const squareOffValuesWithCaptions = ["complete,Complete", "partial,Partial"];

  const expiryForImpliedFuturesOptions = [
    {
      value: "current",
      caption: "Current",
    },
    {
      value: "next",
      caption: "Next",
    },
    {
      value: "monthly",
      caption: "Monthly",
    },
  ];

  const trailingOptionsOptions = [
    {
      value: "lock",
      caption: "Lock",
    },
    {
      value: "lockntrail",
      caption: "Lock and Trail",
    },
  ];

  return (
    <>
      <div className="cell">
        <h6 className="box-title">
          Overall Strategy{" "}
          {overallStrategy.id === -1 ? (
            <span>(New)</span>
          ) : (
            overallStrategy.name && (
              <>
                ({overallStrategy.name} {children})
              </>
            )
          )}
        </h6>
        <hr />
      </div>
      <div className="box-content-fill">
        <div className="box card">
          <div className="flex-row strategy-type-row">
            <div className="cell">
              <div>
                <Label caption="Strategy Type" />
              </div>
              <div>
                <OptionButtons
                  fieldName="strategy_type"
                  fieldValuesWithCaptions={strategyTypeValuesWithCaptions}
                  selectedFieldValue={overallStrategy.strategy_type}
                  callbackFunction={onChangeOverallStrategy}
                />
              </div>
            </div>
            <div className="cell">
              <div>
                <Label caption="Underlying" />
              </div>
              <div>
                <OptionButtons
                  fieldName="underlying"
                  fieldValuesWithCaptions={underlyingValuesWithCaptions}
                  selectedFieldValue={overallStrategy.underlying}
                  callbackFunction={onChangeOverallStrategy}
                />
              </div>
            </div>
            {overallStrategy.underlying === "impliedfutures" && (
              <div className="cell">
                <div>
                  <Label caption="Implied Futures Expiry" />
                </div>
                <div>
                  <SelectDD
                    fieldName="implied_futures_expiry"
                    selectedValue={overallStrategy.implied_futures_expiry}
                    options={expiryForImpliedFuturesOptions}
                    callbackFunction={onChangeOverallStrategy}
                  />
                </div>
              </div>
            )}
            <div className="flex-row entry-exit-time">
              <div className="cell">
                <div>
                  <Label caption="Entry time" />
                </div>
                <div className="input-group input-group-sm">
                  <input
                    type="time"
                    className="form-control"
                    id="entry_time"
                    name="entry_time"
                    value={overallStrategy.entry_time}
                    onChange={(e) =>
                      onChangeOverallStrategy("entry_time", e.target.value)
                    }
                  ></input>
                </div>
              </div>
              <div className="cell">
                <div>
                  <Label caption="Last entry time" />
                </div>
                <div className="input-group input-group-sm">
                  <input
                    type="time"
                    className="form-control"
                    id="last_entry_time"
                    name="last_entry_time"
                    value={overallStrategy.last_entry_time}
                    onChange={(e) =>
                      onChangeOverallStrategy("last_entry_time", e.target.value)
                    }
                  ></input>
                </div>
              </div>
              <div className="cell">
                <div>
                  <Label caption="Exit time" />
                </div>
                <div className="input-group input-group-sm">
                  <input
                    type="time"
                    id="exit_time"
                    className="form-control"
                    name="exit_time"
                    value={overallStrategy.exit_time}
                    onChange={(e) =>
                      onChangeOverallStrategy("exit_time", e.target.value)
                    }
                  ></input>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="box-content-fill">
        <div className="box card">
          <div className="flex-row">
            <div className="cell">
              <div>
                <Label caption="Square Off" />
              </div>
              <div>
                <OptionButtons
                  fieldName="square_off"
                  fieldValuesWithCaptions={squareOffValuesWithCaptions}
                  selectedFieldValue={overallStrategy.square_off}
                  callbackFunction={onChangeOverallStrategy}
                />
              </div>
            </div>
            <div className="cell">
              <div>
                <Label caption="Overall Stoploss" />
              </div>
              <div className="input-group input-group-sm">
                <InputText
                  name="overall_sl"
                  value={overallStrategy.overall_sl}
                  callbackFunction={onChangeOverallStrategy}
                />
              </div>
            </div>
            <div className="cell">
              <div>
                <Label caption="Overall Target" />
              </div>
              <div className="input-group input-group-sm">
                <InputText
                  name="overall_target"
                  value={overallStrategy.overall_target}
                  callbackFunction={onChangeOverallStrategy}
                />
              </div>
            </div>
          </div>
          <div className="flex-row">
            <div className="cell">
              <div>
                <Label caption="Trailing Options" />
              </div>
              <div>
                <SelectDD
                  fieldName="trailing_options"
                  selectedValue={overallStrategy.trailing_options}
                  options={trailingOptionsOptions}
                  callbackFunction={onChangeOverallStrategy}
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
                    name="profit_reaches"
                    value={overallStrategy.profit_reaches}
                    callbackFunction={onChangeOverallStrategy}
                  />
                </div>
              </div>
              <div className="cell">
                <div>
                  <Label caption="Lock profit" />
                </div>
                <div className="input-group input-group-sm">
                  <InputText
                    name="lock_profit"
                    value={overallStrategy.lock_profit}
                    callbackFunction={onChangeOverallStrategy}
                  />
                </div>
              </div>
            </div>
            {overallStrategy.trailing_options === "lockntrail" && (
              <div className="flex-row">
                <div className="cell">
                  <div>
                    <Label caption="For every increase in profit by" />
                  </div>
                  <div className="input-group input-group-sm">
                    <InputText
                      name="increase_in_profit"
                      value={overallStrategy.increase_in_profit}
                      callbackFunction={onChangeOverallStrategy}
                    />
                  </div>
                </div>
                <div className="cell">
                  <div>
                    <Label caption="Trail profit by" />
                  </div>
                  <div className="input-group input-group-sm">
                    <InputText
                      name="trail_profit"
                      value={overallStrategy.trail_profit}
                      callbackFunction={onChangeOverallStrategy}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};
