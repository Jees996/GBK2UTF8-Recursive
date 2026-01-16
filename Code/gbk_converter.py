import os
import shutil
import sys

# 定义路径
# 程序运行时，根据运行方式选择工作目录：
# - 打包为 exe 时（frozen）：使用 exe 所在目录作为自包含的工作目录（所有导入/导出/备份在此目录下）
# - 以脚本运行时：保持原行为，使用项目结构下的 Code 目录
if getattr(sys, 'frozen', False):
    app_dir = os.path.dirname(sys.executable)
    CODE_DIR = app_dir
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(app_dir, os.pardir))
    CODE_DIR = os.path.join(BASE_DIR, "Code")

imput_DIR = os.path.join(CODE_DIR, "imput")
OUTPUT_DIR = os.path.join(CODE_DIR, "output")
BACKUP_DIR = os.path.join(CODE_DIR, "backup")

def convert_files_recursive():
    if not os.path.exists(imput_DIR):
        # 当输入文件夹不存在时，自动创建输入/输出/备份目录（便于 exe 模式的自包含使用）
        os.makedirs(imput_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        print(f"输入文件夹 {imput_DIR} 不存在，已创建。请将要转换的文件放入该文件夹后重新运行。")
        return

    print("开始扫描文件夹并处理文件...")
    print("-" * 30)

    success_count = 0
    
    # os.walk 会自动遍历所有子文件夹
    # root: 当前正在遍历的文件夹路径
    # dirs: 当前文件夹下的子文件夹名列表
    # files: 当前文件夹下的文件名列表
    for root, dirs, files in os.walk(imput_DIR):
        
        # 计算当前文件夹相对于 imput 的相对路径 (例如: "\ProjectA\SubFolder")
        rel_path = os.path.relpath(root, imput_DIR)
        
        # 在 output 和 backup 中创建对应的镜像文件夹
        target_dir = os.path.join(OUTPUT_DIR, rel_path)
        backup_dir = os.path.join(BACKUP_DIR, rel_path)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        for filename in files:
            src_path = os.path.join(root, filename)
            dst_path = os.path.join(target_dir, filename)
            backup_path = os.path.join(backup_dir, filename)

            try:
                # 1. 转码：读取 GBK，写入 UTF-8 到 output 对应的子文件夹
                with open(src_path, 'r', encoding='gbk') as f:
                    content = f.read()

                with open(dst_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"[成功] {os.path.join(rel_path, filename)}")

                # 2. 备份：将原文件移动到 backup 对应的子文件夹
                if os.path.exists(backup_path):
                    os.remove(backup_path) # 防止备份冲突
                shutil.move(src_path, backup_path)
                
                success_count += 1

            except UnicodeDecodeError:
                # 如果不是GBK，直接复制原文件到output(防止丢失)，并移动到backup
                print(f"[跳过转码] 非GBK文件: {filename} (直接复制)")
                shutil.copy(src_path, dst_path)
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.move(src_path, backup_path)
                
            except Exception as e:
                print(f"[错误] {filename}: {e}")

    # 清理 imput 中剩下的空文件夹 (可选)
    # 因为文件都移走了，剩下的只是空壳文件夹
    for root, dirs, files in os.walk(imput_DIR, topdown=False):
        for name in dirs:
            try:
                os.rmdir(os.path.join(root, name))
            except OSError:
                pass # 如果文件夹不为空（可能有没有处理的文件），就不删除

    print("-" * 30)
    print(f"处理完成。共处理 {success_count} 个文件。")
    print(f"转换后文件位置: {OUTPUT_DIR}")
    print(f"原文件备份位置: {BACKUP_DIR}")

if __name__ == '__main__':
    convert_files_recursive()