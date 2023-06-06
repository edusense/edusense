from __future__ import print_function
import torch
import torch.backends.cudnn as cudnn
import numpy as np
import sys
sys.path.insert(0, "./retinaface/")
from data import cfg_mnet, cfg_re50
from layers.functions.prior_box import PriorBox
from retinaface.utils.nms.py_cpu_nms import py_cpu_nms
from retinaface.models.retinaface import RetinaFace
from retinaface.utils.box_utils import decode, decode_landm
from retinaface.utils.timer import Timer
import cv2

def check_keys(model, pretrained_state_dict):
    ckpt_keys = set(pretrained_state_dict.keys())
    model_keys = set(model.state_dict().keys())
    used_pretrained_keys = model_keys & ckpt_keys
    unused_pretrained_keys = ckpt_keys - model_keys
    missing_keys = model_keys - ckpt_keys
    # print('Missing keys:{}'.format(len(missing_keys)))
    # print('Unused checkpoint keys:{}'.format(len(unused_pretrained_keys)))
    # print('Used keys:{}'.format(len(used_pretrained_keys)))
    assert len(used_pretrained_keys) > 0, 'load NONE from pretrained checkpoint'
    return True


def remove_prefix(state_dict, prefix):
    ''' Old style model is stored with all names of parameters sharing common prefix 'module.' '''
    # print('remove prefix \'{}\''.format(prefix))
    f = lambda x: x.split(prefix, 1)[-1] if x.startswith(prefix) else x
    return {f(key): value for key, value in state_dict.items()}


def load_model(model, pretrained_path, load_to_cpu, device):
    # print('Loading pretrained model from {}'.format(pretrained_path))
    if load_to_cpu:
        pretrained_dict = torch.load(pretrained_path, map_location=lambda storage, loc: storage)
    else:
        # device = torch.cuda.current_device()
        pretrained_dict = torch.load(pretrained_path, map_location=lambda storage, loc: storage.cuda(device))
    if "state_dict" in pretrained_dict.keys():
        pretrained_dict = remove_prefix(pretrained_dict['state_dict'], 'module.')
    else:
        pretrained_dict = remove_prefix(pretrained_dict, 'module.')
    check_keys(model, pretrained_dict)
    model.load_state_dict(pretrained_dict, strict=False)
    return model


class RetinaFaceInference(object):
    def __init__(self, threshold = 0.5, network="mobile0.25", device='cuda:0'):
        torch.set_grad_enabled(False)
        cfg = None
        if network == "mobile0.25":
            cfg = cfg_mnet
        elif network == "resnet50":
            cfg = cfg_re50
        # net and model
        net = RetinaFace(cfg=cfg, phase = 'test', device=device)
        net = load_model(net, "./models/retinaface/mobilenet0.25_Final.pth", False,device)
        net.eval()
        # print('Finished loading model!')
        # print(net)
        cudnn.benchmark = True
        self.device = device
        net = net.to(self.device)
        self.net = net
        torch.set_grad_enabled(False)
        self._t = {'forward_pass': Timer(), 'misc': Timer()}
        self.cfg = cfg
        self.threshold = threshold

    def run(self, img, frame_debug=None):

        img = np.float32(img)
        im_height, im_width, _ = img.shape
        scale = torch.Tensor([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
        img -= (104, 117, 123)
        img = img.transpose(2, 0, 1)
        img = torch.from_numpy(img).unsqueeze(0)
        img = img.to(self.device)
        scale = scale.to(self.device)

        try:
            self._t['forward_pass'].tic()
            loc, conf, landms = self.net(img)  # forward pass
            self._t['forward_pass'].toc()
            self._t['misc'].tic()
            priorbox = PriorBox(self.cfg, image_size=(im_height, im_width))
            priors = priorbox.forward()
            priors = priors.to(self.device)
            prior_data = priors.data
            boxes = decode(loc.data.squeeze(0), prior_data, self.cfg['variance'])
            boxes = boxes * scale / 1
            boxes = boxes.cpu().numpy()
            scores = conf.squeeze(0).data.cpu().numpy()[:, 1]
            landms = decode_landm(landms.data.squeeze(0), prior_data, self.cfg['variance'])
            scale1 = torch.Tensor([img.shape[3], img.shape[2], img.shape[3], img.shape[2],
                                   img.shape[3], img.shape[2], img.shape[3], img.shape[2],
                                   img.shape[3], img.shape[2]])
            scale1 = scale1.to(self.device)
            landms = landms * scale1 / 1
            landms = landms.cpu().numpy()

            confidence_threshold = 0.02
            # ignore low scores
            inds = np.where(scores > confidence_threshold)[0]
            boxes = boxes[inds]
            landms = landms[inds]
            scores = scores[inds]

            # keep top-K before NMS
            # order = scores.argsort()[::-1][:args.top_k]
            order = scores.argsort()[::-1]
            boxes = boxes[order]
            landms = landms[order]
            scores = scores[order]
            nms_threshold = 0.4
            # do NMS
            dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
            keep = py_cpu_nms(dets, nms_threshold)

            dets = dets[keep, :]
            landms = landms[keep]

            # keep top-K faster NMS
            # dets = dets[:args.keep_top_k, :]
            # landms = landms[:args.keep_top_k, :]

            dets = np.concatenate((dets, landms), axis=1)
            self._t['misc'].toc()

            conf = dets[:, 4]
            filtered_idx = np.where(conf > self.threshold)
            dets = dets[filtered_idx[0]]

            if frame_debug is not None:
                frame_debug = self.debug(dets, frame_debug)
            else:
                frame_debug = img

            return dets, frame_debug
        except:
            return np.array([]), None

    def debug(self, dets, image):
        
        for b in dets:
            text = "{:.4f}".format(b[4])
            b = list(map(int, b))
            cv2.rectangle(image, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
            cx = b[0]
            cy = b[1] + 12
            cv2.putText(image, text, (cx, cy),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

            # landms
            cv2.circle(image, (b[5], b[6]), 1, (0, 0, 255), 4)
            cv2.circle(image, (b[7], b[8]), 1, (0, 255, 255), 4)
            cv2.circle(image, (b[9], b[10]), 1, (255, 0, 255), 4)
            cv2.circle(image, (b[11], b[12]), 1, (0, 255, 0), 4)
            cv2.circle(image, (b[13], b[14]), 1, (255, 0, 0), 4)


        return image

