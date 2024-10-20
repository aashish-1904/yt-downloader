import os
import streamlit as st
from pytube import YouTube, exceptions
import ffmpeg

# Function to download only audio
def download_audio(yt, output_path):
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file = audio_stream.download(output_path=output_path)
    base, ext = os.path.splitext(audio_file)
    new_file = base + '.mp3'
    os.rename(audio_file, new_file)
    return new_file

# Function to download only video
def download_video(yt, output_path):
    video_stream = yt.streams.filter(only_video=True, file_extension='mp4').first()
    video_file = video_stream.download(output_path=output_path)
    return video_file

# Function to download both video and audio
def download_video_with_audio(yt, output_path):
    video_stream = yt.streams.filter(progressive=False, file_extension='mp4').first()
    audio_stream = yt.streams.filter(only_audio=True).first()

    video_file = video_stream.download(output_path=output_path)
    audio_file = audio_stream.download(output_path=output_path)

    output_file = os.path.join(output_path, f'{yt.title}.mp4')

    # Combine video and audio using ffmpeg
    ffmpeg.input(video_file).output(audio_file, vcodec='copy', acodec='copy').run()
    
    os.remove(video_file)
    os.remove(audio_file)
    return output_file

# Streamlit UI and logic
def main():
    st.title("YouTube Video Downloader")

    urls = st.text_area("Enter YouTube video URLs (one per line)").splitlines()
    option = st.radio("Select download option", ('Audio', 'Video', 'Both (Video + Audio)'))
    output_path = "./downloads"
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    if st.button("Download"):
        if urls:
            for url in urls:
                if url.strip():  # Check if URL is not empty
                    try:
                        yt = YouTube(url)
                        
                        # Attempt to fetch video title, with fallback in case of failure
                        try:
                            st.write(f"Downloading: {yt.title}")
                        except exceptions.PytubeError:
                            st.warning(f"Could not fetch title for {url}. Proceeding with download.")
                        
                        if option == 'Audio':
                            file_path = download_audio(yt, output_path)
                            st.success(f"Audio downloaded: {file_path}")
                            st.audio(file_path)
                        elif option == 'Video':
                            file_path = download_video(yt, output_path)
                            st.success(f"Video downloaded: {file_path}")
                            st.video(file_path)
                        elif option == 'Both (Video + Audio)':
                            file_path = download_video_with_audio(yt, output_path)
                            st.success(f"Video with audio downloaded: {file_path}")
                            st.video(file_path)
                    except exceptions.PytubeError as e:
                        st.error(f"Failed to process {url}: {e}")
        else:
            st.error("Please enter at least one valid YouTube URL.")

if __name__ == '__main__':
    main()
