import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json

load_dotenv()

# Azure Speech Service configuration
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Audio format options - Updated with correct enum values
AUDIO_FORMATS = {
    "mp3": speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
    "wav": speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm,
    "ogg": speechsdk.SpeechSynthesisOutputFormat.Ogg16Khz16BitMonoOpus,
}


# Let's update the AUDIO_FORMATS with the correct enum values
# AUDIO_FORMATS = {
#     "mp3": speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
#     "wav": speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16Bit32KBpsMonoPcm,
#     "ogg": speechsdk.SpeechSynthesisOutputFormat.Ogg16Khz16Bit32KBpsMonoOpus,
# }

# Available voices for different languages
VOICES = {
    "zh-CN": [
        "zh-CN-XiaoxiaoNeural",  # Female
        "zh-CN-YunxiNeural",     # Male
        "zh-CN-YunyangNeural",   # Male
        "zh-CN-XiaochenNeural",  # Female
        "zh-CN-XiaohanNeural",   # Female
        "zh-CN-XiaomengNeural",  # Female
        "zh-CN-XiaomoNeural",    # Female
        "zh-CN-XiaoqiuNeural",   # Female
        "zh-CN-XiaoruiNeural",   # Female
        "zh-CN-XiaoshuangNeural",# Female
        "zh-CN-XiaoxuanNeural",  # Female
        "zh-CN-XiaoyanNeural",   # Female
        "zh-CN-XiaoyiNeural",    # Female
        "zh-CN-XiaozhenNeural",  # Female
        "zh-CN-YunfengNeural",   # Male
        "zh-CN-YunhaoNeural",    # Male
        "zh-CN-YunjianNeural",   # Male
        "zh-CN-YunxiaNeural",    # Male
        "zh-CN-YunzeNeural",     # Male
    ],
    "en-US": [
        "en-US-AriaNeural",      # Female
        "en-US-GuyNeural",       # Male
        "en-US-JennyNeural",     # Female
        "en-US-RogerNeural",     # Male
        "en-US-SteffanNeural",   # Male
    ]
}

def get_voice_info(voice_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific voice
    
    Args:
        voice_name: The voice name to get info for
    
    Returns:
        dict: Voice information including gender, language, etc.
    """
    # Extract language and gender from voice name
    parts = voice_name.split("-")
    if len(parts) >= 3:
        language = f"{parts[0]}-{parts[1]}"
        gender = "Female" if "Xiao" in parts[2] else "Male"
    else:
        language = "unknown"
        gender = "unknown"
    
    return {
        "name": voice_name,
        "language": language,
        "gender": gender,
        "neural": "Neural" in voice_name,
        "description": f"{gender} voice for {language}"
    }

# Get detailed voice information
VOICE_INFO = {
    lang: [get_voice_info(voice) for voice in voices]
    for lang, voices in VOICES.items()
}

def get_speech_config(
    voice_name: str = "zh-CN-XiaoxiaoNeural",
    audio_format: str = "mp3",
    speaking_rate: float = 1.0,
    pitch: float = 0.0
) -> speechsdk.SpeechConfig:
    """
    Get Azure Speech Service configuration with custom settings
    
    Args:
        voice_name: The voice to use
        audio_format: Output audio format (mp3, wav, ogg)
        speaking_rate: Speaking rate (0.5 to 2.0)
        pitch: Voice pitch adjustment (-10 to 10)
    
    Returns:
        SpeechConfig: Configured speech service config
    """
    if not SPEECH_KEY or not SPEECH_REGION:
        raise ValueError("Azure Speech Service credentials not configured")
        
    config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )
    
    # Set voice
    config.speech_synthesis_voice_name = voice_name
    
    # Set audio format
    if audio_format in AUDIO_FORMATS:
        config.set_speech_synthesis_output_format(AUDIO_FORMATS[audio_format])
    
    # Set speaking rate and pitch using SSML
    ssml = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="{voice_name}">
            <prosody rate="{speaking_rate}" pitch="{pitch}st">
                {{text}}
            </prosody>
        </voice>
    </speak>
    """
    config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Ssml)
    
    return config, ssml

async def tts_generate(
    text: str,
    voice_name: str = "zh-CN-XiaoxiaoNeural",
    audio_format: str = "mp3",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    use_ssml: bool = False
) -> bytes:
    """
    Generate speech from text using Azure Text-to-Speech service
    
    Args:
        text: The text to convert to speech
        voice_name: The voice to use
        audio_format: Output audio format (mp3, wav, ogg)
        speaking_rate: Speaking rate (0.5 to 2.0)
        pitch: Voice pitch adjustment (-10 to 10)
        use_ssml: Whether to use SSML for advanced formatting
    
    Returns:
        bytes: The generated audio data
    """
    try:
        # Create speech config
        speech_config, ssml_template = get_speech_config(
            voice_name=voice_name,
            audio_format=audio_format,
            speaking_rate=speaking_rate,
            pitch=pitch
        )
        
        # Create speech synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None
        )
        
        # Synthesize text to speech
        if use_ssml:
            ssml = ssml_template.format(text=text)
            result = synthesizer.speak_ssml_async(ssml).get()
        else:
            result = synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        else:
            error_details = result.cancellation_details
            raise Exception(f"Speech synthesis failed: {error_details.reason}, {error_details.error_details}")
            
    except Exception as e:
        raise Exception(f"TTS generation failed: {str(e)}") 