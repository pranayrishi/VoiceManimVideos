import os
import speech_recognition as sr
import openai
from gtts import gTTS  # Importing the gTTS library
from manim import *
from moviepy.editor import VideoFileClip, AudioFileClip
import glob  # Importing glob to find the generated video file


# Function to get voice input from the user
def get_user_input():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Please say the math topic you want to learn about:")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        topic = recognizer.recognize_google(audio)
        print(f"User said: {topic}")
        return topic
    except sr.UnknownValueError:
        print("Sorry, I could not understand that.")
        return None
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return None


# Function to generate the Manim script using the ChatGPT API
def generate_manim_script(topic):
    openai.api_key = "OPENAI_API_KEY"

    prompt = f"Write a Python script using the Manim library to explain the math concept of {topic}. The script should be valid Manim code that generates a visual explanation for this topic. Please do not include any markdown or extra explanations."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Using the updated model
        messages=[
            {"role": "system", "content": "You are a helpful assistant who writes valid Manim code."},
            {"role": "user", "content": prompt}
        ]
    )

    manim_script = response['choices'][0]['message']['content'].strip()

    # Ensure no markdown or extraneous formatting
    manim_script = manim_script.replace("```python", "").replace("```", "").strip()

    print("Manim script generated successfully!")
    return manim_script


# Function to create a voiceover script that accompanies the video
def generate_voiceover_script(topic, manim_script):
    voiceover_script = f"Let's dive into the concept of {topic}. In this video, we'll explore how to understand and visualize {topic}. " \
                       "As you watch the video, pay attention to the mathematical concepts and the visual aids that are presented to help explain them.\n"

    voiceover_script += f"The first part of this video will focus on {topic} and demonstrate its key properties through engaging visualizations.\n" \
                        "I will guide you through each concept step by step, so let's begin.\n"

    return voiceover_script


# Function to create the Manim video
def create_manim_video(manim_script, topic):
    # Save the script to a temporary file
    with open("generated_manim_script.py", "w") as f:
        f.write(manim_script)

    print(f"Creating the Manim video for {topic}...")

    # Run the Manim command
    os.system("manim -pql generated_manim_script.py")

    # Manim exports the video to a file in media/videos/
    print(f"Manim video created successfully! You can find it in the 'media/videos' directory.")


# Function to find the latest Manim video file
def get_latest_manim_video():
    video_files = glob.glob("media/videos/generated_manim_script/480p15/*.mp4")
    if not video_files:
        raise FileNotFoundError("No Manim video file found in media/videos/")

    latest_video = max(video_files, key=os.path.getctime)  # Get the most recently created file
    print(f"Detected Manim video file: {latest_video}")
    return latest_video


# Function to generate the voiceover using gTTS
def generate_voiceover(text, filename="voiceover.mp3"):
    print("Creating voiceover for the Manim video...")

    tts = gTTS(text=text, lang='en')  # Specify language as English
    tts.save(filename)

    print("Voiceover created successfully!")


# Function to combine the video and the voiceover
def combine_video_audio(manim_video_path, voiceover_audio_path, output_path="final_video.mp4"):
    print("Combining video and audio...")

    # Load the video and the audio
    video = VideoFileClip(manim_video_path)
    audio = AudioFileClip(voiceover_audio_path)

    # Set the audio of the video clip
    final_video = video.set_audio(audio)

    # Export the final combined video
    final_video.write_videofile(output_path, codec="libx264")

    print(f"Final video created successfully: {output_path}")


# Main function to orchestrate the entire process
def main():
    topic = get_user_input()
    if topic:
        print("Generating the Manim script...")
        manim_script = generate_manim_script(topic)

        print("Creating the Manim video...")
        create_manim_video(manim_script, topic)

        print("Creating voiceover script...")
        voiceover_script = generate_voiceover_script(topic, manim_script)

        print("Creating voiceover for the video...")
        generate_voiceover(voiceover_script)

        print("Finding the latest Manim video file...")
        latest_manim_video = get_latest_manim_video()  # Dynamically get the latest video file

        print("Finalizing video with voiceover...")
        combine_video_audio(latest_manim_video, "voiceover.mp3", "final_video.mp4")

        print("The final video is ready to be played!")


if __name__ == "__main__":
    main()
