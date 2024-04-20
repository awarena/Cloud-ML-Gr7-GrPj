import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css'; // Ensure CSS is correctly linked
import { useAuth } from '../../AuthContext'; // Adjust path as necessary

const Navbar = () => {
    const { currentUser, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/logout'); // Assuming you handle the redirection to a logout or home page
    };

    // Specify your logo source here
    const logoSrc = '/path/to/your/logo.png';

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <img src={logoSrc} alt="emoSense Logo" className="logo"/>
                <span>emoSense</span>
            </div>
            <div className="navbar-links">
                <Link to="/test" className="nav-link">Detect Emotion</Link>
                <Link to="/signup" className="nav-link">Register</Link>
                {currentUser ? (
                    <a href="/login" onClick={handleLogout} className="nav-link">Logout</a> // Using an <a> tag for demonstration; replace with <Link> if needed
                ) : (
                    <Link to="/login" className="nav-link">Login</Link>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
