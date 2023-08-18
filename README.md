<div align="center">

# seatizen-to-zenodo

</div>
</br>

## folders_preparation.py

This Python script will help you prepare your [seatizen](https://ocean-indien.ifremer.fr/Projets/Innovations-technologiques/SEATIZEN-2020-2022) data before uploading it to Zenodo. <br/>
It uses Jacques, a package to classify useless and useful images according to marine ecological interests. <br/>
See the [original repository](https://github.com/IRDG2OI/jacques) for more informations on Jacques.

The execution of the **folders_preparation.py** script will:

1. Apply the jacques classification model on each session, moving out every useless images.
2. Export the jacques classification results to a csv file.
3. Create an annotations csv file from the given model, labels and thresholds.

### Installation
#### Local
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
See how to do that here: [Jacques](https://github.com/IRDG2OI/jacques)

5. Install detectron2
```
python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
```
6. Install fiftyone
```
pip install fiftyone
```
#### Datarmor
1. Download the git repository as a ZIP and extract it in a folder of your datahome.
2. Modify lines 15 and 21 of folders_preparation.pbs with your installation path.

### Usage
#### Local
1. Edit the **config.json** file with your local paths as described below.
2. Start the script in your Python environment by typing the following command:
```
python folders_preparation.py
```

#### Datarmor
1. Edit the **config.json** file with your datarmor paths as described below.
2. Indicate the range of sessions to be processed by modifying line 5 of **folders_prepation.pbs**:
```
#PBS -J 5-70
```
This means that you want to process the sessions 5 to 70 in the list of sessions you specified.

3. Start the **folders_preparation.pbs** script:
```
qsub -m bea -M prenom.nom@yourmail.com folders_preparation.pbs
```
By indicating your email in this command, you will be notified when the script starts and when it ends.

## config.json
This is the configuration file for the **folders_preparation.py** script. Here is a description of it's variables:

- **jacques_model_path** <br/>
It's the path to the jacques model. <br/>
(ex: ***'/home/datawork-iot-nos/Seatizen/models/useless_classification/version_17/checkpoints/epoch=7-step=2056.ckpt'***)

- **annotation_model_path** <br/>
It's the path to the annotation model. <br/>
(ex: ***'/home/datawork-iot-nos/Seatizen/models/stage_leanne/herbier_classification/lightning_logs/version_17/checkpoints/epoch=8-step=620.ckpt'***)

- **sessions_path** <br/>
It's the list of sessions, it can be either the path to a single directory that contains every sessions: <br/>
***'/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions/'*** or a list of sessions paths: <br/>
***['/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions/session_2017_11_19_paddle_Black_Rocks']***

- **useless_images_path** <br/>
It's the folder path where useless images will me moved. <br/>
(ex: ***'/home3/datawork/aboyer/mauritiusSessionsOutput/useless_images/'***)

- **annotation_csv_path** <br/>
It's the folder path where annotations csv will be created.<br/>(ex: ***'/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/test/output/results_csv/multilabel_annotation_.csv'***)

- **nb_sessions** <br/>
Max number of sessions to process.

- **threshold_labels** <br/>
It's a dictionnary where the keys are the annotation model labels and the values are their associated thresholds. <br/>
(ex: ***{"herbier": 0.592}***)

---
<div align="center">

This project is being developed as part of the G2OI project, cofinanced by the European union, the Reunion region, and the French Republic.

<img src="https://github.com/IRDG2OI/seatizen-to-zenodo/blob/main/docs/logos_partenaires.png?raw=True" height="40px">

</div>