
import os
import fitz  # PyMuPDF

# --- load environment values from 'info.env' next to this script ---
# Requires: pip install python-dotenv
def _load_env():
    try:
        from dotenv import load_dotenv
    except Exception:
        return False  # dotenv not available; we'll rely on OS envs/defaults

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()  # e.g., interactive contexts

    env_path = os.path.join(script_dir, "info.env")
    return load_dotenv(env_path)  # quietly does nothing if file missing

_ENV_LOADED = _load_env()


def get_env(name: str, default: str) -> str:
    """Fetch env var with a default; trims whitespace and expands ~."""
    val = os.getenv(name, default)
    if val is None:
        return default
    return os.path.expanduser(val.strip())


# --- configuration from env (namespaced for this script) ---
# SPLITPDF_FOLDER_PATH: absolute/relative path to the folder containing source PDFs
# SPLITPDF_OUTPUT_SUBDIR: name of subfolder to place outputs under folder_path
folder_path = get_env("SPLITPDF_FOLDER_PATH", r"./Split PDFs")
output_subdir = get_env("SPLITPDF_OUTPUT_SUBDIR", "_split")

# --- sanity check message so you see which values are used ---
print(f"[CONFIG] Env loaded: {_ENV_LOADED}. Using folder_path: {folder_path}")
print(f"[CONFIG] Output subfolder name: {output_subdir}")

# --- tidy rule 1: put outputs in a subfolder to avoid mixing with sources ---
output_dir = os.path.join(folder_path, output_subdir)

# Ensure the source folder exists before creating the output subfolder
if not os.path.isdir(folder_path):
    print(f"[ERROR] Input folder not found: {folder_path}")
    print("        Fix SPLITPDF_FOLDER_PATH in info.env or create the folder, then re-run.")
else:
    os.makedirs(output_dir, exist_ok=True)

    # --- tidy rule 2: safer naming (source name + page number) and avoid overwrites ---
    def unique_name(base_dir, desired_name):
        """Return a filename that won't overwrite existing files by appending (1), (2), ..."""
        name, ext = os.path.splitext(desired_name)
        candidate = desired_name
        i = 1
        while os.path.exists(os.path.join(base_dir, candidate)):
            candidate = f"{name} ({i}){ext}"
            i += 1
        return candidate

    # --- tidy rule 3: friendly progress messages + robust flow ---
    files_seen = 0
    pages_written = 0

    # Iterate over all PDF files in the folder
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".pdf"):
            continue  # skip non-PDFs

        files_seen += 1
        file_path = os.path.join(folder_path, filename)

        try:
            doc = fitz.open(file_path)
        except Exception as e:
            print(f"[SKIP] Could not open '{filename}': {e}")
            continue

        page_count = doc.page_count
        print(f"[PROCESS] '{filename}' ({page_count} pages)")

        # Split each page into a new PDF
        for page_num in range(page_count):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

            # source-based name: <source>_p<page>.pdf
            base = os.path.splitext(filename)[0]
            desired_name = f"{base}_p{page_num + 1}.pdf"
            safe_name = unique_name(output_dir, desired_name)
            output_path = os.path.join(output_dir, safe_name)

            try:
                new_doc.save(output_path)
                new_doc.close()
                pages_written += 1
            except Exception as e:
                print(f"[ERROR] Save failed for '{filename}' page {page_num + 1}: {e}")

        # After finishing all pages for this file, close the original document
        doc.close()

    # Final status message
    print(f"[DONE] Files processed: {files_seen}, pages written: {pages_written}")