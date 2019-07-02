# pgANN

Approximate Nearest Neighbor with a Postgres backend. 

##Background

Approximate Nearest Neighbor approaches are a powerful tool for various AI/ML tasks, however most existing tools are mostly "in memory". Such tools include `faiss`,`Annoy` etc. The challenge for us was to hold extremely large datasets in memory was challenging, not to mention inserts/updates/deletes which makes it challenging in an "online" environment where fresh data is continuously accumulated.

Today we are open-sourcing a simple, but effective approach that provides ANN using the very popular Postgres database backend. 
We use this tool internally for our image collections and processing and hopefully this is of use to the F/OSS community. 

Feedback and PRs very welcome!

##Advantages

- leverages postgres database queries & indexes
- no additional storage needed, associated metadata is fetched alongwith the "neighbors" (i.e. fewer moving parts)
- no re-training needed for fresh data (CRUDs) due to query time ranking (online mode)
- 

##Challenges

- `cube` type doesn't seem to work for > 100 dimensions, so we need to perform dimensionality reduction. Example included in the code
- haven't tested with sparse vectors, but in theory should work decently with appropriate dimensionality reduction techniques


##Requirements
- Postgres 9.6+ or higher (we have tested on PG 10.x, but cube/GIST/distance operators are available on 9.6+)
- Cube extension from Postgres

##Instructions

1. Make sure you are logged in as superuser into pg and run:
`create extension cube;`

2. We shall use the example of an `images` table to illustrate the approach, the images table stores the url, any metadata tags, vectors and the embeddings for the vectors in the table. You can of course modify table structure to your needs.

```
CREATE TABLE images(
   image_id serial PRIMARY KEY,
   image_url text UNIQUE NOT NULL,
   tags text,
   vectors double precision[],
   emb100 cube   
);
```
