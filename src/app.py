from flask import Flask, request
from models.plate_reader import PlateReader
from PIL import Image
import logging
import io
import requests


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')
URL_IMAGES = 'http://51.250.83.169:7878/images/'

# ip:port/toUpper?s=hello
@app.route('/toUpper')
def to_upper():
    s = request.args['s']
    return {'result': s.upper()}

# ip:port/readNubmer <- img bin
@app.route('/readNumber', methods=["POST"])
def read_number():
    try:
        body = request.get_data()
        im = io.BytesIO(body)
        res = plate_reader.read_text(im)
        return {"name": res}
    except Exception as e:
        logging.error(f"An error occurred while reading number: {e}")
        return {"error": str(e)}, 500

# ip:port/idToNumber?id=10022
@app.route('/idToNumber')
def idToNumber():
    try:
        id = request.args['id']
        url = URL_IMAGES + id 
        response = requests.get(url)
        if response.status_code == 200:
            res = plate_reader.read_text(io.BytesIO(response.content))
            return {id: res}
        else:
            return {"error": f"Failed to get image from server. Server responded with code {response.status_code}"}, 500
    except Exception as e:
        logging.error(f"An error occurred while converting ID to number: {e}")
        return {"error": str(e)}, 500

# ip:port/idsToNumbers?id1=10022&id2=10022&id3=9965
@app.route('/idsToNumbers')
def idsToNumbers():
    ans = {}
    try:
        for k, _ in request.args.to_dict().items():
            id = request.args[k]
            url = URL_IMAGES + id 
            response = requests.get(url)
            if response.status_code == 200:
                ans[k] = plate_reader.read_text(io.BytesIO(response.content))
            else:
                ans[k] = f"Failed to get image from server. Server responded with code {response.status_code}"
        return ans
    except Exception as e:
        logging.error(f"An error occurred while converting IDs to numbers: {e}")
        return {"error": str(e)}, 500


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.run(host='0.0.0.0', port=8080, debug=True)
