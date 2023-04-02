# OpenAIEnterpriseChatBotAndQA
OpenAI Enterprise knowledge search ChatBot and QA 

## Installation 
1. Install Python runtime (This repo is developed with Python 3.11.2)
2. Download and install [Microsoft Visual C++ Redistributable packages](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170&preserve-view=true#visual-studio-2015-2017-2019-and-2022)
3. Install the dependencies on your machine:
```
pip install -r ./requirements.txt
```
3. Create a .env file at the project folder, and insert all necessary environment variable as below example, for instance Azure OpenAI key, as well as Azure Cognitive speech subscription key and Cognitive translation service key, the last two are optional if you don't need speech and tranlation services.
```
OPENAI_API_KEY=11234234324243234234234
OPENAI_BASE=https://xyz.openai.azure.com
cognitive_subscription=600342343242343243243247
txt_translate_key=ba234324234werwef3fwefwefw

```

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
