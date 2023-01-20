
Step1: What will LSTM do?
      1. LSTM will accept the GitHub data from flask microservice and will forecast the data for past 1 year based on past 30 days
      2. It will also plot three different graph (i.e.  "model_loss", "lstm_generated_data", "all_issues_data")using matplot lib 
      3. This graph will be stored as image in gcloud storage.
      4. The image URL are then returned back to flask microservice.

Step2: What is Google Cloud Storage?
       Google Cloud Storage is a RESTful online file storage web service for storing and accessing data on Google Cloud
       Platform infrastructure.    


Step3: Deploying LSTM to gcloud platform
       1: You must have Docker(https://www.docker.com/get-started) and Google Cloud SDK(https://cloud.google.com/sdk/docs/install) 
           installed on your computer.  
       2. Steps to follow while creating LSTM gcloud project:
            1. Go to GCP Platform, create a LSTM gcloud project.enable the following:
               a.billing account
               b.Conatiner Registry API
               c.Cloudbuild API
            2. After creating the LSTM gcloud project follow the below steps:
               a. go to gcloud storage of LSTM gcloud project then click on create bucket.
               b. then add name to your bucket (bucket name should be unique) click on continue.
               c. then choose where to store your data.
               d. there choose location type to "region" and location to "us-central1(Iowa)", then click on continue.
               e. then Choose a default storage class for your data
               f. choose option "standard" and click continue and then click on create then you will automatically navigated to "bucket details"
               g. there you will see "objects" and in "objects" you will see "buckets" click on "buckets", you will be able to see your assigned bucket name with checkbox
               h. click on checkbox, then on the right side you will be able to see "permission" and "labels",in "permission" scroll down you will be able to see
                  "ADD PRINCIPAL" 
               i. click on "ADD PRINCIPAL" you will be able to see "new principals" and "select a role", in "new principals" type "allUsers" and in 
                  "select a role" go to "cloud storage" click on "cloud storage" and select "storage object viewer" and hit on save after this
               j.  copy the BUCKET_NAME (your unique assigned bucket name) and paste it in sticky notes for futher use.
            3. After this, go to "https://cloud.google.com/docs/authentication/getting-started#create-service-account-console"  and 
               there you will see creating service account, go to creating service account, click on console, and hit on creating service account
            4. Then select your LSTM created project, in service account details add service name "your unique service name"(service name should be unique) and click on "create and 
               continue", then in Grant this service account access to project click on "select the role",choose "basic" and choose "owner"and hit on done.
            5. After that you will see your created service, click on the created service, go to keys, click on add key, and click create new key.
            6. Created key will get downloaded in .json format, copy that downloaded file in the given LSTM code
            7. Then, on cmd terminal type "set GOOGLE_APPLICATION_CREDENTIALS=KEY_PATH" (Replace KEY_PATH with the path of the JSON file that contains your service account key.)

       3: Type `docker` on cmd terminal and press enter to get all required information

       4: Type `docker build .` on cmd to build a docker image

       5: Type `docker images` on cmd to see our first docker image. After hitting enter, newest created image will be always on the top of the list

       6: Now type `docker tag <your newest image id> gcr.io/<your project-id>/<project-name>` and hit enter 
            Type `docker images` to see your image id updated with tag name

       7: Type `gcloud init` on cmd and it will prompt Create or select a configuration choose existing configurations and hit enter and
          it will prompt Choose a current Google Cloud project, choose your current gcloud project number and hit enter.
          

       8: Type `gcloud auth configure-docker` on cmd hit enter and then type "docker images"

       9: Type `docker push <your newest created tag>` on cmd and hit enter

       10: Go to container registry you will see your newly pushed docker image, click on that docker image, after clicking, you will be able to see
          docker image id and on the right side you will see "⋮", left click on "⋮" there you will be able to see option "deploy it to cloud run" click on that and 
          it will navigate you to cloud run where in container image url hit select and select your latest id and change the Min Instance to 1 instead of 0 and the option 
          to allow unauthorized access when creating new service and then go to container tab and edit container port to '8080', increase the memory limit 
          to 1GiB and go to variable and secrets tab and click on add environment variable as follows(there will three environment variable):
                Name                                 value  
            a. GOOGLE_APPLICATION_CREDENTIALS     "<your_json_filename>.json"
            b. BASE_IMAGE_PATH                    "https://storage.googleapis.com/your bucket name/"
            c. BUCKET_NAME                         "your bucket name"
            
      NOTE: For the environment variable, ".json" and "/" is mandatory in there respective environment variable value
            because ".json" have all your gcloud information and secrets keys and "/" is a app route path.

       11: Hit the create, this will create the service on port 8080 and will generate the url, hit the url.

       12. Copy the generated LSTM gcloud url and paste it in sticky notes for further use

     
Step4: To run locally:
       1. Go to cmd terminal and type following:
        a. python -m venv env
        b. env\Scripts\activate.bat
        c. pip install -r requirements.txt
        d. python app.py  