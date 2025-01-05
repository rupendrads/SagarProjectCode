import "./ImpliedFuture.css";
import { useForm } from "react-hook-form";
import configData from "../../config.json";
import { useState } from "react";

const ImpliedFuture = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const [uploadResult, setUploadResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const uploadData = async (data) => {
    console.log(data);
    setIsProcessing(true);

    try {
      const response = await fetch(
        `${configData.DATA_UPLOAD_API_URL}/upload/impliedfutures`,
        {
          method: "POST",
          body: JSON.stringify(data),
          headers: { "Content-type": "application/json; charset=UTF-8" },
        }
      );

      const result = await response.json();
      console.log("Result", result);
      setUploadResult(result);
    } catch (error) {
      console.error("Error uploading implied future:", error);
      setUploadResult({ Status: "error" });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="implied-future-container">
      <div>
        <div className="cell">
          <h6 className="box-title">Implied Future</h6>
        </div>
        <hr />
      </div>
      <form onSubmit={handleSubmit(uploadData)}>
        <div className="implied-future-input">
          <div className="label">
            <label className="field-label">Index</label>
          </div>
          <div className="implied-future-input-cell">
            <div>
              <select
                {...register("instrument_name", { required: true })}
                className="form-select form-select-sm"
              >
                <option value="nifty">Nifty</option>
                <option value="banknifty">Banknifty</option>
                <option value="finnifty">Finnifty</option>
              </select>
            </div>
            <div className="input-error">
              {errors.instrument_name && <span>Required</span>}
            </div>
          </div>
        </div>
        <div className="implied-future-input">
          <div className="label">
            <label className="field-label">Start date</label>
          </div>
          <div className="implied-future-input-cell">
            <div className="input-group input-group-sm">
              <input
                type="date"
                {...register("start_date", { required: true })}
                className="form-control"
              ></input>
            </div>
            <div className="input-error">
              {errors.start_date && <span>Required</span>}
            </div>
          </div>
        </div>
        <div className="implied-future-input">
          <div className="label">
            <label className="field-label">End date</label>
          </div>
          <div className="implied-future-input-cell">
            <div className="input-group input-group-sm">
              <input
                type="date"
                {...register("end_date", { required: true })}
                className="form-control"
              ></input>
            </div>
            <div className="input-error">
              {errors.end_date && <span>Required</span>}
            </div>
          </div>
        </div>
        <div className="implied-future-input">
          <div className="label">
            <label className="field-label">Strike Diff</label>
          </div>
          <div className="implied-future-input-cell">
            <div className="input-group input-group-sm">
              <input
                type="text"
                className="form-control"
                {...register("strike_difference", { required: true })}
              ></input>
            </div>
            <div className="input-error">
              {errors.strike_difference && <span>Required</span>}
            </div>
          </div>
        </div>
        <div className="implied-future-upload-button-row">
          <button
            className="btn theme_button"
            type="submit"
            disabled={isProcessing === true}
          >
            {isProcessing ? (
              <>
                <span
                  className="spinner-border spinner-border-sm"
                  role="status"
                  aria-hidden="true"
                ></span>
                &nbsp;&nbsp;<span>Processing...</span>
              </>
            ) : (
              <span>Upload</span>
            )}
          </button>
        </div>
      </form>
      <div className="upload-implied-future-result">
        {uploadResult && (
          <div>
            <h6
              className={`box-title ${
                uploadResult.Status === "error" && "upload-implied-future-error"
              } `}
            >
              Upload {uploadResult.Status === "success" ? "Success" : "Failed"}
            </h6>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImpliedFuture;
