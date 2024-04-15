import React, { useState, useRef } from 'react';
import Navbar from '../Layout/Navbar'
import Footer from '../Layout/Footer'
import './Login.css'; // Import the new CSS styles

const serverUrl = "http://127.0.0.1:8000";

function Login() {
    const [audioUrl, setAudioUrl] = useState('');
    const [welcomeMessage, setWelcomeMessage] = useState('');
    const [error, setError] = useState('');
    const fileInputAuthRef = useRef(null);

    const uploadAuthImage = async (storage) => {
        const file = fileInputAuthRef.current.files[0];
        if (!file) {
            setError("Please select a file to upload.");
            return;
        }
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
                body: JSON.stringify({ filename: file.name, filebytes: encodedString, storage })
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'Failed to upload image');
            return result;
        } catch (error) {
            setError(error.message);
            throw error;
        }
    };

    const authenticateUser = async (image) => {
        try {
            const response = await fetch(`${serverUrl}/users/authenticate`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ imageId: image.fileId })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'Authentication failed');
            console.log(result)
            readAuthResponse(result);
            return result;
        } catch (error) {
            setError(error.message);
            throw error;
        }
    };

    const readAuthResponse = (authResponse) => {
        if (authResponse.Message === 'Success') {
            const welcomeText = `Welcome ${authResponse.firstName} ${authResponse.lastName}!`;
            setWelcomeMessage(welcomeText);
            fetch(`${serverUrl}/users/${authResponse.rekognitionId}/read_auth`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({text: welcomeText})
            }).then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('HTTP error ' + response.status);
                }
            }).then(data => {
                console.log(data)
                // Set the audio URL from the response assuming it is returned in the data object
                setAudioUrl(data.fileUrl);
            });

        } else {
            setError("Authentication failed. Face was not recognized. Please register.");
        }
    };


    const handleAuthenticate = async () => {
        setError(''); // Clear previous errors
        setAudioUrl('');
        try {
            const imageDetails = await uploadAuthImage('contentcen301232634.aws.ai');
            if (imageDetails) {
                await authenticateUser(imageDetails);
            }
        } catch (error) {
            // Error is already set by previous functions
            console.error("Authentication failed:", error.message);
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
