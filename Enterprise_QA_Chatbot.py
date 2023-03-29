"""Ask a question to the vector database."""
import faiss
from langchain.llms import AzureOpenAI
from langchain.chains import (ChatVectorDBChain, VectorDBQAWithSourcesChain)
import pickle
import gradio as gr
import os
import tiktoken
import azure.cognitiveservices.speech as speechsdk
import requests
import uuid
import json
from dotenv import load_dotenv

from GlobalClasses import GlobalContext

load_dotenv()
GlobalContext()  # initialize global context


def language_translate(source_txt, to_language):
    key = GlobalContext.txt_translate_key
    endpoint = GlobalContext.txt_translate_endpoint

    # location, also known as region.
    # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
    location = GlobalContext.cognitive_region

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        # 'from': 'en', # comment out this line if you want to use auto language detection.

        # ['zh-Hant', 'zh-Hans'] # language codes: https://docs.microsoft.com/en-us/azure/cognitive-services/translator/language-support
        'to': to_language  # GlobalContext.txt_translate_to_languages
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': source_txt
    }]

    request = requests.post(constructed_url, params=params,
                            headers=headers, json=body)
    response = request.json()
    result_of_first_translation_languages = response[0]["translations"][0]["text"]
    # print(result_of_first_translation_languages)

    json_result = json.dumps(response, sort_keys=True,
                             ensure_ascii=False, indent=4, separators=(',', ': '))
    return result_of_first_translation_languages


def language_detection(source):
    key = GlobalContext.txt_translate_key
    endpoint = GlobalContext.txt_translate_endpoint
    path = '/detect'
    constructed_url = endpoint + path
    location = GlobalContext.cognitive_region

    params = {
        'api-version': '3.0',
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': source
    }]

    request = requests.post(
        constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    detected_language = response[0]["language"]
    print("[language detected] {}".format(detected_language))
    # print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
    return detected_language


def text_to_voice(text):

    # refer to https://docs.azure.cn/zh-cn/cognitive-services/speech-service/get-started-text-to-speech?tabs=linux%2Cterminal&pivots=programming-language-python
    speech_config = speechsdk.SpeechConfig(
        subscription=GlobalContext.cognitive_subscription, region=GlobalContext.cognitive_region)

    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    # "zh-CN-XiaoxiaoNeural" # 'en-US-JennyNeural'
    if (language_detection(text) == 'en'):
        GlobalContext.text_to_speech_language = 'en-US-JennyNeural'
    else:
        GlobalContext.text_to_speech_language = 'zh-CN-XiaoxiaoNeural'

    speech_config.speech_synthesis_voice_name = GlobalContext.text_to_speech_language

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # print("Speech synthesized for text [{}]".format(text))
        return
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
    return


def voice_to_text():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=GlobalContext.cognitive_subscription, region=GlobalContext.cognitive_region)
    # "zh-cn"  # "en-US"
    speech_config.speech_recognition_language = GlobalContext.speech_recognition_language

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        # print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(
            speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return ""


def translate_from_microphone():
    # refer to https://docs.azure.cn/zh-cn/cognitive-services/speech-service/get-started-speech-translation?tabs=windows%2Cterminal&pivots=programming-language-python

    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=GlobalContext.cognitive_subscription, region=GlobalContext.cognitive_region)
    speech_translation_config.speech_recognition_language = GlobalContext.translation_source_language  # "zh-cn"

    target_language = GlobalContext.translation_targe_language  # "en"  # "zh-Hans"

    speech_translation_config.add_target_language(target_language)

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    translation_recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=speech_translation_config, audio_config=audio_config)

    print("Speak into your microphone.")
    translation_recognition_result = translation_recognizer.recognize_once_async().get()

    if translation_recognition_result.reason == speechsdk.ResultReason.TranslatedSpeech:
        # print("Recognized: {}".format(translation_recognition_result.text))
        # print("""Translated into '{}': {}""".format(target_language, translation_recognition_result.translations[target_language]))
        return translation_recognition_result.text, translation_recognition_result.translations[target_language]
    elif translation_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(
            translation_recognition_result.no_match_details))
    elif translation_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = translation_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return "", ""


def testTranslate():
    original_sound_text, translated_text = translate_from_microphone()
    print("[Original text] {}".format(original_sound_text))
    print("[Translated text] {}".format(translated_text))


def testV2T():
    regstr = voice_to_text()
    print(regstr)


def testT2V():
    # Get text from the console and synthesize to the default speaker.
    print("Enter some text that you want to speak >")
    text = input()
    text = "唔" + text
    text_to_voice(text)


def get_token_len(prompt):
    cl100k_base = tiktoken.get_encoding("cl100k_base")

    enc = tiktoken.Encoding(
        name="gpt-35-turbo",
        pat_str=cl100k_base._pat_str,
        mergeable_ranks=cl100k_base._mergeable_ranks,
        special_tokens={
            **cl100k_base._special_tokens,
            "<|im_start|>": 100264,
            "<|im_end|>": 100265
        }
    )

    tokens = enc.encode(
        prompt,
        allowed_special={"<|im_start|>", "<|im_end|>"}
    )
    return len(tokens)


def create_prompt(system_message, messages):
    prompt = system_message
    for message in messages:
        prompt += f"\n<|im_start|>{message['sender']}\n{message['text']}\n<|im_end|>"
    prompt += "\n<|im_start|>assistant\n"
    return prompt


def execute_chat(user_input):
    GlobalContext.txt_translate_to_languages = language_detection(user_input)
    # user_input = user_input.replace("\n", "\\n")

    print("\n[History]: {}".format(GlobalContext.chat_history))
    result = lc_chatbot({"question": user_input,
                         "chat_history": GlobalContext.chat_history})
    GlobalContext.chat_latest_return = result["answer"]
    print("\n[Answer] {}".format(result["answer"]))

    GlobalContext.chat_history.extend([(user_input, result["answer"])])

    GlobalContext.source_doc_reference_str = ""
    for source_doc in result["source_documents"]:
        GlobalContext.source_doc_reference_str += f"{source_doc.metadata}\n"
        print(source_doc.metadata)

    # keep the history within specific length
    keep_history_turn = 5
    while (len(GlobalContext.chat_history) > keep_history_turn):
        GlobalContext.chat_history.pop(0)

    return result["answer"]


def user(user_message, history):
    GlobalContext.user_message = user_message
    history = history_remove_br(history)
    return history + [[user_message, None]]


def bot(history):
    bot_message = execute_chat(GlobalContext.user_message)
    # bot_message = bot_message.replace("\\n", "\n")

    GlobalContext.message_for_read_out = bot_message
    output_language = language_detection(bot_message)
    if GlobalContext.txt_translate_to_languages != output_language:
        translated = language_translate(
            bot_message, GlobalContext.txt_translate_to_languages)
        GlobalContext.message_for_read_out = translated
        print("\n[Answer Translated]: {}".format(translated))
        bot_message += f"\n{translated}"
    bot_message += f"\n{GlobalContext.source_doc_reference_str}"

    history[-1][1] = bot_message
    history = history_remove_br(history)
    return "", history


def history_remove_br(history):
    for x in range(0, len(history)):
        history[x][0] = history[x][0].replace("<br>", "")
        history[x][1] = history[x][1].replace("<br>", "")
    return history


def readOuput():
    if (GlobalContext.need_read_output):
        print("[reading...] {}".format(GlobalContext.chat_latest_return))
        # text_to_voice("oh " + GlobalContext.chat_latest_return)
        text_to_voice(GlobalContext.chat_latest_return)
        GlobalContext.chat_latest_return = ""
    return gr.Button.update(interactive=True)


def clearHistory():
    GlobalContext.message_for_read_out = ""
    GlobalContext.chat_latest_return = ""
    GlobalContext.chat_history = []
    return ""


def clearHistory_and_backup(history):
    GlobalContext.message_for_read_out = ""
    GlobalContext.chat_latest_return = ""
    GlobalContext.chat_history = []
    return "", history


def change_system_message(system_message):
    GlobalContext.set_openai_system_msg(system_message)
    return clearHistory()


def startRecording(history):
    if (GlobalContext.need_translate):
        GlobalContext.original_sound_text, voice_text = translate_from_microphone()
        print("[Captured text] {}".format(GlobalContext.original_sound_text))
        print("[Translated text] {}".format(voice_text))
    else:
        voice_text = voice_to_text()
        print("[Captured text] {}".format(voice_text))
    GlobalContext.user_message = voice_text
    return history + [[voice_text, None]]


def radioChage(choice):
    if choice == "Say Chinese":
        GlobalContext.speech_recognition_language = "zh-cn"
        GlobalContext.need_translate = False
        # GlobalContext.text_to_speech_language = "zh-CN-XiaoxiaoNeural"
    elif choice == "Say English":
        GlobalContext.speech_recognition_language = "en-US"
        GlobalContext.need_translate = False
        # GlobalContext.text_to_speech_language = 'en-US-JennyMultilingualNeural'  # 'en-US-JennyNeural'
    elif choice == "Say Chinese output English":
        GlobalContext.translation_source_language = "zh-cn"
        GlobalContext.translation_targe_language = "en"
        GlobalContext.need_translate = True
        # GlobalContext.text_to_speech_language = 'en-US-JennyMultilingualNeural'  # 'en-US-JennyNeural'
    elif choice == "Say English output Chinese":
        GlobalContext.translation_source_language = "en-US"
        GlobalContext.translation_targe_language = "zh-Hans"
        GlobalContext.need_translate = True
        # GlobalContext.text_to_speech_language = "zh-CN-XiaoxiaoNeural"
    return None


def readOutSettingChange(checkbox):
    if checkbox:
        GlobalContext.need_read_output = True
    else:
        GlobalContext.need_read_output = False


def change_Openai_param(param_name, value):
    match param_name:
        case "max_tokens":
            GlobalContext.openai_param_max_tokens = value
            print("GlobalContext.openai_param_max_tokens = {}".format(value))
            # print("type is {}".format(type(GlobalContext.openai_param_max_tokens)))
        case "temperature":
            GlobalContext.openai_param_temperature = value
            print("GlobalContext.openai_param_temperature = {}".format(value))
        case "top_p":
            GlobalContext.openai_param_top_p = value
            print("GlobalContext.openai_param_top_p = {}".format(value))
        case _:
            print("unknown param name when call [change_Openai_param]")


def execute_QA(user_message):
    GlobalContext.txt_translate_to_languages = language_detection(user_message)
    result = lc_qa_chain({"question": user_message})
    answer = result['answer']
    print(f"\n[Answer]: {answer}")
    # print(f"\n[Sources]: {result['sources']}")
    return answer


def QA_get_msg(user_message):
    GlobalContext.user_message = user_message
    # history = history_remove_br(history)
    return [[user_message, None]]


def QA_set_panel(history):
    qa_message = execute_QA(GlobalContext.user_message)
    # qa_message = qa_message.replace("\\n", "\n")

    GlobalContext.message_for_read_out = qa_message
    output_language = language_detection(qa_message)
    if GlobalContext.txt_translate_to_languages != output_language:
        translated = language_translate(
            qa_message, GlobalContext.txt_translate_to_languages)
        GlobalContext.message_for_read_out = translated
        print("\n[Answer Translated]: {}".format(translated))
        qa_message += f"\n{translated}"

    history[-1][1] = qa_message
    history = history_remove_br(history)
    return "", history


# GlobalContext = GlobalConext()

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2022-12-01"
os.environ["OPENAI_API_BASE"] = GlobalContext.OPENAI_BASE
os.environ["OPENAI_API_KEY"] = GlobalContext.OPENAI_API_KEY

# Load the vector DB.
index = faiss.read_index("./Doc_Store/vectorDB.index")
with open("./Doc_Store/vectorDB.pkl", "rb") as f:
    vectorstore = pickle.load(f)
vectorstore.index = index

# "text-davinci-003"
# intialize ChatVectorDBChain
lc_chatbot_llm = AzureOpenAI(temperature=0, deployment_name="text-davinci-003",
                             model_name="text-davinci-003", max_tokens=800)

lc_chatbot = ChatVectorDBChain.from_llm(lc_chatbot_llm, vectorstore)
lc_chatbot.top_k_docs_for_context = 3
lc_chatbot.return_source_documents = True


# initialize VectorDBQAWithSourcesChain
lc_qa_chain_llm = AzureOpenAI(temperature=0, deployment_name="text-davinci-003",
                              model_name="text-davinci-003", max_tokens=800)
lc_qa_chain = VectorDBQAWithSourcesChain.from_chain_type(
    lc_qa_chain_llm, chain_type="refine", vectorstore=vectorstore, k=3)  # stuffing , map_reduce, refine, map_rerank


with gr.Blocks(theme=gr.themes.Glass()) as demo:
    title = gr.Label("Enterprise KB Chatbot with Voice",
                     label="", color="lightblue")
    chatbot = gr.Chatbot()
    checkbox_for_read = gr.Checkbox(label="Read result atomatically")
    msg = gr.Textbox(
        label="Type your question below or click the voice botton to say")
    with gr.Row():
        clear = gr.Button("Clear")
        clear_and_move_to_history = gr.Button("Clear with Backup")
    with gr.Row():
        radio = gr.Radio(["Say Chinese", "Say English", "Say Chinese output English",
                         "Say English output Chinese"], value="Say Chinese", label="Voice setting")
        record_button = gr.Button("Click Here to Say")

    title_QA = gr.Label("Enterprise KB QA Only",
                        label="", color="lightblue")
    QA_Panel = gr.Chatbot()
    QA_question = gr.Textbox(label="Type your question below")
    gr.Markdown(
        """
    ---
    # 
    ---
    ```
    ** History and Settings **
    ```
    """)
    with gr.Box(visible=False):
        with gr.Row():
            with gr.Column():
                last_round_chatbot = gr.Chatbot(label="Chatbot History")
            with gr.Column():
                with gr.Row():
                    slider_temperature = gr.Slider(
                        0, 1, 0.5, step=0.1, label="Temperature", interactive=True)
                    slider_top_p = gr.Slider(
                        0, 1, 0.7, step=0.1, label="Top_P", interactive=True)
                    slider_max_token = gr.Slider(
                        50, 1050, 250, step=100, label="Max Token", interactive=True)
                txt_system_message = gr.Textbox(
                    GlobalContext.chat_system_message_plain, label="System message for prompt", interactive=True)
                bt_update_system_message = gr.Button(
                    "Update System Message", interactive=False)

    msg.submit(user, [msg, chatbot], chatbot, queue=False).then(
        bot, chatbot, [msg, chatbot]).then(readOuput, None, record_button)
    clear.click(clearHistory, None, chatbot, queue=False)
    clear_and_move_to_history.click(clearHistory_and_backup, chatbot, [
                                    chatbot, last_round_chatbot], queue=False)
    # clear.click(lambda: None, None, chatbot, queue=False)
    record_button.click(lambda: gr.Button.update("Recording...", interactive=False), None, record_button).then(
        startRecording, chatbot, chatbot).then(lambda: "Click Here to Say", None, record_button).then(
        bot, chatbot, [msg, chatbot]).then(readOuput, None, record_button)
    radio.change(fn=radioChage, inputs=radio, outputs=None)
    checkbox_for_read.change(readOutSettingChange, checkbox_for_read)

    QA_question.submit(QA_get_msg, QA_question, QA_Panel, queue=False).then(
        QA_set_panel, QA_Panel, [QA_question, QA_Panel])

    txt_system_message.change(lambda: gr.Button.update(
        interactive=True), None, bt_update_system_message)
    bt_update_system_message.click(
        change_system_message, txt_system_message, chatbot).then(lambda: gr.Button.update(interactive=False), None, bt_update_system_message)

    slider_temperature.change(lambda x: change_Openai_param(
        "temperature", x), slider_temperature, None)
    slider_max_token.change(lambda x: change_Openai_param(
        "max_tokens", x), slider_max_token, None)
    slider_top_p.change(lambda x: change_Openai_param(
        "top_p", x), slider_top_p, None)

# demo.launch(auth=("admin", "pass1234"), share=True)
demo.launch()
