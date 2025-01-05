import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { Modal } from "bootstrap";
import "./UserDetails.css";
import Steps from "../steps/Steps";
import configData from "../../config.json";

const UserDetails = (props) => {
  const { user, isNewUser, storeUser, forwardStep, stepItems, changeStep } =
    props;
  const {
    register,
    watch,
    reset,
    handleSubmit,
    formState: { data, errors },
  } = useForm();
  const [errorList, setErrorList] = useState([]);
  const [confirmPassword, setConfirmPassword] = useState("");

  const refInfoModal = useRef(null);

  useEffect(() => {
    if (refInfoModal.current) {
      refInfoModal.infoModal = new Modal(refInfoModal.current, {
        backdrop: "static",
      });
    }
  }, [refInfoModal]);

  useEffect(() => {
    reset({ ...user });
  }, [user]);

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

  const confirmPasswordChanged = (e) => {
    setConfirmPassword(() => {
      const password = watch("password");
      const confirmPassword = e.target.value;
      validateConfirmPassword(confirmPassword);
      validatePasswordMatch(password, confirmPassword);
      return confirmPassword;
    });
  };

  const validateConfirmPassword = (confirmPassword) => {
    if (confirmPassword.length === 0) {
      setErrorList([
        ...errorList,
        { field: "confirmPassword", message: "Confirm Password Required!" },
      ]);
      return false;
    } else {
      setErrorList((prevErrorList) => {
        return prevErrorList.filter(
          (error) => error.field !== "confirmPassword"
        );
      });
    }
    return true;
  };

  const validatePasswordMatch = (password, confirmPassword) => {
    if (confirmPassword.length === 0 || confirmPassword === password) {
      setErrorList((prevErrorList) => {
        return prevErrorList.filter((error) => error.field !== "password");
      });
    } else {
      setErrorList((prevErrorList) => {
        const updatedErrorList = [...prevErrorList];
        const password = updatedErrorList.find(
          (error) => error.field === "password"
        );
        if (password) {
          password.message = "Password does not match!";
        } else {
          updatedErrorList.push({
            field: "password",
            message: "Password does not match!",
          });
        }
        return updatedErrorList;
      });
      return false;
    }
    return true;
  };

  const validateDateOfBirth = (dateofbirth) => {
    console.log("dateofbirth", dateofbirth);
    if (dateofbirth.length > 0) {
      const inputDate = new Date(dateofbirth);
      console.log("inputDate", inputDate);
      if (!isNaN(inputDate)) {
        const currentDate = new Date();
        console.log("currentDate", currentDate);
        console.log("inputDate < currentDate", inputDate < currentDate);
        console.log(typeof (inputDate < currentDate));
        const isDobValid = inputDate < currentDate;
        if (isDobValid == false) {
          console.log("isDobValid", isDobValid);
          setErrorList((prevErrorList) => {
            console.log("setting error list");
            const updatedErrorList = [...prevErrorList];
            const dateofbirth = updatedErrorList.find(
              (error) => error.field === "dateofbirth"
            );
            console.log("dateofbirth", dateofbirth);
            if (dateofbirth === undefined) {
              updatedErrorList.push({
                field: "dateofbirth",
                message: "Invalid date of birth!",
              });
            }
            console.log("updatedErrorList", updatedErrorList);
            return updatedErrorList;
          });
          return false;
        } else {
          setErrorList((prevErrorList) => {
            return prevErrorList.filter(
              (error) => error.field !== "dateofbirth"
            );
          });
        }
      } else {
        setErrorList((prevErrorList) => {
          console.log("setting error list");
          const updatedErrorList = [...prevErrorList];
          const dateofbirth = updatedErrorList.find(
            (error) => error.field === "dateofbirth"
          );
          console.log("dateofbirth", dateofbirth);
          if (dateofbirth === undefined) {
            updatedErrorList.push({
              field: "dateofbirth",
              message: "Invalid date of birth!",
            });
          }
          console.log("updatedErrorList", updatedErrorList);
          return updatedErrorList;
        });
        return false;
      }
      return true;
    }
  };

  const registerUser = (data) => {
    console.log(data);
    // validate form and add errors to errorList

    // date of birth
    const isDateOfBirthValid = validateDateOfBirth(data.dateofbirth);
    console.log("isDateOfBirthValid", isDateOfBirthValid);

    // password match
    const isPasswordMatch = validatePasswordMatch(
      data.password,
      confirmPassword
    );
    console.log("isPasswordMatch", isPasswordMatch);

    const isFormValid = isDateOfBirthValid == true && isPasswordMatch == true;

    if (isFormValid === true) {
      const formattedData = { ...data };

      let urlSegment = "user";

      if (configData.JSON_DB === false) {
        if (isNewUser) {
          formattedData["id"] = "-1";
          formattedData["emailVerificationStatus"] = true;
          formattedData["mobileVerificationStatus"] = true;
          formattedData["is_active"] = true;
          urlSegment = "registeruser";
        } else {
          urlSegment = "edituser";
        }
      }

      if (isNewUser) {
        try {
          fetch(`${configData.API_URL}/${urlSegment}`, {
            method: "POST",
            body: JSON.stringify(formattedData),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("user details add response - ", data);
              storeUser(data);
              forwardStep();
            });
        } catch (error) {
          console.error("Error adding user details:", error);
        } finally {
        }
      } else {
        if (configData.JSON_DB === false) {
          try {
            fetch(`${configData.API_URL}/${urlSegment}/${formattedData.id}`, {
              method: "PUT",
              body: JSON.stringify(formattedData),
              headers: { "Content-type": "application/json; charset=UTF-8" },
            })
              .then((res) => res.json())
              .then((data) => {
                console.log("user details modify response - ", data);
                showInfoModal();
              });
          } catch (error) {
            console.error("Error modifying user details:", error);
          } finally {
          }
        } else {
          try {
            fetch(`${configData.API_URL}/${urlSegment}/${user.id}`, {
              method: "PUT",
              body: JSON.stringify(formattedData),
              headers: { "Content-type": "application/json; charset=UTF-8" },
            })
              .then((res) => res.json())
              .then((data) => {
                console.log("user details modify response - ", data);
                showInfoModal();
              });
          } catch (error) {
            console.error("Error modifying user details:", error);
          } finally {
          }
        }
      }
    }
  };

  return (
    <>
      <div className="registration-sidebar">
        <div className="box card registration-steps-container">
          <Steps
            step={1}
            isNewUser={isNewUser}
            stepItems={stepItems}
            changeStep={changeStep}
          />
        </div>
        <div className="user-details-container" style={{ width: "100%" }}>
          <div className="box card">
            <div>
              <h6 className="box-title">User details</h6>
              <hr />
            </div>
            <form onSubmit={handleSubmit(registerUser)}>
              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">First name</label>
                </div>
                <div className="user-details-input-cell">
                  <div className="input-group input-group-sm">
                    <input
                      type="text"
                      className="form-control"
                      {...register("first_name", { required: true })}
                    ></input>
                  </div>

                  <div className="input-error">
                    {errors.first_name && <span>Required</span>}
                  </div>
                </div>
              </div>
              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">Middle name</label>
                </div>
                <div className="user-details-input-cell">
                  <div className="input-group input-group-sm">
                    <input
                      type="text"
                      className="form-control"
                      {...register("middle_name", { required: false })}
                    ></input>
                  </div>

                  <div className="input-error">
                    {errors.middle_name && <span>Required</span>}
                  </div>
                </div>
              </div>
              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">Last name</label>
                </div>
                <div className="user-details-input-cell">
                  <div className="input-group input-group-sm">
                    <input
                      type="text"
                      className="form-control"
                      {...register("last_name", { required: true })}
                    ></input>
                  </div>

                  <div className="input-error">
                    {errors.last_name && <span>Required</span>}
                  </div>
                </div>
              </div>
              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">Mobile</label>
                </div>
                <div className="user-details-input-cell">
                  <div className="input-group input-group-sm">
                    <input
                      type="text"
                      className="form-control"
                      {...register("mobile", { required: true })}
                    ></input>
                  </div>

                  <div className="input-error">
                    {errors.mobile && <span>Required</span>}
                  </div>
                </div>
              </div>
              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">Email</label>
                </div>
                <div className="user-details-input-cell">
                  <div className="input-group input-group-sm">
                    <input
                      type="text"
                      className="form-control"
                      {...register("email", {
                        required: true,
                        pattern: {
                          value:
                            /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/,
                          message: "Invalid email address",
                        },
                      })}
                    ></input>
                  </div>

                  <div className="input-error">
                    {errors.email && errors.email.type === "required" && (
                      <span>Required</span>
                    )}
                    {errors.email &&
                      errors.email.type === "pattern" &&
                      errors.email.message && (
                        <span>{errors.email.message}</span>
                      )}
                  </div>
                </div>
              </div>
              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">Address</label>
                </div>
                <div className="user-details-input-cell">
                  <div className="input-group input-group-sm">
                    <textarea
                      rows="4"
                      className="form-control textarea"
                      {...register("address", { required: false })}
                    ></textarea>
                  </div>

                  <div className="input-error">
                    {errors.address && <span>Required</span>}
                  </div>
                </div>
              </div>
              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">Date of birth</label>
                </div>
                <div className="user-details-input-cell">
                  <div className="input-group input-group-sm">
                    <input
                      type="date"
                      className="form-control"
                      {...register("dateofbirth", { required: false })}
                    ></input>
                  </div>

                  <div className="input-error">
                    {errors.dateofbirth && <span>Required</span>}
                  </div>
                </div>
              </div>

              {isNewUser && (
                <>
                  <div className="user-details-input">
                    <div className="label">
                      <label className="field-label">Username</label>
                    </div>
                    <div className="user-details-input-cell">
                      <div className="input-group input-group-sm">
                        <input
                          type="text"
                          className="form-control"
                          {...register("username", { required: true })}
                        ></input>
                      </div>

                      <div className="input-error">
                        {errors.username && <span>Required</span>}
                      </div>
                    </div>
                  </div>
                  <div className="user-details-input">
                    <div className="label">
                      <label className="field-label">Password</label>
                    </div>
                    <div className="user-details-input-cell">
                      <div className="input-group input-group-sm">
                        <input
                          type="password"
                          className="form-control"
                          {...register("password", { required: true })}
                        ></input>
                      </div>

                      <div className="input-error">
                        {errors.password && <span>Required</span>}
                      </div>
                    </div>
                  </div>

                  <div className="user-details-input">
                    <div className="label">
                      <label className="field-label">Confirm Password</label>
                    </div>
                    <div className="user-details-input-cell">
                      <div className="input-group input-group-sm">
                        <input
                          id="confirm-password"
                          name="confirm-password"
                          type="password"
                          className="form-control"
                          value={confirmPassword}
                          onChange={confirmPasswordChanged}
                        ></input>
                      </div>
                    </div>
                  </div>
                </>
              )}

              <div className="user-details-input">
                <div className="label">
                  <label className="field-label">Risk profile</label>
                </div>
                <div className="user-details-input-cell">
                  <div>
                    <select
                      {...register("risk_profile", { required: true })}
                      className="form-select form-select-sm"
                    >
                      <option value="1">1</option>
                      <option value="2">2</option>
                      <option value="3">3</option>
                      <option value="4">4</option>
                      <option value="5">5</option>
                    </select>
                  </div>
                  <div className="input-error">
                    {errors.risk_profile && <span>Required</span>}
                  </div>
                </div>
              </div>

              <div className="register-button-row">
                <button className="btn theme_button" type="submit">
                  {isNewUser ? (
                    <span>Save and Continue</span>
                  ) : (
                    <span>Update</span>
                  )}
                </button>
              </div>

              <div className="register-error">
                <ul>
                  {errorList.map((error) => {
                    return <li>{error.message}</li>;
                  })}
                </ul>
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
                  User Details Updated Successfully
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

export default UserDetails;
