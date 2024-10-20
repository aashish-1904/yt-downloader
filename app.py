import os
import streamlit as st
import yt_dlp
import subprocess
import requests
import shutil

# Download FFmpeg binary if not already cached
@st.cache_resource
def download_ffmpeg():
    ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
    ffmpeg_tar = "ffmpeg.tar.xz"
    ffmpeg_dir = "ffmpeg"

    if not os.path.exists(ffmpeg_dir):
        # Download the ffmpeg tar file
        with requests.get(ffmpeg_url, stream=True) as r:
            with open(ffmpeg_tar, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        
        # Extract the tar file
        shutil.unpack_archive(ffmpeg_tar, ffmpeg_dir)
    
    # Set the path to ffmpeg binary
    ffmpeg_bin_path = os.path.join(ffmpeg_dir, 'ffmpeg')
    
    return ffmpeg_bin_path

# Function to download only audio using yt-dlp
def download_audio(url, output_path, ffmpeg_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_path,  # Use ffmpeg path
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        return os.path.join(output_path, f"{info_dict['title']}.mp3")

# Function to download only video using yt-dlp
def download_video(url, output_path, ffmpeg_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_path,  # Use ffmpeg path
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        return os.path.join(output_path, f"{info_dict['title']}.mp4")

# Function to download both video and audio using yt-dlp
def download_video_with_audio(url, output_path, ffmpeg_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'ffmpeg_location': ffmpeg_path,  # Use ffmpeg path
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        return os.path.join(output_path, f"{info_dict['title']}.mp4")

# Streamlit UI and logic
def main():
    st.title("YouTube Video Downloader")

    # Download FFmpeg and get the path
    ffmpeg_path = download_ffmpeg()

    urls = st.text_area("Enter YouTube video URLs (one per line)").splitlines()
    option = st.radio("Select download option", ('Audio', 'Video', 'Both (Video + Audio)'))
    output_path = "./downloads"
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    if st.button("Download"):
        if urls:
            for url in urls:
                url = url.strip()  # Strip any leading/trailing whitespace
                if url:  # Check if URL is not empty
                    try:
                        st.write(f"Processing: {url}")
                        
                        if option == 'Audio':
                            file_path = download_audio(url, output_path, ffmpeg_path)
                            st.success(f"Audio downloaded: {file_path}")
                            st.audio(file_path)
                        elif option == 'Video':
                            file_path = download_video(url, output_path, ffmpeg_path)
                            st.success(f"Video downloaded: {file_path}")
                            st.video(file_path)
                        elif option == 'Both (Video + Audio)':
                            file_path = download_video_with_audio(url, output_path, ffmpeg_path)
                            st.success(f"Video with audio downloaded: {file_path}")
                            st.video(file_path)
                    except Exception as e:
                        st.error(f"Failed to download {url}: {e}")
        else:
            st.error("Please enter at least one valid YouTube URL.")

if __name__ == '__main__':
    main()
