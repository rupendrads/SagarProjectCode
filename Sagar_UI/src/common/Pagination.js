import { forwardRef, useImperativeHandle, useState } from "react";
import "./Pagination.css";

export const Pagination = forwardRef(
  ({ postsPerPage, length, pageChanged, _refCurrentPage }) => {
    const [currentPage, setCurrentPage] = useState(1);
    const paginationNumbers = [];

    useImperativeHandle(_refCurrentPage, () => ({
      getCurrentPage: () => {
        return currentPage;
      },
    }));

    for (let i = 1; i <= Math.ceil(length / postsPerPage); i++) {
      paginationNumbers.push(i);
    }

    const getFirstPage = () => {
      setCurrentPage(1);
      const start = 0;
      const end = postsPerPage;
      pageChanged(start, end);
    };

    const getPreviousPage = () => {
      const start = (currentPage - 2) * postsPerPage;
      const end = start + postsPerPage;
      setCurrentPage(currentPage - 1);
      pageChanged(start, end);
    };

    const getNextPage = () => {
      const start = currentPage * postsPerPage;
      const end = start + postsPerPage;
      setCurrentPage(currentPage + 1);
      pageChanged(start, end);
    };

    const getLastPage = () => {
      setCurrentPage(paginationNumbers.length);
      const start = (paginationNumbers.length - 1) * postsPerPage;
      const end = length;
      pageChanged(start, end);
    };

    return (
      <div className="pagination">
        <nav class="prev-next">
          <ul class="pagination justify-content-end">
            <li
              class="page-item"
              onClick={getFirstPage}
              disabled={currentPage === 1}
            >
              <a class="page-link">First</a>
            </li>
            <li
              class="page-item"
              onClick={getPreviousPage}
              disabled={currentPage === 1}
            >
              <a class="page-link">Previous</a>
            </li>
            <li
              style={{
                minWidth: "80px",
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <label>Page</label>
              <label style={{ minWidth: "40px" }}>
                {currentPage} of {paginationNumbers.length}
              </label>
            </li>
            <li
              class="page-item"
              onClick={getNextPage}
              disabled={currentPage === paginationNumbers.length}
            >
              <a class="page-link">Next</a>
            </li>
            <li
              class="page-item"
              onClick={getLastPage}
              disabled={currentPage === paginationNumbers.length}
            >
              <a class="page-link">Last</a>
            </li>
          </ul>
        </nav>
      </div>
    );
  }
);
