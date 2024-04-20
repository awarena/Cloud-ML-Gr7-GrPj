import React, { useState, useRef } from 'react';
import Navbar from '../Layout/Navbar';
import Footer from '../Layout/Footer';

const serverUrl = "http://127.0.0.1:8000";

function Signup() {
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const uploadUserImage = async (storage) => {
        const file = fileInputRef.current.files[0];
        const reader = new FileReader();

        try {
            reader.readAsDataURL(file);
            const encodedString = await new Promise((resolve, reject) => {
                reader.onload = () => resolve(reader.result.replace(/^data:(.*,)?/, ''));
                reader.onerror = error => reject(error);
            });

            const response = await fetch(`${serverUrl}/images`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: file.name, filebytes: encodedString, storage: storage })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'Failed to upload image');
            return result;
        } catch (error) {
            setError(error.message);
            throw error;
        }
    };

    const createUser = async (image) => {
        try {
            const response = await fetch(`${serverUrl}/users`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ imageId: image.fileId })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'Failed to create user');
            return result;
        } catch (error) {
            setError(error.message);
            throw error;
        }
    };

    const handleRegister = async () => {
        try {
            const imageDetails = await uploadUserImage('contentcen301330426.aws.ai');
            await createUser(imageDetails);
            alert('User registered successfully!');
        } catch (error) {
            // Error is already set in state by previous functions
            alert("Registration failed: " + error);
        }
    };

    return (
        <div className='container'>
            <Navbar />
            <div className="login-container">
                <div className="login-form">
                    <h1 className="login-header">Sign Up</h1>
                    <input type="file" ref={fileInputRef} />
                    <button onClick={handleRegister}>Register</button>
                    {error && <p style={{ color: 'red' }}>{error}</p>}
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default Signup;
