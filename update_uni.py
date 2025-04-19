import os
import difflib
import argparse

def read_source_lines(source_file):
    """
    嘗試用不同編碼讀取 source_file
    """
    try:
        with open(source_file, 'r', encoding='utf-8-sig') as f:
            return f.readlines()
    except UnicodeDecodeError:
        # 如果 utf-8-sig 讀取失敗，改用 utf-16-le 嘗試
        with open(source_file, 'r', encoding='utf-16-le') as f:
            return f.readlines()

def process_file(source_file, target_file):
    """
    比對 source_file 與 target_file 的內容，
    只覆蓋 target_file 中與 source_file 不同的區段，
    並保留 target_file 的原始格式（UTF-16 LE）。
    """
    # 嘗試讀取 source 檔案，若編碼錯誤則自動切換編碼
    source_lines = read_source_lines(source_file)
    
    target_lines = read_source_lines(target_file)
    
    # 利用 difflib 比較兩個檔案，取得操作序列
    matcher = difflib.SequenceMatcher(None, target_lines, source_lines)
    patched_lines = target_lines[:]  # 複製原始內容

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ('replace', 'delete', 'insert'):
            # 針對不同部分採用 source 內容覆蓋 target 對應區段
            patched_lines[i1:i2] = source_lines[j1:j2]
    
    # 如果內容有修改，覆寫 target 檔案
    if patched_lines != target_lines:
        try:
            with open(target_file, 'w', encoding='utf-16-le') as f:
                f.writelines(patched_lines)
        except Exception as e:
            print(f"Error writing to {target_file}: {e}")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="使用 source_folder 的 .uni 檔案，針對 target_folder (含子資料夾) 中同名的 .uni 檔做部分覆寫，並列出修改過的檔案")
    parser.add_argument("source_folder", help="Source 資料夾路徑，內含 .uni 檔")
    parser.add_argument("target_folder", help="Target 資料夾路徑，內含 .uni 檔（包含子資料夾），格式為 UTF-16 LE")
    args = parser.parse_args()

    source_folder = args.source_folder
    target_folder = args.target_folder

    # 建立 source_folder 中 .uni 檔案字典，key 為檔名
    source_uni_files = {}
    for file in os.listdir(source_folder):
        if file.endswith(".uni"):
            source_uni_files[file] = os.path.join(source_folder, file)
    
    modified_files = []

    # 遍歷 target_folder (包含所有子資料夾)
    for root, dirs, files in os.walk(target_folder):
        for file in files:
            if file.endswith(".uni") and file in source_uni_files:
                source_file = source_uni_files[file]
                target_file = os.path.join(root, file)
                try:
                    print(f"Before processing: {target_file}")
                    with open(target_file, 'r', encoding='utf-16-le') as f:
                        f.readlines()
                except Exception as e:
                    print(f"Error reading {target_file}: {e}")

                if process_file(source_file, target_file):
                    print(f"After processing: {target_file}")
                    try:
                        with open(target_file, 'r', encoding='utf-16-le') as f:
                            f.readlines()
                    except Exception as e:
                        print(f"Error reading {target_file}: {e}")

                    modified_files.append(target_file)
    
    # 將修改過的檔案路徑寫入 result.txt (此處 result.txt 以 UTF-8 編碼儲存)
    with open("result.txt", "w", encoding="utf-8") as f:
        for file in modified_files:
            f.write(file + "\n")
    
    print("處理完成！修改過的檔案已列於 result.txt 中。")

if __name__ == '__main__':
    main()
