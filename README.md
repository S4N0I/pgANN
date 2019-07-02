# pgANN

Approximate Nearest Neighbor (ANN) searches using a PostgreSQL backend. 

## Background

Approximate Nearest Neighbor approaches are a powerful tool for various AI/ML tasks, however many existing tools ([faiss](https://github.com/facebookresearch/faiss),[Annoy](https://github.com/spotify/annoy), [Nearpy](https://github.com/pixelogik/NearPy) etc.) are "in memory"i.e. the vectors needed to be loaded into RAM, and then model trained therefrom. Furthermore, such models once trained could not be updated i.e. any CRUD operation necessitates a fresh training run.

The challenge for us was to: 
- hold extremely large datasets in memory and 
- support CRUDs which makes it challenging in an "online" environment where fresh data is continuously accumulated.

We are open-sourcing a simple, but effective approach that provides ANN searches using the powerful PostgreSQL database. At [Netra](http://netra.io) we use this tool internally for managing & searching our image collections for further processing and/or feed into our Deep learning models. We consistently see `sub-second` response times on the order of a few million rows on a 32Gb/8 vcpu Ubuntu 16 box. We hope this is of use to the AI community. 

Feedback and PRs very welcome!

## Advantages

- leverages postgres database queries & indexes (no additional tooling needed)
- associated metadata is fetched alongwith the "neighbors" (i.e. fewer moving parts)
- no re-training needed for CRUDs due to query time ranking ("online mode")
- should scale with tried & tested database scaling techniques (partioning etc.)

## Challenges

- `cube` type doesn't seem to work for > [100 dimensions](https://www.postgresql.org/docs/current/cube.html#AEN176262), so we need to perform dimensionality reduction. Example for dim. reduction included in the sample code
- haven't tested with sparse vectors, but in theory should work decently with appropriate dimensionality reduction techniques
- pgANN might *not* perform as accurately as some of the better known approaches, but you can use pgANN to fetch a subset of (say) a fw thousand and then `rerank` based on your favorite metric. Unfortunately, there are no easy wins in ANN approaches, hopefully pgANN gets you a "good enough" subset for your reranking.

## Requirements
- Postgres 10.x+ or higher (we haven't tested on PG 9.6+, but `cube`,`GIST` and distance operators are available on 9.6+, so it *might* work)
- Cube extension from Postgres

## Setup

1. Make sure you are logged in as superuser into pg and run:
`create extension cube;`

2. We shall use the example of an `images` table to illustrate the approach, the images table stores the url, any metadata tags, vectors and the embeddings for the vectors in the table. You can of course modify table structure to your needs.

```
CREATE TABLE images(
   id serial PRIMARY KEY,
   image_url text UNIQUE NOT NULL,
   tags text,
   vectors double precision[],
   embeddings cube   
);
```
3. Create a GIST index on the embeddings column which stores a 100-dimensional embedding of the original vector:

`create index ix_gist on images using GIST (embeddings);`

_Note: you might need to create other indexes (b-tree etc.) on other fields for efficient searching & sorting, but that's outside our scope_

## Populating db
Now we are ready to populate the database with  vectors and associated embeddings. 

_Note: we are using the [dataset](https://dataset.readthedocs.io/en/latest/) library for interfacing with postgres, but this should work just as well with your favorite driver (psycopg2 etc.)_

```
db = dataset.connect('postgresql://user:pass@@localhost:5432/yourdb')
tbl = db['images']

for image in images:
   vect = get_image_vector(image) # <-- use imagenet or such model to generate a vector from one of the final layers
   emb_vect = get_embedding(vect)
   emb_string = "({0})".format(','.join("%10.8f" % x for x in emb_vect)) # <-- pg fails beyond 100 dimensions for cube, so reduce dimensionality
   row_dict["embeddings"] = emb_string
   row_dict["vectors"] = vect.tolist()
   row_id = tbl.insert(row_dict)
```

## Querying
We can start querying the database even as population is in progress

```
    query_vector = [...]
    query_emb = get_embedding(query_vector)
    thresh = 0.25 # <-- making this larger will likely give more relevant results at the expense of time
	

    print ("[+] doing ANN search:")
    emb_string = "'({0})'".format(','.join("%10.8f" % x for x in query_emb))
    sql = "select id,url,tags from images where embeddings <-> cube({0}) < thresh order by embeddings <-> cube({0}) asc limit 10".format((emb_string))
    results = db.query(sql)
    for result in results:
      print(result['url'], result['tags'])
  
  ```
  
  Note: pgsql cube extension supports multiple distance parameters. Here is a quick summary:
  
 - `<-> Euclidean distance`, 
 - `<=> Chebyshev (L-inf metric) distance`, and 
 - `<#> Taxicab distance`.
  
  More details [here](https://www.postgresql.org/docs/10/cube.html).
  
 
