# "build a Docker image from a Dockerfile, assume the Dockerfile is in the current directory, assume docker desktop is running at localhost"
# docker build ./ -t rz-ent-chatbot-azure-openai:0.1
# docker run -it --name ent-chatbot-azure-openai -p80:80 rz-ent-chatbot-azure-openai:0.1

# "login to Azure Container Registry"
# docker login acr0612.azurecr.cn
# "create a new tag for a Docker image with repository name"
# docker tag rz-ent-chatbot-azure-openai:0.1 acr0612.azurecr.cn/rz-ent-chatbot-azure-openai:0.1
# "push a Docker image to a container registry"
# docker push acr0612.azurecr.cn/rz-ent-chatbot-azure-openai:0.1

# "create Azure app service and choose linux docker container"
# "choose above container registry and image, linux docker by default uses 80 port"

FROM python:3.11 

WORKDIR /usr/src/app 

COPY requirements.txt ./ 

RUN pip install --no-cache-dir -r requirements.txt 

COPY . . 

CMD [ "python", "./Enterprise_KB_Chatbot.py" ]
