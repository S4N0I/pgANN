# pgANN

Approximate Nearest Neighbor with a Postgres backend. 

##Background

Approximate Nearest Neighbor approaches are a powerful tool for various AI/ML tasks, however most existing tools are mostly "in memory". Such tools include `faiss`,`Annoy` etc. The challenge for us was to hold extremely large datasets in memory was challenging, not to mention inserts/updates/deletes which makes it challenging in an "online" environment where fresh data is continuously accumulated.

Today we are open-sourcing a simple, but effective approach that provides ANN using the very popular Postgres database backend. 
We use this tool internally for our image collections and processing and hopefully this is of use to the F/OSS community. Feedback and PRs very welcome!

##Advantages

- works ex-memory and leverages database indexes for querying & storage
- no additional storage needed, metadata is fetched with the nearest neighbors (i.e. fewer moving parts)

