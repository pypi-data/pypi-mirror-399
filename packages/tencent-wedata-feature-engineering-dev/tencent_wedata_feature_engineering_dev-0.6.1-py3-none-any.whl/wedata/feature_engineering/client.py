from __future__ import annotations

__doc__ = """
WeData3.0 特征工程客户端

"""

from types import ModuleType
from typing import Union, List, Dict, Optional, Any
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import StructType
import mlflow
from wedata.common.constants.constants import FEATURE_STORE_CLIENT

from wedata.common.constants.constants import APPEND, DEFAULT_WRITE_STREAM_TRIGGER, FEATURE_LOOKUP_CLIENT_PIP_PACKAGE
from wedata.feature_store.constants.engine_types import EngineTypes
from wedata.common.entities.feature_function import FeatureFunction
from wedata.common.entities.feature_lookup import FeatureLookup
from wedata.common.entities.feature_table import FeatureTable
from wedata.common.entities.training_set import TrainingSet
from wedata.feature_engineering.table_client.table_client import FeatureEngineeringTableClient
from wedata.common.spark_client import SparkClient
from wedata.feature_engineering.ml_training_client.ml_training_client import MLTrainingClient
from wedata.common.utils import common_utils, env_utils
from wedata.common.utils.feature_utils import format_feature_lookups_and_functions


_i, _v, _ = common_utils.check_package_version("mlflow", "3.0.0", ">=")
if not _v:
    raise ImportError(f"mlflow version must be greater than or equal to 3.0.0. "
                      f"current version is {mlflow.__version__}. "
                      f"you can install please install {FEATURE_LOOKUP_CLIENT_PIP_PACKAGE}[mlflow3]")


class FeatureEngineeringClient:
    def __init__(self, spark: Optional[SparkSession] = None, ):
        if spark is None:
            spark = SparkSession.builder.getOrCreate()
        self._spark = spark
        self._spark_client = SparkClient(spark)
        cloud_secret_id, cloud_secret_key = env_utils.get_cloud_secret()
        self._feature_table_client = FeatureEngineeringTableClient(
            spark, cloud_secret_id=cloud_secret_id, cloud_secret_key=cloud_secret_key)
        self._training_set_client = MLTrainingClient(self._spark_client)

    def _build_full_database_name(
            self,
            database_name: str,
            catalog_name: Optional[str] = None,
    ) -> str:
        """构建完整的数据库名 `<catalog>.<database>` 或 `<database>`。

        优先使用显式传入的 catalog_name；如果未传入，则使用当前 Spark 会话的 catalog；
        若无法获取当前 catalog，则仅返回数据库名称本身。
        """
        if not database_name or not isinstance(database_name, str):
            raise ValueError("database_name must be a non-empty string")
        if "." in database_name:
            # 避免用户传入 catalog.database 破坏拼接逻辑
            raise ValueError("database_name should not contain dots; pass catalog_name separately")

        target_catalog = catalog_name
        if not target_catalog:
            try:
                target_catalog = self._spark_client.get_current_catalog()
            except Exception:
                target_catalog = None

        if target_catalog:
            return f"{target_catalog}.{database_name}"
        return database_name

    def create_database(
        self,
        database_name: str,
        catalog_name: Optional[str] = None,
        comment: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """创建数据库（如果不存在则创建），支持指定 catalog。

        Args:
            database_name: 数据库名称（不包含 catalog 前缀）
            catalog_name: catalog 名称（可选）。如果不提供，将使用当前 Spark 会话的 catalog。
            comment: 数据库描述（可选）
            location: 数据库存储位置（可选）

        Returns:
            str: 创建的完整数据库名称（包含 catalog）

        Raises:
            ValueError: 如果 database_name 为空或包含非法字符

        Examples:
            >>> # 使用当前 catalog 创建数据库
            >>> client.create_database("my_db")
            'spark_catalog.my_db'

            >>> # 在指定 catalog 下创建数据库
            >>> client.create_database("my_db", catalog_name="DataLakeCatalog")
            'DataLakeCatalog.my_db'

            >>> # 创建带描述的数据库
            >>> client.create_database("my_db", comment="我的特征数据库")
            'spark_catalog.my_db'

        说明:
            使用 ``CREATE DATABASE IF NOT EXISTS`` 实现幂等创建：

            * 如果数据库不存在，则创建；
            * 如果数据库已存在，则不报错。
        """
        from wedata.common.log import get_logger
        logger = get_logger()

        # 构建完整数据库名
        full_db_name = self._build_full_database_name(database_name, catalog_name)

        # 检查数据库是否已存在
        try:
            databases = self._spark.sql(f"SHOW DATABASES").collect()
            db_list = [row.namespace for row in databases]
            exists = full_db_name in db_list or database_name in db_list

            if exists:
                logger.info(f"Database '{full_db_name}' already exists, skipping creation")
                return full_db_name
        except Exception as e:
            logger.warning(f"Failed to check database existence: {e}, proceeding with creation")

        # 构建 DDL
        ddl = f"CREATE DATABASE IF NOT EXISTS {full_db_name}"

        if comment:
            ddl += f" COMMENT '{comment}'"

        if location:
            ddl += f" LOCATION '{location}'"

        logger.info(f"Creating database: {full_db_name}")
        logger.debug(f"DDL: {ddl}")

        try:
            self._spark.sql(ddl)
            logger.info(f"Database '{full_db_name}' created successfully")
        except Exception as e:
            logger.error(f"Failed to create database '{full_db_name}': {e}")
            raise

        return full_db_name

    def drop_database(
        self,
        database_name: str,
        catalog_name: Optional[str] = None,
        cascade: bool = False,
        if_exists: bool = True
    ) -> bool:
        """删除数据库（如果存在则删除），支持指定 catalog。

        Args:
            database_name: 数据库名称（不包含 catalog 前缀）
            catalog_name: catalog 名称（可选）。如果不提供，将使用当前 Spark 会话的 catalog。
            cascade: 是否级联删除数据库中的所有表（默认 False，避免误删）
            if_exists: 是否使用 IF EXISTS（默认 True，数据库不存在时不报错）

        Returns:
            bool: 如果数据库被删除返回 True，如果数据库不存在返回 False

        Raises:
            Exception: 如果数据库非空且 cascade=False，或其他删除失败的情况

        Examples:
            >>> # 删除空数据库
            >>> client.drop_database("my_db")
            True

            >>> # 删除指定 catalog 下的数据库
            >>> client.drop_database("my_db", catalog_name="DataLakeCatalog")
            True

            >>> # 级联删除数据库及其所有表（危险操作！）
            >>> client.drop_database("my_db", cascade=True)
            True

        说明:
            * 默认使用 ``DROP DATABASE IF EXISTS``，数据库不存在时不报错
            * 默认不使用 CASCADE，如果数据库非空会抛出异常，避免误删数据
            * 设置 cascade=True 会删除数据库中的所有表，请谨慎使用
        """
        from wedata.common.log import get_logger
        logger = get_logger()

        # 构建完整数据库名
        full_db_name = self._build_full_database_name(database_name, catalog_name)

        # 检查数据库是否存在
        exists = False
        try:
            databases = self._spark.sql(f"SHOW DATABASES").collect()
            db_list = [row.namespace for row in databases]
            exists = full_db_name in db_list or database_name in db_list

            if not exists:
                logger.info(f"Database '{full_db_name}' does not exist, skipping deletion")
                return False
        except Exception as e:
            logger.warning(f"Failed to check database existence: {e}, proceeding with deletion")

        # 构建 DDL
        if if_exists:
            ddl = f"DROP DATABASE IF EXISTS {full_db_name}"
        else:
            ddl = f"DROP DATABASE {full_db_name}"

        if cascade:
            ddl += " CASCADE"
            logger.warning(f"Dropping database '{full_db_name}' with CASCADE - all tables will be deleted!")

        logger.info(f"Dropping database: {full_db_name}")
        logger.debug(f"DDL: {ddl}")

        try:
            self._spark.sql(ddl)
            logger.info(f"Database '{full_db_name}' dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop database '{full_db_name}': {e}")
            raise

    def list_databases(self, catalog_name: Optional[str] = None) -> List[str]:
        """列出指定 catalog 下的所有数据库。

        Args:
            catalog_name: catalog 名称（可选）。如果不提供，将列出当前 catalog 下的所有数据库。

        Returns:
            List[str]: 数据库名称列表

        Examples:
            >>> # 列出当前 catalog 下的所有数据库
            >>> client.list_databases()
            ['default', 'my_db', 'test_db']

            >>> # 列出指定 catalog 下的所有数据库
            >>> client.list_databases(catalog_name="DataLakeCatalog")
            ['default', 'feature_db']
        """
        from wedata.common.log import get_logger
        logger = get_logger()

        try:
            if catalog_name:
                # 尝试使用 SHOW DATABASES IN catalog 语法
                try:
                    databases = self._spark.sql(f"SHOW DATABASES IN {catalog_name}").collect()
                except Exception:
                    # 如果不支持，尝试切换 catalog
                    original_catalog = self._spark_client.get_current_catalog()
                    try:
                        self._spark.catalog.setCurrentCatalog(catalog_name)
                        databases = self._spark.sql("SHOW DATABASES").collect()
                    finally:
                        # 恢复原 catalog
                        if original_catalog:
                            try:
                                self._spark.catalog.setCurrentCatalog(original_catalog)
                            except Exception:
                                pass
            else:
                databases = self._spark.sql("SHOW DATABASES").collect()

            db_list = [row.namespace for row in databases]
            logger.debug(f"Found {len(db_list)} databases: {db_list}")
            return db_list

        except Exception as e:
            logger.error(f"Failed to list databases: {e}")
            raise

    def database_exists(self, database_name: str, catalog_name: Optional[str] = None) -> bool:
        """检查数据库是否存在。

        Args:
            database_name: 数据库名称（不包含 catalog 前缀）
            catalog_name: catalog 名称（可选）。如果不提供，将在当前 catalog 下检查。

        Returns:
            bool: 数据库存在返回 True，否则返回 False

        Examples:
            >>> # 检查当前 catalog 下的数据库
            >>> client.database_exists("my_db")
            True

            >>> # 检查指定 catalog 下的数据库
            >>> client.database_exists("my_db", catalog_name="DataLakeCatalog")
            False
        """
        try:
            db_list = self.list_databases(catalog_name=catalog_name)
            full_db_name = self._build_full_database_name(database_name, catalog_name)

            # 检查完整名称或简单名称
            return full_db_name in db_list or database_name in db_list
        except Exception:
            return False


    def create_table(
            self,
            name: str,
            primary_keys: Union[str, List[str]],
            timestamp_key: [str],
            engine_type: [EngineTypes],
            database_name: Optional[str] = None,
            catalog_name: Optional[str] = None,
            df: Optional[DataFrame] = None,
            *,
            partition_columns: Union[str, List[str], None] = None,
            schema: Optional[StructType] = None,
            description: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None
    ) -> FeatureTable:
        """
        创建特征表（支持批流数据写入）

        Args:
            name: 特征表全称（格式：<table>）
            primary_keys: 主键列名（支持复合主键）
            timestamp_key: 时间戳键（用于时态特征）
            engine_type: 引擎类型  wedata.feature_store.constants.engine_types.EngineTypes
            database_name: 数据库名
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog
            df: 初始数据（可选，用于推断schema）
            partition_columns: 分区列（优化存储查询）
            schema: 表结构定义（可选，当不提供df时必需）
            description: 业务描述
            tags: 业务标签

        Returns:
            FeatureTable实例

        Raises:
            ValueError: 当schema与数据不匹配时
        """

        return self._feature_table_client.create_table(
            name=name,
            primary_keys=primary_keys,
            engine_type=engine_type,
            database_name=database_name,
            catalog_name=catalog_name,
            df=df,
            timestamp_key=timestamp_key,
            partition_columns=partition_columns,
            schema=schema,
            description=description,
            tags=tags
        )

    def read_table(self, name: str, database_name: Optional[str] = None, catalog_name: Optional[str] = None) -> DataFrame:
        """
        读取特征表数据

        Args:
            name: 特征表名称
            database_name: 特征库名称
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog
        Returns:
            DataFrame: 包含特征表数据的DataFrame对象
        """

        return self._feature_table_client.read_table(name=name, database_name=database_name, catalog_name=catalog_name)

    def get_table(self, name: str, database_name: Optional[str] = None, catalog_name: Optional[str] = None) -> FeatureTable:
        """
        获取特征表元数据
        Args:
            name: 特征表名称
            database_name: 特征库名称
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog

        Returns:
            FeatureTable: 包含特征表元数据的FeatureTable对象
        """

        return self._feature_table_client.get_table(name, self._spark_client, database_name, catalog_name)

    def drop_table(self, name: str, database_name: Optional[str] = None, catalog_name: Optional[str] = None) -> None:
        """
        删除特征表

        Args:
            name: 要删除的特征表名称
            database_name: database name
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog
        Returns:
            None
        """

        return self._feature_table_client.drop_table(name, database_name, catalog_name)

    def write_table(
            self,
            name: str,
            df: DataFrame,
            database_name: Optional[str] = None,
            catalog_name: Optional[str] = None,
            mode: Optional[str] = APPEND,
            checkpoint_location: Optional[str] = None,
            trigger: Dict[str, Any] = DEFAULT_WRITE_STREAM_TRIGGER,
    ) -> Optional[StreamingQuery]:
        """
        写入数据到特征表（支持批处理和流式处理）

        Args:
            name: 特征表名称
            df: 要写入的数据DataFrame
            database_name: 特征库名称
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog
            mode: 写入模式（默认追加）
            checkpoint_location: 流式处理的检查点位置（可选）
            trigger: 流式处理触发器配置（默认使用系统预设）

        Returns:
            如果是流式写入返回StreamingQuery对象，否则返回None
        """

        return self._feature_table_client.write_table(
            name=name,
            df=df,
            database_name=database_name,
            catalog_name=catalog_name,
            mode=mode,
            checkpoint_location=checkpoint_location,
            trigger=trigger,
        )

    def create_training_set(
            self,
            df: DataFrame,
            feature_lookups: List[Union[FeatureLookup, FeatureFunction]],
            label: Union[str, List[str], None],
            exclude_columns: Optional[List[str]] = None,
            database_name: Optional[str] = None,
            catalog_name: Optional[str] = None,
            **kwargs,
    ) -> TrainingSet:
        """
        创建训练集

        Args:
            df: 基础数据
            feature_lookups: 特征查询列表
            label: 标签列名
            exclude_columns: 排除列名
            database_name: database name
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog

        Returns:
            TrainingSet实例
        """

        if exclude_columns is None:
            exclude_columns = []

        # 如果为FeatureLookup，则将需要校验FeatureLookup的table_name，并构建完整表名
        for feature in feature_lookups:
            if isinstance(feature, FeatureLookup):
                if not feature.table_name:
                    raise ValueError("FeatureLookup must specify a table_name")
                # 先校验表名格式是否合法
                common_utils.validate_table_name(feature.table_name)
                # 再构建完整表名（支持catalog），并赋值给FeatureLookup对象
                feature.table_name = common_utils.build_full_table_name(
                    feature.table_name, database_name, catalog_name=catalog_name, spark_client=self._spark_client
                )

        features = feature_lookups
        del feature_lookups

        features = format_feature_lookups_and_functions(self._spark_client, features)

        return self._training_set_client.create_training_set_from_feature_lookups(
            df=df,
            feature_lookups=features,
            label=label,
            exclude_columns=exclude_columns,
            **kwargs
        )

    def log_model(
            self,
            model: Any,
            artifact_path: str,
            *,
            flavor: ModuleType,
            training_set: Optional[TrainingSet] = None,
            registered_model_name: Optional[str] = None,
            model_registry_uri: Optional[str] = None,
            await_registration_for: int = mlflow.tracking._model_registry.DEFAULT_AWAIT_MAX_SLEEP_SECONDS,
            infer_input_example: bool = False,
            **kwargs,
    ):
        """
         记录MLflow模型并关联特征查找信息

         注意：必须使用TrainingSet.load_df返回的DataFrame训练模型，
         任何对DataFrame的修改(如标准化、添加列等)都不会在推理时应用

         Args:
             model: 要记录的模型对象
             artifact_path: 模型存储路径
             flavor: MLflow模型类型模块(如mlflow.sklearn)
             training_set: 训练模型使用的TrainingSet对象(可选)
             registered_model_name: 要注册的模型名称(可选)
             model_registry_uri: 模型注册中心地址(可选)
             await_registration_for: 等待模型注册完成的秒数(默认300秒)
             infer_input_example: 是否自动记录输入示例(默认False)

         Returns:
             None
         """

        self._training_set_client.log_model(
            model=model,
            artifact_path=artifact_path,
            flavor=flavor,
            training_set=training_set,
            registered_model_name=registered_model_name,
            model_registry_uri=model_registry_uri,
            await_registration_for=await_registration_for,
            infer_input_example=infer_input_example,
            **kwargs
        )

    def score_batch(
            self, model_uri: str, df: DataFrame, result_type: str = "double", timestamp_key: str = None
    ) -> DataFrame:
        """
        Evaluate the model on the provided :class:`DataFrame <pyspark.sql.DataFrame>`.

        Additional features required for
        model evaluation will be automatically retrieved from :mod:`Feature Store <databricks.feature_store.client>`.

        .. todo::

           [ML-15539]: Replace the bitly URL in doc string

        The model must have been logged with :meth:`.FeatureStoreClient.log_model`,
        which packages the model with feature metadata. Unless present in ``df``,
        these features will be looked up from :mod:`Feature Store <databricks.feature_store.client>` and joined with ``df``
        prior to scoring the model.

        If a feature is included in ``df``, the provided feature values will be used rather
        than those stored in :mod:`Feature Store <databricks.feature_store.client>`.

        For example, if a model is trained on two features ``account_creation_date`` and
        ``num_lifetime_purchases``, as in:

        .. code-block:: python

            feature_lookups = [
                FeatureLookup(
                    table_name = 'trust_and_safety.customer_features',
                    feature_name = 'account_creation_date',
                    lookup_key = 'customer_id',
                ),
                FeatureLookup(
                    table_name = 'trust_and_safety.customer_features',
                    feature_name = 'num_lifetime_purchases',
                    lookup_key = 'customer_id'
                ),
            ]

            with mlflow.start_run():
                training_set = fs.create_training_set(
                    df,
                    feature_lookups = feature_lookups,
                    label = 'is_banned',
                    exclude_columns = ['customer_id']
                )
                ...
                  fs.log_model(
                    model,
                    "model",
                    flavor=mlflow.sklearn,
                    training_set=training_set,
                    registered_model_name="example_model"
                  )

        Then at inference time, the caller of :meth:`FeatureStoreClient.score_batch` must pass
        a :class:`DataFrame <pyspark.sql.DataFrame>` that includes ``customer_id``, the ``lookup_key`` specified in the
        ``FeatureLookups`` of the :mod:`training_set <databricks.feature_engineering.training_set>`.
        If the :class:`DataFrame <pyspark.sql.DataFrame>` contains a column
        ``account_creation_date``, the values of this column will be used
        in lieu of those in :mod:`Feature Store <databricks.feature_store.client>`. As in:

        .. code-block:: python

            # batch_df has columns ['customer_id', 'account_creation_date']
            predictions = fs.score_batch(
                'models:/example_model/1',
                batch_df
            )

        :param model_uri: The location, in URI format, of the MLflow model logged using
          :meth:`FeatureStoreClient.log_model`. One of:

            * ``runs:/<mlflow_run_id>/run-relative/path/to/model``

            * ``models:/<model_name>/<model_version>``

            * ``models:/<model_name>/<stage>``

          For more information about URI schemes, see
          `Referencing Artifacts <https://bit.ly/3wnrseE>`_.
        :param df: The :class:`DataFrame <pyspark.sql.DataFrame>` to score the model on. :mod:`Feature Store <databricks.feature_store.client>` features will be joined with
          ``df`` prior to scoring the model. ``df`` must:

              1. Contain columns for lookup keys required to join feature data from Feature
              Store, as specified in the ``feature_spec.yaml`` artifact.

              2. Contain columns for all source keys required to score the model, as specified in
              the ``feature_spec.yaml`` artifact.

              3. Not contain a column ``prediction``, which is reserved for the model's predictions.
              ``df`` may contain additional columns.

          Streaming DataFrames are not supported.

        :param result_type: The return type of the model.
           See :func:`mlflow.pyfunc.spark_udf` result_type.
        :return: A :class:`DataFrame <pyspark.sql.DataFrame>`
           containing:

            1. All columns of ``df``.

            2. All feature values retrieved from Feature Store.

            3. A column ``prediction`` containing the output of the model.

        """
        return self._training_set_client.score_batch(
            model_uri=model_uri,
            df=df,
            result_type=result_type,
            client_name=FEATURE_STORE_CLIENT,
            timestamp_key=timestamp_key,
        )

    def set_feature_table_tag(self, name: str, database_name: str, key: str, value: str, catalog_name: Optional[str] = None):
        """
        设置特征表标签
        Args:
            name: 特征表名称
            database_name: 数据库名称
            key: 标签键
            value: 标签值
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog
        Returns:
            None
        """
        self._feature_table_client.alter_table_tag(
            name=name,
            database_name=database_name,
            catalog_name=catalog_name,
            properties={key: value},
            mode="add",
        )

    def delete_feature_table_tag(self, name: str, database_name: str, key: str, catalog_name: Optional[str] = None):
        """
        删除特征表标签
        Args:
            name: 特征表名称
            database_name: 数据库名称
            key: 标签键
            catalog_name: catalog名称（可选）。如果不提供，将使用当前Spark会话的catalog
        Returns:
            None
        """
        self._feature_table_client.alter_table_tag(
            name=name,
            database_name=database_name,
            catalog_name=catalog_name,
            properties={key: ""},
            mode="delete"
        )

    @property
    def spark(self):
        return self._spark
