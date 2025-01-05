// import logo from "../logo.svg";
import logo from "../vecteezy_pegasus-silhouette-logo_6552390.jpg";
import "./Header.css";

const Header = () => {
  return (
    <header className="App-header">
      <nav
        class="navbar navbar-expand-lg navbar-dark bg-dark"
        style={{ fontSize: "16px" }}
      >
        <a class="navbar-brand" href="#" style={{ marginLeft: "10px" }}>
          <img src={logo} className="App-logo" alt="logo" />
        </a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item active">
              <a class="nav-link" href="/">
                Home
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/strategy">
                Strategy
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/portfolio">
                Portfolio
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/backtest">
                Backtest
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/optimization">
                Optimization
              </a>
            </li>

            <li class="nav-item dropdown">
              <a
                class="nav-link"
                href="#"
                id="navbarDropdownMenuLink"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                Upload
              </a>
              <ul
                class="dropdown-menu"
                aria-labelledby="navbarDropdownMenuLink"
              >
                <li>
                  <a class="dropdown-item" href="/upload/gdfl">
                    GDFL Upload
                  </a>
                </li>
                <li>
                  <a class="dropdown-item" href="/upload/gdfldataverification">
                    GDFL Data Verification
                  </a>
                </li>
                <li>
                  <a class="dropdown-item" href="/upload/impliedfuture">
                    Implied Future
                  </a>
                </li>
              </ul>
            </li>

            <li class="nav-item">
              <a class="nav-link" href="#">
                Livetest
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">
                Forwardtest
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">
                Broker setup
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">
                Broker setup
              </a>
            </li>
            <li class="nav-item dropdown">
              <a
                class="nav-link"
                href="#"
                id="navbarDropdownMenuLink"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                Admin
              </a>
              <ul
                class="dropdown-menu"
                aria-labelledby="navbarDropdownMenuLink"
              >
                <li>
                  <a class="dropdown-item" href="/users">
                    Users
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  );
};

export default Header;
