"""
Script para varrer métricas de ElastiCache, DynamoDB e DocumentDB usando boto3.

O script pergunta quantos meses de histórico devem ser avaliados e grava em um
CSV todos os recursos que não apresentaram atividade de conexão nos últimos
três meses, informando também qual foi a última atividade encontrada dentro da
janela analisada.
"""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import boto3


@dataclass
class ResourceActivity:
    resource_type: str
    identifier: str
    last_activity: Optional[dt.datetime]

    def to_row(self, months: int) -> Dict[str, str]:
        return {
            "resource_type": self.resource_type,
            "identifier": self.identifier,
            "last_activity_utc": self.last_activity.isoformat() if self.last_activity else "nunca",
            "checked_months": str(months),
        }


def prompt_months(default: int = 6) -> int:
    raw = input(f"Quantos meses deseja analisar? [{default}]: ").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        print("Valor inválido, usando padrão de 6 meses.")
        return default


def build_time_range(months: int) -> Tuple[dt.datetime, dt.datetime, dt.datetime]:
    now = dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(days=30 * months)
    three_months_ago = now - dt.timedelta(days=90)
    return start, now, three_months_ago


def metric_last_activity(
    cw, *,
    namespace: str,
    metric_name: str,
    dimensions: Sequence[Dict[str, str]],
    stat: str,
    start: dt.datetime,
    end: dt.datetime,
    period: int = 86_400,
) -> Optional[dt.datetime]:
    query_id = "m1"
    resp = cw.get_metric_data(
        MetricDataQueries=[
            {
                "Id": query_id,
                "MetricStat": {
                    "Metric": {
                        "Namespace": namespace,
                        "MetricName": metric_name,
                        "Dimensions": [
                            {"Name": d["Name"], "Value": d["Value"]}
                            for d in dimensions
                        ],
                    },
                    "Period": period,
                    "Stat": stat,
                },
                "ReturnData": True,
            }
        ],
        StartTime=start,
        EndTime=end,
        ScanBy="TimestampDescending",
    )
    if not resp.get("MetricDataResults"):
        return None

    result = resp["MetricDataResults"][0]
    timestamps = result.get("Timestamps", [])
    values = result.get("Values", [])

    for ts, value in zip(timestamps, values):
        if value and value > 0:
            return ts
    return None


def combined_last_activity(cw, queries: Iterable[Tuple[str, str, Sequence[Dict[str, str]], str]], start: dt.datetime, end: dt.datetime) -> Optional[dt.datetime]:
    latest: Optional[dt.datetime] = None
    for namespace, metric, dimensions, stat in queries:
        ts = metric_last_activity(
            cw,
            namespace=namespace,
            metric_name=metric,
            dimensions=dimensions,
            stat=stat,
            start=start,
            end=end,
        )
        if ts and (latest is None or ts > latest):
            latest = ts
    return latest


def scan_elasticache(cw, client, start: dt.datetime, end: dt.datetime) -> List[ResourceActivity]:
    activities: List[ResourceActivity] = []
    paginator = client.get_paginator("describe_replication_groups")
    for page in paginator.paginate():
        for group in page.get("ReplicationGroups", []):
            group_id = group["ReplicationGroupId"]
            member_clusters = group.get("MemberClusters", [])
            if not member_clusters:
                continue

            # Avalia o nó primário; se necessário, expanda para todos os membros.
            cache_cluster_id = member_clusters[0]
            dims = [
                {"Name": "CacheClusterId", "Value": cache_cluster_id},
            ]
            last = combined_last_activity(
                cw,
                [
                    ("AWS/ElastiCache", "CacheHits", dims, "Sum"),
                    ("AWS/ElastiCache", "CacheMisses", dims, "Sum"),
                    ("AWS/ElastiCache", "CurrConnections", dims, "Average"),
                ],
                start,
                end,
            )
            activities.append(ResourceActivity("elasticache-replication-group", group_id, last))
    return activities


def scan_dynamodb(cw, client, start: dt.datetime, end: dt.datetime) -> List[ResourceActivity]:
    activities: List[ResourceActivity] = []
    paginator = client.get_paginator("list_tables")
    for page in paginator.paginate():
        for table_name in page.get("TableNames", []):
            dims = [{"Name": "TableName", "Value": table_name}]
            last = combined_last_activity(
                cw,
                [
                    ("AWS/DynamoDB", "ConsumedReadCapacityUnits", dims, "Sum"),
                    ("AWS/DynamoDB", "ConsumedWriteCapacityUnits", dims, "Sum"),
                ],
                start,
                end,
            )
            activities.append(ResourceActivity("dynamodb", table_name, last))
    return activities


def scan_documentdb(cw, client, start: dt.datetime, end: dt.datetime) -> List[ResourceActivity]:
    activities: List[ResourceActivity] = []
    paginator = client.get_paginator("describe_db_clusters")
    for page in paginator.paginate():
        for cluster in page.get("DBClusters", []):
            identifier = cluster["DBClusterIdentifier"]
            dims = [{"Name": "DBClusterIdentifier", "Value": identifier}]
            last = combined_last_activity(
                cw,
                [("AWS/DocDB", "DatabaseConnections", dims, "Average")],
                start,
                end,
            )
            activities.append(ResourceActivity("documentdb", identifier, last))
    return activities


def generate_csv(rows: List[ResourceActivity], months: int, output_path: str = "inactive_resources.csv") -> None:
    fieldnames = ["resource_type", "identifier", "last_activity_utc", "checked_months"]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_row(months))


def main() -> None:
    months = prompt_months()
    start, end, three_months_ago = build_time_range(months)

    cloudwatch = boto3.client("cloudwatch")
    elasticache = boto3.client("elasticache")
    dynamodb = boto3.client("dynamodb")
    docdb = boto3.client("docdb")

    candidates: List[ResourceActivity] = []
    for activity in (
        scan_elasticache(cloudwatch, elasticache, start, end)
        + scan_dynamodb(cloudwatch, dynamodb, start, end)
        + scan_documentdb(cloudwatch, docdb, start, end)
    ):
        if activity.last_activity is None or activity.last_activity < three_months_ago:
            candidates.append(activity)

    generate_csv(candidates, months)

    for item in candidates:
        last = item.last_activity.isoformat() if item.last_activity else "nunca"
        print(f"{item.resource_type}: {item.identifier} | última atividade: {last}")


if __name__ == "__main__":
    main()
