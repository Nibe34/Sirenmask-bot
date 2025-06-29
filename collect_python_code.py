import os

def collect_python_code(output_file, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = []

    current_dir = os.path.dirname(os.path.abspath(__file__))

    with open(output_file, 'w', encoding='utf-8') as out_file:
        for root, dirs, files in os.walk(current_dir):
            # Пропускаємо виключені теки
            rel_root = os.path.relpath(root, current_dir)
            if any(excluded in rel_root.split(os.sep) for excluded in exclude_dirs):
                continue

            for file in files:
                if file.endswith('.py') and file != os.path.basename(__file__):  # не включати сам скрипт
                    file_path = os.path.join(root, file)
                    out_file.write(f"\n{'='*80}\n")
                    out_file.write(f"# Файл: {file_path}\n")
                    out_file.write(f"{'='*80}\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as py_file:
                            out_file.write(py_file.read())
                    except Exception as e:
                        out_file.write(f"# [Помилка читання файлу]: {e}\n")

if __name__ == '__main__':
    output_filename = 'all_python_code.txt'
    exclude = ['rvc_lib', '.venv', '.idea', '.git']

    collect_python_code(output_filename, exclude_dirs=exclude)
    print(f"✅ Код зібрано в '{output_filename}', окрім тек: {exclude}")
