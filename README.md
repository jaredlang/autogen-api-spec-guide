# AutoGen Service API Chatbot

The app is created to go through an end-to-end deployment of a streamlit app to Azure App Service. It was a bumpy journey and took me several hours. It worked finally but the experience was quite frustrating.

## Use Visual Code

- It may be convenient, but it is not working reliably.
- It takes a long time (like 20+ minutes) to complete it.
- Sometimes the deployment is stuck with no info given in Visual Code or Azure App Service.
- Even after it is deployed, the app can't start with the issue: *the chromadb issue with sqlite3*. This is the same issue when deploying the app to Streamlit Cloud.
- Azure Log Stream has serious delay and misses any log, which basically is useless.

## Use Github Action

- I set up continuous deployment in Deployment Center.
- Similarly to the deployment from Visual Code, it takes a long time. Most of the time (18+ minutes) was to Run azure/webapps-deploy@v3. The build performance is tolerable.
- Even after it is deployed, the app can't start with the issue: *the chromadb issue with sqlite3*.

## Deploy a dockerized image

- This approach is the only one that works. But there are a lot of catches after the successful local run.
    * **The port must be 8501** due to Azure App Service network restriction.
    * The startup command need to be *CMD [ "bash", "./startup.sh"]* in the docker image.
    * Azure Container Registry must be in the same region as the ASP.
    * The image is almost 10GB (crazy!). The slim image only gives a couple of GB saving. It didn't help much.
    * With my upload network bandwidth, it took about 30+ minutes to push the image to Azure CR.
    * The troubleshooting is problematic. Azure Log Stream offers no help, but frustration.
    * Azure does offer continuous deployment to the container-based deployment, but there is a good amount of delay between an image is pushed and the deployment is trigger. Not reliable!
- At the end the app runs. It requires a lot of work compared with the other two.
- The warmup duration is pretty long at the first time, but it gets shorter afterwards.
- Then I ran into several issues:
  - Firstly, it ran into an issue: Not able to access MongoDB Atlas. I changed the MongoDB network settings to all network access. It fixed the issue.
  - Secondly, occasionally I ran into this error after several initial runs: "ValueError: Could not connect to tenant default_tenant. Are you sure it exists?". The issue can be fixed by restarting the app service. The chromadb file definitely exists. Haven't yet investigated it.
  - Thirdly, even with the Premium0V3 (P0v3) ASP, it takes several minutes to get a response. It is much slower than the local hosting, which is understandable.

## Deploy to HuggingFace.co

With the frustrating experience with Azure App Service, I want to try the deployment on HuggingFace.

1. Create a space *Api Dev Chatbot* in HuggingFace.co, <https://huggingface.co/spaces/liangchen76/api-dev-chatbot>.
2. Decide to build a docker image to avoid the chromadb issue with sqlite3, even though HF does provide a streamlit deployment.
3. [HF only opens **port 7860**](https://huggingface.co/spaces/liangchen76/api-dev-chatbot/blob/main/Dockerfile). Keep everything else the same and push the source code to the HF space.
4. Have to set up ssh to commit to HF space.
5. HF requires [this README template](https://huggingface.co/spaces/liangchen76/api-dev-chatbot/blob/main/README.md).
6. After the source code is pushed, the build and deployment are significantly faster than Azure.
7. Even with the free tier, the running performance is pretty good. It is way better than Azure App Service free tier.
8. One catch: the whole space can either be private or public, including the source code.

**The plumbing work is killing the productivity.**
