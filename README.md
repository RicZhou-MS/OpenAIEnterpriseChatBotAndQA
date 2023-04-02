# OpenAIEnterpriseChatBotAndQA
This repo is made to use [Langchain](https://python.langchain.com/en/latest/getting_started/getting_started.html) to integrate vector search and Azure OpenAI to support Enterprise knowledge search as ChatBot scenario. 

## High level architecture
![image](https://user-images.githubusercontent.com/75886466/229343379-ff315985-cad1-4e14-8ac3-3e6e69021a52.png)

## Installation 
1. Install Python runtime (This repo is developed with Python 3.11.2)
2. Download and install [Microsoft Visual C++ Redistributable packages](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170&preserve-view=true#visual-studio-2015-2017-2019-and-2022) (choose X64 version if you setup inside windows VM on Azure)
3. Clone the project onto your local Windows, install the python dependencies:
```
pip install -r ./requirements.txt
```
4. Create your Azure OpenAI service and get your `OPENAI_API_BASE` and `OPENAI_API_KEY`.
5. [Deploy OpenAI models](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model), deploy at least `text-embedding-ada-002` and `text-davinci-003`, and remember keep the deployment name same as model name, otherwise you need change the source code file `Enterprise_KB_Chatbot.py` and `Enterprise_KB_Ingest.py` accorddingly.
6. (Optional) Create Azure speech service and get `SPEECH_KEY`, `SPEECH_REGION` according to [this KB](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-speech-to-text?tabs=windows%2Cterminal&pivots=programming-language-csharp#prerequisites).
7. (Optional) Create Azure cognitive translation service and get `TRANSLATOR_KEY`, `TRANSLATOR_LOCATION`, `TRANSLATOR_ENDPOINT` according to [this KB](https://learn.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translator?tabs=python#prerequisites).
8. Create a .env file at the project folder, and provide all necessary environment variables you get from above steps as below example. Azure Speech and Translator service keys are optional if you don't need speech and tranlation services integrated.
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
This repo has two demo documents at **Doc_Store** folder, you can replace with your enterprise documents (PDF, DOCX, PPTX are supported so far), then run following command to re-build the vector DB. 
```
python ./Enterprise_KB_Ingest.py
```
**NOTE: If your documents are Chinese version, it's recommended to replace following line code in `Enterprise_KB_Ingest.py` before re-build vector DB.**
```
text_splitter = RecursiveCharacterTextSplitter(chunk_size=ENGLISH_CHUCK_SIZE, chunk_overlap=0) 
```
to
```
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHINESE_CHUNK_SIZE, chunk_overlap=0) 
```
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

## How to change chain type
This project relies on [LangChain](https://python.langchain.com/en/latest/) , you can change the [chain type](https://python.langchain.com/en/latest/modules/chains/index_examples/qa_with_sources.html) according to your needs.
open `Enterprise_KB_Chatbot.py`, find follwing line
```
lc_chatbot = CustomConversationalRetrievalChain.from_llm(lc_chatbot_llm, vectorstore.as_retriever(
), condense_question_prompt=MyPromptCollection.CONDENSE_QUESTION_PROMPT, chain_type="stuff") 
```
and change the **chain_type** to any of `stuff`, `refine`,`map-reduce` or `map-rerank`.

## Enable Speech and Translation
speech and translation functions are disabled by default, if you have speech and translator API key configured at beginning, you can use following approach to enable.

Open `Enterprise_KB_Chatbot.py`, find following code
```
GlobalContext.ENABLE_TRANSLATION = False 
GlobalContext.ENABLE_VOICE = False  
```
and change to
```
GlobalContext.ENABLE_TRANSLATION = True 
GlobalContext.ENABLE_VOICE = True  
```
run the application and you will see the web page changed to below capture (**Note** speech only works when you run the application locally)
![image](https://user-images.githubusercontent.com/75886466/229342647-e6b60727-1476-4c00-80e0-193b87dd3a7f.png)


## Enable single turn Q&A
Single turn Q&A uses [VectorDBQAWithSourcesChain](https://python.langchain.com/en/latest/_modules/langchain/chains/qa_with_sources/vector_db.html), and provide single turn question and answer experience rather than conversational chatbot, which can support some special requirement for enterprise. you use follow approach to enable
Open `Enterprise_KB_Chatbot.py`, find following code
```
GlobalContext.SHOW_SINGLE_TURN_QA = False
```
and change to
```
GlobalContext.SHOW_SINGLE_TURN_QA = True  
```
run the application and you will see the web page append additional portion at bottom as below capture
![image](https://user-images.githubusercontent.com/75886466/229343001-43ee9e21-acd5-48f7-b9de-b475e29df5c0.png)


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
