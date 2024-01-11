from random import Random
import os
import pathlib
import shutil
from tqdm import tqdm

def create_subset(dataset, count, seed, path, dataset_tag_path=None, filter_func: callable = None, behavior="copy"):
    """
    Creates subset from the original dataset.
    Dataset : Folder containing images and corresponding text files.
    Count : Number of images to be selected.
    Seed : Seed for random number generator.
    Path : Path to the new dataset.
    Dataset_tag_path : Path to the dataset tags.
    Filter_func : Function to filter the files. (filename) -> bool
    """
    # Create the folder if it doesn't exist.
    # if exists and files are present, then it will throw an error.
    copyfunc = shutil.copy if behavior == "copy" else shutil.move
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    if count <= 0:
        return
    # count files in subset folder.
    files = os.listdir(path)
    print("Files in subset folder : ", len(files))
    # Get all the files in the dataset.
    files = os.listdir(dataset)
    # exclude the text files.
    files = [file for file in files if file.split('.')[-1] != 'txt']
    print("Sampling from : ", len(files), " files.")
    # Shuffle the files.
    Random(seed).shuffle(files)
    # Copy the first count files to the new dataset.
    moved = 0
    pbar = tqdm(total=count)
    for file in files:
        if moved >= count:
            break
        if filter_func and not filter_func(os.path.abspath(os.path.join(dataset, file))):
            continue
        #print(f"Copying {file} to {path}")
        # if already exists, then skip.
        if os.path.exists(os.path.join(path, file)):
            continue
        copyfunc(os.path.join(dataset, file), path)
        moved += 1
        pbar.update(1)
        # Copy the corresponding text file.
        if os.path.exists(os.path.join(path, file.split('.')[0] + '.txt')):
            continue
        if dataset_tag_path:
            file_base = file.split('.')[0]
            if os.path.exists(os.path.join(dataset_tag_path, file_base + '.txt')):
                copyfunc(os.path.join(dataset_tag_path, file_base + '.txt'), path)
        else:
            if os.path.exists(os.path.join(dataset, file.split('.')[0] + '.txt')):
                copyfunc(os.path.join(dataset, file.split('.')[0] + '.txt'), path)

def filter_nsfw(filename):
    basename = os.path.basename(filename)
    # .txt
    tag_filename = basename.split('.')[0] + '.txt'
    # read, filter if "2girl"
    # get 2girls, 3girls, 4girls, 5girls, 6+girls, 2boys, 3boys, 4boys, 5boys, 6+boys, yuri
    list_to_filter = [
        "sex", 
        "penis",
        "nipples",
        "vaginal",
        "censored",
        "nude",
        "pussy",
        "cum",
        "mosaic_censoring",
        "cum_in_pussy",
        "bar_censor",
        "completely_nude",
        "pubic_hair",
        "testicles",
        "cowgirl_position",
        "clothed_sex",
        "uncensored",
        "group_sex",
        "doggystyle",
        "anal",
        "pussy_juice",
        "missionary",
        "anus",
        "scat",
        "guro",
        "intestines",
        "decapitation",
        "drugs",
        "bdsm"
    ]
    basename_path_dir = os.path.dirname(filename)
    tag_filename = os.path.join(basename_path_dir, tag_filename)
    if not os.path.exists(tag_filename):
        print(f"tag_filename: {tag_filename}")
        return False
    #print(f"tag_filename: {tag_filename}")
    with open(tag_filename, 'r',encoding='utf-8') as f:
        tags = f.read()
    if any(tag in tags for tag in list_to_filter):
        return True
    return False

filter_sfw = lambda x: not filter_nsfw(x)
