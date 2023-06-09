import matplotlib as mpl
import os
import re
from os.path import join, dirname
from dotenv import load_dotenv
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from janome.tokenizer import Tokenizer

# 環境変数に認証ファイルのパスを設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
mpl.rcParams['font.family'] = 'Noto Sans JP'


def transcribe_audio():
    client = speech.SpeechClient()


    # audio = speech.RecognitionAudio(content=content)
    uri = os.environ.get("AUDIO_URI")
    audio = speech.RecognitionAudio(uri=uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="es-ES",
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript


def translate_text(text):
    translate_client = translate.Client()

    result = translate_client.translate(text, target_language='ja')

    return result['translatedText']


def extract_words(text, exclusion=[]):
    token = Tokenizer().tokenize(text)
    words = []

    for line in token:
        tkn = re.split('\t|,', str(line))
        if (tkn[1] in ['名詞'] and tkn[2] in ['一般', '固有名詞']) or (tkn[1] in ['動詞', '形容詞']):
            words.append(tkn[7])

    return ' ' . join(words)


def create_word_cloud(words, output_file):
    font_path = os.path.abspath("NotoSansJP-VariableFont_wght.ttf")

    wordcloud = WordCloud(background_color='white',
                          font_path=font_path, width=2000, height=1500, prefer_horizontal=1, margin=10).generate(words)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)

    plt.savefig(output_file)


def main():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    transcribed_text = transcribe_audio()
    print(transcribed_text)

    with open('transcribed_text_es.txt', 'w') as f:
        f.write(transcribed_text)

    print("Translating text...")
    translated_text = translate_text(transcribed_text)
    with open('translated_text_ja.txt', 'w') as f:
        f.write(translated_text)

    words = extract_words(translated_text)

    print("Creating word cloud...")
    create_word_cloud(words, 'word_cloud.png')


if __name__ == "__main__":
    main()
