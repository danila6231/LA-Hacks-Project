declare module 'recorder-js' {
    interface RecorderOptions {
        numChannels?: number;
        sampleRate?: number;
        bitRate?: number;
    }

    interface BlobResult {
        blob: Blob;
        buffer: ArrayBuffer;
    }

    class Recorder {
        constructor(audioContext: AudioContext, options?: RecorderOptions);
        init(stream: MediaStream): Promise<void>;
        start(): void;
        stop(): Promise<{ buffer: ArrayBuffer }>;
        getBlob(): Promise<BlobResult>;
        clear(): void;
    }

    export default Recorder;
} 