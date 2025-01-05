import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import Header from "./header/Header";
import Footer from "./Footer/Footer";
import Strategy from "./strategy/Strategy";
import Portfolio from "./portfolio/Portfolio";
import BackTest from "./backtest/BackTest";
import Upload from "./Upload/gdfl/Upload";
import DataVerification from "./Upload/gdflDataVerification/DataVerification";
import ImpliedFuture from "./Upload/impliedFuture/ImpliedFuture";
import Optimization from "./optimization/Optimization";
//import Feed from "./feed/Feed";
import Registration from "./user/registration/Registration";
import Users from "./user/users/Users";

function App() {
  return (
    <Router>
      <div className="App container-fluid">
        <Header />
        <main className="main">
          <Routes>
            <Route exact path="/" element={<Strategy />} />
            <Route path="/strategy" element={<Strategy />} />
            {/* <Route path="/feed" element={<Feed />} /> */}
            <Route path="/strategy/:id" exact element={<Strategy />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/backtest" element={<BackTest />} />
            <Route path="/optimization" element={<Optimization />} />
            <Route path="/upload/gdfl" element={<Upload />} />
            <Route
              path="/upload/gdfldataverification"
              element={<DataVerification />}
            />
            <Route path="/upload/impliedfuture" element={<ImpliedFuture />} />
            <Route path="/user/register" element={<Registration />} />
            <Route path="/users" element={<Users />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
