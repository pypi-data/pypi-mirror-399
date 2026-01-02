import io
import tarfile
import warnings
from typing import Sequence, overload
from uuid import UUID

import polars
import requests

from vitalx.aggregation.auth_utils import ExecutorAuth, infer_executor_auth
from vitalx.aggregation.dsl import QueryPartial
from vitalx.aggregation.types import QueryBatch, RelativeTimeframe
from vitalx.types.environments import VitalEnvironmentT, VitalRegionT, api_base_url
from vitalx.types.query import Query, QueryConfig


class Executor:
    environment: VitalEnvironmentT
    region: VitalRegionT
    team_id: UUID
    auth: ExecutorAuth

    def __init__(
        self,
        *,
        environment: VitalEnvironmentT,
        region: VitalRegionT,
        team_id: UUID,
        api_key: str | None = None,
    ) -> None:
        self.auth = infer_executor_auth(team_id=team_id, explicit_api_key=api_key)
        self.team_id = team_id
        self.region = region
        self.environment = environment

        warnings.filterwarnings("ignore", message="Polars found a filename")

    @overload
    def query(
        self,
        timeframe: RelativeTimeframe,
        query: Query | QueryPartial,
        /,
        *,
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> tuple[polars.DataFrame]:
        pass

    @overload
    def query(
        self,
        timeframe: RelativeTimeframe,
        query_1: Query | QueryPartial,  # noqa: F841
        query_2: Query | QueryPartial,  # noqa: F841
        /,
        *,
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> tuple[polars.DataFrame, polars.DataFrame]:
        pass

    @overload
    def query(
        self,
        timeframe: RelativeTimeframe,
        query_1: Query | QueryPartial,  # noqa: F841
        query_2: Query | QueryPartial,  # noqa: F841
        query_3: Query | QueryPartial,  # noqa: F841
        /,
        *,
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> tuple[polars.DataFrame, polars.DataFrame, polars.DataFrame]:
        pass

    @overload
    def query(
        self,
        timeframe: RelativeTimeframe,
        query_1: Query | QueryPartial,  # noqa: F841
        query_2: Query | QueryPartial,  # noqa: F841
        query_3: Query | QueryPartial,  # noqa: F841
        query_4: Query | QueryPartial,  # noqa: F841
        /,
        *,
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> tuple[polars.DataFrame, polars.DataFrame, polars.DataFrame, polars.DataFrame]:
        pass

    @overload
    def query(
        self,
        timeframe: RelativeTimeframe,
        query_1: Query | QueryPartial,  # noqa: F841
        query_2: Query | QueryPartial,  # noqa: F841
        query_3: Query | QueryPartial,  # noqa: F841
        query_4: Query | QueryPartial,  # noqa: F841
        query_5: Query | QueryPartial,  # noqa: F841
        /,
        *,
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> tuple[
        polars.DataFrame,
        polars.DataFrame,
        polars.DataFrame,
        polars.DataFrame,
        polars.DataFrame,
    ]:
        pass

    @overload
    def query(
        self,
        timeframe: RelativeTimeframe,
        query_1: Query | QueryPartial,  # noqa: F841
        query_2: Query | QueryPartial,  # noqa: F841
        query_3: Query | QueryPartial,  # noqa: F841
        query_4: Query | QueryPartial,  # noqa: F841
        query_5: Query | QueryPartial,  # noqa: F841
        query_6: Query | QueryPartial,  # noqa: F841
        /,
        *,
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> tuple[
        polars.DataFrame,
        polars.DataFrame,
        polars.DataFrame,
        polars.DataFrame,
        polars.DataFrame,
        polars.DataFrame,
    ]:
        pass

    @overload
    def query(
        self,
        timeframe: RelativeTimeframe,
        /,
        *queries: Query | QueryPartial,  # noqa: F841
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> tuple[polars.DataFrame, ...]:
        pass

    def query(
        self,
        timeframe: RelativeTimeframe,
        /,
        *queries: Query | QueryPartial,
        user_id: UUID,
        config: QueryConfig = QueryConfig(),
    ) -> Sequence[polars.DataFrame]:
        batch = QueryBatch(
            timeframe=timeframe,
            queries=list(
                query if isinstance(query, Query) else query.finalize()
                for query in queries
            ),
            config=config,
        )

        resp = requests.post(
            "{}aggregate/v1/user/{}/query".format(
                api_base_url(self.environment, self.region),
                str(user_id),
            ),
            headers={
                **(self.auth.headers()),
                "Accept": "application/vnd.vital.tar+gzip+parquet",
            },
            json=batch.model_dump(mode="json"),
        )

        resp.raise_for_status()

        df = list[polars.DataFrame]()

        with tarfile.open(fileobj=io.BytesIO(resp.content), mode="r:gz") as tar:
            members = sorted(
                tar.getmembers(), key=lambda m: int(m.name.removesuffix(".parquet"))
            )

            for member in members:
                file = tar.extractfile(member)
                assert file is not None
                df.append(polars.read_parquet(file))

        return df

    def get_result_table(
        self, query_id_or_slug: UUID | str, /, user_id: UUID
    ) -> polars.DataFrame:
        resp = requests.get(
            "{}aggregate/v1/user/{}/continuous_query/{}/result_table".format(
                api_base_url(self.environment, self.region),
                str(user_id),
                str(query_id_or_slug),
            ),
            headers={
                **(self.auth.headers()),
                "Accept": "application/vnd.apache.parquet",
            },
        )

        resp.raise_for_status()

        return polars.read_parquet(resp.content)
