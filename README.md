# OpenAIEnterpriseChatBotAndQA
OpenAI Enterprise knowledge search ChatBot and QA 

## Installation 
1. Install Python runtime (This repo is developed with Python 3.11.2)
2. Download and install [Microsoft Visual C++ Redistributable packages](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170&preserve-view=true#visual-studio-2015-2017-2019-and-2022) (choose X64 version if you setup inside windows VM on Azure)
3. Install the dependencies on your machine:
```
pip install -r ./requirements.txt
```
4. Create your Azure OpenAI service and get your `OPENAI_API_BASE` and `OPENAI_API_KEY`.
5. [Deploy OpenAI models](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model), deploy at least `text-embedding-ada-002` and `text-davinci-003`, and remember keep the deployment name same as model name, otherwise you need change the source code file `Enterprise_KB_Chatbot.py` and `Enterprise_KB_Ingest.py` accorddingly.
6. (Optional) Create Azure speech service and get `SPEECH_KEY`, `SPEECH_REGION` according to [this KB](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-speech-to-text?tabs=windows%2Cterminal&pivots=programming-language-csharp#prerequisites).
7. (Optional) Create Azure cognitive translation service and get `TRANSLATOR_KEY`, `TRANSLATOR_LOCATION`, `TRANSLATOR_ENDPOINT` according to [this KB](https://learn.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translator?tabs=python#prerequisites).
8. Clone the project onto your Windows, create a .env file at the project folder, and provide all necessary environment variables you get from above steps as below example. Azure Speech and Translator service keys are optional if you don't need speech and tranlation services integrated.
```
OPENAI_API_KEY=00000000000000000000000000000000
OPENAI_BASE=https://<youroai>.openai.azure.com
SPEECH_KEY=00000000000000000000000000000000
SPEECH_REGION=chinaeast2
TRANSLATOR_KEY=00000000000000000000000000000000
TRANSLATOR_LOCATION=chinaeast2
TRANSLATOR_ENDPOINT=https://api.translator.azure.cn/
```

## Prepare VectorDB ingestion

## Run chatbot
1. Run following command at your project folder
```
python ./Enterprise_KB_Chatbot.py
```
2. Use local brower to access http://127.0.0.1:7860/
3. If you want to make your application internate accessiable, change the last line code in `Enterprise_KB_Chatbot.py`
from
```
demo.launch()
```
to
```
demo.launch(auth=("admin", "pass1234"), share=True)
```
then run your application, get the internet accessiable url which printed on the screen, you need keep your application running locally while have others access from this public URL. ( **NOTE**: internet url only available for maximum 72 hours)


## Interaction example for multi-turn conversation 
![image](https://user-images.githubusercontent.com/75886466/229332117-8b410405-007e-4a80-8d1b-ff2b4bf43bfd.png)
![image](https://user-images.githubusercontent.com/75886466/229334605-79464489-0166-4d83-a2dd-da41691d3f51.png)
![image](https://user-images.githubusercontent.com/75886466/229334615-7e9ac57a-844c-4e68-9a2d-fa802d6c61da.png)

## Interaction example for multi language support with cognitive translation integrated
![image](https://user-images.githubusercontent.com/75886466/229334634-97cf1c55-42ca-4e1a-b3fe-ff9377326ff8.png)
![image](https://user-images.githubusercontent.com/75886466/229334639-2502b403-b5fc-4395-8c2e-afb7429814bb.png)

## Interaction example for question un-related to the enterprise KBs 
![image](https://user-images.githubusercontent.com/75886466/229334679-cc6941f5-07fc-4d66-a25e-0969d499fd75.png)
![image](https://user-images.githubusercontent.com/75886466/229334681-8460acd8-1aa7-4b7c-97fd-7c5a2d3cdf8b.png)

**NOTE** : Here we can see the OpenAI model sometimes still try to answer any well-known question even we have indicated not to do so in the prompt, this is also an area of prompt improvement.
