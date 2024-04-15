import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css'; // Make sure to create a corresponding CSS file for styling

const Navbar = () => {
    // Specify your logo source here
    const logoSrc = '/path/to/your/logo.png';

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <img src={logoSrc} alt="emoSense Logo" className="logo"/>
                <span>emoSense</span>
            </div>
            <div className="navbar-links">
                <Link to="/test" className="nav-link">Dashboard</Link>
                <Link to="/test" className="nav-link">Detect Emotion</Link>
                <Link to="/login" className="nav-link">Login</Link>
            </div>
        </nav>
    );
};

export default Navbar;
