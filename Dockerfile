# docker build ./ -t rz-ent-chatbot-azure-openai:0.1
# docker run -it --name ent-chatbot-azure-openai -p80:80 rz-ent-chatbot-azure-openai:0.1
FROM python:3.11 

WORKDIR /usr/src/app 

COPY requirements.txt ./ 

RUN pip install --no-cache-dir -r requirements.txt 

COPY . . 

CMD [ "python", "./Enterprise_KB_Chatbot.py" ]
