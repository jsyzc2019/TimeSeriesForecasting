import os
import torch


def model_get(args):
    if os.path.exists(args.weight):
        model_dict = torch.load(args.weight, map_location='cpu')
    else:
        choice_dict = {'lstm': 'model_prepare(args)._lstm()',
                       'linear': 'model_prepare(args)._linear()',
                       'nlinear': 'model_prepare(args)._nlinear()',
                       'nlinear_multi': 'model_prepare(args)._nlinear_multi()',
                       'nlinear_plus': 'model_prepare(args)._nlinear_plus()',
                       'scinet': 'model_prepare(args)._scinet()',
                       }
        model = eval(choice_dict[args.model])
        model_dict = {}
        model_dict['model'] = model
        model_dict['epoch'] = -1  # 已训练的轮次
        model_dict['optimizer_state_dict'] = None  # 学习率参数
        model_dict['lr_adjust_item'] = 0  # 学习率调整参数
        model_dict['ema_updates'] = 0  # ema参数
        model_dict['standard'] = 999  # 评价指标
    model_dict['model'](torch.rand(args.batch, len(args.input_column), args.input_size))  # 检查
    return model_dict


class model_prepare(object):
    def __init__(self, args):
        self.args = args

    def _linear(self):
        from model.linear import linear
        model = linear(self.args)
        return model

    def _nlinear_multi(self):
        from model.nlinear_multi import nlinear_multi
        model = nlinear_multi(self.args)
        return model

    def _lstm(self):
        from model.lstm import lstm
        model = lstm(self.args)
        return model

    def _nlinear(self):
        from model.nlinear import nlinear
        model = nlinear(self.args)
        return model

    def _nlinear_plus(self):
        from model.nlinear_plus import nlinear_plus
        model = nlinear_plus(self.args)
        return model

    def _scinet(self):
        from model.scinet import scinet
        model = scinet(self.args)
        return model
