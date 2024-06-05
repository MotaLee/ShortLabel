import json
import threading

from utils.torch_utils import select_device
from utils.general import check_img_size
from utils.general import non_max_suppression
from utils.general import print_args, scale_coords, xyxy2xywh
from utils.datasets import LoadImages
from models.experimental import attempt_load

import argparse
import os
import sys
from pathlib import Path

import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--weights",
        nargs="+",
        type=str,
        default="Lib/Yolov5/Pt/best.pt",
        help="model path(s)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=r"C:\Work\ExProject\LSSEx\Dataset\240425\4.mp4",
        help="file/dir/URL/glob, 0 for webcam",
    )
    parser.add_argument(
        "--imgsz",
        "--img",
        "--img-size",
        nargs="+",
        type=int,
        default=[640],
        help="inference size h,w",
    )
    parser.add_argument(
        "--conf-thres", type=float, default=0.25, help="confidence threshold"
    )
    parser.add_argument(
        "--iou-thres", type=float, default=0.45, help="NMS IoU threshold"
    )
    parser.add_argument(
        "--max-det", type=int, default=1000, help="maximum detections per image"
    )
    parser.add_argument(
        "--device", default="", help="cuda device, i.e. 0 or 0,1,2,3 or cpu"
    )
    parser.add_argument(
        "--view-img", action="store_true", default=False, help="show results"
    )
    parser.add_argument("--save-txt", action="store_true", help="save results to *.txt")
    parser.add_argument(
        "--save-conf", action="store_true", help="save confidences in --save-txt labels"
    )
    parser.add_argument(
        "--save-crop", action="store_true", help="save cropped prediction boxes"
    )
    parser.add_argument(
        "--nosave", action="store_true", default=True, help="do not save images/videos"
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        type=int,
        help="filter by class: --classes 0, or --classes 0 2 3",
    )
    parser.add_argument(
        "--agnostic-nms", action="store_true", help="class-agnostic NMS"
    )
    parser.add_argument("--augment", action="store_true", help="augmented inference")
    parser.add_argument("--visualize", action="store_true", help="visualize features")
    parser.add_argument("--update", action="store_true", help="update all models")
    parser.add_argument(
        "--project", default=ROOT / "runs/detect", help="save results to project/name"
    )
    parser.add_argument("--name", default="exp", help="save results to project/name")
    parser.add_argument(
        "--exist-ok",
        action="store_true",
        help="existing project/name ok, do not increment",
    )
    parser.add_argument(
        "--line-thickness", default=3, type=int, help="bounding box thickness (pixels)"
    )
    parser.add_argument(
        "--hide-labels", default=False, action="store_true", help="hide labels"
    )
    parser.add_argument(
        "--hide-conf", default=False, action="store_true", help="hide confidences"
    )
    parser.add_argument(
        "--dnn", action="store_true", help="use OpenCV DNN for ONNX inference"
    )
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(FILE.stem, opt)
    return opt


class Yolov5:
    def __init__(self) -> None:
        self.Source = ""
        self.Weights = ""
        self.Confidence = 0.3
        self.IOU = 0.45
        self.FlagIdle = False
        self.FlagRun = True
        self.Boxes = list()
        return

    def loadModel(self, **opt):
        self.Weights = opt.get("weights")
        imgsz = [640]
        imgsz *= 2 if len(imgsz) == 1 else 1

        weights = self.Weights
        device = select_device("")

        stride = 64
        names = [f"class{i}" for i in range(1000)]  # assign defaults

        model = attempt_load(weights, map_location=device)
        stride = int(model.stride.max())  # model stride
        names = (
            model.module.names if hasattr(model, "module") else model.names
        )  # get class names

        imgsz = check_img_size(imgsz, s=stride)  # check image size

        self.Stride = stride
        self.Model = model
        self.Device = device
        self.ImgSize = imgsz
        self.Names = names
        return True

    def detect(self, source=""):
        self.FlagIdle = False

        if source == "":
            source = self.Source

        # Dataloader
        dataset = LoadImages(source, img_size=self.ImgSize, stride=self.Stride)

        # Run inference
        if self.Device.type != "cpu":
            # run once
            self.Model(
                torch.zeros(1, 3, *self.ImgSize)
                .to(self.Device)
                .type_as(next(self.Model.parameters()))
            )

        seen = 0
        boxes = []
        for path, img, im0s, vid_cap in dataset:
            img = torch.from_numpy(img).to(self.Device)
            img = img.float() / 255.0
            if len(img.shape) == 3:
                img = img[None]  # expand for batch dim

            # Inference
            if True:
                pred = self.Model(img, augment=False, visualize=False)[0]

            # NMS
            pred = non_max_suppression(
                pred, self.Confidence, self.IOU, None, False, max_det=1000
            )

            # Process predictions
            for i, det in enumerate(pred):  # per image
                seen += 1
                im0 = im0s.copy()

                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]
                if len(det):
                    det[:, :4] = scale_coords(
                        img.shape[2:], det[:, :4], im0.shape
                    ).round()

                    for *xyxy, conf, cls in reversed(det):
                        xywh = (
                            (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn)
                            .view(-1)
                            .tolist()
                        )
                        boxes.append([int(cls), int(conf), *xywh])

        ret = {"Result": True, "Source": self.Source, "Boxes": boxes}
        sys.stdout.write(json.dumps(ret) + "\r\n")
        sys.stdout.flush()
        self.Source = ""
        self.FlagIdle = True
        return boxes

    def run(self):
        import _winapi
        import msvcrt

        fn = sys.stdin.fileno()
        sys.stdin = os.fdopen(fn)

        opt = parse_opt()

        handle = msvcrt.get_osfhandle(sys.stdin.fileno())

        try:
            self.FlagIdle = self.loadModel(**vars(opt))
        except BaseException as e:
            self.FlagRun = False
        while self.FlagRun:
            j = None
            try:
                read, avail_count = _winapi.PeekNamedPipe(handle, 0)
                if read > 0:
                    data, errcode = _winapi.ReadFile(handle, read)
                    j = json.loads(data.decode())
            except BaseException as e:
                pass

            if j is not None:
                cmd = j["Command"]
                if cmd == "isIdle":
                    ret = {"Return": self.FlagIdle, "Command": "isIdle"}
                    sys.stdout.write(json.dumps(ret) + "\r\n")
                    sys.stdout.flush()
                elif cmd == "detect":
                    self.Source = j["Source"]
                    if self.Source != "" and self.FlagIdle:
                        thd = threading.Thread(target=self.detect)
                        thd.start()
        return

    pass


if __name__ == "__main__":
    yolo = Yolov5()
    yolo.run()
