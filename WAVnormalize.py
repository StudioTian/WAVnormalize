import sys
import os
import subprocess
import glob

# 定義一個函數來找到 ffmpeg 可執行檔的路徑
def find_ffmpeg():
    # 檢查是否為 PyInstaller 打包的執行檔
    if getattr(sys, 'frozen', False):
        # 如果是打包後的執行檔，ffmpeg 應該被放在 _MEIPASS 目錄下
        ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg')
    else:
        # 如果是原始的 .py 腳本，直接嘗試呼叫 'ffmpeg'
        ffmpeg_path = 'ffmpeg'
    
    return ffmpeg_path

# 定義正規化音訊的函式
def normalize_audio(input_file, ffmpeg_path):
    try:
        # 建立輸出檔案路徑
        file_name, file_ext = os.path.splitext(os.path.basename(input_file))
        output_file_name = f"{file_name}_normalized{file_ext}"
        output_file = os.path.join(os.path.dirname(input_file), output_file_name)

        # 使用 subprocess 呼叫 ffmpeg 進行正規化
        # -i: 輸入檔案
        # -af loudnorm: 使用 EBU R128 標準進行音量正規化
        # -y: 強制覆蓋輸出檔案，無需確認
        command = [
            ffmpeg_path,
            '-i', input_file,
            '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',  # 音量正規化參數
            '-y',
            output_file
        ]
        
        # 執行指令並捕獲輸出
        print(f"正在處理：{os.path.basename(input_file)}...")
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"成功正規化：{os.path.basename(input_file)} -> {os.path.basename(output_file)}")
        print("FFmpeg 輸出訊息：")
        print(process.stderr)

    except FileNotFoundError:
        print("錯誤：找不到 ffmpeg。請確認 ffmpeg 已安裝在你的系統上，並在打包時使用 --add-binary 參數。")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"執行 ffmpeg 時發生錯誤：{e}")
        print("FFmpeg 錯誤訊息：")
        print(e.stderr)
        sys.exit(1)

# 主程式
def main():
    ffmpeg_path = find_ffmpeg()

    # 取得當前執行腳本或執行檔的資料夾路徑
    if getattr(sys, 'frozen', False):
        # 這是打包後的執行檔，取得其所在資料夾
        current_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 這是原始的 .py 腳本，取得其所在資料夾
        current_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"程式將處理資料夾：{current_dir} 中的音訊檔案。")

    # 搜尋所有 .wav 和 .mp3 檔案
    wav_files = glob.glob(os.path.join(current_dir, '*.wav'))
    mp3_files = glob.glob(os.path.join(current_dir, '*.mp3'))
    
    all_audio_files = wav_files + mp3_files

    if not all_audio_files:
        print(f"在 {current_dir} 中沒有找到任何 .wav 或 .mp3 檔案。")
        sys.exit(1)
            
    for input_file in all_audio_files:
        normalize_audio(input_file, ffmpeg_path)

if __name__ == "__main__":
    main()