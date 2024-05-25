import pandas as pd
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

csv_file_path = 'Trendyol_Trendyol.csv'
df = pd.read_csv(csv_file_path)

index_name = 'trendyollololo'

mappings = {
    "mappings": {
        "_meta": {
            "created_by": "file-data-visualizer"
        },
        "properties": {
            "Id": {
                "type": "long"
            },
            "Image": {
                "type": "keyword"
            },
            "Name": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "Price": {
                "type": "keyword"
            },
            "Title": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            }
        }
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mappings)

def csv_to_elasticsearch(df, index_name):
    actions = [
        {
            "_index": index_name,
            "_source": row.to_dict()
        }
        for i, row in df.iterrows()
    ]
    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    print(f"Başarılı: {success}, Başarısız: {len(failed)}")
    if failed:
        print("Başarısız olanlar:")
        for fail in failed:
            print(fail)

csv_to_elasticsearch(df, index_name)

print("Veriler başarıyla Elasticsearch'e yüklendi!")
