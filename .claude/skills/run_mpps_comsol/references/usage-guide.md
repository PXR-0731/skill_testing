# COMSOL MPPS Skill 使用指南

详细参数说明、输出格式规范和故障排查。

## 目录

- [前提条件](#前提条件)
- [功能一：运行仿真](#功能一运行仿真)
- [功能二：读取结果与绘图](#功能二读取结果与绘图)
- [故障排查](#故障排查)

---

## 前提条件

- COMSOL Multiphysics 已安装且许可证有效
- Python 环境已安装 `mph`、`scipy`、`matplotlib`、`numpy`
- 仿真耗时约 10-60s，执行后耐心等待，勿重复调用

---

## 功能一：运行仿真（comsol_runner.py）

### 执行命令

```bash
python scripts/comsol_runner.py --model_path <model_path> --param_path <param_path> --result_path <result_path>
```

### 参数说明

| 参数 | 类型 | 必需 | 说明                         |
|------|------|----|----------------------------|
| `model_path` | string | 是  | `.mph` 仿真模型文件的绝对路径         |
| `param_path` | string | 是  | `.mat` 参数文件的绝对路径（含几何/物理参数） |
| `result_path` | string | 是  | `.txt` 输出文件的绝对路径           |


---

## 功能二：读取结果与绘图（result_reader.py）

### 执行命令

```bash
python scripts/result_reader.py --result_file <result_file> --output_plot <output_plot>
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `result_file` | string | 是 | 仿真结果 `.txt` 文件路径（由 comsol_runner.py 生成或用户直接提供） |
| `output_plot` | string | 否 | 输出图片路径，默认 `absorption_curve.png` |

### 输出格式

脚本以 JSON 格式输出到 stdout：

```json
{
  "status": "ok",
  "plot_path": "C:/Users/82612/Desktop/mpps/alpha.png",
  "metrics": {
    "peak_absorption": 0.923,
    "peak_frequency": 1250.0,
    "average_100_5000Hz": 0.654,
    "frequency_range": [100.0, 5000.0]
  },
  "data": {
    "frequencies": [100, 125, 160, ...],
    "absorption_coefficients": [0.15, 0.22, 0.38, ...]
  }
}
```

图表特征：
- 横轴：对数频率坐标（Hz）
- 纵轴：吸声系数（0-1）
- 含峰值标注（红色虚线 + 文字）
- 含 0.8 参考线（灰色点线）

---

## 故障排查

| 现象 | 可能原因 | 解决方案 |
|------|---------|---------|
| comsol_runner.py 报 `ModuleNotFoundError` | 未安装 `mph` 或 `scipy` | `pip install mph scipy` |
| comsol_runner.py 报许可证错误 | COMSOL 许可证失效 | 检查 COMSOL 许可证状态 |
| result_reader.py 报 `FileNotFoundError` | 结果文件路径错误 | 确认 .txt 文件存在，检查路径 |
| 图表中吸声系数 > 1 | 数据异常 | 检查 COMSOL 模型设置，脚本已自动 clip 到 [0,1] |
