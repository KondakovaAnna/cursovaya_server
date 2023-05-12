import torch
from torch import nn
import os
import json
from torchvision import transforms as T
import torchvision.models as models
def init_weights(m):
    if isinstance(m, nn.Linear):
        torch.nn.init.kaiming_normal_(m.weight)
        torch.nn.init.zeros_(m.bias)
    if isinstance(m, nn.Conv2d):
        torch.nn.init.kaiming_normal_(m.weight)
        torch.nn.init.zeros_(m.bias)

class Idle(nn.Module):
    def __init__(self):
        super(Idle, self).__init__()

    def forward(self, x):
        return x

class MyResNet18(nn.Module):
    def __init__(self,
        labels_num = 38,
        chanel1_num = 128,
        input_size = 512
    ):
        super(MyResNet18, self).__init__()
        self.content = nn.Sequential(
            nn.Linear(input_size, chanel1_num),
            nn.ReLU(),
            nn.Linear(chanel1_num, labels_num))
        self.content.apply(init_weights)
        self.resnet = models.resnet18(pretrained = False)

    def forward(self, x):
        return self.content(self.resnet(x))

MODEL_PATH = os.getcwd() + "/nets/resnet18_train30ep_v2reg"
PREPROCESS_SETUP = T.Compose([
            T.Resize(32),
            T.ToTensor(),
            # T.Normalize(
            #     mean=[0.485, 0.456, 0.406],
            #     std=[0.229, 0.224, 0.225]
            # )
        ])

JSON_PATH = os.getcwd() + "/class_num.json"

class Model_predictor:
    def __init__(self) -> None:
        self.load_model()
        self.load_names_dict()
        pass

    def load_model(self):
        print("Loading model")
        self.model = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
        self.model.eval()

    def load_names_dict(self):
        with open(JSON_PATH, 'r') as j:
            json_data = json.load(j)
            self.class_names_data = {v: k for k, v in json_data.items()}

    def preproprocess_image(self, img):
        preprocess = PREPROCESS_SETUP
        img_t = preprocess(img)
        img_t = img_t.unsqueeze_(0)
        return img_t

    def prdict_with_model(self, image_tensor):
        scores = self.model(image_tensor)
        class_num = scores.data.cpu().numpy().argmax()
        name_class = self.class_names_data[class_num]
        return {"class_num": int(class_num), "class_name": name_class}

