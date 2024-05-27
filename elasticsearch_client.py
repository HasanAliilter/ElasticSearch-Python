from elasticsearch import Elasticsearch

def connect_elasticsearch():
    es = Elasticsearch(["http://localhost:9200"])
    if es.ping():
        print("Bağlantı başarılı!")
    else:
        print("Bağlantı başarısız!")
    return es
