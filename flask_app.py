from flask import Flask, request, jsonify, render_template, redirect, url_for
from elasticsearch_client import connect_elasticsearch

app = Flask(__name__)

def search_trendyol_index(es, query, min_price=None, max_price=None, index_name="trendyol_trendyol"):
    query_terms = query.split()

    must_queries = [
        {
            "bool": {
                "should": [
                    {"match": {"Title": term}},
                    {"match": {"Name": term}},
                ]
            }
        } for term in query_terms
    ]

    if min_price is not None or max_price is not None:
        price_range_query = {"range": {"Price": {}}}
        if min_price is not None:
            price_range_query["range"]["Price"]["gte"] = min_price
        if max_price is not None:
            price_range_query["range"]["Price"]["lte"] = max_price
        must_queries.append(price_range_query)

    search_param = {
        "query": {
            "bool": {
                "must": must_queries
            }
        }
    }

    try:
        response = es.search(index=index_name, body=search_param, size=1000)
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            source['_id'] = hit['_id']
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

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    min_price = request.args.get('minPrice')
    max_price = request.args.get('maxPrice')

    # Convert min_price and max_price to floats if they are provided
    min_price = float(min_price) if min_price else None
    max_price = float(max_price) if max_price else None

    if not query:
        return jsonify({"error": "Lütfen bir arama sorgusu girin."}), 400

    es = connect_elasticsearch()
    if not es:
        return jsonify({"error": "Elasticsearch bağlantısı kurulamadı."}), 500

    results = search_trendyol_index(es, query, min_price, max_price)
    if not results:
        return jsonify({"message": "Hiçbir sonuç bulunamadı."}), 404

    return jsonify(results), 200

@app.route('/delete/<id>', methods=['DELETE'])
def delete_data(id):
    es = connect_elasticsearch()
    if not es:
        return jsonify({"error": "Elasticsearch bağlantısı kurulamadı."}), 500

    try:
        response = es.delete(index="trendyol_trendyol", id=id)
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
            response = es.update(index="trendyol_trendyol", id=id, body={"doc": data})
            if 'result' in response and response['result'] == 'updated':
                return redirect(url_for('index'))
            else:
                return jsonify({"error": "Veri güncellenirken beklenmedik bir yanıt alındı.", "response": response}), 500
        except Exception as e:
            print(f"Veri güncellenirken bir hata oluştu: {e}")
            return jsonify({"error": f"Veri güncellenirken bir hata oluştu: {e}"}), 500
    else:
        try:
            response = es.get(index="trendyol_trendyol", id=id)
            if response['found']:
                return render_template('update_data.html', data=response['_source'], id=id)
            else:
                return jsonify({"error": "Veri bulunamadı."}), 404
        except Exception as e:
            print(f"Veri getirilirken bir hata oluştu: {e}")
            return jsonify({"error": f"Veri getirilirken bir hata oluştu: {e}"}), 500

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)