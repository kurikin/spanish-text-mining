import matplotlib as mpl
import os
import re
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from janome.tokenizer import Tokenizer

# 環境変数に認証ファイルのパスを設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
mpl.rcParams['font.family'] = 'Noto Sans JP'


def transcribe_audio(file_name):
    client = speech.SpeechClient()

    with open(file_name, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="es-ES",
    )

    response = client.recognize(config=config, audio=audio)

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
            words.append(tkn[0])

    return ' ' . join(words)


def create_word_cloud(words, output_file):
    font_path = os.path.abspath("NotoSansJP-VariableFont_wght.ttf")

    wordcloud = WordCloud(background_color='white',
                          font_path=font_path, width=800, height=800, prefer_horizontal=1).generate(words)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)

    plt.savefig(output_file)


def main():
    audio_dir = 'audios'
    audio_file_name = input('Enter the name of the audio file: ')

    audio_path = os.path.join(audio_dir, audio_file_name)

    if not os.path.exists(audio_path):
        print(f"The file {audio_file_name} does not exist.")
        return

    print("Transcribing audio...")
    transcribed_text = transcribe_audio(audio_path)
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
