from flask import Flask, request, jsonify, render_template, redirect, url_for
from elasticsearch_client import connect_elasticsearch

app = Flask(__name__)

def search_trendyol_index(es, query, index_name="trendyol"):
    search_param = {
        "query": {
            "bool":{
                "must":[
                    {"multi_match": {
                "query": query,
                "fields": ["Price", "Name", "Title"],
                "operator":"and"
                             
            }
            }
            ]
            
            }
        }
    } 

    try:
        response = es.search(index=index_name, body=search_param, size=1000)
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            source['_id'] = hit['_id']  # Elasticsearch ID'sini kaydediyoruz
            results.append(source)
        return results
    except Exception as e:
        print(f"Arama sırasında bir hata oluştu: {e}")
        return []

@app.route('/')
def index():
    es = connect_elasticsearch()
    if not es:
        return "Elasticsearch bağlantısı kurulamadı.", 500

    results = search_trendyol_index(es, "")
    return render_template('index.html', results=results)

@app.route('/add_data')
def add_data_page():
    return render_template('add_data.html')

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    es = connect_elasticsearch()
    if not es:
        return jsonify({"error": "Elasticsearch bağlantısı kurulamadı."}), 500

    try:
        response = es.index(index="trendyol", document=data)
        if 'result' in response and response['result'] == 'created':
            return jsonify({"message": "Veri başarıyla eklendi.", "response": response}), 200
        else:
            return jsonify({"error": "Veri eklenirken beklenmedik bir yanıt alındı.", "response": response}), 500
    except Exception as e:
        print(f"Veri eklerken bir hata oluştu: {e}")
        return jsonify({"error": f"Veri eklenirken bir hata oluştu: {e}"}), 500

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')

    if not query:
        return jsonify({"error": "Lütfen bir arama sorgusu girin."}), 400

    es = connect_elasticsearch()
    if not es:
        return jsonify({"error": "Elasticsearch bağlantısı kurulamadı."}), 500

    results = search_trendyol_index(es, query)
    if not results:
        return jsonify({"message": "Hiçbir sonuç bulunamadı."}), 404

    return jsonify(results), 200

@app.route('/delete/<id>', methods=['DELETE'])
def delete_data(id):
    es = connect_elasticsearch()
    if not es:
        return jsonify({"error": "Elasticsearch bağlantısı kurulamadı."}), 500

    try:
        response = es.delete(index="trendyol", id=id)
        if 'result' in response and response['result'] == 'deleted':
            return jsonify({"message": "Veri başarıyla silindi.", "response": response}), 200
        else:
            return jsonify({"error": "Veri silinirken beklenmedik bir yanıt alındı.", "response": response}), 500
    except Exception as e:
        print(f"Veri silinirken bir hata oluştu: {e}")
        return jsonify({"error": f"Veri silinirken bir hata oluştu: {e}"}), 500

@app.route('/update/<id>', methods=['GET', 'POST'])
def update_data(id):
    es = connect_elasticsearch()
    if not es:
        return jsonify({"error": "Elasticsearch bağlantısı kurulamadı."}), 500

    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            response = es.update(index="trendyol", id=id, body={"doc": data})
            if 'result' in response and response['result'] == 'updated':
                return redirect(url_for('index'))
            else:
                return jsonify({"error": "Veri güncellenirken beklenmedik bir yanıt alındı.", "response": response}), 500
        except Exception as e:
            print(f"Veri güncellenirken bir hata oluştu: {e}")
            return jsonify({"error": f"Veri güncellenirken bir hata oluştu: {e}"}), 500
    else:
        try:
            response = es.get(index="trendyol", id=id)
            if response['found']:
                return render_template('update_data.html', data=response['_source'], id=id)
            else:
                return jsonify({"error": "Veri bulunamadı."}), 404
        except Exception as e:
            print(f"Veri getirilirken bir hata oluştu: {e}")
            return jsonify({"error": f"Veri getirilirken bir hata oluştu: {e}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
