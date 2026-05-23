import os

project_dir = r"d:\Project AryaX 2\Project AryaX"
output_file = os.path.join(project_dir, "AryaX_Master_Prompt.txt")

files_to_export = [
    "app.py",
    "utils/db.py",
    "utils/api_keys.py",
    "public/index.html",
    "public/style.css",
    "public/script.js",
    "requirements.txt",
    "Procfile"
]

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("This is the complete codebase for AryaX (Artificial Super Intelligence).\n")
    outfile.write("Please use this context to understand the project architecture and generate new features.\n\n")
    outfile.write("="*50 + "\n\n")
    
    for relative_path in files_to_export:
        file_path = os.path.join(project_dir, relative_path.replace('/', os.sep))
        outfile.write(f"--- FILE: {relative_path} ---\n\n")
        try:
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
        except Exception as e:
            outfile.write(f"[Error reading file: {e}]\n")
        outfile.write("\n\n" + "="*50 + "\n\n")

print(f"Successfully generated {output_file}")
