import pandas as pd
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

csv_file_path = '../web_scraping/Trendyol_Trendyol.csv'
df = pd.read_csv(csv_file_path)

index_name = 'trendyol_trendyol2'

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
                "type": "float"
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

def clean_price(price_str):
    price_str = price_str.replace('TL', '')
    price_str = price_str.replace('.', '')
    price_str = price_str.strip()
    price_str = price_str.replace('"', '')
    price_str = price_str.replace(',', '.')
    return float(price_str)


def csv_to_elasticsearch(df, index_name):
    df['Price'] = df['Price'].apply(clean_price)
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
