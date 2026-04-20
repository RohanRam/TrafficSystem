import os

def download_sample_video():
    url = "https://www.youtube.com/watch?v=O1mvuIQ_Lhw" # Sample Ambulance Video
    output_filename = "sample_video.mp4"
    if not os.path.exists(output_filename):
        print(f"Downloading sample video from {url}...")
        os.system(f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o {output_filename} {url}')
        print("Download complete.")
    else:
        print("Sample video already exists.")

if __name__ == "__main__":
    download_sample_video()
