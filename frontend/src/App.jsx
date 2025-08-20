import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from "./components/Sidebar/Sidebar.jsx";
import Main from "./components/Main/Main.jsx";
import TryOn from './components/TryOn/TryOn.jsx';
import VirtualTryOn from './VirtualTryOn.jsx';
import ProductsList from './productsList.jsx';
import './index.css';
import './index copy.css';

const App = () => {
    return (
        <BrowserRouter>
            <div className="app-container">
                <Sidebar />
                <div className="main-content">
                    <Routes>
                        <Route path="/" element={<Main />} />
                        <Route path="/try-on" element={<TryOn />} />
                        <Route path="/2dtry-on" element={<ProductsList />} />
                    </Routes>
                </div>
            </div>
        </BrowserRouter>
    );
};

export default App;