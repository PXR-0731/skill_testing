import mph
import sys


def test_comsol_connection():
    print("--- 正在检测 mph 环境 ---")

    try:
        # 1. 检查 mph 版本
        print(f"[1/3] mph 库版本: {mph.__version__}")

        # 2. 查找本地 COMSOL 安装路径
        # 这步不需要启动软件，只是检查配置
        print("[2/3] 正在搜索本地 COMSOL 安装...")
        # 注意：在某些版本中，可以用 mph.discovery.backend()
        # 这里我们直接尝试初始化一个 discovery 实例
        try:
            versions = mph.discovery.search()
            if not versions:
                print("❌ 错误：未在系统中找到已安装的 COMSOL。")
                return
            for v in versions:
                print(f"找到 COMSOL 版本: {v}")
        except Exception as e:
            print(f"⚠️ 无法自动发现 COMSOL 路径: {e}")

        # 3. 尝试启动 COMSOL Server (这是最核心的测试)
        print("[3/3] 尝试启动 COMSOL Server (这可能需要 10-20 秒)...")
        # cores=1 表示仅使用单核启动，用于快速测试
        client = mph.start(cores=1)

        print("✅ 成功！mph 已成功连接到 COMSOL Server。")
        print(f"当前运行模式: {client.backend}")

        # 断开连接
        client.disconnect()
        print("--- 测试完成 ---")

    except Exception as e:
        print("\n❌ 测试失败！")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {e}")
        print("\n常见排查建议:")
        print("1. 确保已安装 JDK (Java Development Kit)。")
        print("2. 确保 COMSOL 已激活且许可有效。")
        print("3. 如果报错 JPype 相关，说明 JPype1 编译仍有问题。")


if __name__ == "__main__":
    test_comsol_connection()