import streamlit as st
import yt_dlp
import os
import requests
from dotenv import load_dotenv
import json
from urllib.parse import urlparse, parse_qs
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import base64
import streamlit as st
import yt_dlp
import os
import requests
from dotenv import load_dotenv
import json
from urllib.parse import urlparse, parse_qs
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import base64
from main import generate_combined_data

# Load environment variables
load_dotenv()

def get_youtube_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None


def download_video(url):
    video_id = get_youtube_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{video_id}.%(ext)s',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return filename
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Listing available formats:")
        
        ydl_opts_list = {
            'listformats': True,
            'dump_single_json': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts_list) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info['formats']
            
            print("Available formats:")
            for f in formats:
                print(f"Format code: {f['format_id']}, Extension: {f['ext']}, Resolution: {f.get('resolution', 'N/A')}")
        
        raise ValueError("Please choose an available format and update the 'format' option in ydl_opts.")

def process_with_deepgram(file_path):
    url = "https://api.deepgram.com/v1/listen"
    params = {
        "diarize": "true",
        "punctuate": "true",
        "utterances": "true"
    }
    
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "video/webm"
    }
    
    with open(file_path, "rb") as file:
        data = file.read()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    session = requests.Session()
    session.mount("https://", adapter)
    
    try:
        response = session.post(url, params=params, headers=headers, data=data, verify=True, timeout=30)
        response.raise_for_status()
        
        if response.status_code == 200:
            result = response.json()
            
            # Create 'transcripts' directory if it doesn't exist
            os.makedirs('transcripts', exist_ok=True)
            
            # Generate output filename in the 'transcripts' directory
            output_filename = os.path.join('transcripts', f"{os.path.splitext(os.path.basename(file_path))[0]}_transcript.json")
            
            with open(output_filename, "w") as outfile:
                json.dump(result, outfile, indent=2)
            return output_filename
        else:
            st.error(f"Error: {response.status_code}")
            st.error(response.text)
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred during the request: {e}")
    except json.JSONDecodeError:
        st.error("Error decoding JSON response")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    return None

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def main():
    st.set_page_config(layout="centered")
    st.title("What's your ASL?")

    url = st.text_input("Enter YouTube URL", value="https://www.youtube.com/watch?v=S0P3hjM0DDM")
    process_button = st.button("Process Video")

    transcript_path = None  # Initialize transcript_path

    if process_button:
        if url:
            try:
                with st.spinner("Downloading video..."):
                    video_path = download_video(url)
                st.success("Video downloaded successfully!")
                
                with st.spinner("Processing with Deepgram..."):
                    transcript_path = process_with_deepgram(video_path)
                
                if transcript_path:
                    st.success(f"Transcript generated successfully and saved at: {transcript_path}")
                    st.markdown(get_binary_file_downloader_html(transcript_path, 'Transcript'), unsafe_allow_html=True)
                    
                    # Display video
                    st.video(video_path)

                    # Generate combined data
                    with st.spinner("Generating combined data..."):
                        combined_data = generate_combined_data()
                    
                    # Create a hideable section for combined_data
                    with st.expander("Show Combined Data"):
                        st.json(combined_data)
                    
                    # Generate and display new video
                    with st.spinner("Generating new video..."):
                        new_video_path = generate_new_video(combined_data)
                    st.video(new_video_path)

                    # Show new video at ./test.mp4 if combined data and transcript generated successfully
                    if combined_data and transcript_path:
                        st.video("./S0P3hjM0DDM_duration_40s_combined.mp4")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main()
