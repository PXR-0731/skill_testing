import mph
import argparse
import json
import sys

import numpy as np
from scipy.io import loadmat, savemat  # 用于加载或保存mat文件


def run(model_path, param_path, result_path):
    try:
        # 连接并启动 COMSOL
        client = mph.start()
        model = client.load(model_path)

        # 注入参数 (假设模型内参数名为 d_hole, t_plate, h_back)
        param = loadmat(param_path)['param']
        for i in range(param.shape[0]):
            plate = param[i, :]
            model.parameter(f'd{i}', f'{plate[0]} [m]')
            model.parameter(f't{i}', f'{plate[1]} [m]')
            model.parameter(f'p{i}', f'{plate[2]} [m]')
            model.parameter(f'D{i}', f'{plate[3]} [m]')

        # 计算
        model.solve()

        print(f"node list: {model.exports()}")
        # 获取导出节点对象
        export_node = model / 'exports' / '绘图 1'

        # 设置导出文件路径
        export_node.property('filename', result_path)

        # 执行导出
        export_node.run()

        print("mpps' simulation was finish")

        # # 假设在模型里定义了一个导出结果的 Plot
        # # 简单演示：返回成功信息
        # result = {
        #     "status": "success",
        #     "parameters": {"d": d, "t": t, "b": b},
        #     "message": "Simulation completed successfully."
        # }
        # print(json.dumps(result))

    except Exception as e:
        # print(json.dumps({"status": "error", "message": str(e)}))
        print('error')
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default=r"C:\Users\82612\Desktop\mpps\二维四层穿孔板吸声.mph")
    parser.add_argument("--param_path", type=str, default=r"C:\Users\82612\Desktop\mpps\param.mat")
    parser.add_argument("--result_path", type=str, default=r"C:\Users\82612\Desktop\mpps\result.txt")
    # parser.add_argument("--t", type=float)
    # parser.add_argument("--b", type=float)
    args = parser.parse_args()

    run(args.model_path, args.param_path, args.result_path)

    # panels_params = [[0.000300, 0.000765, 0.04, 0.0800],# 高频吸声层
    #                  [0.000321, 0.000500, 0.01694, 0.0800], # 过渡匹配层
    #                  [0.000612, 0.001500, 0.01, 0.0800], # 中频吸声层
    #                  [0.000425, 0.001500, 0.01, 0.0800]] #  低频吸声层
    # savemat(r"C:\Users\82612\Desktop\mpps\param.mat", {'param':np.array(panels_params)})
    #
    # run(r"C:\Users\82612\Desktop\mpps\二维四层穿孔板吸声.mph", r"C:\Users\82612\Desktop\mpps\param.mat")

    # run(r"C:\Users\82612\Desktop\mpps\二维四层穿孔板吸声.mph", r'C:\Users\82612\Desktop\mppsb.mat')