import dataset
import joblib
import numpy as np
import umap


N_SAMPLES = 100000  #training data for UMAP model
N_EMBEDDING_DIM = 100 #note this can be between 2-100, lower numbers in general provide better speeds at the cost of lower accuracy

#train our dimensionality reduction model , this assumes the table images is populated with vectors for each image
# sample bernoulli to train a representative model for dimensionality reduction
# we use UMAP - a much faster (and better) approaches than comparable ones such as t-sne - you might need to experiment what works for your case.
def train(db):
    print("[+] fetching training data:")
    sql = "select id,vector from images TABLESAMPLE BERNOULLI(0.5) where vector is not null limit {0}".format(N_SAMPLES)
    train_data = db.query(sql)
    X=[]
    for n,result in enumerate(train_data):
        X.append(result['vector'])

    print("[+] fitting UMAP:")
    embedding = umap.UMAP(n_neighbors=10,
                        n_components=N_EMBEDDING_DIM,
                        min_dist=0.3,
                        metric='correlation').fit(X)
    return embedding

def populate(db):
    print("[+] populating embeddings:")
    model = joblib.load("clf_umap.job")
    page_size = 100
    results = 1
    while results is not None:
            sql = "select id,vectors from images where embeddings is null and vector is not null limit {0}".format(page_size)
            results = db.query(sql)
            X=[]
            y=[]
            for n,result in enumerate(results):
                X.append(result['vectors'])
                y.append(result['id'])

            emb_vect = model.transform(X)
            sql_cmds = []
            for i,p in zip(y,emb_vect):
                emb_string = "({0})".format(','.join("%10.8f" % x for x in p)) # <-- pg fails beyond 100 dimensions for cube, so reduce dimensionality
                sql = "update images set embeddings = {0} where id={1}".format(p,i)

            db.query(';'.join(sql_cmds))
    return 

def find_similar(id):
	
    print ("[+] doing ANN search:")
    emb_string = "'({0})'".format(','.join("%10.8f" % x for x in query_vector))
    sql = "select id,url,vector from images where embeddings <-> cube({0}) < 0.25 order by embeddings <-> cube({0}) asc limit 25".format((emb_string))
    results = db.query(sql)
    for result in results:
        print(result['id'])
        vect = result["vector"] # use for reranking if needed


if __name__ == '__main__':
    db = dataset.connect('postgresql://user:pass@localhost:5432/mydb')
    
    #1. train a umap model and populate db with the embeddings
    model = train(db)
    joblib.dump(model,"clf_umap.job")
    populate(db)

    #2. ANN search table using the embedding 
    query_vector = [0.12178352,....,0.006058750]
    find_similar(query_vector)
