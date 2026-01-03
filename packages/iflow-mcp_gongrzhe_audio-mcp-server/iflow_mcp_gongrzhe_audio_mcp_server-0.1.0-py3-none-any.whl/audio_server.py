#!/usr/bin/env python3
"""Audio MCP Server using standard MCP SDK"""
import asyncio
import base64
import json
import os
import tempfile
import wave
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Initialize MCP server
app = Server("audio-interface")

# Constants
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_CHANNELS = 1
DEFAULT_DURATION = 5  # seconds

# Global variable to store the latest recording
latest_recording = None

def get_audio_devices():
    """Get a list of all available audio devices."""
    import sounddevice as sd
    
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    output_devices = [d for d in devices if d['max_output_channels'] > 0]
    
    return {
        "input_devices": input_devices,
        "output_devices": output_devices
    }

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="list_audio_devices",
            description="List all available audio input and output devices on the system.",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="record_audio",
            description="Record audio from the microphone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "number",
                        "description": "Recording duration in seconds (default: 5)",
                        "default": 5
                    },
                    "sample_rate": {
                        "type": "integer",
                        "description": "Sample rate in Hz (default: 44100)",
                        "default": 44100
                    },
                    "channels": {
                        "type": "integer",
                        "description": "Number of audio channels (default: 1)",
                        "default": 1
                    },
                    "device_index": {
                        "type": "integer",
                        "description": "Specific input device index to use (default: system default)"
                    }
                }
            }
        ),
        Tool(
            name="play_latest_recording",
            description="Play the latest recorded audio through the speakers.",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="play_audio",
            description="Play audio from text using text-to-speech.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to convert to speech"
                    },
                    "voice": {
                        "type": "string",
                        "description": "The voice to use (default: 'default')",
                        "default": "default"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="play_audio_file",
            description="Play an audio file through the speakers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the audio file"
                    },
                    "device_index": {
                        "type": "integer",
                        "description": "Specific output device index to use (default: system default)"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    
    global latest_recording
    
    if name == "list_audio_devices":
        devices = get_audio_devices()
        
        result = "Audio devices available on your system:\n\n"
        
        result += "INPUT DEVICES (MICROPHONES):\n"
        for i, device in enumerate(devices["input_devices"]):
            result += f"{i}: {device['name']} (Channels: {device['max_input_channels']})\n"
        
        result += "\nOUTPUT DEVICES (SPEAKERS):\n"
        for i, device in enumerate(devices["output_devices"]):
            result += f"{i}: {device['name']} (Channels: {device['max_output_channels']})\n"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "record_audio":
        duration = arguments.get("duration", DEFAULT_DURATION)
        sample_rate = arguments.get("sample_rate", DEFAULT_SAMPLE_RATE)
        channels = arguments.get("channels", DEFAULT_CHANNELS)
        device_index = arguments.get("device_index")
        
        try:
            # Check if the specified device exists and is an input device
            if device_index is not None:
                devices = get_audio_devices()
                input_devices = devices["input_devices"]
                if device_index < 0 or device_index >= len(input_devices):
                    return [TextContent(type="text", text=f"Error: Invalid device index {device_index}. Use list_audio_devices tool to see available devices.")]
            
            # Record audio
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=channels,
                device=device_index
            )
            
            # Wait for the recording to complete
            sd.wait()
            
            # Generate a temp file for storage
            fd, temp_path = tempfile.mkstemp(suffix='.wav')
            try:
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(sample_rate)
                    wf.writeframes((recording * 32767).astype(np.int16).tobytes())
                
                # Encode the file for storage
                with open(temp_path, 'rb') as f:
                    encoded_audio = base64.b64encode(f.read()).decode('utf-8')
                    
                # Store the audio in a global variable for later playback
                latest_recording = {
                    'audio_data': encoded_audio,
                    'sample_rate': sample_rate,
                    'channels': channels
                }
                
                return [TextContent(type="text", text=f"Successfully recorded {duration} seconds of audio. Use play_latest_recording tool to play it back.")]
            finally:
                os.close(fd)
                os.unlink(temp_path)
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error recording audio: {str(e)}")]
    
    elif name == "play_latest_recording":
        if latest_recording is None:
            return [TextContent(type="text", text="No recording available. Use record_audio tool first.")]
        
        try:
            # Decode the audio data
            audio_data = base64.b64decode(latest_recording['audio_data'])
            sample_rate = latest_recording['sample_rate']
            channels = latest_recording['channels']
            
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.wav')
            try:
                # Write the audio data to the temp file
                with open(temp_path, 'wb') as f:
                    f.write(audio_data)
                
                # Read the audio file
                data, fs = sf.read(temp_path)
                
                # Play the audio
                sd.play(data, fs)
                sd.wait()  # Wait until the audio is done playing
                
                return [TextContent(type="text", text="Successfully played the latest recording.")]
            finally:
                os.close(fd)
                os.unlink(temp_path)
        except Exception as e:
            return [TextContent(type="text", text=f"Error playing audio: {str(e)}")]
    
    elif name == "play_audio":
        text = arguments.get("text", "")
        voice = arguments.get("voice", "default")
        
        try:
            # Note: This is a simplified implementation that would need to be expanded
            # with an actual TTS service like gTTS, pyttsx3, or an external API
            
            # For now, we'll return a message indicating that TTS is not implemented
            return [TextContent(type="text", text=(
                "Text-to-speech functionality requires additional setup. "
                "You would need to install a TTS library like gTTS or pyttsx3, "
                f"which would convert the text '{text}' to audio using voice '{voice}'. "
                "This would then be played through your speakers."
            ))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error playing audio: {str(e)}")]
    
    elif name == "play_audio_file":
        file_path = arguments.get("file_path", "")
        device_index = arguments.get("device_index")
        
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return [TextContent(type="text", text=f"Error: File not found at {file_path}")]
            
            # Check if the specified device exists and is an output device
            if device_index is not None:
                devices = get_audio_devices()
                output_devices = devices["output_devices"]
                if device_index < 0 or device_index >= len(output_devices):
                    return [TextContent(type="text", text=f"Error: Invalid device index {device_index}. Use list_audio_devices tool to see available devices.")]
            
            # Read the audio file
            data, fs = sf.read(file_path)
            
            # Play the audio
            sd.play(data, fs, device=device_index)
            sd.wait()  # Wait until the audio is done playing
            
            return [TextContent(type="text", text=f"Successfully played audio file: {file_path}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error playing audio file: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

def main_sync():
    """Synchronous entry point"""
    import anyio
    anyio.run(main)

if __name__ == "__main__":
    main_sync()