'''
Created on 2013-3-7 common helper
'''
# import faiss
# from langchain.llms import AzureOpenAI
# from langchain.chains import (ChatVectorDBChain, VectorDBQAWithSourcesChain)
# import pickle
# import gradio as gr
# import os
import tiktoken
import azure.cognitiveservices.speech as speechsdk
import requests
import uuid
import json
# from dotenv import load_dotenv

from GlobalClasses import GlobalContext

# load_dotenv()
# GlobalContext()  # initialize global context


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


def get_rough_token_len(content):
    '''  Encoding reference:

    # chat
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    # text
    "text-davinci-003": "p50k_base",
    "text-davinci-002": "p50k_base",
    "text-davinci-001": "r50k_base",
    "text-curie-001": "r50k_base",
    "text-babbage-001": "r50k_base",
    "text-ada-001": "r50k_base",
    "davinci": "r50k_base",
    "curie": "r50k_base",
    "babbage": "r50k_base",
    "ada": "r50k_base",
    # code
    "code-davinci-002": "p50k_base",
    "code-davinci-001": "p50k_base",
    "code-cushman-002": "p50k_base",
    "code-cushman-001": "p50k_base",
    "davinci-codex": "p50k_base",
    "cushman-codex": "p50k_base",
    # edit
    "text-davinci-edit-001": "p50k_edit",
    "code-davinci-edit-001": "p50k_edit",
    # embeddings
    "text-embedding-ada-002": "cl100k_base",
    # old embeddings
    "text-similarity-davinci-001": "r50k_base",
    "text-similarity-curie-001": "r50k_base",
    "text-similarity-babbage-001": "r50k_base",
    "text-similarity-ada-001": "r50k_base",
    "text-search-davinci-doc-001": "r50k_base",
    "text-search-curie-doc-001": "r50k_base",
    "text-search-babbage-doc-001": "r50k_base",
    "text-search-ada-doc-001": "r50k_base",
    "code-search-babbage-code-001": "r50k_base",
    "code-search-ada-code-001": "r50k_base",
    # open source
    "gpt2": "gpt2",
    '''
    enc = tiktoken.encoding_for_model("text-davinci-003")
    tokens = enc.encode(content)
    return len(tokens)


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
