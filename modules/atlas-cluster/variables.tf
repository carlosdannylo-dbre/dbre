variable "project_id" {
  description = "Atlas project identifier where the cluster will be created."
  type        = string
}

variable "name" {
  description = "Cluster name."
  type        = string
}

variable "provider_name" {
  description = "Cloud provider for the cluster (AWS or AZURE)."
  type        = string
  validation {
    condition     = contains(["AWS", "AZURE"], upper(var.provider_name))
    error_message = "provider_name must be AWS or AZURE"
  }
}

variable "region" {
  description = "Cloud provider region where the cluster and private endpoint will live."
  type        = string
}

variable "instance_size" {
  description = "Base instance size for electable nodes (for example M10)."
  type        = string
}

variable "max_instance_size" {
  description = "Optional maximum instance size for compute auto-scaling."
  type        = string
  default     = null
}

variable "node_count" {
  description = "Number of electable nodes to provision."
  type        = number
  default     = 3
}

variable "backup_enabled" {
  description = "Enable continuous cloud backups."
  type        = bool
  default     = true
}

variable "auto_scaling_compute" {
  description = "Enable compute auto scaling."
  type        = bool
  default     = true
}

variable "auto_scaling_compute_scale_down" {
  description = "Allow compute to scale down automatically."
  type        = bool
  default     = true
}

variable "auto_scaling_disk" {
  description = "Enable disk auto-scaling."
  type        = bool
  default     = true
}

variable "termination_protection" {
  description = "Protect the cluster against accidental deletion."
  type        = bool
  default     = true
}

variable "mongo_db_major_version" {
  description = "MongoDB major version to deploy (e.g. 7.0)."
  type        = string
  default     = "7.0"
}

variable "tags" {
  description = "Map of labels to attach to the cluster."
  type        = map(string)
  default     = {}
}

variable "aws_interface_endpoint_ids" {
  description = "List of AWS VPC endpoint IDs to attach to the Atlas AWS private endpoint."
  type        = list(string)
  default     = []
}

variable "azure_private_endpoint_resource_id" {
  description = "Azure private endpoint resource ID to connect to the Atlas service."
  type        = string
  default     = null
}

variable "azure_private_endpoint_ip" {
  description = "Azure private endpoint static IP address (optional)."
  type        = string
  default     = null
}

variable "azure_connection_names" {
  description = "List of Azure private endpoint connection names to approve."
  type        = list(string)
  default     = []
}
