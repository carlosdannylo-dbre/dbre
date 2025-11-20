locals {
  provider_name = upper(var.provider_name)
  labels        = [for key, value in var.tags : { key = key, value = value }]
}

resource "mongodbatlas_advanced_cluster" "this" {
  project_id                   = var.project_id
  name                         = var.name
  cluster_type                 = "REPLICASET"
  backup_enabled               = var.backup_enabled
  mongo_db_major_version       = var.mongo_db_major_version
  termination_protection_enabled = var.termination_protection
  labels                       = local.labels

  replication_specs {
    num_shards = 1

    region_configs {
      provider_name = local.provider_name
      region_name   = var.region

      electable_specs {
        instance_size = var.instance_size
        node_count    = var.node_count
      }

      auto_scaling {
        disk_gb_enabled = var.auto_scaling_disk

        compute {
          enabled            = var.auto_scaling_compute
          scale_down_enabled = var.auto_scaling_compute_scale_down
          min_instance_size  = var.instance_size
          max_instance_size  = coalesce(var.max_instance_size, var.instance_size)
        }
      }
    }
  }
}

resource "mongodbatlas_private_endpoint" "aws" {
  count = local.provider_name == "AWS" ? 1 : 0

  project_id    = var.project_id
  provider_name = "AWS"
  region        = var.region
}

resource "mongodbatlas_private_endpoint_interface_link" "aws_links" {
  for_each = local.provider_name == "AWS" ? toset(var.aws_interface_endpoint_ids) : []

  project_id            = var.project_id
  private_endpoint_id   = mongodbatlas_private_endpoint.aws[0].id
  interface_endpoint_id = each.value
}

resource "mongodbatlas_private_endpoint" "azure" {
  count = local.provider_name == "AZURE" ? 1 : 0

  project_id                    = var.project_id
  provider_name                 = "AZURE"
  region                        = var.region
  private_endpoint_resource_id  = var.azure_private_endpoint_resource_id
  private_endpoint_ip_address   = var.azure_private_endpoint_ip
}

resource "mongodbatlas_private_endpoint_connection" "azure_connections" {
  for_each = local.provider_name == "AZURE" ? toset(var.azure_connection_names) : []

  project_id                     = var.project_id
  private_endpoint_id            = mongodbatlas_private_endpoint.azure[0].id
  private_endpoint_connection_name = each.value
}
