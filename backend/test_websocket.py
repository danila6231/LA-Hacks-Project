import pyaudio
import websockets
import asyncio
import signal
import sys
import time

CHUNK = 16384
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

should_record = True

def signal_handler(sig, frame):
    global should_record
    should_record = False
    print("\nStopping recording...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def connect_websocket():
    uri = "ws://localhost:8000/ws/test_client"
    while should_record:
        try:
            async with websockets.connect(uri) as websocket:
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
                
                print("Recording started. Press Ctrl+C to stop.")
                
                while should_record:
                    try:
                        data = stream.read(CHUNK)
                        await websocket.send(data)
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed, attempting to reconnect...")
                        break
                    
                stream.stop_stream()
                stream.close()
                p.terminate()
                
        except Exception as e:
            print(f"Connection error: {str(e)}, retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect_websocket()) 