Problem Statement:
The goal of this tutorial is to use GitHub to track created and closed issues of a given repository(angular, material-design, angular-cli,D3)
for the past year along with timeseries forecasting using Tensorflow/LSTM Keras and we will then see how to deploy it to gcloud platform.

Solution:
Step 1: We are creating three microservices:
        1. React 
        2. Flask
        3. LSTM/Keras

Step 2: What will React do?
        1. React will retrieve GitHub created and closed issues for a given repository and will display the bar-charts of same using high-charts        
        2. It will also display the images of the forecasted data for the given GitHub repository and images are being retrieved from GCP storage
        3. React will make a fetch api call to flask microservice.

Step 3: Prerequisites to work with this application:
        1:You must have following installed on your computer:
           a.Docker(https://www.docker.com/get-started) 
           b.Google Cloud SDK(https://cloud.google.com/sdk/docs/install) 
           c.NodeJs (https://nodejs.org/en/download/) (You must install NodeJS if you want to run React application on your machine)
             1. Rules to follow while installing NodeJs
		    a. Go to the link (https://nodejs.org/en/download/)
		    b. Click the Windows Installer button to download the latest default version and choose the location where you want to store Node.js. 
                   (The Node.js installer includes the NPM package manager.)
		    c. Open the newly downloaded Node.js setup. and there you will be able to see
			  "Welcome to the Node.js setup wizard" , "Next", and "cancel". Hit on "Next"
		    d. After clicking next, you will be able to see "End-User Licence Agreement", one
			checkbox with "I accept the terms in the Licence Agreement", click on that checkbox
		    e. After clicking on next, you will be able to see "Destination Folder", there you dont have to make any changes, you just have to click "next"
                f. After clicking next, you should see "Custom Setup" and there you have to click "next"
		    g. After clicking next, you will able to see "Tools for Native Modules" and one checkbox where it is written"Automatically install the necessary tools.
                   Note that this will also install chocolatey. The script will pop-up in a new window after installation completes", you have to click that checkbox and then click "next
		    h. After clicking next. you will be able to see "Ready to install Node.js" there you have to click on "Install"
			 and it will start installing
		    i. After installation, it will show "completed the NOde.js Setup Wizard" there you have to click on "finish"
		    j. After clicking on finish, you will navigate to "user access control" where you have to select "yes"
		    k. After clicking on yes, it will navigate you to "Intall additional tools for Node.js", there it will ask for"press any key to continue" there you have to hit "enter"
                l. you have successfully installed Node.js, NPM and python(Chocolatey will automatically install the latest version of python)
 		    m. After you download and install Node, start your terminal/command prompt and run "node -v" and 
                 "npm -v" to see which versions you have.
                n. Your version of NPM should be at least 5.2.0 or newer because create-react-app requires that we 
                    have NPX installed. If you have an older version of NPM, run the command to update it:"npm install -g npm"
                      
Step 4: Deploying React to gcloud platform
        1: You must have Docker(https://www.docker.com/get-started) and Google Cloud SDK(https://cloud.google.com/sdk/docs/install) 
           installed on your computer. Then, Create a gcloud project and enable the following:
           a.billing account
           b.Conatiner Registry API
           c. Cloudbuild API

        2: Copy the Flask project url from gcloud and paste it in src/setupProxy.js file line 14 where it is written "your_flask_gcloud_url"  

        3: Type `docker` on cmd terminal and press enter to get all required information

        4: Type `docker build .` on cmd to build a docker image

        5: Type `docker images` on cmd to see our first docker image. After hitting enter, newest created image will be always on the top of the list

        6: Now type `docker tag <your newest image id> gcr.io/<your project-id>/<project-name>` and hit enter 
            Type `docker images` to see your image id updated with tag name

        7: Type `gcloud init` on cmd and it will prompt Create or select a configuration choose existing configurations and hit enter and
          it will prompt Choose a current Google Cloud project, choose your current gcloud project number and hit enter.


        8: Type `gcloud auth configure-docker` on cmd hit enter and then type "docker images"

        9: Type `docker push <your newest created tag>` on cmd and hit enter

        10:Go to container registry you will see your newly pushed docker image, click on that docker image, after clicking, you will be able to see
          docker image id and on the right side you will see "⋮", left click on "⋮" there you will be able to see option "deploy it to cloud run" click on that and 
          it will navigate you to cloud run where in container image url hit select and select your latest id and change the Min Instance to 1 instead of 0 and the option 
          to allow unauthorized access when creating new service and then go to container tab and edit container port to '3000', increase the memory limit to 1GiB 
          and click on create.
            
        11: This will create the service on port 3000 and will generate the url, hit the url.   

        

Step 5: To run locally, go to cmd terminal and type following: 
        1. npm install
        2. change the url of flask of file setupProxy.js to "http://localhost:5000"
        3. npm start 

        NOTE: IF YOU WANT TO MAKE YOUR OWN NEW REACT APP THEN GO TO CMD/TERMINAL AND TYPE "npx create-react-app your_folder_name" THAT WILL AUTOMATICALLY INSTALL "node modules",
        "package.json".