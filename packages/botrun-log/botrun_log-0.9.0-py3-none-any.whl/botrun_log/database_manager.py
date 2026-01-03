import os
from google.cloud import bigquery
from google.oauth2 import service_account
import psycopg2

class DatabaseManager:
    def __init__(self, db_type='bigquery', pg_config=None, credentials_path=None, project_id=None, dataset_name=None):
        self.db_type = db_type.lower()
        self.project_id = project_id or os.getenv('BOTRUN_LOG_PROJECT_ID')
        self.dataset_name = dataset_name or os.getenv('BOTRUN_LOG_DATASET_NAME')

        if self.db_type == 'bigquery':
            self.credentials_path = credentials_path or os.getenv('BOTRUN_LOG_CREDENTIALS_PATH')
            self.credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
            self._client = bigquery.Client(credentials=self.credentials, project=self.project_id)
        elif self.db_type == 'postgresql':
            if pg_config is None:
                pg_config = {
                    'host': os.getenv('PG_HOST'),
                    'database': os.getenv('PG_DATABASE'),
                    'user': os.getenv('PG_USER'),
                    'password': os.getenv('PG_PASSWORD'),
                    'port': os.getenv('PG_PORT')
                }
                if not all(pg_config.values()):
                    raise ValueError("環境變數中缺少PostgreSQL config")
            self._conn = psycopg2.connect(**pg_config)
            self._cursor = self._conn.cursor()
        else:
            raise ValueError(f"Invalid db_type '{self.db_type}'. Supported values are 'bigquery' or 'postgresql'.")

    def initialize_database(self, department):
        if self.db_type == 'bigquery':
            self._init_bq(department)
            self._init_etl_bq()
            self._init_audio_bq(department)
            self._init_image_bq(department)
            self._init_vector_bq(department)
            # 自動更新所有 table 的 schema
            self._ensure_all_schemas_updated(department)
        elif self.db_type == 'postgresql':
            self._init_pg(department)
            self._init_etl_pg()
            self._init_audio_pg(department)
            self._init_image_pg(department)
            self._init_vector_pg(department)
            # 自動更新所有 table 的 schema
            self._ensure_all_schemas_updated_pg(department)

    def execute_query(self, query, params=None):
        if self.db_type == 'bigquery':
            job_config = bigquery.QueryJobConfig()
            if params:
                job_config.query_parameters = params
            query_job = self._client.query(query, job_config=job_config)
            return query_job.result()
        elif self.db_type == 'postgresql':
            with self._conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self._conn.commit()
                    return cursor.rowcount  # 返回受影響的行數

    def insert_rows(self, table_name, rows):
        if self.db_type == 'bigquery':
            table_ref = f"{self.project_id}.{self.dataset_name}.{table_name}"
            errors = self._client.insert_rows_json(table_ref, rows)
            if errors:
                raise Exception(f"Encountered errors while inserting rows: {errors}")
        elif self.db_type == 'postgresql':
            columns = rows[0].keys()
            values = [tuple(row[column] for column in columns) for row in rows]
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            self._cursor.executemany(query, values)
            self._conn.commit()

    def _init_bq(self, department):
        dataset_id = f"{self.project_id}.{self.dataset_name}"
        table_id = f"{dataset_id}.{department}_logs"

        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "asia-east1"
        self._client.create_dataset(dataset, exists_ok=True)

        schema = self._get_text_log_schema()
        table = bigquery.Table(table_id, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(field="timestamp")
        self._client.create_table(table, exists_ok=True)

    def _init_pg(self, department):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {department}_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            domain_name VARCHAR(255) NOT NULL,
            user_department VARCHAR(255) NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            source_ip VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            action_type VARCHAR(255) NOT NULL,
            action_details TEXT,
            model VARCHAR(255),
            botrun VARCHAR(255),
            user_agent VARCHAR(255),
            resource_id VARCHAR(255),
            developer VARCHAR(255) NOT NULL,
            ch_characters INT NOT NULL,
            en_characters INT NOT NULL,
            total_characters INT NOT NULL,
            input_tokens INT,
            output_tokens INT,
            total_tokens INT,
            input_cost FLOAT,
            output_cost FLOAT,
            total_cost FLOAT,
            create_timestamp TIMESTAMP NOT NULL
        );
        """
        self._cursor.execute(create_table_query)
        self._conn.commit()

    def _init_etl_bq(self):
        table_id = f"{self.project_id}.{self.dataset_name}.daily_character_usage"
        schema = [
            bigquery.SchemaField("date", "DATE", "REQUIRED", description="日期"),
            bigquery.SchemaField("department", "STRING", "REQUIRED", description="機關"),
            bigquery.SchemaField("user_name", "STRING", "REQUIRED", description="使用者帳號"),
            bigquery.SchemaField("ch_characters", "INT64", "REQUIRED", description="中文字元數"),
            bigquery.SchemaField("en_characters", "INT64", "REQUIRED", description="英文字元數"),
        ]
        table = bigquery.Table(table_id, schema=schema)
        self._client.create_table(table, exists_ok=True)

    def _init_etl_pg(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS daily_character_usage (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            department VARCHAR(255) NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            ch_characters INT NOT NULL,
            en_characters INT NOT NULL
        );
        """
        self._cursor.execute(create_table_query)
        self._conn.commit()

    def _init_audio_bq(self, department):
        table_id = f"{self.project_id}.{self.dataset_name}.{department}_audio_logs"
        schema = self._get_audio_log_schema()
        table = bigquery.Table(table_id, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(field="timestamp")
        self._client.create_table(table, exists_ok=True)

    def _init_image_bq(self, department):
        table_id = f"{self.project_id}.{self.dataset_name}.{department}_image_logs"
        schema = self._get_image_log_schema()
        table = bigquery.Table(table_id, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(field="timestamp")
        self._client.create_table(table, exists_ok=True)

    def _init_vector_bq(self, department):
        table_id = f"{self.project_id}.{self.dataset_name}.{department}_vector_logs"
        schema = self._get_vector_log_schema()
        table = bigquery.Table(table_id, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(field="timestamp")
        self._client.create_table(table, exists_ok=True)

    def _init_audio_pg(self, department):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {department}_audio_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            domain_name VARCHAR(255) NOT NULL,
            user_department VARCHAR(255) NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            source_ip VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            action_type VARCHAR(255) NOT NULL,
            action_details TEXT,
            model VARCHAR(255),
            botrun VARCHAR(255),
            user_agent VARCHAR(255),
            resource_id VARCHAR(255),
            developer VARCHAR(255) NOT NULL,
            file_size_mb FLOAT NOT NULL,
            input_tokens INT,
            output_tokens INT,
            total_tokens INT,
            input_cost FLOAT,
            output_cost FLOAT,
            total_cost FLOAT,
            create_timestamp TIMESTAMP NOT NULL
        );
        """
        self._cursor.execute(create_table_query)
        self._conn.commit()

    def _init_image_pg(self, department):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {department}_image_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            domain_name VARCHAR(255) NOT NULL,
            user_department VARCHAR(255) NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            source_ip VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            action_type VARCHAR(255) NOT NULL,
            action_details TEXT,
            model VARCHAR(255),
            botrun VARCHAR(255),
            user_agent VARCHAR(255),
            resource_id VARCHAR(255),
            developer VARCHAR(255) NOT NULL,
            img_size_mb FLOAT NOT NULL,
            input_tokens INT,
            output_tokens INT,
            total_tokens INT,
            input_cost FLOAT,
            output_cost FLOAT,
            total_cost FLOAT,
            create_timestamp TIMESTAMP NOT NULL
        );
        """
        self._cursor.execute(create_table_query)
        self._conn.commit()

    def _init_vector_pg(self, department):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {department}_vector_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            domain_name VARCHAR(255) NOT NULL,
            user_department VARCHAR(255) NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            source_ip VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            action_type VARCHAR(255) NOT NULL,
            action_details TEXT,
            model VARCHAR(255),
            botrun VARCHAR(255),
            user_agent VARCHAR(255),
            resource_id VARCHAR(255),
            developer VARCHAR(255) NOT NULL,
            page_num INT NOT NULL,
            input_tokens INT,
            output_tokens INT,
            total_tokens INT,
            input_cost FLOAT,
            output_cost FLOAT,
            total_cost FLOAT,
            create_timestamp TIMESTAMP NOT NULL
        );
        """
        self._cursor.execute(create_table_query)
        self._conn.commit()

    def _get_text_log_schema(self):
        """取得 text log table 的完整 schema"""
        return [
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED", description="時間戳"),
            bigquery.SchemaField("domain_name", "STRING", mode="REQUIRED", description="波特人網域"),
            bigquery.SchemaField("user_department", "STRING", mode="REQUIRED", description="使用者部門"),
            bigquery.SchemaField("user_name", "STRING", mode="REQUIRED", description="使用者帳號"),
            bigquery.SchemaField("source_ip", "STRING", mode="REQUIRED", description="使用者的IP地址"),
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED", description="工作階段ID"),
            bigquery.SchemaField("action_type", "STRING", mode="REQUIRED", description="操作類型"),
            bigquery.SchemaField("action_details", "STRING", mode="NULLABLE", description="操作內容，加密"),
            bigquery.SchemaField("model", "STRING", mode="NULLABLE", description="使用的模型"),
            bigquery.SchemaField("botrun", "STRING", mode="NULLABLE", description="Botrun 資訊"),
            bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE", description="使用者的客戶端資訊"),
            bigquery.SchemaField("resource_id", "STRING", mode="NULLABLE", description="資源ID（上傳的文件等）"),
            bigquery.SchemaField("developer", "STRING", mode="REQUIRED", description="寫入log的套件或開發者"),
            bigquery.SchemaField("ch_characters", "INT64", mode="REQUIRED", description="中文字元數"),
            bigquery.SchemaField("en_characters", "INT64", mode="REQUIRED", description="英數字元數"),
            bigquery.SchemaField("total_characters", "INT64", mode="REQUIRED", description="總字元數"),
            bigquery.SchemaField("input_tokens", "INT64", mode="NULLABLE", description="輸入 token 數量"),
            bigquery.SchemaField("output_tokens", "INT64", mode="NULLABLE", description="輸出 token 數量"),
            bigquery.SchemaField("total_tokens", "INT64", mode="NULLABLE", description="總 token 數量"),
            bigquery.SchemaField("input_cost", "FLOAT64", mode="NULLABLE", description="輸入成本"),
            bigquery.SchemaField("output_cost", "FLOAT64", mode="NULLABLE", description="輸出成本"),
            bigquery.SchemaField("total_cost", "FLOAT64", mode="NULLABLE", description="總成本"),
            bigquery.SchemaField("create_timestamp", "TIMESTAMP", mode="REQUIRED", description="寫入BigQuery的時間戳"),
        ]

    def _get_audio_log_schema(self):
        """取得 audio log table 的完整 schema"""
        return [
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("domain_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_department", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_ip", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("action_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("action_details", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("model", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("botrun", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("resource_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("developer", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("file_size_mb", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("input_tokens", "INT64", mode="NULLABLE", description="輸入 token 數量"),
            bigquery.SchemaField("output_tokens", "INT64", mode="NULLABLE", description="輸出 token 數量"),
            bigquery.SchemaField("total_tokens", "INT64", mode="NULLABLE", description="總 token 數量"),
            bigquery.SchemaField("input_cost", "FLOAT64", mode="NULLABLE", description="輸入成本"),
            bigquery.SchemaField("output_cost", "FLOAT64", mode="NULLABLE", description="輸出成本"),
            bigquery.SchemaField("total_cost", "FLOAT64", mode="NULLABLE", description="總成本"),
            bigquery.SchemaField("create_timestamp", "TIMESTAMP", mode="REQUIRED"),
        ]

    def _get_image_log_schema(self):
        """取得 image log table 的完整 schema"""
        return [
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("domain_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_department", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_ip", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("action_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("action_details", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("model", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("botrun", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("resource_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("developer", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("img_size_mb", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("input_tokens", "INT64", mode="NULLABLE", description="輸入 token 數量"),
            bigquery.SchemaField("output_tokens", "INT64", mode="NULLABLE", description="輸出 token 數量"),
            bigquery.SchemaField("total_tokens", "INT64", mode="NULLABLE", description="總 token 數量"),
            bigquery.SchemaField("input_cost", "FLOAT64", mode="NULLABLE", description="輸入成本"),
            bigquery.SchemaField("output_cost", "FLOAT64", mode="NULLABLE", description="輸出成本"),
            bigquery.SchemaField("total_cost", "FLOAT64", mode="NULLABLE", description="總成本"),
            bigquery.SchemaField("create_timestamp", "TIMESTAMP", mode="REQUIRED"),
        ]

    def _get_vector_log_schema(self):
        """取得 vector log table 的完整 schema"""
        return [
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("domain_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_department", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_ip", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("action_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("action_details", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("model", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("botrun", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("resource_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("developer", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("page_num", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("input_tokens", "INT64", mode="NULLABLE", description="輸入 token 數量"),
            bigquery.SchemaField("output_tokens", "INT64", mode="NULLABLE", description="輸出 token 數量"),
            bigquery.SchemaField("total_tokens", "INT64", mode="NULLABLE", description="總 token 數量"),
            bigquery.SchemaField("input_cost", "FLOAT64", mode="NULLABLE", description="輸入成本"),
            bigquery.SchemaField("output_cost", "FLOAT64", mode="NULLABLE", description="輸出成本"),
            bigquery.SchemaField("total_cost", "FLOAT64", mode="NULLABLE", description="總成本"),
            bigquery.SchemaField("create_timestamp", "TIMESTAMP", mode="REQUIRED"),
        ]

    def _ensure_all_schemas_updated(self, department):
        """自動更新所有 BigQuery table 的 schema"""
        # 定義所有需要 token 欄位的 tables
        tables_to_update = [
            (f"{department}_logs", self._get_text_log_schema()),
            (f"{department}_audio_logs", self._get_audio_log_schema()),
            (f"{department}_image_logs", self._get_image_log_schema()),
            (f"{department}_vector_logs", self._get_vector_log_schema()),
        ]

        for table_name, expected_schema in tables_to_update:
            self._ensure_schema_updated(table_name, expected_schema)

    def _ensure_schema_updated(self, table_name, expected_schema):
        """確保 BigQuery table schema 包含所有需要的欄位"""
        try:
            table_id = f"{self.project_id}.{self.dataset_name}.{table_name}"
            table = self._client.get_table(table_id)

            # 取得目前的欄位名稱
            current_field_names = {field.name for field in table.schema}
            expected_field_names = {field.name for field in expected_schema}

            # 找出缺少的欄位
            missing_fields = expected_field_names - current_field_names

            if missing_fields:
                # 需要更新 schema
                # 建立新的 schema（保留舊欄位 + 新欄位）
                new_schema = list(table.schema)
                for field in expected_schema:
                    if field.name in missing_fields:
                        new_schema.append(field)

                table.schema = new_schema
                self._client.update_table(table, ["schema"])
                print(f"✓ Updated schema for {table_name}: added {missing_fields}")
        except Exception as e:
            print(f"Warning: Could not update schema for {table_name}: {e}")

    def _ensure_all_schemas_updated_pg(self, department):
        """自動更新所有 PostgreSQL table 的 schema"""
        tables_to_update = [
            f"{department}_logs",
            f"{department}_audio_logs",
            f"{department}_image_logs",
            f"{department}_vector_logs",
        ]

        for table_name in tables_to_update:
            self._ensure_schema_updated_pg(table_name)

    def _ensure_schema_updated_pg(self, table_name):
        """確保 PostgreSQL table schema 包含所有需要的欄位"""
        try:
            # 檢查欄位是否存在
            check_columns_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """
            self._cursor.execute(check_columns_query)
            existing_columns = {row[0] for row in self._cursor.fetchall()}

            # 需要的欄位 (欄位名稱, 類型)
            required_columns = [
                ('input_tokens', 'INT'),
                ('output_tokens', 'INT'),
                ('total_tokens', 'INT'),
                ('input_cost', 'FLOAT'),
                ('output_cost', 'FLOAT'),
                ('total_cost', 'FLOAT'),
            ]

            # 新增缺少的欄位
            for column, col_type in required_columns:
                if column not in existing_columns:
                    alter_query = f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN IF NOT EXISTS {column} {col_type}
                    """
                    self._cursor.execute(alter_query)
                    print(f"✓ Added column {column} to {table_name}")

            self._conn.commit()
        except Exception as e:
            print(f"Warning: Could not update schema for {table_name}: {e}")
            self._conn.rollback()

    def close(self):
        if self.db_type == 'postgresql':
            self._cursor.close()
            self._conn.close()