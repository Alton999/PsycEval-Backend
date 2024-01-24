from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from openai import OpenAI
import os
app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})




client = OpenAI(
    api_key=OPENAI_API_KEY
)


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():  # put application's code here
    print("New api endpoint")
    print("Files", request.files)
    # print("Should be a string", request.form.get('filename'))
    # print("Checking for files", request.files['file'].filename)
    if 'file' not in request.files:
        print("No files found")
        return jsonify({'error': 'No file part'}), 400

    filestorage = request.files['file']
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_file_path = os.path.join(temp_dir, filestorage.filename)
    print("Found file executing", filestorage.filename)
    print("audio_file", filestorage)
    # print("Content:", content)
    try:
        # Temp save of file to local
        filestorage.save(temp_file_path)

        # Transcribe the saved file
        with open(temp_file_path, "rb") as audio_file:
            print("Audio file", audio_file)
            transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        os.remove(temp_file_path)
        print("Transcript", transcription.text)
        return jsonify(transcription.text)
    except Exception as e:
        # ensures path is deleted even if fails
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print("Error during transcription: ", str(e))
        return jsonify({'Error': 'Failed to transcribe the audio'}, str(e))


@app.route('/count-animals', methods=["POST"])
def count_animals():
    transcription = request.form.get("transcription")
    print("Transcription from count-animals", transcription)
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a assistant that takes an input transcription and counts the number of unique animal species in this transcription. Names and other items are NOT animals. Output in JSON format with a list of unique animals and the total count."},
            {"role": "user", "content": "In this transcription how many unique animals are there?" + transcription},

        ],
        response_format={"type": "json_object"}
    )
    print("Number of animals", completion.choices[0].message.content)
    return jsonify(completion.choices[0].message.content)


if __name__ == '__main__':
    app.run(host="192.168.1.90", port=8081)
    app.run(debug=True)
