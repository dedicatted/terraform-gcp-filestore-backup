## Filestore backups

This Terraform code providing accessibility to automatically deploy Google Function and Google Scheduler to trigger scheduled Filestore instance backup.
For Google Function I've decided to choose Python and write a simple script what is making a simple POST request to filestore's api what's triggering create of a new isntance backup.

Terraform code in this repository provide you possibility to deploy a needed function for backups for already exist Filestore instance. 
In my case I needed it for a couple of clusters in GKE, so I decided to write a simple terraform code, basic Python script with a few functions to trigger the backup, check a state in loop (wait until it's
READY) and notify in Failed state in Slack. 

Google Cloud Resources in use:

1. Google Functions       (Required)
2. Google Secret Manager  (Optional)
3. Google Storage Bucket  (Required)
4. Google Cloud IAM       (Required)

```
To store your slack in to Google Secret Manager it should be done manually. 
After you'll create a new secret with your Slack webhook URL pay attention you'll need an ID of this resource.
Now just add it in to the field secret_name in main.tf for each replica of module in use.

If you don't want to use Google Secrets Manager you can simply delete a section with 
*secret_environment_variables* in *module/filestore-backup.tf* and replace it with *environment_variables*
```

Terraform version: v1.2.3
Terraform state in my case is on Terraform Enterprise side, so it commented in *provider.tf*

### How to add a new cluster to backups:

1. Go in to main.tf and add one more part of code below:
```
module "terraform-gcp-filestore-backups-mycluster" {
  source  = "./module/"

  # Define ONLY the name of needed cluster
  cluster = "mycluster1" # <- Your cluster name (e.g. mycluster1 / mycluster2 / mycluster3 ... / etc)
}
```

There is only two Required variable to define under "module" block called *cluster*.
1. It should have a short identifier of a cluster (e.g. mycluster1 / mycluster2 / mycluster3 ... / etc).
2. Go to *src/* dir, create a new folder with a short name of your cluster (e.g. mycluster1 / mycluster2 / mycluster3 ... / etc).
3. secret_name is a name of your secret in Google Secret Manager

Now go inside the /src/mycluster1/main.py you need to edit two things:

- #### Block with main script variables (edit with your values):
```
# Backup environment variables
PROJECT_ID = 'PROJECT_NAME'
SOURCE_INSTANCE_ZONE = 'INSTANCE_ZONE'
SOURCE_INSTANCE_NAME = 'INSTANCE_NAME'
SOURCE_FILE_SHARE_NAME = 'volumes'
BACKUP_REGION = 'YOUR_REGION'
```
- #### Name of your cluster Filestore backups
```
def get_backup_id():
    return "mycluster1-" + time.strftime("%Y%m%d-%H%M%S")
```
Here you are required to change only a section with "mycluster1" to short ID of your cluster.

This thing should be done for each one of script-replica under main.tf and src/mycluster$/main.py