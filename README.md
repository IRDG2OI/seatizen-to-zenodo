<div align="center">

# seatizen-to-zenodo

</div>

## folders_preparation.py

This Python script will help you prepare your [seatizen](https://ocean-indien.ifremer.fr/Projets/Innovations-technologiques/SEATIZEN-2020-2022) data before uploading it to Zenodo. <br/>
It uses Jacques, a package to classify useless and useful images according to marine ecological interests.

### Installation

1. Clone the git repository
```
cd path/to/installation/folder/
git clone https://github.com/IRDG2OI/seatizen-to-zenodo.git
cd seatizen-to-zenodo/
```
2. Create your own Python environment in the cloned Git project.
```
python -m venv env
```
3. Activate the environment
```
Windows
.\env\Scripts\activate

Linux
source ./env/bin/activate
```
4. Install pytorch and jacques in your working environment. </br>
See how to do that here: [Jacques](https://github.com/6tronl/jacques/tree/v0.2.1)

5. Install detectron2
```
python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
```
6. Install fiftyone
```
pip install fiftyone
```

### Usage
Load all the imports then use the function **restructure_sessions()** in order to restructure the sessions folders of your choice to be Zenodo ready. <br/>
This function takes eight arguments:
- **sessions** <br/>
It's the list of sessions, it can be either a single directory that contains every sessions (ex: ***'sessions/'***) or a list of sessions paths. (ex: ***['sessions/session_2017_11_19_paddle_Black_Rocks']***).

- **dest_path** <br/>
It's the folder path where useless images will me moved. <br/>
(ex: ***'useless/session_2017_11_19_paddle_Black_Rocks_useless_images/'***)

- **class_path** <br/>
It's the folder path where classification result csv will be written.<br/> (ex: ***'results_csv/classifications_results.csv'***)

- **annot_path** <br/>
It's the folder path where multilabel annotations csv will be created.<br/>(ex: ***'results_csv/annotations_.csv'***)

- **output_txt_path** <br/>
It's the folder path where a txt file will be created to monitor multilabel annotations progression. <br/>(ex: ***'results_txt/output_.txt'***)

- **merged_csv_path** <br/>
It's the path where annotation csv will be merged with gps infos to create a new csv. <br/>(ex: **'results_csv/merged_.csv'**)

- **thresholds_csv_path** <br/>
It's the path where the csv file with thresholds values is located.

- **final_csv_path** <br/>
It's where the final csv file will be created. <br/>(ex: **'results_csv/final_.csv'**)

The execution of **restructure_sessions(sessions, dest_path, class_path, annot_path, output_txt_path, merged_csv_path, thresholds_csv_path, final_csv_path)** will:
1. Apply the jacques classification model on each session, moving every useless images to **dest_path**.
2. Export the classification results to a csv file written at **class_path**.
3. Delete BEFORE and AFTER folders if they exists.
4. Create multilabel annotations csv at **annot_path**.
5. Merge multilabel annotations with gps informations (latitude, longitude and date) at **merged_csv_path**.
6. Apply probabilities thresholds to the multilabel annotations values and create the final csv file at **final_csv_path**.

---
<div align="center">

This project is being developed as part of the G2OI project, cofinanced by the European union, the Reunion region, and the French Republic.

<img src="https://github.com/alexandreBoy/seatizen-to-zenodo/blob/main/docs/logos_partenaires.png?raw=True" height="40px">

</div>