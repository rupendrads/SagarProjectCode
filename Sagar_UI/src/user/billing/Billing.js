import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { Modal } from "bootstrap";
import "./Billing.css";
import Steps from "../steps/Steps";
import configData from "../../config.json";

const Billing = (props) => {
  const { userId, isNewUser, forwardStep, stepItems, changeStep } = props;
  const {
    register,
    watch,
    reset,
    handleSubmit,
    formState: { data, errors },
  } = useForm({
    defaultValues: {
      billing_type: "one time",
      subscription_type: "trial",
      subscription_fee: "",
      one_time_fee: "",
      profit_sharing_type: "flat",
    },
  });
  const [errorList, setErrorList] = useState([]);
  const [profitSharingSlabs, setProfitSharingSlabs] = useState([
    { from: 0, to: 30, profit_percent: "", less_percent: "" },
    { from: 31, to: 70, profit_percent: "", less_percent: "" },
    { from: 71, to: 100, profit_percent: "", less_percent: "" },
  ]);
  const refInfoModal = useRef(null);

  useEffect(() => {
    if (refInfoModal.current) {
      refInfoModal.infoModal = new Modal(refInfoModal.current, {
        backdrop: "static",
      });
    }
  }, [refInfoModal]);

  const showInfoModal = () => {
    if (refInfoModal.infoModal) {
      refInfoModal.infoModal.show();
    }
  };

  const hideInfoModal = () => {
    if (refInfoModal.infoModal) {
      refInfoModal.infoModal.hide();
    }
  };

  useEffect(() => {
    console.log(profitSharingSlabs);
    if (!isNewUser) {
      let urlSegment = "billing";

      if (configData.JSON_DB === false) {
        urlSegment = "getBilling";
        try {
          fetch(`${configData.API_URL}/${urlSegment}/${userId}`, {
            method: "GET",
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("billing get by user id response - ", data);
              console.log("userId", userId);

              if (data.length > 0) {
                if (data[0].subscription_type === null) {
                  data[0].subscription_type = "trial";
                }
                if (data[0].profit_sharing_type === null) {
                  data[0].profit_sharing_type = "flat";
                }
                if (data[0]?.profit_sharing_slabs) {
                  setProfitSharingSlabs([...data[0].profit_sharing_slabs]);
                }
                reset({ ...data[0] });
              }
            });
        } catch (error) {
          console.error("Error receiving billing by user id data", error);
        } finally {
        }
      } else {
        try {
          fetch(`${configData.API_URL}/${urlSegment}`, {
            method: "GET",
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("billing get all response - ", data);
              console.log("userId", userId);
              const billingData = data.filter((ua) => ua.user_id === userId);

              console.log("billingData", billingData);
              if (billingData.length > 0) {
                setProfitSharingSlabs([...billingData[0].profit_sharing_slabs]);
                reset({ ...billingData[0] });
              }
            });
        } catch (error) {
          console.error("Error receiving billing data", error);
        } finally {
        }
      }
    }
  }, [userId]);

  const slabProfitPercentChanged = (index, value) => {
    setProfitSharingSlabs((prevValue) => {
      const newValue = [...prevValue];
      newValue[index].profit_percent = value;
      console.log("newValue", newValue);
      return newValue;
    });
  };

  const slabLessPercentChanged = (index, value) => {
    setProfitSharingSlabs((prevValue) => {
      const newValue = [...prevValue];
      newValue[index].less_percent = value;
      console.log("newValue", newValue);
      return newValue;
    });
  };

  const saveBilling = (data) => {
    console.log(data);
    let billingData = {
      user_id: userId,
      ...data,
      profit_sharing_slabs: [...profitSharingSlabs],
    };

    console.log(billingData.billing_type);
    console.log(billingData.billing_type == "one time");
    if (billingData.billing_type == "one time") {
      billingData = {
        ...billingData,
        subscription_type: "trial",
        subscription_fee: "",
        profit_sharing_type: "flat",
        profit_sharing_flat_profit_percent: "",
        profit_sharing_flat_less_percent: "",
        profit_sharing_slabs: [
          { from: 0, to: 30, profit_percent: "", less_percent: "" },
          { from: 31, to: 70, profit_percent: "", less_percent: "" },
          { from: 71, to: 100, profit_percent: "", less_percent: "" },
        ],
      };
    }
    if (billingData.billing_type == "subscription") {
      billingData = {
        ...billingData,
        one_time_fee: "",
        profit_sharing_type: "flat",
        profit_sharing_flat_profit_percent: "",
        profit_sharing_flat_less_percent: "",
        profit_sharing_slabs: [
          { from: 0, to: 30, profit_percent: "", less_percent: "" },
          { from: 31, to: 70, profit_percent: "", less_percent: "" },
          { from: 71, to: 100, profit_percent: "", less_percent: "" },
        ],
      };
    }
    if (billingData.billing_type == "profit sharing") {
      billingData.one_time_fee = "";
      billingData.subscription_type = "trial";
      billingData.subscription_fee = "";
      if (billingData.profit_sharing_type === "flat") {
        billingData.profit_sharing_slabs = [
          { from: 0, to: 30, profit_percent: "", less_percent: "" },
          { from: 31, to: 70, profit_percent: "", less_percent: "" },
          { from: 71, to: 100, profit_percent: "", less_percent: "" },
        ];
      } else {
        billingData.profit_sharing_flat_profit_percent = "";
        billingData.profit_sharing_flat_less_percent = "";
      }
    }

    console.log(billingData);

    let urlSegment = "billing";

    if (isNewUser) {
      if (configData.JSON_DB === false) {
        urlSegment = "addBilling";
      }

      try {
        fetch(`${configData.API_URL}/${urlSegment}`, {
          method: "POST",
          body: JSON.stringify(billingData),
          headers: { "Content-type": "application/json; charset=UTF-8" },
        })
          .then((res) => res.json())
          .then((data) => {
            console.log("billing response - ", data);
            forwardStep();
          });
      } catch (error) {
        console.error("Error billing:", error);
      } finally {
      }
    } else {
      if (configData.JSON_DB === false) {
        urlSegment = "editBilling";
      }
      try {
        fetch(`${configData.API_URL}/${urlSegment}/${billingData.id}`, {
          method: "PUT",
          body: JSON.stringify(billingData),
          headers: { "Content-type": "application/json; charset=UTF-8" },
        })
          .then((res) => res.json())
          .then((data) => {
            console.log("billing update response - ", data);
            showInfoModal();
          });
      } catch (error) {
        console.error("Error update billing:", error);
      } finally {
      }
    }
  };

  return (
    <>
      <div className="registration-sidebar">
        <div className="box card registration-steps-container">
          <Steps
            step={2}
            stepItems={stepItems}
            isNewUser={isNewUser}
            changeStep={changeStep}
          />
        </div>
        <div className="billing-container" style={{ width: "100%" }}>
          <div className="box card">
            <div>
              <h6 className="box-title">Billing</h6>
              <hr />
            </div>
            <form onSubmit={handleSubmit(saveBilling)}>
              <div className="billing-input">
                <div className="label">
                  <label className="field-label">Billing Type</label>
                </div>
                <div className="billing-input-cell">
                  <div className="input-group input-group-sm">
                    <select
                      {...register("billing_type", { required: true })}
                      className="form-select form-select-sm"
                    >
                      <option value="one time">One time</option>
                      <option value="subscription">Subscription</option>
                      <option value="profit sharing">Profit sharing</option>
                    </select>
                  </div>
                  <div className="input-error">
                    {errors.billing_type && <span>Required</span>}
                  </div>
                </div>
              </div>
              {watch("billing_type") === "one time" && (
                <div className="billing-input">
                  <div className="label">
                    <label className="field-label">One time fee</label>
                  </div>
                  <div className="billing-input-cell">
                    <div className="input-group input-group-sm">
                      <input
                        type="text"
                        className="form-control"
                        {...register("one_time_fee", { required: false })}
                      ></input>
                    </div>

                    <div className="input-error">
                      {errors.one_time_fee && <span>Required</span>}
                    </div>
                  </div>
                </div>
              )}

              {watch("billing_type") === "subscription" && (
                <>
                  <div className="billing-input">
                    <div className="label">
                      <label className="field-label">Subscription Type</label>
                    </div>
                    <div className="billing-input-cell">
                      <div className="input-group input-group-sm">
                        <select
                          {...register("subscription_type", { required: true })}
                          className="form-select form-select-sm"
                        >
                          <option value="trial">Trial</option>
                          <option value="monthly">Monthly</option>
                          <option value="quarterly">Quarterly</option>
                          <option value="yearly">Yearly</option>
                        </select>
                      </div>

                      <div className="input-error">
                        {errors.subscription_type && <span>Required</span>}
                      </div>
                    </div>
                  </div>
                  <div className="billing-input">
                    <div className="label">
                      <label className="field-label">Subscription fee</label>
                    </div>
                    <div className="billing-input-cell">
                      <div className="input-group input-group-sm">
                        <input
                          type="text"
                          className="form-control"
                          {...register("subscription_fee", { required: true })}
                        ></input>
                      </div>

                      <div className="input-error">
                        {errors.subscription_fee && <span>Required</span>}
                      </div>
                    </div>
                  </div>
                </>
              )}

              {watch("billing_type") === "profit sharing" && (
                <>
                  <div className="billing-input">
                    <div className="label">
                      <label className="field-label">Profit sharing type</label>
                    </div>
                    <div className="billing-input-cell">
                      <div className="input-group input-group-sm">
                        <select
                          {...register("profit_sharing_type", {
                            required: true,
                          })}
                          className="form-select form-select-sm"
                        >
                          <option value="flat">Flat</option>
                          <option value="slab">Slab</option>
                        </select>
                      </div>

                      <div className="input-error">
                        {errors.profit_sharing_type && <span>Required</span>}
                      </div>
                    </div>
                  </div>
                  {watch("profit_sharing_type") === "flat" && (
                    <>
                      <div className="billing-input">
                        <div className="label">
                          <label className="field-label">Profit percent</label>
                        </div>
                        <div className="billing-input-cell">
                          <div className="input-group input-group-sm">
                            <input
                              type="text"
                              className="form-control"
                              {...register(
                                "profit_sharing_flat_profit_percent",
                                {
                                  required: false,
                                }
                              )}
                            ></input>
                          </div>

                          <div className="input-error">
                            {errors.profit_sharing_flat_profit_percent && (
                              <span>Required</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="billing-input">
                        <div className="label">
                          <label className="field-label">Less percent</label>
                        </div>
                        <div className="billing-input-cell">
                          <div className="input-group input-group-sm">
                            <input
                              type="text"
                              className="form-control"
                              {...register("profit_sharing_flat_less_percent", {
                                required: false,
                              })}
                            ></input>
                          </div>

                          <div className="input-error">
                            {errors.profit_sharing_flat_less_percent && (
                              <span>Required</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                  {watch("profit_sharing_type") === "slab" &&
                    profitSharingSlabs &&
                    profitSharingSlabs.map((slab, index) => {
                      return (
                        <div className="profit_sharing_slab">
                          <div className="billing-input">
                            <div className="label">
                              <label className="field-label">From</label>
                            </div>
                            <div className="billing-input-cell">
                              <div className="input-group input-group-sm">
                                <input
                                  type="text"
                                  className="form-control"
                                  value={slab.from}
                                  disabled
                                ></input>
                              </div>
                            </div>
                          </div>
                          <div className="billing-input">
                            <div className="label">
                              <label className="field-label">To</label>
                            </div>
                            <div className="billing-input-cell">
                              <div className="input-group input-group-sm">
                                <input
                                  type="text"
                                  className="form-control"
                                  value={slab.to}
                                  disabled
                                ></input>
                              </div>
                            </div>
                          </div>
                          <div className="billing-input">
                            <div className="label">
                              <label className="field-label">
                                Profit percent
                              </label>
                            </div>
                            <div className="billing-input-cell">
                              <div className="input-group input-group-sm">
                                <input
                                  type="text"
                                  className="form-control"
                                  value={slab.profit_percent}
                                  onChange={(e) =>
                                    slabProfitPercentChanged(
                                      index,
                                      e.target.value
                                    )
                                  }
                                ></input>
                              </div>
                            </div>
                          </div>
                          <div className="billing-input">
                            <div className="label">
                              <label className="field-label">
                                Less percent
                              </label>
                            </div>
                            <div className="billing-input-cell">
                              <div className="input-group input-group-sm">
                                <input
                                  type="text"
                                  className="form-control"
                                  value={slab.less_percent}
                                  onChange={(e) =>
                                    slabLessPercentChanged(
                                      index,
                                      e.target.value
                                    )
                                  }
                                ></input>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                </>
              )}

              <div className="billing-button-row">
                <button className="btn theme_button" type="submit">
                  {isNewUser ? (
                    <span>Save and Continue</span>
                  ) : (
                    <span>Update</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div className="modal" tabIndex={-1} role="dialog" ref={refInfoModal}>
        <div className="modal-dialog modal-dialog-centered" role="document">
          <div className="modal-content">
            <div className="modal-body">
              <div className="form-group info-modal-body">
                <label className="field-label">
                  Billing Updated Successfully
                </label>
              </div>
            </div>
            <div className="modal-footer info-modal-footer">
              <button
                type="button"
                className="btn btn-light ok-button"
                onClick={hideInfoModal}
              >
                Ok
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Billing;
