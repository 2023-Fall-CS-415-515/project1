Running the code on the VM:
sudo docker-compose up --build

As of right now, there is an issue with the docker deployment between the postgres database connecting with each of the crawlers.
We have tried hours upon hours of troubleshooting, with no success as of yet. 
We are able to run locally with no issue as well as on the VM, but not while the crawlers are running continuously
within a container. 
