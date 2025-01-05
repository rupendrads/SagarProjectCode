import { useEffect, useState } from "react";
import configData from "../../config.json";
import "./Upload.css";

const Upload = () => {
  const [files, setFiles] = useState([]);
  const [forceUpload, setForceUpload] = useState(false);
  const [createIndices, setCreateIndices] = useState(false);
  const [progressValue, setProgressValue] = useState(0);
  const [currentFile, setCurrentFile] = useState(undefined);
  const [incrementor, setIncrementor] = useState(0);
  const [basePath, setBasePath] = useState("C:/");
  const [isDeletingIndices, setIsDeletingIndices] = useState(false);
  const [isCreateIndices, setIsCreateIndices] = useState(false);

  useEffect(() => {
    if (currentFile !== undefined && incrementor > 0) {
      console.log(currentFile.srno);
      if (configData.JSON_DB === true) {
        setTimeout(() => {
          setProgressValue((prevValue) => {
            setCurrentFile(files[currentFile.srno]);
            const newFiles = [...files];
            if (currentFile.srno % 3 === 0) {
              newFiles[currentFile.srno - 1].isUploaded = false;
              newFiles[currentFile.srno - 1].details =
                "Here are file details Here are file details Here are file details Here are file details Here are file detailsHere are file details Here are file details Here are file details";
            } else {
              newFiles[currentFile.srno - 1].isUploaded = true;
              newFiles[currentFile.srno - 1].details =
                "Here are file details Here are file details";
            }

            setFiles(newFiles);
            return prevValue + incrementor;
          });
        }, 2000);
      } else {
        try {
          const filePath = basePath + currentFile.file.webkitRelativePath;
          console.log("filePath", filePath);
          fetch(`${configData.DATA_UPLOAD_API_URL}/processdata`, {
            method: "POST",
            body: JSON.stringify({
              filePath: filePath,
              force_upload: { forceUpload },
            }),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => {
              console.log("res", res);
              return res.json();
            })
            .then((data) => {
              console.log("data", data);
              setProgressValue((prevValue) => {
                setCurrentFile(files[currentFile.srno]);
                const newFiles = [...files];
                newFiles[currentFile.srno - 1].isUploaded =
                  data.Status === "success" ? true : false;
                newFiles[currentFile.srno - 1].details = data.Details;
                setFiles(newFiles);
                return prevValue + incrementor;
              });
            })
            .catch((error) => console.error("Error uploading gdfl:", error));
        } catch (error) {
          console.error("Error uploading gdfl:", error);
        }
      }
    }
    console.log("currentFile", currentFile);
    console.log("incrementor", incrementor);
    console.log("files count", files.length);
    if (
      currentFile === undefined &&
      incrementor > 0 &&
      createIndices === true
    ) {
      createIndice();
    }
  }, [currentFile, files, incrementor, basePath, forceUpload]);

  const onSelectFolder = (event) => {
    event.preventDefault();
    const files = event.target.files;

    const selectedFiles = [];
    for (var i = 0; i < files.length; i++) {
      const file = files.item(i);
      if (file.webkitRelativePath.toString().split("/").length === 2) {
        selectedFiles.push({
          srno: i + 1,
          file: file,
          isUploaded: undefined,
          details: "",
        });
      }
    }
    setFiles(selectedFiles);
    console.log(selectedFiles);
  };

  const deleteIndices = () => {
    let fileNames = [];
    for (var i = 0; i < files.length; i++) {
      console.log(files[i].file.name);
      fileNames.push(files[i].file.name);
    }
    const filenames = {
      filenames: [...fileNames],
    };
    console.log(JSON.stringify(filenames));

    if (configData.JSON_DB === true) {
      setIsDeletingIndices(true);
      setTimeout(() => {
        console.log("calling delete indices api");
        setIsDeletingIndices(false);
        uploadFiles();
      }, 2000);
    } else {
      setIsDeletingIndices(true);
      try {
        fetch(`${configData.DATA_UPLOAD_API_URL}/delete-indices`, {
          method: "DELETE",
          body: JSON.stringify(filenames),
          headers: { "Content-type": "application/json; charset=UTF-8" },
        })
          .then((res) => {
            console.log("res", res);
            return res.json();
          })
          .then((result) => {
            console.log("result", result);
            if (result.status === "success") {
              uploadFiles();
            } else {
              alert("Error occured while uploading gdfl");
            }
          })
          .catch((error) => console.error("Error uploading gdfl:", error));
      } catch (error) {
        console.error("Error uploading gdfl:", error);
      } finally {
        setIsDeletingIndices(false);
      }
    }
  };

  const uploadFiles = () => {
    const filesCount = files.length;
    const incrementor = 100 / filesCount;
    console.log(incrementor);
    setIncrementor(incrementor);

    setCurrentFile({ ...files[0] });
  };

  const createIndice = () => {
    if (configData.JSON_DB === true) {
      setIsCreateIndices(true);
      console.log("calling create indices api");
      setTimeout(() => {
        setIsCreateIndices(false);
      }, 2000);
    } else {
      setIsCreateIndices(true);
      console.log("calling create indices api");
      try {
        fetch(`${configData.DATA_UPLOAD_API_URL}/create-indices`, {
          method: "POST",
          headers: { "Content-type": "application/json; charset=UTF-8" },
        })
          .then((res) => {
            console.log("res", res);
            return res.json();
          })
          .then((result) => {
            console.log("result", result);
            if (result.status !== "success") {
              alert("Error occured while creating indices");
            }
          })
          .catch((error) => console.error("Error creating indices", error));
      } catch (error) {
        console.error("Error creating indices", error);
      } finally {
        setIsCreateIndices(false);
      }
    }
  };

  const basePathChanged = (e) => {
    setBasePath(e.target.value);
  };

  const forceUploadChanged = () => {
    setForceUpload(!forceUpload);
  };

  const createIndicesChanged = () => {
    setCreateIndices(!createIndices);
  };

  return (
    <div className="gdfl-upload-container">
      <div className="cell">
        <h6 className="box-title">Upload GDFL</h6>
      </div>
      <hr />
      <div className="base-path-wrapper">
        <div className="cell">
          <label className="field-label">Base Path</label>
        </div>
        <div className="cell base-path-input-text-cell">
          <div className="input-group input-group-sm">
            <input
              type="text"
              className="form-control"
              id="base-path"
              name="base-path"
              value={basePath}
              onChange={basePathChanged}
            ></input>
          </div>
        </div>
      </div>

      <div className="force-upload-wrapper">
        <div>
          <div className="cell">
            <label className="field-label">Force Upload</label>
          </div>
          <div className="cell">
            <input
              type="checkbox"
              class="form-check-input"
              id="force_upload"
              name="force_upload"
              checked={forceUpload}
              onChange={forceUploadChanged}
            />
          </div>
        </div>
        <div>
          <div className="cell">
            <label className="field-label">Create Indices</label>
          </div>
          <div className="cell">
            <input
              type="checkbox"
              class="form-check-input"
              id="create_indices"
              name="create_indices"
              checked={createIndices}
              onChange={createIndicesChanged}
            />
          </div>
        </div>
      </div>

      <div className="cell">
        <input
          type="file"
          id="folder"
          directory=""
          webkitdirectory=""
          onChange={onSelectFolder}
          className="gdfl-file-input"
        />
        <button
          className="btn theme_button"
          onClick={deleteIndices}
          disabled={
            files.length === 0 ||
            currentFile !== undefined ||
            isDeletingIndices === true ||
            isCreateIndices === true
          }
        >
          Upload
        </button>
      </div>
      <hr />
      {currentFile && (
        <div className="file-counter">
          <div className="cell">
            <label>
              Uploading {currentFile.srno} of {files.length}
            </label>
          </div>
        </div>
      )}
      {(isDeletingIndices || isCreateIndices) && (
        <div className="file-counter">
          <div className="cell">
            <label>
              {isDeletingIndices === true
                ? "Preparing upload"
                : "Finishing upload"}
            </label>
          </div>
        </div>
      )}
      <div className="cell">
        <div class="progress">
          <div
            class="progress-bar bg-success"
            role="progressbar"
            style={{ width: progressValue.toString() + "%" }}
            aria-valuemin="0"
            aria-valuemax="100"
          ></div>
        </div>
      </div>
      {files.length > 0 && (
        <div className="cell">
          <div
            className="card-title"
            style={{ fontWeight: "600", marginBottom: "15px" }}
          >
            <label>Files ({files.length})</label>
          </div>
          <hr />
          {files.map((file) => {
            return (
              <>
                <div className="file-item">
                  <div className="upload-status-icon">
                    {file.isUploaded === true ? (
                      <i
                        class="bi bi-check-circle h6"
                        style={{ color: "green" }}
                      ></i>
                    ) : file.isUploaded === false ? (
                      <i class="bi bi-x-circle h6" style={{ color: "red" }}></i>
                    ) : (
                      <i class="bi bi-circle h6"></i>
                    )}
                  </div>
                  <div className="upload-file-name">
                    <label className="upload-file-name">
                      {file.file.webkitRelativePath}
                    </label>
                  </div>
                  <div className="upload-status">
                    <label
                      className={
                        file.isUploaded === false ? "upload-failed" : ""
                      }
                    >
                      {file.details}
                    </label>
                  </div>
                </div>
                <hr />
              </>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Upload;
