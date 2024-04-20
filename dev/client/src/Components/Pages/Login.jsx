import React, { useState, useRef } from 'react';
import Navbar from '../Layout/Navbar';
import Footer from '../Layout/Footer';
import './Login.css';
import { useAuth } from '../../AuthContext';  // Make sure this path is correct

const serverUrl = "http://127.0.0.1:8000"; // Define serverUrl

function Login() {
    const { login } = useAuth(); // Destructure to get the login function from your context
    // const [username, setUsername] = useState('');
    // const [password, setPassword] = useState('');
    const [jwt, setJwt] = useState('');
    const [audioUrl, setAudioUrl] = useState('');
    const [welcomeMessage, setWelcomeMessage] = useState('');
    const [error, setError] = useState('');
    const fileInputAuthRef = useRef(null);

    const handleAuthenticate = async () => {
        setError('');
        setAudioUrl('');
        const file = fileInputAuthRef.current.files[0];
        if (!file) {
            setError("Please select a file to upload.");
            return;
        }
        const reader = new FileReader();
        reader.readAsDataURL(file);
        const encodedString = await new Promise((resolve, reject) => {
            reader.onload = () => resolve(reader.result.replace(/^data:(.*,)?/, ''));
            reader.onerror = error => reject(error);
        });
        try {
            const response = await fetch(`${serverUrl}/images`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: file.name, filebytes: encodedString, storage: 'contentcen301232634.aws.ai' })
            });
            const imageDetails = await response.json();
            if (!response.ok) throw new Error(imageDetails.message || 'Failed to upload image');

            const authResponse = await fetch(`${serverUrl}/users/authenticate`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ imageId: imageDetails.fileId })
            });
            const result = await authResponse.json();
            if (!authResponse.ok) throw new Error(result.message || 'Authentication failed');

            if (result.Message === 'Success') {
                const welcomeText = `Welcome ${result.firstName} ${result.lastName}!`;
                setWelcomeMessage(welcomeText);
                setJwt(result.token);
                login(result.token); // Correctly use the login function here
                const audioResponse = await fetch(`${serverUrl}/users/${result.rekognitionId}/read_auth`, {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({text: welcomeText})
                });
                const audioData = await audioResponse.json();
                if (!audioResponse.ok) throw new Error('HTTP error ' + audioResponse.status);
                setAudioUrl(audioData.fileUrl);
            } else {
                setError("Authentication failed. Face was not recognized. Please register.");
            }
        } catch (error) {
            console.error("Authentication failed:", error.message);
            setError(error.message);
        }
    };

    return (
        <div className='container'>
            <Navbar />
            <div className="login-container">
                <div className="login-form">
                    <h1 className="login-header">Login</h1>
                    <input type="file" className="input-file" ref={fileInputAuthRef} />
                    <button onClick={handleAuthenticate} className="login-button">
                        Authenticate
                    </button>
                    {audioUrl && (
                        <div className="audio-control">
                            <audio controls>
                                <source src={audioUrl} type="audio/mpeg" />
                            </audio>
                        </div>
                    )}
                    {welcomeMessage && <p>{welcomeMessage}</p>}
                    {error && <p className="error-message">{error}</p>}
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default Login;
