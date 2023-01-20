
Step 1: What will Flask do?
       1. Flask will take the repository_name from the body of the api(i.e. from React) and will fetch the created and closed issues 
          for the given repository for past 1 year
       2. Additionally, it will also fetch the author_name and other information for the created and closed issues.
       3. It will use group_by to group the created and closed issues for a given month and will return back the data to client
       4. It will then use the data obtained from the GitHub and pass it as a input request in the POST body to LSTM microservice
          to predict and to forecast the data
       5. The response obtained from LSTM microservice is also return back to client. 

Step 2: Deploying Flask to gcloud platform
       1: You must have Docker(https://www.docker.com/get-started) and Google Cloud SDK(https://cloud.google.com/sdk/docs/install) 
           installed on your computer. Then, Create a gcloud project and enable the following:
           a.billing account
           b.Conatiner Registry API
           c. Cloudbuild API

       2. Copy the LSTM project url from gcloud and paste it in app.py file line 192 where it is written "your_lstm_gcloud_url/"
       (NOTE: DO NOT REMOVE "/")   

       3: Type `docker` on cmd terminal and press enter to get all required information

       4: Type `docker build .` on cmd to build a docker image

       5: Type `docker images` on cmd to see our first docker image. After hitting enter, newest created image will be always on the top of the list

       6: Now type `docker tag <your newest image id> gcr.io/<your project-id>/<project-name>` and hit enter 
            Type `docker images` to see your image id updated with tag name

       7: Type `gcloud init` on cmd and it will prompt Create or select a configuration choose existing configurations and hit enter and
          it will prompt Choose a current Google Cloud project, choose your current gcloud project number and hit enter.
          
       8: Type `gcloud auth configure-docker` on cmd hit enter and then type "docker images"

       9: Type `docker push <your newest created tag>` on cmd and hit enter

       10: Generate a Personal Access Token on GitHub by following below steps:
          a. Navigate to your Git account settings, then Developer Settings. Click the Personal access tokens menu, then click Generate new token.
          b. Select repo and public as the scope as shown in recording. 
          c. Click Generate Token.
          d. Copy the generated token and paste it in your sticky notes

       11 Go to container registry you will see your newly pushed docker image, click on that docker image, after clicking, you will be able to see
          docker image id and on the right side you will see "⋮", left click on "⋮" there you will be able to see option "deploy it to cloud run" click on that and 
          it will navigate you to cloud run where in container image url hit select and select your latest id and change the Min Instance to 1 instead of 0 and the option 
          to allow unauthorized access when creating new service and then go to container tab and edit container port to '5000', increase the memory limit 
          to 1GiB and go to variable and secrets tab and click on add environment variable as follows
               Name                     value
           a. GITHUB_TOKEN              "Your GitHub generated token"

       12: Click on create, this will create the service on port 5000 and will generate the url, hit the url.

       13: Copy flask gcloud generated url and paste in it sticky notes.
       

Step 3: To run locally:
       1. In app.py, at line 60, add your GitHub token
       2. Go to cmd terminal and type following:
        a. python -m venv env
        b. env\Scripts\activate.bat
        c. pip install -r requirements.txt
        d. change the url of LSTM of file app.py (line 192) http://localhost:8080/
        d. python app.py