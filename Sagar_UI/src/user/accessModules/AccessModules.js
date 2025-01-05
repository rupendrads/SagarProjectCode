import { useEffect, useRef, useState } from "react";
import { Modal } from "bootstrap";
import "./AccessModules.css";
import Steps from "../steps/Steps";
import configData from "../../config.json";

const AccessModules = (props) => {
  const { userId, isNewUser, forwardStep, stepItems, changeStep } = props;
  console.log("userId", userId);
  const [modules, setModules] = useState(undefined);
  const refInfoModal = useRef(null);

  useEffect(() => {
    let urlSegment = "modules";

    if (configData.JSON_DB === false) {
      urlSegment = "getAllModules";
    }

    try {
      fetch(`${configData.API_URL}/${urlSegment}`, {
        method: "GET",
        headers: { "Content-type": "application/json; charset=UTF-8" },
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("modules response - ", data);

          ////////////////////
          if (!isNewUser) {
            let urlAccessSegment = "userAccessModules";

            if (configData.JSON_DB === false) {
              urlAccessSegment = "getUserAccessModules";
              try {
                fetch(`${configData.API_URL}/${urlAccessSegment}/${userId}`, {
                  method: "GET",
                  headers: {
                    "Content-type": "application/json; charset=UTF-8",
                  },
                })
                  .then((res) => res.json())
                  .then((uadata) => {
                    console.log("user access modules response - ", uadata);
                    console.log("userId", userId);

                    setModules(() => {
                      const formattedData = [];
                      for (var i = 0; i < data.length; i++) {
                        formattedData.push({
                          id: data[i].id,
                          name: data[i].name,
                          enabled: i < 2 ? true : false,
                        });
                      }
                      for (var i = 0; i < formattedData.length; i++) {
                        formattedData[i].id = uadata[i].id;
                        formattedData[i]["module_id"] = uadata[i].module_id;
                        formattedData[i].enabled = uadata[i].enabled;
                      }
                      console.log("formattedData", formattedData);
                      return formattedData;
                    });
                  });
              } catch (error) {
                console.error(
                  "Error receiving user access modules by user id:",
                  error
                );
              } finally {
              }
            } else {
              try {
                fetch(`${configData.API_URL}/${urlAccessSegment}`, {
                  method: "GET",
                  headers: {
                    "Content-type": "application/json; charset=UTF-8",
                  },
                })
                  .then((res) => res.json())
                  .then((uadata) => {
                    console.log("user access modules response - ", uadata);
                    console.log("userId", userId);
                    const userAccessModulesData = uadata.filter(
                      (ua) => ua.user_id === userId
                    );

                    console.log("userAccessModulesData", userAccessModulesData);

                    setModules(() => {
                      const formattedData = [];
                      for (var i = 0; i < data.length; i++) {
                        formattedData.push({
                          id: data[i].id,
                          name: data[i].name,
                          enabled: i < 2 ? true : false,
                        });
                      }
                      for (var i = 0; i < formattedData.length; i++) {
                        const uaItemIndex = userAccessModulesData.findIndex(
                          (ua) => ua.module_id === formattedData[i].id
                        );
                        if (uaItemIndex > -1) {
                          formattedData[i].id =
                            userAccessModulesData[uaItemIndex].id;
                          formattedData[i]["module_id"] =
                            userAccessModulesData[uaItemIndex].module_id;
                          formattedData[i].enabled =
                            userAccessModulesData[uaItemIndex].enabled;
                        }
                      }
                      console.log("formattedData", formattedData);
                      return formattedData;
                    });
                  });
              } catch (error) {
                console.error(
                  "Error receiving user access modules by user id:",
                  error
                );
              } finally {
              }
            }
          } else {
            setModules(() => {
              const formattedData = [];
              for (var i = 0; i < data.length; i++) {
                formattedData.push({
                  id: data[i].id,
                  name: data[i].name,
                  enabled: i < 2 ? true : false,
                });
              }
              return formattedData;
            });
          }
          /////////////////////
        });
    } catch (error) {
      console.error("Error receiving modules:", error);
    } finally {
    }

    //     id: "1",
    //     name: "profile",
    //     enabled: true,
    //   },
    //   {
    //     id: "2",
    //     name: "pnl",
    //     enabled: true,
    //   },
    //   {
    //     id: "3",
    //     name: "strategy builder",
    //     enabled: false,
    //   },
    //   {
    //     id: "4",
    //     name: "backtesting",
    //     enabled: false,
    //   },
    //   {
    //     id: "5",
    //     name: "portfolio builder",
    //     enabled: false,
    //   },
    //   {
    //     id: "6",
    //     name: "live deployment",
    //     enabled: false,
    //   },
    //   {
    //     id: "7",
    //     name: "forward testing",
    //     enabled: false,
    //   },
    // ]);
  }, []);

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

  const moduleAccessChanged = (e, index) => {
    console.log(e.target.name);
    console.log(e.target.checked);
    setModules((prevModules) => {
      const updatedModules = [...prevModules];
      updatedModules[index].enabled = e.target.checked;
      console.log(updatedModules);
      return updatedModules;
    });
  };

  const saveAccessModules = () => {
    console.log("modules", modules);

    const userAccessModules = [];
    if (isNewUser) {
      for (var i = 0; i < modules.length; i++) {
        userAccessModules.push({
          user_id: userId,
          module_id: modules[i].id,
          enabled: modules[i].enabled,
        });
      }
    } else {
      for (var j = 0; j < modules.length; j++) {
        if (modules[j].module_id) {
          userAccessModules.push({
            id: modules[j].id,
            user_id: userId,
            module_id: modules[j].module_id,
            enabled: modules[j].enabled,
          });
        } else {
          userAccessModules.push({
            user_id: userId,
            module_id: modules[j].id,
            enabled: modules[j].enabled,
          });
        }
      }
    }

    console.log("userAccessModules", userAccessModules);

    if (configData.JSON_DB === false) {
      if (isNewUser) {
        try {
          fetch(`${configData.API_URL}/addUserAccessModules`, {
            method: "POST",
            body: JSON.stringify(userAccessModules),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("userAccessModules response - ", data);
              forwardStep();
            });
        } catch (error) {
          console.error("Error userAccessModules:", error);
        } finally {
        }
      } else {
        try {
          fetch(`${configData.API_URL}/editUserAccessModules`, {
            method: "PUT",
            body: JSON.stringify(userAccessModules),
            headers: {
              "Content-type": "application/json; charset=UTF-8",
            },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("userAccessModules edit response - ", data);
              showInfoModal();
            });
        } catch (error) {
          console.error("Error userAccessModules edit:", error);
        } finally {
        }
      }
    } else {
      for (var i = 0; i < userAccessModules.length; i++) {
        if (isNewUser) {
          try {
            fetch(`${configData.API_URL}/userAccessModules`, {
              method: "POST",
              body: JSON.stringify(userAccessModules[i]),
              headers: { "Content-type": "application/json; charset=UTF-8" },
            })
              .then((res) => res.json())
              .then((data) => {
                console.log("userAccessModules response - ", data);
              });
          } catch (error) {
            console.error("Error userAccessModules:", error);
          } finally {
          }
        } else {
          if (userAccessModules[i].id) {
            try {
              fetch(
                `${configData.API_URL}/userAccessModules/${userAccessModules[i].id}`,
                {
                  method: "PUT",
                  body: JSON.stringify(userAccessModules[i]),
                  headers: {
                    "Content-type": "application/json; charset=UTF-8",
                  },
                }
              )
                .then((res) => res.json())
                .then((data) => {
                  console.log("userAccessModules edit response - ", data);
                });
            } catch (error) {
              console.error("Error userAccessModules edit:", error);
            } finally {
            }
          } else {
            try {
              fetch(`${configData.API_URL}/userAccessModules`, {
                method: "POST",
                body: JSON.stringify(userAccessModules[i]),
                headers: { "Content-type": "application/json; charset=UTF-8" },
              })
                .then((res) => res.json())
                .then((data) => {
                  console.log("userAccessModules response - ", data);
                });
            } catch (error) {
              console.error("Error userAccessModules:", error);
            } finally {
            }
          }
        }
      }
      if (isNewUser) {
        forwardStep();
      } else {
        showInfoModal();
      }
    }
  };

  return (
    <>
      <div className="registration-sidebar">
        <div className="box card registration-steps-container">
          <Steps
            step={3}
            stepItems={stepItems}
            isNewUser={isNewUser}
            changeStep={changeStep}
          />
        </div>
        <div className="am-container" style={{ width: "100%" }}>
          <div className="box card">
            <div>
              <h6 className="box-title">Access Modules</h6>
              <hr />
            </div>
            <form>
              <div className="am-input">
                <div className="modules-checkboxes">
                  {modules &&
                    modules.map((module, index) => {
                      return (
                        <div className="module-checkbox">
                          <input
                            type="checkbox"
                            className="form-check-input checkbox-lg"
                            name={module.name}
                            id={module.name}
                            autocomplete="off"
                            checked={module.enabled == true}
                            value={module.enabled}
                            onChange={(e) => moduleAccessChanged(e, index)}
                          />
                          <label className="field-label" for={module.name}>
                            {module?.name?.charAt(0).toUpperCase() +
                              module?.name?.slice(1)}
                          </label>
                        </div>
                      );
                    })}
                </div>
              </div>
              <div className="am-button-row">
                <button
                  className="btn theme_button"
                  type="button"
                  onClick={saveAccessModules}
                >
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
                  User Access Moduels Updated Successfully
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

export default AccessModules;
