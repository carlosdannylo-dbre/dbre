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
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import boto3


@dataclass
class ResourceActivity:
    profile: str
    resource_type: str
    identifier: str
    last_activity: Optional[dt.datetime]

    def to_row(self, months: int) -> Dict[str, str]:
        return {
            "profile": self.profile,
            "resource_type": self.resource_type,
            "identifier": self.identifier,
            "last_activity_utc": self.last_activity.isoformat() if self.last_activity else "nunca",
            "checked_months": str(months),
        }


def prompt_months(default: int = 6) -> int:
    raw = input(f"Quantos meses deseja analisar? [{default}]: ").strip()
    try:
        value = int(raw) if raw else default
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        print("Valor inválido, usando padrão de 6 meses.")
        return default


def build_time_range(months: int) -> Tuple[dt.datetime, dt.datetime, dt.datetime]:
    now = dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(days=30 * months)
    three_months_ago = now - dt.timedelta(days=90)
    return start, now, three_months_ago


def load_profiles(config_path: Path) -> List[str]:
    """Carrega os profiles a partir de um arquivo de configuração AWS."""
    import configparser

    if not config_path.exists():
        print(f"Arquivo de configuração {config_path} não encontrado. Usando profile padrão.")
        return ["default"]

    config = configparser.ConfigParser()
    config.read(config_path)

    profiles: List[str] = []
    for section in config.sections():
        if section == "default":
            profiles.append("default")
        elif section.startswith("profile "):
            profiles.append(section.split(" ", 1)[1])
        else:
            profiles.append(section)

    if not profiles:
        profiles.append("default")
    return profiles


def resolve_shared_credentials(credentials_path: Path) -> None:
    """Aponta boto3 para um arquivo de credenciais se ele existir."""
    if credentials_path.exists():
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(credentials_path)
    else:
        # Permite observabilidade explícita caso o arquivo esperado não exista.
        print(
            f"Arquivo de credenciais {credentials_path} não encontrado. "
            "Usando credenciais padrão configuradas no ambiente."
        )


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


def combined_last_activity(
    cw,
    queries: Iterable[Tuple[str, str, Sequence[Dict[str, str]], str]],
    start: dt.datetime,
    end: dt.datetime,
) -> Optional[dt.datetime]:
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


def scan_elasticache(
    profile: str,
    cw,
    client,
    start: dt.datetime,
    end: dt.datetime,
) -> List[ResourceActivity]:
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
            activities.append(ResourceActivity(profile, "elasticache-replication-group", group_id, last))
    return activities


def scan_dynamodb(
    profile: str,
    cw,
    client,
    start: dt.datetime,
    end: dt.datetime,
) -> List[ResourceActivity]:
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
            activities.append(ResourceActivity(profile, "dynamodb", table_name, last))
    return activities


def scan_documentdb(
    profile: str,
    cw,
    client,
    start: dt.datetime,
    end: dt.datetime,
) -> List[ResourceActivity]:
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
            activities.append(ResourceActivity(profile, "documentdb", identifier, last))
    return activities


def generate_csv(rows: List[ResourceActivity], months: int, output_path: str = "inactive_resources.csv") -> None:
    fieldnames = ["profile", "resource_type", "identifier", "last_activity_utc", "checked_months"]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_row(months))


def main() -> None:
    months = prompt_months()
    start, end, three_months_ago = build_time_range(months)

    config_path = Path("./AWS/config")
    credentials_path = Path("./AWS/credentials")
    os.environ["AWS_CONFIG_FILE"] = str(config_path)
    resolve_shared_credentials(credentials_path)
    profiles = load_profiles(config_path)

    candidates: List[ResourceActivity] = []
    failures: List[str] = []
    scanned_count = 0

    for profile in profiles:
        print(f"Processando profile: {profile}")
        try:
            session = boto3.Session(profile_name=profile)
            cloudwatch = session.client("cloudwatch")
            elasticache = session.client("elasticache")
            dynamodb = session.client("dynamodb")
            docdb = session.client("docdb")

            for activity in (
                scan_elasticache(profile, cloudwatch, elasticache, start, end)
                + scan_dynamodb(profile, cloudwatch, dynamodb, start, end)
                + scan_documentdb(profile, cloudwatch, docdb, start, end)
            ):
                scanned_count += 1
                if activity.last_activity is None or activity.last_activity < three_months_ago:
                    candidates.append(activity)
        except Exception as exc:  # boto3/botocore failures
            failures.append(f"{profile}: {exc}")
            continue

    generate_csv(candidates, months)

    if candidates:
        print("Recursos inativos identificados:")
        for item in candidates:
            last = item.last_activity.isoformat() if item.last_activity else "nunca"
            print(
                f"{item.profile} | {item.resource_type}: {item.identifier} | última atividade: {last}"
            )
    else:
        print("Nenhum recurso inativo encontrado para os perfis processados.")

    print(f"Recursos adicionados ao CSV: {len(candidates)} (de {scanned_count} analisados)")
    if failures:
        print("Perfis com falha:")
        for failure in failures:
            print(f" - {failure}")
    else:
        print("Nenhum profile falhou durante a execução.")

    sys.stdout.flush()


if __name__ == "__main__":
    main()
