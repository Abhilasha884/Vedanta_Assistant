
import React from "react";
import {
    BrowserRouter,
    Routes,
    Route,
    Link,
    Navigate
} from "react-router-dom";

import Chat from "./Pages/Chat";
import Explore from "./Pages/Explore";

import "./App.css";

function App() {
    return (
        <BrowserRouter>
            <div className="App">

                {/* Navigation Bar */}
                <nav className="navbar">
                    <h2>Vedanta Assistant</h2>

                    <div className="nav-links">
                        <Link to="/">Chat</Link>
                        <Link to="/explore">Explore Topics</Link>
                    </div>
                </nav>

                {/* Application Pages */}
                <Routes>
                    <Route path="/" element={<Chat />} />
                    <Route path="/explore" element={<Explore />} />
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>

            </div>
        </BrowserRouter>
    );
}

export default App;
