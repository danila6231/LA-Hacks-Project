import React, { useState, useRef, useEffect } from 'react';
import { Button, Box } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import axios from 'axios';
import { AUDIO_CHUNK_DURATION_MS, SNAP_USER_ID, LECTURE_ID} from '../config';
console.log(LECTURE_ID);

const Microphone: React.FC = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [lectureId, setLectureId] = useState<string | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const animationFrameRef = useRef<number | null>(null);
    const speakingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const silenceCounterRef = useRef<number>(0);
    const wsRef = useRef<WebSocket | null>(null);
    const shortIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const isRecordingRef = useRef(false);
    let counter = 0;

    // Add new ref for tracking connection status
    const isConnectingRef = useRef(false);
    const reconnectAttemptsRef = useRef(5);

    const checkAudioLevel = () => {
        if (!analyserRef.current) return;

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);

        // Calculate average volume
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;

        // Check if currently speaking based on volume threshold
        const currentlySpeaking = average > 20;

        if (currentlySpeaking) {
            silenceCounterRef.current = 0;
            setIsSpeaking(true);
            if (speakingTimeoutRef.current) {
                clearTimeout(speakingTimeoutRef.current);
                speakingTimeoutRef.current = null;
            }
        } else {
            silenceCounterRef.current++;
            if (silenceCounterRef.current >= 10) { // About 1 second of silence
                if (!speakingTimeoutRef.current) {
                    speakingTimeoutRef.current = setTimeout(() => {
                        setIsSpeaking(false);
                        speakingTimeoutRef.current = null;
                    }, 1000);
                }
            }
        }

        animationFrameRef.current = requestAnimationFrame(checkAudioLevel);
    };

    const createWavBlob = (audioData: Float32Array, sampleRate: number): Blob => {
        const numChannels = 1;
        const format = 1; // PCM
        const bitDepth = 16;

        const bytesPerSample = bitDepth / 8;
        const blockAlign = numChannels * bytesPerSample;

        const wavData = new Uint8Array(44 + audioData.length * 2);
        const view = new DataView(wavData.buffer);

        // Write WAV header
        view.setUint32(0, 0x46464952, true); // "RIFF"
        view.setUint32(4, 36 + audioData.length * 2, true); // File size
        view.setUint32(8, 0x45564157, true); // "WAVE"
        view.setUint32(12, 0x20746D66, true); // "fmt "
        view.setUint32(16, 16, true); // Format chunk size
        view.setUint16(20, format, true); // Format (PCM)
        view.setUint16(22, numChannels, true); // Channels
        view.setUint32(24, sampleRate, true); // Sample rate
        view.setUint32(28, sampleRate * blockAlign, true); // Byte rate
        view.setUint16(32, blockAlign, true); // Block align
        view.setUint16(34, bitDepth, true); // Bits per sample
        view.setUint32(36, 0x61746164, true); // "data"
        view.setUint32(40, audioData.length * 2, true); // Data chunk size

        // Write audio data
        const offset = 44;
        for (let i = 0; i < audioData.length; i++) {
            const s = Math.max(-1, Math.min(1, audioData[i]));
            view.setInt16(offset + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }

        return new Blob([wavData], { type: 'audio/wav' });
    };

    // WebSocket connection management
    useEffect(() => {
        const connectWebSocket = () => {
            if (!isRecordingRef.current) return;
            if (isConnectingRef.current) {
                console.log('Already attempting to connect, skipping...');
                return;
            }

            if (wsRef.current) {
                console.log('Closing existing WebSocket connection...');
                wsRef.current.close();
                wsRef.current = null;
            }

            console.log(`Creating new WebSocket (attempt ${reconnectAttemptsRef.current})...`);
            isConnectingRef.current = true;

            try {
                const ws = new WebSocket('wss://la-hacks-project.onrender.com/ws/test_client');
                wsRef.current = ws;

                ws.onopen = () => {
                    console.log('WebSocket connected successfully');
                    isConnectingRef.current = false;
                    reconnectAttemptsRef.current = 5;
                };

                ws.onclose = (event) => {
                    console.log(`WebSocket disconnected:`, event.code, event.reason);
                    isConnectingRef.current = false;
                    if (isRecordingRef.current && reconnectAttemptsRef.current > 0) {
                        reconnectAttemptsRef.current--;
                        setTimeout(connectWebSocket, 1000); // Add delay between reconnection attempts
                    }
                };

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    isConnectingRef.current = false;
                    if (isRecordingRef.current && reconnectAttemptsRef.current > 0) {
                        reconnectAttemptsRef.current--;
                        setTimeout(connectWebSocket, 1000); // Add delay between reconnection attempts
                    }
                };
            } catch (error) {
                console.error('Error creating WebSocket:', error);
                isConnectingRef.current = false;
                if (isRecordingRef.current && reconnectAttemptsRef.current > 0) {
                    reconnectAttemptsRef.current--;
                    setTimeout(connectWebSocket, 1000); // Add delay between reconnection attempts
                }
            }
        };

        if (isRecordingRef.current) {
            connectWebSocket();
        }

        // Cleanup function
        return () => {
            if (wsRef.current) {
                console.log('Cleaning up WebSocket connection...');
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, [isRecordingRef.current]); // Only re-run when recording state changes

    const startRecording = async () => {
        try {
            setIsRecording(true);
            isRecordingRef.current = true;
            reconnectAttemptsRef.current = 5; // Reset reconnection attempts

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            streamRef.current = stream;

            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
                sampleRate: 16000
            });

            // Set up audio analyzer
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyserRef.current = analyser;

            // Set up script processor for audio processing
            const CHUNK_SIZE = 16384;  // Match Python script's chunk size
            const processor = audioContext.createScriptProcessor(CHUNK_SIZE, 1, 1);
            const audioData: Int16Array[] = [];

            processor.onaudioprocess = (e) => {
                const inputData = e.inputBuffer.getChannelData(0);
                // Convert to Int16Array immediately to match Python's format
                const pcmData = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    const s = Math.max(-1, Math.min(1, inputData[i]));
                    pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                }
                audioData.push(pcmData);
            };

            source.connect(processor);
            processor.connect(audioContext.destination);

            checkAudioLevel();

            // Add 2-second chunk collection and sending
            shortIntervalRef.current = setInterval(() => {
                counter += 1;
                console.log("Counter: ", counter);

                if (audioData.length > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
                    // Calculate how many chunks we need for 2 seconds
                    const chunksPerSecond = Math.ceil(audioContext.sampleRate / CHUNK_SIZE);
                    const targetChunks = chunksPerSecond * 2;

                    // Get the last 2 seconds of audio
                    const startIndex = Math.max(0, audioData.length - targetChunks);
                    const lastTwoSeconds = audioData.slice(startIndex + 1);

                    // Concatenate the chunks
                    const totalLength = lastTwoSeconds.reduce((acc, arr) => acc + arr.length, 0);
                    const concatenated = new Int16Array(totalLength);
                    let offset = 0;
                    lastTwoSeconds.forEach(arr => {
                        concatenated.set(arr, offset);
                        offset += arr.length;
                    });

                    // Send raw PCM data
                    wsRef.current?.send(concatenated.buffer);

                    if (counter % 30 === 0) {
                        console.log("Sending audio to backend");
                        const totalLength = audioData.reduce((acc, arr) => acc + arr.length, 0);
                        const concatenated = new Float32Array(totalLength);
                        let offset = 0;
                        audioData.forEach(arr => {
                            concatenated.set(arr, offset);
                            offset += arr.length;
                        });
                        
                        // Create WAV blob
                        const wavBlob = createWavBlob(concatenated, audioContext.sampleRate);
                        setAudioChunks((prev) => [...prev, wavBlob]);
                        
                        // Clear audio data
                        audioData.length = 0;
                    }
                }
            }, 500);
        } catch (error) {
            console.error('Error accessing microphone:', error);
        }
    };

    const stopRecording = async () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
        }
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
        }
        if (speakingTimeoutRef.current) {
            clearTimeout(speakingTimeoutRef.current);
        }
        if (shortIntervalRef.current) {
            clearInterval(shortIntervalRef.current);
        }
        setIsRecording(false);
        isRecordingRef.current = false;
        setIsSpeaking(false);
        silenceCounterRef.current = 0;
    };

    useEffect(() => {
        if (audioChunks.length > 0) {
            const audioBlob = audioChunks[0]; // We're only sending one chunk at a time
            sendAudioToBackend(audioBlob);
            setAudioChunks([]);
        }
    }, [audioChunks]);

    const sendAudioToBackend = async (audioBlob: Blob) => {
        try {
            const formData = new FormData();
            const file = new File([audioBlob], "recording.wav", { type: "audio/wav" });
            formData.append('audio', file);

            console.log("Sending audio to backend");

            await axios.patch(
                // 'http://localhost:8000/api/updateInfo',
                'https://la-hacks-project.onrender.com/api/updateInfo',
                formData,
                {
                    params: {
                        snap_user_id: SNAP_USER_ID,
                        lecture_id: LECTURE_ID
                    },
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }
            );
        } catch (error) {
            console.error('Error sending audio to backend:', error);
        }
    };

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '100vh',
            }}
        >
            <Button
                variant="contained"
                color={isRecording ? 'error' : 'primary'}
                onClick={isRecording ? stopRecording : startRecording}
                sx={{
                    width: '150px',
                    height: '150px',
                    borderRadius: '50%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: 'none',
                    '&:hover': {
                        boxShadow: 'none',
                    },
                }}
            >
                {isRecording ? <MicOffIcon sx={{ fontSize: 60 }} /> : <MicIcon sx={{ fontSize: 60 }} />}
            </Button>
            {isRecording && (
                <Box
                    sx={{
                        marginTop: 3,
                        display: 'flex',
                        gap: 2,
                        animation: isSpeaking ? 'wave 1s infinite' : 'none',
                        '@keyframes wave': {
                            '0%': { transform: 'scaleY(0.5)' },
                            '50%': { transform: 'scaleY(1.5)' },
                            '100%': { transform: 'scaleY(0.5)' },
                        },
                    }}
                >
                    {[...Array(5)].map((_, i) => (
                        <Box
                            key={i}
                            sx={{
                                width: '8px',
                                height: '40px',
                                backgroundColor: '#1976d2',
                                borderRadius: '4px',
                                animation: isSpeaking ? `wave ${0.5 + i * 0.1}s infinite` : 'none',
                            }}
                        />
                    ))}
                </Box>
            )}
        </Box>
    );
};

export default Microphone; 