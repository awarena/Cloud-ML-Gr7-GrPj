import React, { useState, useRef } from 'react';
import './Test.css';  // Assuming styles are defined in Test.css
import Navbar from '../Layout/Navbar'
import Footer from '../Layout/Footer'

const serverUrl = "http://127.0.0.1:8000";

function Test() {
    const [fileUrl, setFileUrl] = useState('');
    const [audioUrl, setAudioUrl] = useState('');
    const [fileId, setFileId] = useState('');
    const [emotionsText, setEmotionsText] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fileInputRef = useRef(null);
    const imageRef = useRef(null);
    const emotionsRef = useRef(null);

    const uploadImage = async (storage) => {
        const file = fileInputRef.current.files[0];
        if (!file) {
            setError("Please select a file first.");
            return;
        }
        setLoading(true);
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
            setFileId(result.fileId);
            setFileUrl(result.fileUrl);
            return result;
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleUploadAndDetect = async () => {
        setError(null); // Clear previous errors
        const imageDetails = await uploadImage('contentcen301232634.aws.ai');
        if (imageDetails) {
            updateImage(imageDetails);
            detectEmotion(imageDetails);
        }
    };

    const updateImage = (image) => {
        const { fileUrl, fileId } = image;
        if (imageRef.current) {
            imageRef.current.src = fileUrl;
            imageRef.current.alt = fileId;
        }
        setFileUrl(fileUrl);
        setFileId(fileId);
    };

    const detectEmotion = async (image) => {
        if (!image) return;
        setLoading(true);
        try {
            const response = await fetch(`${serverUrl}/images/${image.fileId}/detect-emotion`, {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fromLang: "auto",
                    toLang: "en"
                })
            });
            const emotions = await response.json();
            if (!response.ok) throw new Error(emotions.message || 'Failed to detect emotions');
            annotateImage(emotions);
            console.log(emotions)
            readEmotion(emotions[0], image.fileId);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const annotateImage = (emotions) => {
        const emotionElements = emotions.map(emotion => (
            <React.Fragment key={emotion}>
                <h6>{emotion}</h6>
                <hr />
            </React.Fragment>
        ));
        setEmotionsText(emotionElements);
    };

    const readEmotion = (emotionText, fileId) => {
        fetch(`${serverUrl}/images/${fileId}/read`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({text: emotionText})
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(response);
            }
        }).then(data => {
            console.log(data)
            setAudioUrl(data.fileUrl);
        });
    }
    return (
        <div>
            <Navbar />
            <div className="box">
                <div className="test-container">
                    <h1>Upload Image and Detect Emotions</h1>
                    <input type="file" ref={fileInputRef} />
                    <button onClick={handleUploadAndDetect} disabled={loading}>
                        {loading ? 'Processing...' : 'Upload and Detect'}
                    </button>
                    {error && <p className="error-message">{error}</p>}
                    <div className="results" style={{ display: fileUrl ? 'block' : 'none' }}>
                        <img ref={imageRef} alt="" />
                        <div ref={emotionsRef}>{emotionsText}</div>
                    </div>
                    {audioUrl && (
                    <div className="audio-control">
                        <audio controls>
                            <source src={audioUrl} type="audio/mpeg" />
                        </audio>
                    </div>
                )}
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default Test;
