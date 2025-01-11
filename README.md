# AutoGen Service API Chatbot

The app is created to go through an end-to-end deployment of a streamlit app to Azure App Service. It was a bumpy journey. It worked finally but the experience was quite frustrating.

## Use Visual Code

- It may be convenient, but it is not working reliably.
- It takes a long time (like 20+ minutes) to complete it.
- Sometimes the deployment is stuck with no info given in Visual Code or Azure App Service.
- Even after it is deployed, the app can't start with the issue: *the chromadb issue with sqlite3*.
- Azure Log Stream has serious delay and misses any log, which basically is useless.

## Use github action to deploy to App Service

- I set up continuous deployment in Deployment Center.
- Similarly to the deployment from Visual Code, it takes a long time (18+ minutes) to Run azure/webapps-deploy@v3. The build performance is tolerable.
- Even after it is deployed, the app can't start with the issue: *the chromadb issue with sqlite3*.

## Deploy a dockerized image

- This approach is the only one that works. But there are a lot of catches after the successful local run.
  a. The port must be 8501 due to Azure App Service network restriction.
  b. The startup command must be *CMD [ "bash", "./startup.sh"]*.
  c. Azure Container Registry must be in the same region as the ASP.
  d. The image is almost 10GB (crazy!). The slim image only gives a couple of GB saving. It didn't help much.
  e. With my upload network bandwidth, it took about 30+ minutes to push the image to Azure CR.
  f. The troubleshooting is problematic. Azure Log Stream offers no help, but frustration.
  g. Azure does offer continuous deployment to the container-based deployment, but there is a good amount of delay between an image is pushed and the deployment is trigger.
- At the end the app runs. It requires a lot of work compared with the other two.
- The warmup duration is pretty long at the first time, but it gets shorter afterwards.
- Then I ran into several issues:
  - Firstly, it ran into an issue: Not able to access MongoDB Atlas. I changed the MongoDB network settings to all network access. It fixed the issue.
  - Secondly, occasionally I ran into this error after several initial runs: "ValueError: Could not connect to tenant default_tenant. Are you sure it exists?". The issue can be fixed by restarting the app service. The chromadb file definitely exists. Haven't yet investigated it.
  - Thirdly, even with the Premium0V3 (P0v3) ASP, it takes several minutes to get a response. It is much slower than the local hosting, which is understandable.
