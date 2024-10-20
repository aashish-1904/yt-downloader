import os
import streamlit as st
import yt_dlp
import subprocess

# Function to ensure ffmpeg is installed and accessible
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

# Function to download only audio using yt-dlp
def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        return os.path.join(output_path, f"{info_dict['title']}.mp3")

# Function to download only video using yt-dlp
def download_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        return os.path.join(output_path, f"{info_dict['title']}.mp4")

# Function to download both video and audio using yt-dlp
def download_video_with_audio(url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
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

    # Check if ffmpeg is installed
    if not check_ffmpeg():
        st.error("FFmpeg is not installed or not accessible. Please install FFmpeg to use this tool.")
        return

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
                            file_path = download_audio(url, output_path)
                            st.success(f"Audio downloaded: {file_path}")
                            st.audio(file_path)
                        elif option == 'Video':
                            file_path = download_video(url, output_path)
                            st.success(f"Video downloaded: {file_path}")
                            st.video(file_path)
                        elif option == 'Both (Video + Audio)':
                            file_path = download_video_with_audio(url, output_path)
                            st.success(f"Video with audio downloaded: {file_path}")
                            st.video(file_path)
                    except Exception as e:
                        st.error(f"Failed to download {url}: {e}")
        else:
            st.error("Please enter at least one valid YouTube URL.")

if __name__ == '__main__':
    main()
