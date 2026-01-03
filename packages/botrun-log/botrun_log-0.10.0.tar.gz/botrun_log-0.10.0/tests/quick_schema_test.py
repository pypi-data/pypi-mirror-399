"""
快速測試 Schema 自動更新

此腳本只測試 schema 是否會自動新增 token 欄位，不會寫入任何資料。
適合用於驗證現有 table 的 schema 更新功能。

執行方式：
    python tests/quick_schema_test.py
"""
from botrun_log import Logger
import os

print("=" * 60)
print("測試 Schema 自動更新功能")
print("=" * 60)
print()

# 取得環境變數
department = os.getenv('BOTRUN_LOG_DEPARTMENT', 'test_org')
print(f"部門: {department}")
print(f"專案: {os.getenv('BOTRUN_LOG_PROJECT_ID')}")
print(f"資料集: {os.getenv('BOTRUN_LOG_DATASET_NAME')}")
print()

print("初始化 Logger（會觸發 schema 檢查和更新）...")
print("-" * 60)

# 初始化 Logger 會自動觸發 initialize_database()
# 這會執行 _ensure_all_schemas_updated() 檢查並新增欄位
logger = Logger()

print("-" * 60)
print()
print("✓ 初始化完成！")
print()
print("請檢查上方是否有以下訊息：")
print("  ✓ Updated schema for {department}_logs: added {'input_tokens', 'output_tokens'}")
print()
print("如果沒有看到更新訊息，表示 table 已經包含這些欄位。")
print()
print("你可以到 BigQuery Console 查看 table schema 確認：")
print(f"  https://console.cloud.google.com/bigquery?project={os.getenv('BOTRUN_LOG_PROJECT_ID')}")
