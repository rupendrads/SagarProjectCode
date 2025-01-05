import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import "./Registration.css";
import Billing from "../billing/Billing";
import Brokers from "../brokers/Brokers";
import UserDetails from "../userDetails/UserDetails";
import AccessModules from "../accessModules/AccessModules";

const Registration = (props) => {
  const {
    isNewUser,
    user,
    storeUser,
    step,
    forwardStep,
    stepItems,
    changeStep,
  } = props;
  console.log(isNewUser);

  return (
    <div className="register-container" style={{ width: "100%" }}>
      {isNewUser && (
        <div className="box card">
          <div>
            <h6 className="box-title">Register new user</h6>
            <hr />
          </div>
          {step === 1 && (
            <UserDetails
              user={user}
              isNewUser={isNewUser}
              forwardStep={forwardStep}
              storeUser={storeUser}
              stepItems={stepItems}
            />
          )}
          {step === 2 && (
            <Billing
              userId={user?.id}
              isNewUser={isNewUser}
              forwardStep={forwardStep}
              stepItems={stepItems}
            />
          )}
          {step === 3 && (
            <AccessModules
              userId={user?.id}
              isNewUser={isNewUser}
              forwardStep={forwardStep}
              stepItems={stepItems}
            />
          )}
          {step === 4 && (
            <Brokers
              userId={user?.id}
              isNewUser={isNewUser}
              forwardStep={forwardStep}
              stepItems={stepItems}
            />
          )}
        </div>
      )}
      {!isNewUser && (
        <div className="box card">
          <div>
            <h6 className="box-title">Edit existing user</h6>
            <hr />
          </div>
          {step === 1 && (
            <UserDetails
              user={user}
              isNewUser={isNewUser}
              storeUser={storeUser}
              stepItems={stepItems}
              changeStep={changeStep}
            />
          )}
          {step === 2 && (
            <Billing
              userId={user.id}
              isNewUser={isNewUser}
              forwardStep={forwardStep}
              stepItems={stepItems}
              changeStep={changeStep}
            />
          )}
          {step === 3 && (
            <AccessModules
              userId={user.id}
              isNewUser={isNewUser}
              forwardStep={forwardStep}
              stepItems={stepItems}
              changeStep={changeStep}
            />
          )}
          {step === 4 && (
            <Brokers
              userId={user.id}
              isNewUser={isNewUser}
              forwardStep={forwardStep}
              stepItems={stepItems}
              changeStep={changeStep}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default Registration;
