variable "environment" {
  description = "Deployment environment suffix to help name resources."
  type        = string
  default     = "dev"
}

variable "org_id" {
  description = "Atlas organization ID."
  type        = string
}

variable "project_owner_id" {
  description = "User ID to own created projects."
  type        = string
  default     = null
}

variable "project_teams" {
  description = "Team bindings for every project."
  type = map(object({
    team_id = string
    roles   = list(string)
  }))
  default = {}
}

variable "federation_settings_id" {
  description = "Federation settings ID for SSO mappings."
  type        = string
}

variable "aws_region" {
  description = "AWS region for the finance workload."
  type        = string
}

variable "azure_region" {
  description = "Azure region for the datahub workload."
  type        = string
}

variable "instance_size" {
  description = "Base instance size."
  type        = string
  default     = "M10"
}

variable "max_instance_size" {
  description = "Maximum instance size for auto scaling."
  type        = string
  default     = null
}

variable "node_count" {
  description = "Number of electable nodes."
  type        = number
  default     = 3
}

variable "mongo_db_major_version" {
  description = "MongoDB major version to deploy."
  type        = string
  default     = "7.0"
}

variable "aws_interface_endpoint_ids" {
  description = "AWS VPC interface endpoint IDs for PrivateLink."
  type        = list(string)
  default     = []
}

variable "azure_private_endpoint_resource_id" {
  description = "Azure private endpoint resource ID to connect to Atlas."
  type        = string
  default     = null
}

variable "azure_private_endpoint_ip" {
  description = "Optional static IP address for the Azure private endpoint."
  type        = string
  default     = null
}

variable "azure_connection_names" {
  description = "Azure private endpoint connection names to approve."
  type        = list(string)
  default     = []
}

variable "api_access_list" {
  description = "Access list entries shared by API keys."
  type = map(object({
    cidr_block = optional(string)
    ip_address = optional(string)
    comment    = optional(string, "Managed by Terraform")
  }))
  default = {}
}
