from roboflow.models.classification import ClassificationModel
from roboflow.models.object_detection import ObjectDetectionModel
import os
import json
import requests
import urllib
import wget
import zipfile
from roboflow.config import *
import sys
from tqdm import tqdm

from dotenv import load_dotenv

load_dotenv()


class Version():
    def __init__(self, version_dict, type, api_key, name, version, model_format, local):
        self.__api_key = api_key
        self.name = name
        self.version = version
        self.type = type
        self.augmentation = version_dict['augmentation']
        self.created = version_dict['created']
        self.id = version_dict['id']
        self.images = version_dict['images']
        self.preprocessing = version_dict['preprocessing']
        self.splits = version_dict['splits']
        self.model_format = model_format

        version_without_workspace = os.path.basename(version)

        if self.type == "object-detection":
            self.model = ObjectDetectionModel(self.__api_key, self.id, self.name, version_without_workspace, local=local)
        elif self.type == "classification":
            self.model = ClassificationModel(self.__api_key, self.id, self.name, version_without_workspace, self.id, local=local)
        else:
            self.model = None


    def download(self, download_type=None, location=None):
        
        if location == None:
            location = '../datasets/' + self.name + "-" +  self.version

        if not os.path.exists(location):
            os.makedirs(location)

        if download_type == None:
            if self.model_format == 'yolov5':
                download_type = 'yolov5pytorch'
            else:
                RuntimeError("You must pass a download_type to version.download() or define model in your Roboflow object")

        url = self.__get_download_url(download_type)
        resp = requests.get(url)
        if resp.status_code == 200: 
            link = resp.json()['export']['link']
    
            def bar_progress(current, total, width=80):
                progress_message = "Downloading Dataset Version Zip in " + location + " to " + download_type + ": %d%% [%d / %d] bytes" % (current / total * 100, current, total)
                sys.stdout.write("\r" + progress_message)
                sys.stdout.flush()
            
            wget.download(link, out=location + "/roboflow.zip", bar=bar_progress)
            sys.stdout.write("\n")
            sys.stdout.flush()

            with zipfile.ZipFile(location + "/roboflow.zip", 'r') as zip_ref:
                for member in tqdm(zip_ref.infolist(), desc="Extracting Dataset Version Zip to " + location + " in " + download_type + ":"):
                    try:
                        zip_ref.extract(member, location)
                    except zipfile.error as e:
                        pass

            os.remove(location + '/roboflow.zip')
        else:
            raise RuntimeError(resp.json())



    def __get_download_url(self, download_type):
        temporary = self.id.rsplit("/")
        workspace, project = temporary[0], temporary[1]
        url = "".join([
            API_URL + '/' + workspace + '/' + project,
            "/" + self.version,
            "/" + download_type,
            "?api_key=" + self.__api_key,
            ])
        return url



    def __str__(self):
        json_value = {
            'name': self.name,
            'type': self.type,
            'version': self.version,
            'augmentation': self.augmentation,
            'created': self.created,
            'preprocessing': self.preprocessing,
            'splits': self.splits}
        return json.dumps(json_value, indent=2)