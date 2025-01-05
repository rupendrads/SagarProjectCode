import { useState } from "react";
import "./DataVerification.css";
import configData from "../../config.json";
import { useForm } from "react-hook-form";

const DataVerification = () => {
  const [validationResult, setValidationResult] = useState(null);
  const [error, setError] = useState("");
  const [missingFiles, setMissingFiles] = useState([]);
  const [dateRange, setDateRange] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm();

  const ValidateData = async (data) => {
    console.log(data);
    setError("");
    setValidationResult(null);
    setMissingFiles([]);
    setDateRange("");

    let validationResult = undefined;
    try {
      if (configData.JSON_DB === true) {
        // local json call start
        validationResult = {
          status: true,
          missing_dates: ["2020-06-30", "2020-02-24", "2022-08-04"],
          error: null,
          date_range: "2020-04-07 to 2023-12-29",
        };
        // const validationResult = {
        //   status: false,
        //   missing_dates: [],
        //   error:
        //     "Database connection failed: 1049 (42000): Unknown database 'index_daxta'",
        //   date_range: null,
        // };

        // const validationResult = {
        //   status: false,
        //   missing_dates: [],
        //   error:
        //     "Database connection failed: 1045 (28000): Access denied for user 'rootX'@'localhost' (using password: YES)",
        //   date_range: null,
        // };

        // local json call end
      } else {
        // api call start
        const response = await fetch(
          `${configData.DATA_UPLOAD_API_URL}/tradingdaysvalidator?db_host=${data.host}&db_name=${data.database}&db_user=${data.user}&db_password=${data.password}`,
          {
            method: "GET",
          }
        );
        validationResult = await response.json();
        console.log("Validate response", validationResult);
        // api call end
      }

      if (validationResult && validationResult.status === true) {
        setValidationResult(validationResult);
        setDateRange(validationResult.date_range || "");

        if (validationResult.missing_dates.length > 0) {
          const files = validationResult.missing_dates.map((date) => {
            const [year, month, day] = date.split("-");
            return `GFDLNFO_BACKADJUSTED_${day}${month}${year}.csv`;
          });
          setMissingFiles(files);
        }
      } else {
        setError(`Validation failed: ${validationResult.error}`);
      }
    } catch (error) {
      setError(
        "Failed to upload the configuration or validate the trading days."
      );
    }
  };

  return (
    <div className="gdfl-data-verification-container">
      <div>
        <div className="cell">
          <h6 className="box-title">GDFL Data Verification</h6>
        </div>
        <hr />
        <form onSubmit={handleSubmit(ValidateData)}>
          <div className="data-verification-input">
            <div className="label">
              <label className="field-label">Host</label>
            </div>
            <div className="data-verification-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("host", { required: true })}
                ></input>
              </div>

              <div className="input-error">
                {errors.host && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="data-verification-input">
            <div className="label">
              <label className="field-label">User</label>
            </div>
            <div className="data-verification-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("user", { required: true })}
                ></input>
              </div>
              <div className="input-error">
                {errors.user && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="data-verification-input">
            <div className="label">
              <label className="field-label">Password</label>
            </div>
            <div className="data-verification-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("password", { required: true })}
                ></input>
              </div>
              <div className="input-error">
                {errors.password && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="data-verification-input">
            <div className="label">
              <label className="field-label">Database</label>
            </div>
            <div className="data-verification-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("database", { required: true })}
                ></input>
              </div>
              <div className="input-error">
                {errors.database && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="validate-button-row">
            <button className="btn theme_button" type="submit">
              Validate
            </button>
          </div>
        </form>
      </div>
      <div>
        {error && <div className="validation-result-error">{error}</div>}
        {validationResult && (
          <div className="validation-result">
            <div className="validation-result-header">
              <h6 className="box-title">Validation Result</h6>
            </div>
            <hr />
            {dateRange && (
              <div>
                <label className="field-label">Date Range:</label>{" "}
                <span className="font-bold">{dateRange}</span>
              </div>
            )}
            {missingFiles.length > 0 ? (
              <>
                <label className="field-label">Missing Files:</label>
                <div className="missing-file-list">
                  {missingFiles.map((file, index) => (
                    <div key={index} className="missing-file">
                      <div>
                        <label className="field-label">{index + 1}. </label>
                      </div>
                      <div>
                        <label>{file}</label>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-gray-700 text-lg">
                There are no missing files.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataVerification;
