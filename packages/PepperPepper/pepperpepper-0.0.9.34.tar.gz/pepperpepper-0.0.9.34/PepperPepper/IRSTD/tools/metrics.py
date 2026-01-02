from PepperPepper.environment import threading, np, torch, F, cv2
from skimage import measure
import tqdm

__all__ = ['SegmentationMetricTPFNFP', 'PD_FA']

def get_miou_prec_recall_fscore(total_tp, total_fp, total_fn):
    miou = 1.0 * total_tp / (np.spacing(1) + total_tp + total_fp + total_fn)
    prec = 1.0 * total_tp / (np.spacing(1) + total_tp + total_fp)
    recall = 1.0 * total_tp / (np.spacing(1) + total_tp + total_fn)
    fscore = 2.0 * prec * recall / (np.spacing(1) + prec + recall)

    return miou, prec, recall, fscore

class SegmentationMetricTPFNFP(object):
    """Computes pixAcc and mIoU metric scroes
    """

    def __init__(self, nclass):
        self.nclass = nclass
        self.lock = threading.Lock()
        self.reset()

    def update(self, labels, preds):
        def evaluate_worker(self, label, pred):
            tp, fp, fn = batch_tp_fp_fn(pred, label, self.nclass)
            with self.lock:
                self.total_tp += tp
                self.total_fp += fp
                self.total_fn += fn
                self.single_iou += 1.0 * tp / (np.spacing(1) + tp + fp + fn)
                self.sample_num += 1
            return

        if isinstance(preds, torch.Tensor):
            preds = (preds.detach().numpy() > 0).astype('int64')  # P
            labels = labels.numpy().astype('int64')  # T
            evaluate_worker(self, labels, preds)
        elif isinstance(preds, (list, tuple)):
            threads = [threading.Thread(target=evaluate_worker,
                                        args=(self, label, pred),
                                        )
                       for (label, pred) in zip(labels, preds)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        #elif preds.dtype == numpy.uint8:
        elif isinstance(preds, np.ndarray):
            preds = ((preds / np.max(preds)) > 0.5).astype('int64')  # P
            labels = (labels / np.max(labels)).astype('int64')  # T
            evaluate_worker(self, labels, preds)
        else:
            raise NotImplemented

    def get_all(self):
        return self.total_tp, self.total_fp, self.total_fn

    def get(self):
        miou, prec, recall, fscore = get_miou_prec_recall_fscore(self.total_tp, self.total_fp, self.total_fn)
        niou = self.single_iou / self.sample_num
        return miou, prec, recall, fscore, niou

    def reset(self):
        self.total_tp = 0
        self.total_fp = 0
        self.total_fn = 0
        self.single_iou = 0
        self.sample_num = 0
        return

def batch_tp_fp_fn(predict, target, nclass):
    """Batch Intersection of Union
    Args:
        predict: input 4D tensor
        target: label 3D tensor
        nclass: number of categories (int)
    """

    mini = 1
    maxi = nclass
    nbins = nclass

    # predict = (output.detach().numpy() > 0).astype('int64')  # P
    # target = target.numpy().astype('int64')  # T
    intersection = predict * (predict == target)  # TP

    # areas of intersection and union
    area_inter, _ = np.histogram(intersection, bins=nbins, range=(mini, maxi))
    area_pred, _ = np.histogram(predict, bins=nbins, range=(mini, maxi))
    area_lab, _ = np.histogram(target, bins=nbins, range=(mini, maxi))

    # areas of TN FP FN
    area_tp = area_inter[0]
    area_fp = area_pred[0] - area_inter[0]
    area_fn = area_lab[0] - area_inter[0]

    # area_union = area_pred + area_lab - area_inter
    assert area_tp <= (area_tp + area_fn + area_fp)
    return area_tp, area_fp, area_fn

class PD_FA():
    def __init__(self, nclass, bins, size):
        super(PD_FA, self).__init__()
        self.nclass = nclass
        self.bins = bins
        self.image_area_total = []
        self.image_area_match = []
        self.FA = np.zeros(self.bins + 1)
        self.PD = np.zeros(self.bins + 1)
        self.target = np.zeros(self.bins + 1)
        self.size = size
        self.Flag_save = False
        self.preds_list = []
        self.labels_list = []



    def update(self, preds, labels):
        if self.Flag_save:
            self.preds_list.append(preds)
            self.labels_list.append(labels)


        for iBin in range(self.bins + 1):
            score_thresh = iBin * (255 / self.bins)
            predits = np.array((preds > score_thresh).cpu()).astype('int64')

            predits = np.reshape(predits, (self.size, self.size))
            labelss = np.array((labels).cpu()).astype('int64')
            labelss = np.reshape(labelss, (self.size, self.size))

            image = measure.label(predits, connectivity=2)
            coord_image = measure.regionprops(image)
            label = measure.label(labelss, connectivity=2)
            coord_label = measure.regionprops(label)

            self.target[iBin] += len(coord_label)
            self.image_area_total = []
            self.image_area_match = []
            self.distance_match = []
            self.dismatch = []

            for K in range(len(coord_image)):
                area_image = np.array(coord_image[K].area)
                self.image_area_total.append(area_image)

            for i in range(len(coord_label)):
                centroid_label = np.array(list(coord_label[i].centroid))
                for m in range(len(coord_image)):
                    centroid_image = np.array(list(coord_image[m].centroid))
                    distance = np.linalg.norm(centroid_image - centroid_label)
                    area_image = np.array(coord_image[m].area)
                    if distance < 3:
                        self.distance_match.append(distance)
                        self.image_area_match.append(area_image)

                        del coord_image[m]
                        break

            self.dismatch = [x for x in self.image_area_total if x not in self.image_area_match]
            self.FA[iBin] += np.sum(self.dismatch)
            self.PD[iBin] += len(self.distance_match)

    def get(self, img_num):

        Final_FA = self.FA / ((self.size * self.size) * img_num)
        Final_PD = self.PD / self.target

        return Final_FA, Final_PD




    def get_value(self, score_thresh = 0.5):
        if self.Flag_save is False:
            print(f'The Flag_save is {self.Flag_save}, so i can\'t calculate PD and FA for threshold!!!')
            return None

        image_area_total = []
        image_area_match = []

        FA = np.zeros(1)
        PD = np.zeros(1)
        target = np.zeros(1)

        for idx_iter in range(len(self.preds_list)):
            predits = self.preds_list[idx_iter]
            labels = self.labels_list[idx_iter]

            predits = np.array((predits > score_thresh).cpu()).astype('int64')
            predits = np.reshape(predits, (self.size, self.size))
            labelss = np.array((labels).cpu()).astype('int64')
            labelss = np.reshape(labelss, (self.size, self.size))

            image = measure.label(predits, connectivity=2)
            coord_image = measure.regionprops(image)
            label = measure.label(labelss, connectivity=2)
            coord_label = measure.regionprops(label)

            target[0] += len(coord_label)
            image_area_total = []
            image_area_match = []
            distance_match = []
            dismatch = []


            for K in range(len(coord_image)):
                area_image = np.array(coord_image[K].area)
                image_area_total.append(area_image)


            for i in range(len(coord_label)):
                centroid_label = np.array(list(coord_label[i].centroid))
                for m in range(len(coord_image)):
                    centroid_image = np.array(list(coord_image[m].centroid))
                    distance = np.linalg.norm(centroid_image - centroid_label)
                    area_image = np.array(coord_image[m].area)
                    if distance < 3:
                        distance_match.append(distance)
                        image_area_match.append(area_image)

                        del coord_image[m]
                        break

            dismatch = [x for x in self.image_area_total if x not in self.image_area_match]
            FA[0] += np.sum(dismatch)
            PD[0] += len(distance_match)

        Final_FA = FA / ((self.size * self.size) * len(self.preds_list))
        Final_PD = PD / target

        return Final_FA[0], Final_PD[0]





    def get_threshold(self, thresholds = [0, 1]):
        if self.Flag_save is False:
            print(f'The Flag_save is {self.Flag_save}, so i can\'t calculate PD and FA for threshold!!!')
            return None


        image_area_total = []
        image_area_match = []
        FA = np.zeros(len(thresholds))
        PD = np.zeros(len(thresholds))
        target = np.zeros(len(thresholds))

        tbar = tqdm.tqdm(thresholds)

        for idx_iter, score_thresh in enumerate(tbar):

            for i in range(len(self.preds_list)):
                predits = self.preds_list[i]
                labels = self.labels_list[i]

                predits = np.array((predits > score_thresh).cpu()).astype('int64')
                predits = np.reshape(predits, (self.size, self.size))
                labelss = np.array((labels).cpu()).astype('int64')
                labelss = np.reshape(labelss, (self.size, self.size))

                image = measure.label(predits, connectivity=2)
                coord_image = measure.regionprops(image)
                label = measure.label(labelss, connectivity=2)
                coord_label = measure.regionprops(label)

                target[idx_iter] += len(coord_label)
                image_area_total = []
                image_area_match = []
                distance_match = []
                dismatch = []




                for K in range(len(coord_image)):
                    area_image = np.array(coord_image[K].area)
                    image_area_total.append(area_image)

                for i in range(len(coord_label)):
                    centroid_label = np.array(list(coord_label[i].centroid))
                    for m in range(len(coord_image)):
                        centroid_image = np.array(list(coord_image[m].centroid))
                        distance = np.linalg.norm(centroid_image - centroid_label)
                        area_image = np.array(coord_image[m].area)
                        if distance < 3:
                            distance_match.append(distance)
                            image_area_match.append(area_image)

                            del coord_image[m]
                            break

                dismatch = [x for x in self.image_area_total if x not in self.image_area_match]
                FA[idx_iter] += np.sum(dismatch)
                PD[idx_iter] += len(distance_match)

            tbar.set_description('Get processing.... LAST FA, PD')

        Final_FA = FA / ((self.size * self.size) * len(self.preds_list))
        Final_PD = PD / target
        return Final_FA, Final_PD



    def reset(self):
        self.nclass = self.nclass
        self.bins = self.bins
        self.image_area_total = []
        self.image_area_match = []
        self.FA = np.zeros(self.bins + 1)
        self.PD = np.zeros(self.bins + 1)
        self.target = np.zeros(self.bins + 1)
        self.size = self.size

        self.preds_list = []
        self.labels_list = []

def cal_tp_pos_fp_neg(output, target, score_thresh):
    predict = np.array((output.sigmoid() > score_thresh).cpu()).astype('int64')
    target = np.array((target).cpu()).astype('int64')
    predict = predict.squeeze()
    target = target.squeeze()
    intersection = predict * ((predict == target).astype('float32'))


    tp = intersection.sum()
    fp = (predict * ((predict != target).astype('float32'))).sum()
    tn = ((1 - predict) * ((predict == target).astype('float32'))).sum()
    fn = (((predict != target).astype('float32')) * (1 - predict)).sum()
    pos = tp + fn
    neg = fp + tn
    class_pos = tp + fp

    return tp, pos, fp, neg, class_pos




class ROCMetric():
    """
    Computes pixAcc and mIoU metric scores
    """
    def __init__(self, nclass, bins):
        super(ROCMetric, self).__init__()
        self.nclass = nclass
        self.bins = bins
        self.tp_arr = np.zeros(self.bins+1)
        self.pos_arr = np.zeros(self.bins+1)
        self.fp_arr = np.zeros(self.bins+1)
        self.neg_arr = np.zeros(self.bins+1)
        self.class_pos=np.zeros(self.bins+1)
        self.preds_list=[]
        self.labels_list=[]
        self.Flag_save=False


    def get(self):
        tp_rates    = self.tp_arr / (self.pos_arr + np.spacing(1))
        fp_rates    = self.fp_arr / (self.neg_arr + np.spacing(1))

        # recall      = self.tp_arr / (self.pos_arr   + 0.001)
        # precision   = self.tp_arr / (self.class_pos + 0.001)
        return tp_rates, fp_rates


    def reset(self):
        self.tp_arr = np.zeros(self.bins+1)
        self.pos_arr = np.zeros(self.bins+1)
        self.fp_arr = np.zeros(self.bins+1)
        self.neg_arr = np.zeros(self.bins+1)
        self.class_pos=np.zeros(self.bins+1)
        self.preds_list=[]
        self.labels_list=[]


    def update(self, preds, labels):
        if self.Flag_save:
            self.preds_list.append(preds)
            self.labels_list.append(labels)

        for iBin in range(self.bins+1):
            score_thresh = (iBin + 0.0) / self.bins
            # print(iBin, "-th, score_thresh: ", score_thresh)
            i_tp, i_pos, i_fp, i_neg,i_class_pos = cal_tp_pos_fp_neg(preds, labels, score_thresh)
            self.tp_arr[iBin]   += i_tp
            self.pos_arr[iBin]  += i_pos
            self.fp_arr[iBin]   += i_fp
            self.neg_arr[iBin]  += i_neg
            self.class_pos[iBin]+=i_class_pos


    def get_threshold(self, thresholds = [0, 1]):
        if self.Flag_save is False:
            print(f'The Flag_save is {self.Flag_save}, so i can\'t calculate PD and FA for threshold!!!')
            return None


        tp_arr = np.zeros(len(thresholds))
        pos_arr = np.zeros(len(thresholds))
        fp_arr = np.zeros(len(thresholds))
        neg_arr = np.zeros(len(thresholds))
        class_pos=np.zeros(len(thresholds))

        tbar = tqdm.tqdm(thresholds)

        for idx_iter, score_thresh in enumerate(tbar):
            for i in range(len(self.preds_list)):
                predits = self.preds_list[i]
                labels = self.labels_list[i]
                predits = np.array((predits > score_thresh).cpu()).astype('float64')
                labels = np.array((labels).cpu()).astype('float64')
                intersection = (predits == labels).astype('float64') * predits
                tp = intersection.sum()
                fp = (predits * ((predits != labels).astype('float64'))).sum()
                tn = ((1 - predits) * ((predits == labels).astype('float64'))).sum()
                fn = (((predits != labels).astype('float64')) * (1 - predits)).sum()

                i_pos = tp + fn
                i_neg = fp + tn
                i_class_pos = tp + fp

                tp_arr[idx_iter] += tp
                pos_arr[idx_iter] += i_pos
                fp_arr[idx_iter] += fp
                neg_arr[idx_iter] += i_neg
                class_pos[idx_iter] += i_class_pos



        tp_rates    = tp_arr / (pos_arr + np.spacing(1))
        fp_rates    = fp_arr / (neg_arr + np.spacing(1))
        return tp_rates, fp_rates




    def get_value(self, thresholds):
        if self.Flag_save is False:
            print(f'The Flag_save is {self.Flag_save}, so i can\'t calculate PD and FA for threshold!!!')
            return None

        tp_arr = np.zeros(1)
        pos_arr = np.zeros(1)
        fp_arr = np.zeros(1)
        neg_arr = np.zeros(1)
        class_pos=np.zeros(1)

        tbar = tqdm.tqdm(self.preds_list)


        for idx_iter, _ in enumerate(tbar):
            predits = self.preds_list[idx_iter]
            labels = self.labels_list[idx_iter]
            predits = np.array((predits > thresholds).cpu()).astype('float64')
            labels = np.array((labels).cpu()).astype('float64')
            intersection = (predits == labels).astype('float64') * predits
            tp = intersection.sum()
            fp = (predits * ((predits != labels).astype('float64'))).sum()
            tn = ((1 - predits) * ((predits == labels).astype('float64'))).sum()
            fn = (((predits != labels).astype('float64')) * (1 - predits)).sum()

            i_pos = tp + fn
            i_neg = fp + tn
            i_class_pos = tp + fp

            tp_arr[0] += tp
            pos_arr[0] += i_pos
            fp_arr[0] += fp
            neg_arr[0] += i_neg
            class_pos[0] += i_class_pos

        tp_rates = tp_arr / (pos_arr + np.spacing(1))
        fp_rates = fp_arr / (neg_arr + np.spacing(1))
        return tp_rates[0], fp_rates[0]



























