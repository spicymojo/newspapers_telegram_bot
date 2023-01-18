from resources.config import FilesAPI
import requests, os, glob

TMP_PATH = 'tmp/'
NEWSPAPER = 'NEWSPAPER'
MAGAZINE = 'MAGAZINE'

# Aux
def is_pdf(file):
    try:
        return file.media.mime_type == "application/pdf"
    except AttributeError:
        return False

def check_tmp_folder():
    if not os.path.isdir(TMP_PATH):
        os.makedirs(TMP_PATH)
        print("Created TMP folder")

def count_pdf_files():
    pdf_files = glob.glob('')
    return len(pdf_files)

def open_link_file(path):
    return open(path, "r")

# Cleaning
def remove_pdf_files():
    pdf_files = glob.glob(TMP_PATH + '*')
    for f in pdf_files:
        try:
            os.remove(f)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (f, e))

def get_filenames_from_wanted_files(clean_files):
    clean_filenames = []
    for file in clean_files:
        clean_filenames.append(file.name)
    return clean_filenames

def remove_files_from_filenames(clean_files, clean_names):
    filtered_clean_files = []
    for file in clean_files:
        if file.name in clean_names:
            filtered_clean_files.append(file)
    return filtered_clean_files

# Cleaning methods
def clean():
        print("Cleaning the files...")
        remove_pdf_files()
        if (count_pdf_files() == 0):
            print("Done! All clean for tomorrow!")
        else:
            print("Error deleting files, please delete them manually")

# Decission making
def we_want(filename):
    filename = filename.split("-")[3].upper()

    if filename in newspapers_filter:
        return True, NEWSPAPER
    elif filename in magazines_filter:
        return True, MAGAZINE
    return False, None

# Downloads
def download_file(file):
    if not os.path.isfile(file.filename):
        try:
            if downloads_path != "":
                file.filename = downloads_path + "/" + file.filename
            else:
                file.filename = file.filename.replace(r"/"," ")
            print("  Downloading " + file.filename + " ...")
            open(file.filename, "wb").write(requests.get(file.url).content)
        except Exception:
            print("Error downloading " + file.filename)

# Preparing variables
def remove_already_sended_files(files_that_we_want, sended_newspapers, sended_magazines):
    print("We want to download " + str(len(files_that_we_want)) + " files")
    print("Check already sended files...")
    not_filtered_files = len(files_that_we_want)
    names = get_filenames_from_wanted_files(files_that_we_want)

    filtered_clean_names = []
    for name in names:
        if name not in sended_newspapers and name not in sended_magazines:
            filtered_clean_names.append(name)

    files_that_we_want = remove_files_from_filenames(files_that_we_want, filtered_clean_names)
    print((str(not_filtered_files - len(files_that_we_want)) + " files already sended, removed"))
    return files_that_we_want

def clean_list(files, sended_newspapers, sended_magazines):
    files_that_we_want = []
    if files:
        for f in files:
            if f is not None and f not in files_that_we_want:
                files_that_we_want.append(f)

    files_that_we_want = remove_already_sended_files(files_that_we_want, sended_newspapers, sended_magazines)
    return files_that_we_want

newspapers_filter = FilesAPI.newspapers_filter
magazines_filter = FilesAPI.magazines_filter
downloads_path = FilesAPI.downloads_path