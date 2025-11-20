locals {
  default_tags = {
    managed_by  = "terraform"
    environment = var.environment
  }
}

module "project_finance" {
  source = "../../modules/atlas-project"

  name                     = "finance-${var.environment}"
  org_id                   = var.org_id
  project_owner_id         = var.project_owner_id
  teams                    = var.project_teams
  federation_settings_id   = var.federation_settings_id
  external_group_name      = "finance-sre"
  federated_project_roles  = ["GROUP_DATA_ACCESS_ADMIN", "GROUP_OWNER"]
}

module "api_finance" {
  source = "../../modules/atlas-api"

  org_id       = var.org_id
  description  = "Finance automation key (${var.environment})"
  org_roles    = ["ORG_MEMBER"]
  project_ids  = [module.project_finance.project_id]
  project_roles = ["GROUP_DATA_ACCESS_READ_WRITE"]
  access_list  = var.api_access_list
}

module "cluster_finance" {
  source = "../../modules/atlas-cluster"

  name                   = "finance-${var.environment}"
  project_id             = module.project_finance.project_id
  provider_name          = "AWS"
  region                 = var.aws_region
  instance_size          = var.instance_size
  max_instance_size      = var.max_instance_size
  node_count             = var.node_count
  mongo_db_major_version = var.mongo_db_major_version
  tags                   = local.default_tags

  aws_interface_endpoint_ids = var.aws_interface_endpoint_ids
}

module "project_datahub" {
  source = "../../modules/atlas-project"

  name                    = "datahub-${var.environment}"
  org_id                  = var.org_id
  project_owner_id        = var.project_owner_id
  teams                   = var.project_teams
  federation_settings_id  = var.federation_settings_id
  external_group_name     = "datahub-engineering"
  federated_project_roles = ["GROUP_DATA_ACCESS_READ_ONLY"]
}

module "api_datahub" {
  source = "../../modules/atlas-api"

  org_id        = var.org_id
  description   = "Datahub automation key (${var.environment})"
  org_roles     = ["ORG_MEMBER"]
  project_ids   = [module.project_datahub.project_id]
  project_roles = ["GROUP_DATA_ACCESS_READ_ONLY"]
  access_list   = var.api_access_list
}

module "cluster_datahub" {
  source = "../../modules/atlas-cluster"

  name                   = "datahub-${var.environment}"
  project_id             = module.project_datahub.project_id
  provider_name          = "AZURE"
  region                 = var.azure_region
  instance_size          = var.instance_size
  max_instance_size      = var.max_instance_size
  node_count             = var.node_count
  mongo_db_major_version = var.mongo_db_major_version
  tags                   = local.default_tags

  azure_private_endpoint_resource_id = var.azure_private_endpoint_resource_id
  azure_private_endpoint_ip          = var.azure_private_endpoint_ip
  azure_connection_names             = var.azure_connection_names
}
