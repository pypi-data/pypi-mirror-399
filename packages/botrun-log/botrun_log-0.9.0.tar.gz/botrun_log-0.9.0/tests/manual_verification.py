"""
手動驗證腳本 - Token 欄位功能測試

此檔案用於手動驗證 token 欄位的完整功能，包含實際的 BigQuery 連線測試。

注意：
- 此檔案不會被 pytest 自動執行（檔名不符合 test_*.py 或 *_test.py 模式）
- 需要真實的 BigQuery 憑證和環境變數設定
- 執行此腳本可能會產生 GCP 費用

執行方式：
    python tests/manual_verification.py

需要的環境變數：
    - BOTRUN_LOG_CREDENTIALS_PATH
    - BOTRUN_LOG_PROJECT_ID
    - BOTRUN_LOG_DATASET_NAME
    - BOTRUN_LOG_DEPARTMENT
    - BOTRUN_LOG_AES_KEY
"""
from botrun_log import Logger, TextLogEntry
from datetime import datetime
import os

def test_with_tokens():
    """測試包含 token 欄位"""
    print("=" * 60)
    print("測試 1: 插入包含 token 欄位的 log")
    print("=" * 60)

    logger = Logger()

    log_entry = TextLogEntry(
        timestamp=datetime.now().isoformat(),
        domain_name='botrun.ai',
        user_department=os.getenv('BOTRUN_LOG_DEPARTMENT', 'test_org'),
        user_name="test_user_with_tokens",
        source_ip="127.0.0.1",
        session_id="session_token_test_1",
        action_type="llm_chat",
        developer="manual_test",
        model="gpt-4",
        botrun="test_botrun",
        action_details="測試 token 欄位功能",
        input_tokens=150,
        output_tokens=300,
        total_tokens=450,
        input_cost=0.0015,
        output_cost=0.006,
        total_cost=0.0075
    )

    try:
        logger.insert_text_log(log_entry)
        print("✓ 成功插入包含 token 和 cost 的 log")
        print(f"  - input_tokens: {log_entry.input_tokens}")
        print(f"  - output_tokens: {log_entry.output_tokens}")
        print(f"  - total_tokens: {log_entry.total_tokens}")
        print(f"  - input_cost: {log_entry.input_cost}")
        print(f"  - output_cost: {log_entry.output_cost}")
        print(f"  - total_cost: {log_entry.total_cost}")
        return True
    except Exception as e:
        print(f"✗ 失敗: {e}")
        return False

def test_without_tokens():
    """測試不包含 token 欄位（向後相容）"""
    print("\n" + "=" * 60)
    print("測試 2: 插入不包含 token 欄位的 log（向後相容）")
    print("=" * 60)

    logger = Logger()

    log_entry = TextLogEntry(
        timestamp=datetime.now().isoformat(),
        domain_name='botrun.ai',
        user_department=os.getenv('BOTRUN_LOG_DEPARTMENT', 'test_org'),
        user_name="test_user_without_tokens",
        source_ip="127.0.0.1",
        session_id="session_token_test_2",
        action_type="llm_chat",
        developer="manual_test",
        model="gpt-4",
        botrun="test_botrun",
        action_details="測試向後相容性"
    )

    try:
        logger.insert_text_log(log_entry)
        print("✓ 成功插入不包含 token 的 log")
        print(f"  - input_tokens: {log_entry.input_tokens} (None 表示未提供)")
        print(f"  - output_tokens: {log_entry.output_tokens} (None 表示未提供)")
        return True
    except Exception as e:
        print(f"✗ 失敗: {e}")
        return False

def verify_schema():
    """檢查 BigQuery schema"""
    print("\n" + "=" * 60)
    print("測試 3: 驗證 BigQuery Schema")
    print("=" * 60)

    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account

        credentials_path = os.getenv('BOTRUN_LOG_CREDENTIALS_PATH')
        project_id = os.getenv('BOTRUN_LOG_PROJECT_ID')
        dataset_name = os.getenv('BOTRUN_LOG_DATASET_NAME')
        department = os.getenv('BOTRUN_LOG_DEPARTMENT', 'test_org')

        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = bigquery.Client(credentials=credentials, project=project_id)

        table_id = f"{project_id}.{dataset_name}.{department}_logs"
        table = client.get_table(table_id)

        print(f"Table: {table_id}")
        print("\n欄位列表:")

        required_fields = ['input_tokens', 'output_tokens', 'total_tokens', 'input_cost', 'output_cost', 'total_cost']
        found_fields = set()

        for field in table.schema:
            if field.name in required_fields:
                print(f"  ✓ {field.name}: {field.field_type} ({field.mode})")
                found_fields.add(field.name)

        missing_fields = set(required_fields) - found_fields
        if not missing_fields:
            print("\n✓ Schema 包含所有 token 和 cost 欄位")
            return True
        else:
            print(f"\n✗ Schema 缺少欄位: {missing_fields}")
            return False

    except Exception as e:
        print(f"✗ 無法驗證 schema: {e}")
        return False

if __name__ == "__main__":
    print("\n開始測試 token 欄位功能...\n")

    results = []

    # 執行測試
    results.append(("插入包含 token", test_with_tokens()))
    results.append(("插入不包含 token", test_without_tokens()))
    results.append(("驗證 Schema", verify_schema()))

    # 總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)

    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 所有測試通過！")
    else:
        print("\n⚠️  有測試失敗，請檢查錯誤訊息")
