import tqdm
import torch
from block.metric_get import metric


def val_get(args, val_dataloader, model, loss, data_dict, ema):
    with torch.no_grad():
        model = ema.ema if args.ema else model.eval()
        pred = []
        true = []
        tqdm_len = ((data_dict['val_input'].shape[1] - args.input_size - args.output_size + 1)
                    // args.batch // args.device_number * args.device_number)
        tqdm_show = tqdm.tqdm(total=tqdm_len, mininterval=0.2)
        for item, (series_batch, true_batch) in enumerate(val_dataloader):
            series_batch = series_batch.to(args.device, non_blocking=args.latch)
            true_batch = true_batch.to(args.device, non_blocking=args.latch)
            pred_batch = model(series_batch)
            loss_batch = loss(pred_batch, true_batch)
            pred.extend(pred_batch.cpu())
            true.extend(true_batch.cpu())
            # tqdm
            tqdm_show.set_postfix({'val_loss': loss_batch.item()})  # 添加loss显示
            tqdm_show.update(args.device_number)  # 更新进度条
        # tqdm
        tqdm_show.close()
        # 计算指标
        pred = torch.stack(pred, dim=0)
        true = torch.stack(true, dim=0)
        val_loss = loss(pred, true)
        # 计算总相对指标
        mae, mse = metric(pred, true)
        print('\n| all | val_loss:{:.4f} | val_mae:{:.4f} | val_mse:{:.4f} |'.format(val_loss, mae, mse))
        # 计算各类别相对指标和真实指标
        for i in range(pred.shape[1]):
            column = args.output_column[i]
            _mae, _mse = metric(pred[:, i], true[:, i])
            pred[:, i] = pred[:, i] * data_dict['std_output'][i] + data_dict['mean_output'][i]
            true[:, i] = true[:, i] * data_dict['std_output'][i] + data_dict['mean_output'][i]
            _mae_true, _mse_true = metric(pred[:, i], true[:, i])
            print('| {} | mae:{:.4f} | mse:{:.4f} | mae_true:{:.4f} | mse_true:{:.4f} |'
                  .format(column, _mae, _mse, _mae_true, _mse_true))
    return val_loss.item(), mae.item(), mse.item()
