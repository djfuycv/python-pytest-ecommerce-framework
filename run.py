import sys
import pytest
from pathlib import Path  # 更优雅的路径处理（兼容Windows/Mac/Linux）

def run_tests():
    """
    自动化测试执行入口函数
    功能:
    1. 自动创建报告目录（避免目录不存在报错）
    2. 执行测试用例并捕获执行结果
    3. 输出清晰的执行状态（成功/失败）
    4. 兼容多系统路径格式
    """
    # ========== 1. 配置基础参数（可根据需求调整） ==========
    test_dir = "testcases"  # 测试用例目录
    report_dir = "./report/allure_report"  # allure原始报告目录

    # 转换为Path对象，兼容不同系统路径分隔符（\ /）
    report_path = Path(report_dir)

    # ========== 2. 确保报告目录存在 ==========
    if not report_path.exists():
        report_path.mkdir(parents=True, exist_ok=True)  # parents=True: 自动创建多级目录
        print(f"✅ 自动创建报告目录: {report_path.absolute()}")

    # ========== 3. 构造pytest执行参数 ==========
    pytest_args = [
        test_dir,
        "-v",  # 详细输出用例执行结果
        "-s",  # 打印用例中的print/日志
        f"--alluredir={report_path}",  # 指定allure报告目录
        "--clean-alluredir",  # 清空旧报告数据
        "--tb=short",  # 简化异常栈信息（避免输出过长）
        # "-q"  # 精简输出（可选，去掉-v的冗余信息）
    ]

    # ========== 4. 执行测试用例并捕获结果 ==========
    print("\n🚀 开始运行自动化测试用例...")
    exit_code = pytest.main(pytest_args)

    # ========== 5. 输出执行结果 ==========
    if exit_code == 0:
        print("\n✅ 所有测试用例执行成功！")
    else:
        print(f"\n❌ 测试执行失败，退出码: {exit_code}")

    # ========== 6. 生成Allure报告（可选，需安装allure命令行） ==========
    try:
        import subprocess
        print("\n📊 正在生成Allure HTML报告...")
        # 生成报告到 ./report/html 目录
        html_report_path = Path("./report/html")
        if not html_report_path.exists():
            html_report_path.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["allure", "generate", str(report_path), "-o", str(html_report_path), "--clean"],
            check=True
        )
        print(f"✅ Allure报告已生成: {html_report_path.absolute()}")
        print(f"👉 可执行 'allure open {html_report_path}' 查看报告")
    except ImportError:
        print("⚠️ 未安装subprocess模块，跳过Allure报告生成")
    except FileNotFoundError:
        print("⚠️ 未找到allure命令行工具，请先安装Allure: https://docs.qameta.io/allure/")
    except subprocess.CalledProcessError as e:
        print(f"❌ Allure报告生成失败: {e}")

    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())