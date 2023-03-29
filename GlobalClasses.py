import os


class GlobalContext:
    OPENAI_API_KEY = ""  # set by __init__ # your Azure openai api key
    OPENAI_BASE = ""  # set by __init__ , e.g. "https://<your_azure_open_ai>.openai.azure.com"
    MY_CHATGPT_ENGINE = "gpt-35-turbo"
    openai_param_temperature = 0.7
    openai_param_max_tokens = 250
    openai_param_top_p = 0.9
    openai_param_frequency_penalty = 0
    openai_param_n = 1
    openai_param_timeout = 60
    openai_param_presence_penalty = 0
    cognitive_subscription = ""  # set by __init__ # your cognitive subscription key
    cognitive_region = "chinaeast2"  # your cognitive region
    txt_translate_key = ""  # set by __init__ # your cognitive translation key
    txt_translate_endpoint = "https://api.translator.azure.cn"  # cognitive endpoint
    txt_translate_to_languages = ['zh-Hans']  # ['zh-Hant', 'zh-Hans', 'en']
    speech_recognition_language = "zh-cn"  # "en-US"
    text_to_speech_language = "zh-CN-XiaoxiaoNeural"  # 'en-US-JennyNeural'
    translation_source_language = "zh-cn"  # "en-US"
    translation_targe_language = "en"  # "zh-Hans"
    chat_system_message_plain = ""
    chat_system_message = ""
    chat_history = []
    chat_prompt = ""
    chat_latest_return = ""
    message_for_read_out = ""
    user_message = ""
    source_doc_reference_str = ""
    need_read_output = False
    need_translate = False
    original_sound_text = ""
    # system_plain_message = '''Assistant is an intelligent chatbot designed to help users answer any questions, and also able to access internet to retrieve content for analysis and giving advice'''
    system_plain_message = '''Assistant is an intelligent chatbot designed to help users answer consumer product related questions and sell P&G products. 
Instructions:
- Only answer questions related to Procter & Gamble. 
- If you're unsure of an answer, you can say "I don't know" or "I'm not sure" and recommend users go to the P&G website for more information.'''
    system_message = "<|im_start|>system\n{}\n<|im_end|>".format(
        system_plain_message.replace("\n", "\\n"))

    def __init__(self):
        # get environment variables set by .env file
        GlobalContext.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        GlobalContext.OPENAI_BASE = os.getenv("OPENAI_BASE")
        GlobalContext.cognitive_subscription = os.getenv(
            "cognitive_subscription")
        GlobalContext.txt_translate_key = os.getenv("txt_translate_key")
