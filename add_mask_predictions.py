from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from detectron2.structures import Boxes, Instances
from torchvision.transforms import functional as func
from torchvision.ops import nms
from io import BytesIO
from PIL import Image
import numpy as np
import torch
import imageio.v3 as iio
import tempfile
import os
import requests
import fiftyone as fo
import fiftyone.utils.annotations as foua
import fiftyone.utils.labels as foul
import warnings

warnings.simplefilter(action = "ignore", category = RuntimeWarning)


def build_predictor(checkpoint, device, num_classes):
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes
    cfg.MODEL.WEIGHTS = checkpoint
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5 
    cfg.MODEL.DEVICE = device
    predictor = DefaultPredictor(cfg)
    return predictor


def predict(predictor, image):
    # image = cv2.imread(filepath)
    image = np.array(image)
    outputs = predictor(image)
    return outputs


def crop_mask(bbox, mask):
    ''' Input : 
        bbox : the bounding box of the object predicted.
        mask : the mask of the object predicted returned bu detectron2 (it is actually a mask for the whole image
        and 51 requires a mask within the bbox)

        Output: 
        a cropped mask corresponding to the inside of the bbox for the predicted object.'''

    x1, y1, x2, y2 = bbox.cpu().detach().numpy().astype(np.int32)
    return mask[y1:y2, x1:x2]


def predict_species(image, predictor, device, classes, nms_threshold=1):
    '''predict species occurrences on an image

    Inputs:
    - image_path : a path to an image
    - predictor : the result of build_predictor() 
    - device : whether to load data on cpu or gpu
    - classes : a list of the classes predicted by the model

    Outputs :
    - predictions of the model in a fiftyone detections field
    '''
    # response = requests.get(image_path)
    # image = Image.open(BytesIO(response.content))
    image_tensor = func.to_tensor(image).to(device)
    c, h, w = image_tensor.shape

    preds = predict(predictor, image)

    preds = apply_nms(preds, nms_threshold)
    
    labels = preds['instances'].pred_classes.cpu().detach().numpy()
    scores = preds['instances'].scores.cpu().detach().numpy()
    boxes = preds['instances'].pred_boxes
    masks = preds['instances'].pred_masks.cpu().detach().numpy()

    predictions = []
    for label, score, box, mask in zip(labels, scores, boxes, masks):
        # Convert to [top-left-x, top-left-y, width, height]
        # in relative coordinates in [0, 1] x [0, 1]
        x1, y1, x2, y2 = box
        rel_box = [x1 / w, y1 / h, (x2 - x1) / w, (y2 - y1) / h]
        
        mask = crop_mask(box, mask)

        predictions.append(
            fo.Detection(
                label=classes[label],
                bounding_box=rel_box,
                confidence=score, 
                mask=mask
            )
        )

    return predictions


def apply_nms(outputs, nms_treshold) :
    ''' 
    Inputs :
    1.outputs = list[dict] in the "outputs" inference format of detectron2 lib, 
    see : https://detectron2.readthedocs.io/en/latest/tutorials/models.html
    2.nms_treshold = Overlap threshold used for non-maximum suppression (suppress boxes with
                      IoU >= this threshold)
    
    Outputs :
    The function applies the NMS technique for predictions of different class types,
    the default Detectron2 parameter MODEL.ROI_HEADS.NMS_THRESH_TEST applies NMS only
    for same class types instances :
    see :
    https://github.com/facebookresearch/detectron2/issues/978
    1.res = list[dict] in the "outputs" inference format of detectron2 lib 
    '''

    detections = outputs['instances']
    pred_boxes = detections.pred_boxes.tensor
    scores = detections.scores
    pred_classes = detections.pred_classes
    pred_masks = detections.pred_masks
    image_size = detections.image_size
    # Performs non-maximum suppression (NMS) on the boxes according to their intersection-over-union (IoU).
    # see :
    # https://pytorch.org/vision/stable/generated/torchvision.ops.nms.html#torchvision.ops.nms
    keep_idx = nms(pred_boxes, scores, nms_treshold)
    res = Instances(image_size)
    res.pred_boxes = Boxes(pred_boxes[keep_idx])
    res.scores = scores[keep_idx]
    res.pred_classes = pred_classes[keep_idx]
    res.pred_masks = pred_masks[keep_idx]
    res = {"instances": res}
    
    return res

def predict_image(images_path, outpath):
    # Paths and variables settings
    # image_name = image_url.split("/")[-1].split(".")[0]
    # response = requests.get(image_url)
    # img = Image.open(BytesIO(response.content))
    
    # Load the list of images of the given path
    image_list = os.listdir(images_path)
    for i in range(len(image_list)):
        img = os.path.join(images_path, image_list[i])
        image_name = img.split("/")[-1]
        image = np.array(Image.open(img))
        
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        iio.imwrite(temp_file.name, image, extension=".jpeg")
        temp_file.close()
        
        # image = utils.data.read_image(temp_file.name)
        
        checkpoint_path = '2022-06-15_LR_0.00025_BATCH_2_ITER_150000_1655286559.4163053/model_final.pth'
        device = ("cuda" if torch.cuda.is_available() else "cpu")
        
        thing_classes = [
            'sea cucumber', 'Syringodium isoetifolium', 'Sand', 'Scrap', 
            'Rock', 'Trample', 'Waste', 'Acropore Branched', 
            'Acropore Digitised', 'Acropore Sub-massive', 'Acropore Tabular', 'No acropore Branched', 
            'No acropore Encrusting', 'No acropore Foliaceous', 'No acropore Massive', 'No acropore Sub massive', 
            'No acropore Solitary', 'Millepore', 'Dead coral', 'fish', 
            'Sponge', 'Sea urchins', 'Clam', 'Algae Limestone', 
            'Algae Drawn up', 'Algae assembly', 'Soft coral', 'Living Coral', 
            'Bleached coral'
            ]
        
        # Building the model from the checkpoint
        model = build_predictor(checkpoint_path, device, len(thing_classes))
        
        # Image prediction with the help of the model
        predictions = predict_species(
            image=image,
            predictor=model,
            device=device,
            classes=thing_classes
            )
        
        # Configuring the display of predictions on the image
        # Mapping between the prediction and the image, export of the image annotated by the model to a folder
        sample = fo.Sample(
            temp_file.name,
            pred_objects=fo.Detections(detections=predictions)
            )
        
        dataset_one_sample = fo.Dataset(name="seatizen_app", persistent=False, overwrite=True)
    
        dataset_one_sample.add_sample(sample)
    
        foul.instances_to_polylines(
            dataset_one_sample,
            in_field='pred_objects',
            out_field='IA'
        )
        
        config = foua.DrawConfig(
            {
                "show_object_boxes" : False,
                "font_size" : 10,
                "show_polyline_labels":True,
                "show_polyline_attr_confidences":False,
                "per_polyline_label_colors":True,
                "per_polyline_name_colors":True,
                "polyline_alpha":0.4,
                "polyline_linewidth":2,
                "fill_polylines":True
            }
        )
        
        foua.draw_labeled_image(
            dataset_one_sample.first(),
            outpath=os.path.join(outpath, f'predicted_{image_name}.jpg'), # f'predicted_images/predicted_{image_name}.jpg'
            label_fields="IA",
            config=config
            )
    
        os.unlink(temp_file.name)
