# Cluster mycluster1

module "terraform-gcp-filestore-backups-mycluster1" {
  source  = "./module/"

  # Define ONLY the name of needed cluster
  cluster = "mycluster1"
  secret_name = "your_secret_name"
}

# Cluster mycluster2

module "terraform-gcp-filestore-backups-mycluster2" {
  source  = "./module/"

  # Define ONLY the name of needed cluster
  cluster = "mycluster2"
  secret_name = "your_secret_name"
}

# Cluster mycluster3

module "terraform-gcp-filestore-backups-mycluster3" {
  source  = "./module/"

  # Define ONLY the name of needed cluster
  cluster = "mycluster3"
  secret_name = "your_secret_name"
}