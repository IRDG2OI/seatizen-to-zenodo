 
# ACKNOWLEDGEMENT

This project is being developed as part of the G2OI project, cofinanced by the European Union, the Reunion region, and the French Republic.
<div align="center">


<img src="https://github.com/IRDG2OI/geoflow-g2oi/blob/main/img/logos_partenaires.png?raw=True" height="80px">

</div>

# seatizen-to-zenodo



This repository contains three runnable Python scripts: **copy_folders.py**, **folders_preparation.py** and **zenodoDownloadWorkflow.py** <br/>
Those scripts will help you prepare your [Seatizen](https://ocean-indien.ifremer.fr/Projets/Innovations-technologiques/SEATIZEN-2020-2022) data before uploading it to Zenodo, and it also offers a solution to download specific data you uploaded on Zenodo.

## copy_folders.py
This script can be called in the **copy_folders.pbs** file to parallelize the copy of the sessions you want to process. <br/>
A use case example is available [here](https://github.com/alexandreBoy/seatizen-to-zenodo-example/blob/main/1_sessions_copy/copy_folders.pbs).

## zenodoDownloadWorkflow.py
You can use this script to download images from Zenodo based on a filtered csv file created from **metadata_image.csv**. <br/>
The csv file must have a column "Session_doi" that associate each image to a Zenodo DOI.

## folders_preparation.py

This is the main script to prepare your data. <br/>
It uses Jacques, a package to classify useless and useful images according to marine ecological interests. <br/>
See the [original repository](https://github.com/IRDG2OI/jacques) for more information on Jacques.

With the **folders_preparation.py** script, you can:

1. Apply the jacques classification model on each session, moving out every useless images.
2. Export the jacques classification results to a csv file.
3. Create annotations csv files from a given model, labels and thresholds.
4. Create a .txt file with jacques classification statistics (total images, number of useful/useless images, percentage of useless images in relation to total images).
5. Create a PDF preview for each session (composed of a trajectory map, 100 thumbnails of images representative of the session and a metadata sneak peek). 
6. Create zipped versions of each session folder.
7. Create a file metadata_image.csv that contains metadata of every session merged together.
8. Create a .txt file that describe the content of metadata_image.csv (total images, number of useful/useless images, percentage of useless images in relation of total images).
9. Create a global map showing the location of all images.

Depending on what you want to do, you may decide to carry out one step rather than another. <br/>
The **config.json** file will allow you to precisely do that. See the end of this README for more information on the configuration file.

:warning: This script can only be used on sessions folders that respect one of the architectures below:
```
1st architecture

YYYYMMDD_countrycode-optionalplace_device_nb
│
└───DCIM
└───GPS
│   └───BASE
│   └───DEVICE
└───METADATA
└───PROCESSED_DATA
│   └───BATHY
│   └───FRAMES
│   └───IA
│   └───PHOTOGRAMMETRY
└───SENSORS
```
OR
```
2sd architecture

YYYYMMDD_countrycode-optionalplace_device_nb
│
└───DCIM
└───GPS
└───LABEL
└───METADATA
```

### Installation
The installation can either be done locally or on datarmor. <br/>
:bulb: Datarmor is Ifremer's supercomputer on which you can parallelize code execution for a large amount of data.
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
4. Install **pytorch** and **jacques** in your working environment. </br>
See how to do that here: [Jacques](https://github.com/IRDG2OI/jacques)

5. Install **detectron2**
```
python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
```
6. Check the **requirements.txt** file and install with **pip** the packages that are missing in your environment.
#### Datarmor
1. Download the git repository as a ZIP and extract it in a folder of your datahome or clone the repository if you are able to do so.
2. Modify the following lines of **folders_preparation.pbs** with your own installation path.
```
cd /home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest
python /home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/folders_preparation.py 
```
3. Download the resnet model
```
wget https://download.pytorch.org/models/resnet50-11ad3fa6.pth
mv resnet50-11ad3fa6.pth ~/.cache/torch/hub/checkpoints/resnet50-11ad3fa6.pth
```
4. Check if you have access to ***'/home/datawork-iot-nos/Seatizen/conda-env/jacques_cpu'*** on Datarmor. <br/>
This is the folder where the execution environment is located.
### Usage
#### Local
1. Edit the **config.json** file with your local paths as described below.
2. Start the script in your Python environment by typing the following command:
```
python folders_preparation.py
```
This will process every session of the folder indicated in the config.json file. <br/>
If you want to process a specific session in the folder, you can do so by adding the argument **--session-index** to the previous command:
```
python folders_preparation.py --session-index 1
``` 
This will process the first session of the folder.

#### Datarmor
:man_student: You can find a use case example here: [seatizen-to-zenodo-example](https://github.com/alexandreBoy/seatizen-to-zenodo-example)
1. Edit the **config.json** file with your datarmor paths as described below.
2. Choose the right queue based on what you want to do:

***Creation of PDF previews and global trajectories map***:
```
#PBS -q ftp
```
:warning: Because this queue is the only one that can download maps from the internet, you should only be using it for maps creation and limit the number of parallel jobs you run to 6.

Here is the recommended configuration for the simultaneous creation of six PDF previews from six different sessions:
```
#PBS -q ftp
#PBS -l select=1:ncpus=2:mem=25g
#PBS -l walltime=00:15:00
#PBS -J 1-6
```
Some maps can take more or less memory to be generated, so adjust it accordingly.

***All other tasks:***
```
#PBS -q omp
```

3. Modify the number of cpu, memory and the execution time needed by editing the following lines in **folders_preparation.pbs**:
```
#PBS -l select=1:ncpus=8:mem=10g
#PBS -l walltime=07:00:00
```
If you are doing jacques classification, multilabel annotation and grass kelly annotation on 84 sessions that can contain up to 10 000 images each, above configuration should be enough. 

4. Indicate the **range of sessions** to be processed by adding or modifying the following line in **folders_preparation.pbs**:
```
#PBS -J 1-84
```
This means that you want to process the sessions 1 to 84 in the list of sessions you specified. <br/>
If you are adding this line, don't forget to add **$PBS_ARRAY_INDEX** here:
```
python /path/to/folders_preparation.py --session-index $PBS_ARRAY_INDEX
```

If you want to process only **one session**, you can do so by removing the **#PBS -J 1-84** line and replace **$PBS_ARRAY_INDEX** in the following line with the index of the session you want to process:
```
python /path/to/folders_preparation.py --session-index 1
```
This will only process the first session of the folder. <br/>

You can simply write the following if you want to process a **list of sessions** indicated in the config.json file:
```
python /path/to/folders_preparation.py
```
5. Indicate a name for the pbs log files that will be created in your working directory for each session processed:
```
#PBS -N parallelSessionsProcessing
```
6. Start the **folders_preparation.pbs** script:
```
qsub -m bea -M prenom.nom@yourmail.com folders_preparation.pbs
```
:bulb: By indicating your email in this command, you will be notified when the script starts and when it ends.

## config.json
This is the configuration file for the **folders_preparation.py** script. Here is a description of it's variables:

- **jacques_model_path** <br/>
It's the path to the jacques model. <br/>
(ex: ***'/home/datawork-iot-nos/Seatizen/models/useless_classification/version_alexmatteo_20230904/version_13/checkpoints/epoch=8-step=2817.ckpt'***) <br/>
You can leave the quotes empty if you don't want to use the jacques classification model.

- **annotation_model_path** <br/>
There you can add models names and their associated paths. Models names must match the ones defined in **annotation_csv_path** and **threshold_labels**.<br/>
(ex: ***{"multilabel": "/home/datawork-iot-nos/Seatizen/mauritius_use_case/Mauritius/models/multilabel_with_sable.pth", "grass_kelly": "/home/datawork-iot-nos/Seatizen/models/stage_leanne/herbier_classification/lightning_logs/version_31/checkpoints/epoch=7-step=688.ckpt"}***) <br/>
You can leave the brackets empty if you don't want to use any model.

- **sessions_path** <br/>
This path must be provided. It's the list of sessions, it can be either the path to a single directory which contains all sessions: <br/>
(ex: ***'/my/path/to/my_sessions/'*** or a list of sessions paths:
***['/my/path/to/session1', '/my/path/to/session2']***)

- **zipped_sessions_path** <br/>
It's the path to the folder where you want to create the zipped version of each session: <br/>
(ex:***'/my/path/to/zip_folder/'***) <br/>
If you don't want to zip the sessions, do not fill in a path, leave the quotes empty. <br/>
:warning: This path must be provided if **pdf_preview** is true: only the pdf previews will be created, sessions will not be zipped.

- **global_data_path** <br/>
You can provide this path to enable the creation of the **metadata_image.csv** file. <br/>
(ex:***'/my/path/to/global_data/'***) <br/>
:warning: This path must be provided if **global_trajectory_map** is true.

- **useless_images_path** <br/>
It's the folder path where useless images will be moved. <br/>
(ex: ***'/my/path/to/useless_images_folder/'***) <br/>
If you don't want to move the useless images, leave the quotes empty.

- **annotation_csv_path** <br/>
There you can define the paths where annotations csv will be created for each model. <br/>
Models names must match the ones defined in **annotation_model_path** and **threshold_labels**. <br/>
(ex: ***{"multilabel": "/my/path/to/multilabel_annotation_.csv", "grass_kelly": "/my/path/to/grass_kelly_annotation_.csv"}***) <br/>
You can leave the brackets empty if you don't want to use any model.

- **threshold_labels** <br/>
There you can associate each model to it's labels and corresponding thresholds. <br/>
(ex: ***{"multilabel": {"Acropore_branched": 0.56, "Acropore_digitised": 0.48,...},"grass_kelly": {"herbier": 0.592}}***)

- **delete_before_after_useless** <br/>
Boolean value to enable or disable the deletion of the folders **BEFORE**, **AFTER** and **USELESS** if they exist. Can either be **true** or **false**.

- **global_trajectory_map** <br/>
Boolean value to indicate if the user wants to create the global trajectory map or not. Can either be **true** or **false**.

- **pdf_preview** <br/>
Boolean value to indicate if a pdf preview will be created for each session. Can either be **true** or **false**.

---
<div align="center">

This project is being developed as part of the G2OI project, cofinanced by the European Union, the Reunion region, and the French Republic.

<img src="https://github.com/IRDG2OI/seatizen-to-zenodo/blob/main/docs/logos_partenaires.png?raw=True" height="40px">

</div>
